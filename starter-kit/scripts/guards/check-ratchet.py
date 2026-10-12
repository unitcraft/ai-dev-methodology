# -*- coding: utf-8 -*-
"""Храповик долга: поимённая база нарушений другого стража, которая может только убывать.

Зачем: страж, включённый в проекте с накопленными нарушениями, красный с первого дня, и его выключают
    или обходят; храповик принимает старые нарушения поимённо, с причиной, и не пускает новые. Без
    поимённой базы «долг не растёт» держался бы на счёте, а счёт не видит подмену: одно нарушение
    исправлено, другое внесено, число то же.
Проверяет: прогоняет каждого стража из RATCHET_GUARD (guards.conf) тем же источником (дерево, --index,
    --commit), забирает его находки «FAIL файл:строка: правило: описание» и сверяет с базой
    RATCHET_BASELINE: находка без записи — красный с адресом (ratchet-new) и готовым ключом; запись,
    чьей находки нет, — красный «запись устарела» (ratchet-stale); запись похожа на секрет или путь
    машины (правила guard-secrets.py) — красный (ratchet-secret); строка не по форме, без причины,
    повтор ключа — красный (ratchet-format); запись для стража не из RATCHET_GUARD — красный
    (ratchet-unwired). Зелёный прогон печатает долг: число записей, чьи нарушения на месте. Ключ
    записи — «<страж>:<путь>:<правило>:<хэш>[#n]», хэш — первые 8 знаков SHA-256 нарушающей строки без
    пробелов по краям (у находки без строки — описания); номер строки в ключ не входит, вставка строк
    выше нарушения ключ не меняет, правка самой строки — меняет; #n различает одинаковые строки
    файла по порядку.
Не проверяет: сами правила (их судит оборачиваемый страж); в режиме --commit — записи файлов, которые
    коммит не меняет (их судят дерево в CI и индекс в pre-commit). Оборачиваемый страж не найден,
    красный по предпосылке или с потерянной мишенью, ответ его не разобран — красный, а не «ок».
    Нет файла базы при включённом храповике — мишень потеряна. RATCHET_GUARD=off — «судить нечего»,
    если база пуста, и красный, если в ней остались записи.
Правило: docs/guards.md (README комплекта), «Храповик долга»: новое нарушение не входит в базу молча,
    исправленное убирается из базы тем же изменением; пометка guard-allow и проверка добавленных строк —
    не храповик.
"""
import sys

sys.dont_write_bytecode = True

import hashlib
import importlib.util
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))

import conf as confmod  # noqa: E402
import guardlib  # noqa: E402
from guardlib import Unavailable  # noqa: E402

GUARD = "check-ratchet"
FINDING_RE = re.compile(r"^FAIL (.+?)(?::(\d+))?: ([a-z0-9-]+): (.*)$")
COUNT_RE = re.compile(r"^FAIL: \S+: (\d+) нарушений$")
ENTRY_RE = re.compile(r"^(?P<key>(?P<guard>check-[A-Za-z0-9_-]+\.(?:py|sh)):(?P<path>.+?):[a-z0-9-]+:"
                      r"[0-9a-f]{8}(?:#[0-9]+)?):(?P<reason>.*)$")
KEY_FORM = "<страж>:<путь>:<правило>:<хэш>[#n]"


class Lost(Exception):
    """Мишень потеряна: красный «FAIL: мишень потеряна»."""


