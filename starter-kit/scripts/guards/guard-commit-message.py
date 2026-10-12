# -*- coding: utf-8 -*-
"""Страж сообщения коммита: политика проекта из guards.conf, приватные данные, пустое сообщение.

Зачем: сообщения коммитов остаются в публичной истории навсегда; подпись, язык, трейлеры и
    приватные данные в них проверяются до коммита и до пуша, а не по просьбе.
Проверяет: сообщение в смысле «что git сохранит» (lib/message.py). По политике проекта: signoff —
    при COMMIT_SIGNOFF=required строка «Signed-off-by» есть и совпадает с автором (имя и адрес);
    forbidden-trailer — нет трейлеров из COMMIT_FORBIDDEN_TRAILERS (без учёта регистра); non-ascii —
    при COMMIT_ASCII_ONLY=yes только ASCII, кроме строк цитаты на «>»; expected-email — при
    COMMIT_AUTHOR_EMAIL_CHECK=yes адрес автора равен git config <EXPECTED_EMAIL_KEY> (пишет
    установщик; нет настройки — красный «запусти установщик»). Всегда: author-name — имя автора не
    пусто; machine-path и forbidden-name — нет пути машины и образца из списка запрещённых имён (в том
    числе в строках на «#» при -m и -F и на «>»); empty-message — сообщение не пусто. Вердикт называет
    «сообщение коммита», строку и номер образца, не значение.
Не проверяет: содержание diff, который редактор показывает при -v; прошлые коммиты; правку истории.
    В режиме --ci правило expected-email не применимо (установщик в CI не запускается) и печатает
    «судить нечего: CI, нет настройки установщика»; адрес автора там сверяется с подписью.
Правило: README комплекта, «Сообщение коммита».

Вызов из хука commit-msg: --message-file <путь> --mode editor|message (режим задаёт обёртка хука по
GIT_EDITOR, сам страж среды не читает). Для pre-push и CI: --commit <хеш> (сообщение как сохранено),
CI добавляет --ci.
"""
import sys

sys.dont_write_bytecode = True

import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import conf as confmod  # noqa: E402
import guardlib  # noqa: E402
import machine_paths  # noqa: E402
import message  # noqa: E402
import names  # noqa: E402

SIGNOFF = re.compile(r"^\s*Signed-off-by:\s*(.*?)\s*<([^<>]*)>\s*$", re.I)
IDENT = re.compile(r"^(.*) <([^<>]*)> \d+ [+-]\d{4}$")


def author_of(source, args):
    """(имя, адрес) автора: у готового коммита — из него, в хуке — из git var GIT_AUTHOR_IDENT."""
    if args.commit:
        out = guardlib.git(source.root, "show", "-s", "--format=%an%n%ae", args.commit)
        parts = out.decode("utf-8", "replace").rstrip("\n").split("\n")
        return (parts[0] if parts else ""), (parts[1] if len(parts) > 1 else "")
    out = guardlib.git(source.root, "var", "GIT_AUTHOR_IDENT", check=False).decode("utf-8", "replace").strip()
    m = IDENT.match(out)
    return (m.group(1), m.group(2)) if m else ("", "")


def config_value(source, *keys):
    out = guardlib.git(source.root, "config", *keys, check=False)
    return out.decode("utf-8", "replace").strip()


def message_lines(source, args):
    """Строки сообщения [(номер, текст)] в смысле «что git сохранит»."""
    if args.commit:
        raw = guardlib.git(source.root, "show", "-s", "--format=%B", args.commit).decode("utf-8", "replace")
        lines = [(i, line.rstrip("\r")) for i, line in enumerate(raw.split("\n"), 1)]
        while lines and not lines[-1][1].strip():
            lines.pop()
        return lines
    try:
        with open(args.message_file, "rb") as handle:
            raw = handle.read().decode("utf-8", "replace")
    except OSError:
        raise guardlib.Unavailable("не читается файл сообщения коммита")
    verbose = config_value(source, "--bool", "commit.verbose") == "true"
    comment = config_value(source, "core.commentChar")
    if len(comment) != 1:
        comment = "#"
    return message.effective_message(raw, args.mode, verbose, comment)


def check_signoff(label, lines, author, rep):
    signoffs = [(m.group(1), m.group(2)) for m in (SIGNOFF.match(t) for _, t in lines) if m]
    if not signoffs:
        rep.add(label, None, "signoff-missing", "нет строки Signed-off-by (git commit -s)")
    elif (author[0], author[1]) not in signoffs:
        rep.add(label, None, "signoff-author", "подпись не совпадает с автором коммита (имя и адрес)")


def check_trailers(label, lines, trailers, rep):
    if not trailers:
        return
    pattern = re.compile(r"^\s*(%s)\s*:" % "|".join(re.escape(t) for t in trailers), re.I)
    for number, text in lines:
        m = pattern.match(text)
        if m:
            rep.add(label, number, "forbidden-trailer", "трейлер %s запрещён политикой проекта" % m.group(1))


def check_author(label, author, rep):
    if not author[0].strip():
        rep.add(label, None, "author-name", "имя автора пусто")


def check_email(label, author, expected, ci, key, installer, rep):
    if ci:
        rep.accept(label, None, "expected-email", "судить нечего: CI, нет настройки установщика")
    elif not expected:
        rep.add(label, None, "expected-email",
                "нет настройки %s: запусти установщик (sh %s)" % (key, installer))
    elif author[1] != expected:
        rep.add(label, None, "expected-email", "адрес автора не совпадает с ожидаемым установщиком")


def check_ascii(label, lines, rep):
    for number, text in lines:
        if text.startswith(">"):
            continue
        if any(ord(ch) > 127 for ch in text):
            rep.add(label, number, "non-ascii", "не ASCII вне строк цитаты (политика проекта: только ASCII)")


def check_private(label, lines, patterns, rep):
    for number, text in lines:
        for kind in machine_paths.find_machine_paths(text):
            rep.add(label, number, "machine-path", "путь машины (%s)" % kind)
        for sample in names.find_names(text, patterns):
            rep.add(label, number, "forbidden-name", "образец №%d" % sample)


def judge(source, args, rep):
    if bool(args.commit) == bool(args.message_file):
        raise guardlib.Unavailable("укажите либо --message-file и --mode, либо --commit")
    if args.message_file and not args.mode:
        raise guardlib.Unavailable("с --message-file нужен --mode editor|message")
    conf = confmod.Conf()
    signoff = conf.get("COMMIT_SIGNOFF") == "required"
    trailers = conf.words("COMMIT_FORBIDDEN_TRAILERS")
    ascii_only = conf.get("COMMIT_ASCII_ONLY") == "yes"
    email_check = conf.get("COMMIT_AUTHOR_EMAIL_CHECK") == "yes"
    label = "сообщение коммита"
    if args.commit:
        short = guardlib.git(source.root, "rev-parse", "--short=7", args.commit).decode().strip()
        label += " " + short
    patterns = names.load_names(conf)
    lines = message_lines(source, args)
    if not lines:
        rep.add(label, None, "empty-message", "сообщение пусто")
        return guardlib.Outcome(count=1)
    author = author_of(source, args)
    if signoff:
        check_signoff(label, lines, author, rep)
    check_trailers(label, lines, trailers, rep)
    check_author(label, author, rep)
    if email_check:
        key = conf.get("EXPECTED_EMAIL_KEY")
        expected = config_value(source, "--get", key)
        check_email(label, author, expected, args.ci, key, conf.get("INSTALLER"), rep)
    if ascii_only:
        check_ascii(label, lines, rep)
    check_private(label, lines, patterns, rep)
    return guardlib.Outcome(count=1)


def extra(parser):
    parser.add_argument("--message-file")
    parser.add_argument("--mode", choices=("editor", "message"))


if __name__ == "__main__":
    sys.exit(guardlib.run("guard-commit-message", "сообщений", judge, extra=extra))