def secret_rules():
    """Правила строки стража секретов (judge_line); не загружается — красная предпосылка."""
    path = os.path.join(HERE, "guard-secrets.py")
    try:
        spec = importlib.util.spec_from_file_location("guard_secrets", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.judge_line
    except (Exception, SystemExit):
        raise Unavailable("страж секретов guard-secrets.py не загружается: базу нечем проверить на секреты")


def run_wrapped(name, source, args):
    """Прогон стража под храповиком: (вид вердикта, находки, вердикт). Вид: ok, fail, nothing, skip."""
    path = os.path.join(HERE, name)
    if not os.path.isfile(path):
        raise Unavailable("страж %s из RATCHET_GUARD не найден в папке стражей" % name)
    cmd = [sys.executable, path] if name.endswith(".py") else ["sh", path]
    cmd += ["--root", source.root]
    if source.mode == "index":
        cmd.append("--index")
    elif source.mode == "commit":
        cmd += ["--commit", source.commit]
    if args.ci:
        cmd.append("--ci")
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    except OSError as exc:
        raise Unavailable("страж %s не запускается (%s)" % (name, exc.__class__.__name__))
    lines = [x for x in proc.stdout.decode("utf-8", "replace").replace("\r\n", "\n").split("\n") if x.strip()]
    verdict = lines[-1] if lines else ""
    findings = []
    for line in lines[:-1]:
        m = FINDING_RE.match(line)
        if m:
            findings.append((m.group(1), int(m.group(2)) if m.group(2) else None, m.group(3), m.group(4)))
    rc = proc.returncode
    if rc == 0 and not findings:
        for prefix, kind in (("ок: ", "ok"), ("судить нечего: ", "nothing"), ("пропущено: ", "skip")):
            if verdict.startswith(prefix):
                return kind, findings, verdict
    m = COUNT_RE.match(verdict)
    if rc == 1 and m and int(m.group(1)) == len(findings):
        return "fail", findings, verdict
    if verdict.startswith("FAIL: мишень потеряна"):
        raise Lost("страж %s: %s" % (name, verdict[len("FAIL: мишень потеряна: "):]))
    raise Unavailable("страж %s не судил: %s (код %d)" % (name, verdict or "вердикта нет", rc))


def keyed(guard, findings, source, by_path):
    """Ключи находок стража: {ключ: (путь, строка, правило, описание)}."""
    cache = {}
    base = []
    for path, line, rule, desc in sorted(findings, key=lambda f: (f[0], f[2], f[1] or 0, f[3])):
        material = None
        if line is not None and path in by_path:
            if path not in cache:
                cache[path] = (source.read(by_path[path]) or b"").split(b"\n")
            rows = cache[path]
            if 1 <= line <= len(rows):
                material = rows[line - 1].strip()
        if material is None:
            material = ("описание: " + desc).encode("utf-8")
        digest = hashlib.sha256(material).hexdigest()[:8]
        base.append(("%s:%s:%s:%s" % (guard, path, rule, digest), (path, line, rule, desc)))
    out = {}
    seen = {}
    for key, finding in base:
        seen[key] = seen.get(key, 0) + 1
        out[key if seen[key] == 1 else "%s#%d" % (key, seen[key])] = finding
    return out


def read_baseline(source, by_path, path, wrapped, rep):
    """Записи базы {ключ: (номер строки, путь нарушения, причина)} или None, если файла нет."""
    if path not in by_path:
        return None
    data = source.read(by_path[path])
    if data is None:
        return None
    judge_line = secret_rules()
    entries = {}
    for number, raw in enumerate(data.decode("utf-8", "replace").split("\n"), 1):
        line = raw.rstrip("\r")
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        risky = judge_line(line, False)
        if risky:
            rep.add(path, number, "ratchet-secret",
                    "запись похожа на секрет или путь машины (%s): в базе только ключ и причина словами, без значений"
                    % ", ".join(sorted(set(rule for rule, _ in risky))))
            continue
        m = ENTRY_RE.match(text)
        if not m:
            rep.add(path, number, "ratchet-format", "строка не вида «<ключ>: <причина>», ключ — " + KEY_FORM)
            continue
        key, reason = m.group("key"), m.group("reason").strip()
        if not reason:
            rep.add(path, number, "ratchet-format", "запись без причины: " + key)
        elif key in entries:
            rep.add(path, number, "ratchet-format", "ключ повторяется (впервые — строка %d)" % entries[key][0])
        elif m.group("guard") not in wrapped:
            rep.add(path, number, "ratchet-unwired",
                    "запись для стража %s, которого нет в RATCHET_GUARD: исправьте нарушения и уберите записи "
                    "или подключите стража" % m.group("guard"))
        else:
            entries[key] = (number, m.group("path"), reason)
    return entries


def judge(source, args, rep, notes):
    conf = confmod.Conf()
    wrapped = conf.get("RATCHET_GUARD")
    base_path = conf.get("RATCHET_BASELINE")
    if wrapped == ["off"]:
        wrapped = []
    by_path = dict((e.path, e) for e in source.entries())
    entries = read_baseline(source, by_path, base_path, wrapped, rep)
    if not wrapped:
        return "nothing", "храповик не подключён ни к одному стражу (RATCHET_GUARD=off в guards.conf)"
    if entries is None:
        raise Lost("нет файла базы %s (RATCHET_BASELINE) в источнике; новый проект начинает с пустого файла под git"
                   % base_path)
    scope = set(e.path for e in source.changed()) if source.mode == "commit" else None
    judged = 0
    debt = 0
    idle = []
    for name in wrapped:
        kind, findings, verdict = run_wrapped(name, source, args)
        if kind in ("nothing", "skip"):
            idle.append((kind, "%s: %s" % (name, verdict)))
            if kind == "skip":
                continue
        else:
            judged += 1
        found = keyed(name, findings, source, by_path)
        own_debt = 0
        for key in sorted(found):
            path, line, rule, desc = found[key]
            if key in entries:
                own_debt += 1
                rep.accept(path, line, rule, "долг: " + entries[key][2])
            else:
                rep.add(path, line, "ratchet-new", "новое нарушение стража %s (%s: %s); ключ для базы: %s"
                        % (name, rule, desc, key))
        for key in sorted(entries, key=lambda k: entries[k][0]):
            number, path, _ = entries[key]
            if not key.startswith(name + ":") or key in found:
                continue
            if scope is not None and path not in scope:
                continue
            rep.add(base_path, number, "ratchet-stale",
                    "запись устарела: исправленное убирается из базы тем же изменением (%s)" % key)
        debt += own_debt
        notes.append("%s: долг %d; вердикт стража: %s" % (name, own_debt, verdict))
    if not judged:
        kinds = set(kind for kind, _ in idle)
        reason = "; ".join(text for _, text in idle)
        return ("skip" if "skip" in kinds else "nothing"), "стражи под храповиком не судили: " + reason
    if any(kind == "skip" for kind, _ in idle):
        return "skip", "часть стражей под храповиком пропущена: " + "; ".join(t for k, t in idle if k == "skip")
    if scope is not None:
        return "ok", "ок: осмотрено %d стражей под храповиком (файлы коммита); долг в файлах коммита: %d" % (judged, debt)
    return "ok", "ок: осмотрено %d стражей под храповиком; долг: %d" % (judged, debt)


def main(argv=None):
    guardlib.setup_io()
    args = guardlib.build_parser(prog=GUARD).parse_args(argv)
    rep = guardlib.Report()
    notes = []
    try:
        source = guardlib.open_source(args)
    except Unavailable as exc:
        return guardlib.finish([], "FAIL: предпосылка: %s" % exc, 1)
    try:
        try:
            kind, text = judge(source, args, rep, notes)
        finally:
            source.close()
    except Unavailable as exc:
        return guardlib.finish(notes + rep.lines(), "FAIL: предпосылка: %s" % exc, 1)
    except Lost as exc:
        return guardlib.finish(notes + rep.lines(), guardlib.no_target(str(exc)), 1)
    lines = notes + rep.lines()
    if rep.findings:
        return guardlib.finish(lines, guardlib.fail(GUARD, len(rep.findings)), 1)
    if kind == "skip":
        return guardlib.finish(lines, guardlib.skipped(text), 0)
    if kind == "nothing":
        return guardlib.finish(lines, guardlib.nothing_to_judge(text), 0)
    return guardlib.finish(lines, text, 0)


if __name__ == "__main__":
    sys.exit(main())
