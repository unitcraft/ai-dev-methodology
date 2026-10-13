# -*- coding: utf-8 -*-
"""Самотест стража сообщения коммита guard-commit-message.py и определения lib/message.py.

Зачем: сообщения остаются в публичной истории; страж, который судит файл сообщения целиком, краснит
    то, что git выбросит (diff при -v), и пропускает то, что git оставит (строки на решётку при -m и -F).
Проверяет: красную пробу на каждое правило (подпись, подпись не автора, запрещённый трейлер, не
    ASCII, адрес автора, путь машины, запрещённое имя, пустое сообщение); режимы editor, message и
    --commit, режим --ci; строки на решётку (в сообщении они в истории, в редакторе — нет), строки
    цитаты, режим с diff и строку-ножницы; значение из списка нигде не печатается (с положительным
    контролем); политику из guards.conf: выключенные правила не судятся, пропавший обязательный ключ —
    красная предпосылка с подсказкой.
Не проверяет: сам хук commit-msg (test-commit-msg.py).
Правило: docs/guards.md (README комплекта), «Сообщение коммита».

Режим задаётся аргументом в каждой пробе явно. Список имён и образцы собираются при прогоне.
"""
import sys

sys.dont_write_bytecode = True

import os

import stlib

import message  # noqa: E402

NAME = "Test Author"
EMAIL = "author@example.test"
SIGN = "Signed-off-by: %s <%s>" % (NAME, EMAIL)
P1 = "zorblax" + "-" + "project"
WIN = "E" + ":/" + "Projects" + "/" + "alpha" + "/f.txt"
CYR = "привет"
SCISSORS = message.SCISSORS
SERVICE = message.SERVICE


def main():
    pr = stlib.Probes("guard-commit-message")
    base = pr.mkdtemp()
    env0 = stlib.isolated_env(base)
    names = stlib.names_file(base, ["# list", P1])
    env = dict(env0, **{stlib.NAMES_FILE_VAR: names})
    repo = stlib.make_repo(base, env, {"a.txt": "x\n"})
    stlib.git(repo, env, "config", stlib.EMAIL_KEY, EMAIL)
    counter = [0]

    def write_msg(text):
        counter[0] += 1
        path = os.path.join(base, "msg%d.txt" % counter[0])
        with open(path, "wb") as handle:
            handle.write(text.encode("utf-8"))
        return path

    def run(text, mode, *extra, **kw):
        e = kw.get("env", env)
        r = kw.get("repo", repo)
        return stlib.guard("guard-commit-message.py", r, e, "--message-file", write_msg(text), "--mode", mode, *extra)

    def good(subject="Add a thing"):
        return "%s\n\nBody line.\n\n%s\n" % (subject, SIGN)

    def red(text, mode, rule, line=None, count=1, extra=()):
        def fn():
            proc = run(text, mode, *extra)
            stlib.expect(proc, 1, "FAIL: guard-commit-message: %d нарушений" % count)
            tail = "%s: %s:" % ("сообщение коммита" + (":%d" % line if line else ""), rule)
            assert stlib.has_line(proc, "FAIL " + tail), proc.out
            assert P1 not in proc.out and WIN not in proc.out, "значение напечатано"
        return fn

    def legit(text, mode, *extra, **kw):
        def fn():
            stlib.expect(run(text, mode, *extra, **kw), 0, "ок: осмотрено 1 сообщений")
        return fn

    def editor_good_with_template_and_diff():
        text = good() + "# Please enter the commit message\n# %s\n" % CYR + SCISSORS + "\n" + SERVICE + "\n# Everything below it will be ignored.\ndiff --git a/x b/x\n+" + CYR + " " + P1 + "\n-" + WIN + "\n"
        stlib.expect(run(text, "editor"), 0, "ок: осмотрено 1 сообщений")

    def verbose_diff_name_in_message_red():
        text = good("Mention " + P1) + SCISSORS + "\n" + SERVICE + "\ndiff\n+x\n"
        proc = run(text, "editor")
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
        assert stlib.has_line(proc, "FAIL сообщение коммита:1: forbidden-name: образец №1"), proc.out

    def scissors_with_f_no_verbose_tail_judged():
        text = good() + SCISSORS + "\ntail " + P1 + "\n"
        stlib.expect(run(text, "message"), 1, "FAIL: guard-commit-message: 1 нарушений")

    def scissors_with_verbose_config_cut():
        stlib.git(repo, env, "config", "commit.verbose", "true")
        try:
            text = good() + SCISSORS + "\ntail " + P1 + "\n"
            stlib.expect(run(text, "message"), 0, "ок: осмотрено 1 сообщений")
        finally:
            stlib.git(repo, env, "config", "--unset", "commit.verbose")

    def typed_scissors_without_service_line_judged():
        text = good() + SCISSORS + "\ntail " + P1 + "\n"
        stlib.expect(run(text, "editor"), 1, "FAIL: guard-commit-message: 1 нарушений")

    def hash_line_in_message_mode_red_editor_ok():
        text = good() + "# note " + P1 + "\n"
        proc = run(text, "message")
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
        assert stlib.has_line(proc, "forbidden-name"), proc.out
        stlib.expect(run(text, "editor"), 0, "ок: осмотрено 1 сообщений")

    def hash_cyrillic_message_red_editor_ok():
        text = good() + "# " + CYR + "\n"
        stlib.expect(run(text, "message"), 1, "FAIL: guard-commit-message: 1 нарушений")
        stlib.expect(run(text, "editor"), 0, "ок: осмотрено 1 сообщений")

    def quote_line_name_red_both_cyrillic_ok():
        stlib.expect(run(good() + "> " + CYR + " quote\n", "message"), 0, "ок: осмотрено 1 сообщений")
        for mode in ("message", "editor"):
            proc = run(good() + "> quote " + P1 + "\n", mode)
            stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")

    def empty_editor_only_comments():
        stlib.expect(run("# only comments\n\n", "editor"), 1, "FAIL: guard-commit-message: 1 нарушений")

    def empty_message():
        proc = run("", "message")
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
        assert stlib.has_line(proc, "empty-message"), proc.out

    def crlf_message_file():
        text = good().replace("\n", "\r\n")
        stlib.expect(run(text, "message"), 0, "ок: осмотрено 1 сообщений")

    def no_email_setting():
        env2 = dict(env0, **{stlib.NAMES_FILE_VAR: names})
        repo2 = stlib.make_repo(base, env2, {"a.txt": "x\n"}, name="noset")
        proc = run(good(), "message", repo=repo2, env=env2)
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
        assert stlib.has_line(proc, "запусти установщик"), proc.out
        env3 = dict(env2, CI="true")
        proc = run(good(), "message", repo=repo2, env=env3)
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
        assert stlib.has_line(proc, "запусти установщик"), proc.out

    def ci_no_setting_nothing_to_judge():
        env2 = dict(env0, **{stlib.NAMES_FILE_VAR: names})
        repo2 = stlib.make_repo(base, env2, {"a.txt": "x\n"}, name="noset2")
        proc = run(good(), "message", "--ci", repo=repo2, env=env2)
        stlib.expect(proc, 0, "ок: осмотрено 1 сообщений")
        assert stlib.has_line(proc, "судить нечего: CI, нет настройки установщика"), proc.out

    def email_mismatch():
        stlib.git(repo, env, "config", stlib.EMAIL_KEY, "other@example.test")
        try:
            proc = run(good(), "message")
            stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
            assert stlib.has_line(proc, "expected-email: адрес автора не совпадает"), proc.out
            stlib.expect(run(good(), "message", "--ci"), 0, "ок: осмотрено 1 сообщений")
        finally:
            stlib.git(repo, env, "config", stlib.EMAIL_KEY, EMAIL)

    def no_names_list():
        e = dict(env0, **{stlib.NAMES_FILE_VAR: os.path.join(base, "absent.txt")})
        proc = run(good(), "message", env=e)
        stlib.expect(proc, 1, "FAIL: предпосылка")

    def missing_arguments():
        proc = stlib.guard("guard-commit-message.py", repo, env)
        stlib.expect(proc, 1, "FAIL: предпосылка")
        proc = stlib.guard("guard-commit-message.py", repo, env, "--message-file", write_msg(good()))
        stlib.expect(proc, 1, "FAIL: предпосылка")

    # --- режим --commit ---------------------------------------------------------------------
    def make_commit(message_text, author_email=None, name="c"):
        path = write_msg(message_text)
        e = dict(env)
        if author_email:
            e["GIT_AUTHOR_EMAIL"] = author_email
        stlib.write_files(repo, {"f_%s_%d.txt" % (name, counter[0]): "x\n"})
        stlib.git(repo, e, "add", "--", "f_%s_%d.txt" % (name, counter[0]))
        stlib.git(repo, e, "commit", "-q", "-F", path)
        return stlib.git(repo, env, "rev-parse", "HEAD").out.strip()

    def commit_good():
        sha = make_commit(good())
        proc = stlib.guard("guard-commit-message.py", repo, env, "--commit", sha)
        stlib.expect(proc, 0, "ок: осмотрено 1 сообщений")

    def commit_no_signoff():
        sha = make_commit("Plain subject\n")
        proc = stlib.guard("guard-commit-message.py", repo, env, "--commit", sha)
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
        assert stlib.has_line(proc, "signoff-missing"), proc.out

    def commit_other_signoff():
        sha = make_commit("Subj\n\nSigned-off-by: Someone Else <else@example.test>\n")
        proc = stlib.guard("guard-commit-message.py", repo, env, "--commit", sha)
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
        assert stlib.has_line(proc, "signoff-author"), proc.out

    def commit_coauthor():
        sha = make_commit(good() + "Co-Authored-By: Bot <bot@example.test>\n")
        proc = stlib.guard("guard-commit-message.py", repo, env, "--commit", sha)
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
        assert stlib.has_line(proc, "forbidden-trailer"), proc.out

    def commit_ci_author_vs_signoff():
        sha = make_commit(good(), author_email="stranger@example.test")
        proc = stlib.guard("guard-commit-message.py", repo, env, "--commit", sha, "--ci")
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
        assert stlib.has_line(proc, "signoff-author"), proc.out
        sha2 = make_commit("Subj\n\nSigned-off-by: Test Author <stranger@example.test>\n",
                           author_email="stranger@example.test")
        proc = stlib.guard("guard-commit-message.py", repo, env, "--commit", sha2, "--ci")
        stlib.expect(proc, 0, "ок: осмотрено 1 сообщений")

    def commit_ci_signoff_matches_author():
        e = dict(env, GIT_AUTHOR_NAME="Alt Person", GIT_AUTHOR_EMAIL="alt@example.test")
        path = write_msg("Subj\n\nSigned-off-by: Alt Person <alt@example.test>\n")
        stlib.write_files(repo, {"alt.txt": "x\n"})
        stlib.git(repo, e, "add", "--", "alt.txt")
        stlib.git(repo, e, "commit", "-q", "-F", path)
        sha = stlib.git(repo, env, "rev-parse", "HEAD").out.strip()
        proc = stlib.guard("guard-commit-message.py", repo, env, "--commit", sha, "--ci")
        stlib.expect(proc, 0, "ок: осмотрено 1 сообщений")
        assert stlib.has_line(proc, "судить нечего: CI, нет настройки установщика"), proc.out
        proc = stlib.guard("guard-commit-message.py", repo, env, "--commit", sha)
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")  # локально адрес не равен ожидаемому

    def commit_private_in_message():
        sha = make_commit(good("Path " + WIN + " and " + P1))
        proc = stlib.guard("guard-commit-message.py", repo, env, "--commit", sha)
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 2 нарушений")
        assert P1 not in proc.out and WIN not in proc.out
        assert stlib.has_line(proc, "machine-path") and stlib.has_line(proc, "образец №1"), proc.out

    def positive_control():
        proc = run(good("Mention " + P1), "message")
        assert "образец №1" in proc.out, "положительный контроль"
        assert proc.out.count(P1) == 0 and proc.err.count(P1) == 0

    def with_conf(changes, env_base=None):
        return dict(env_base or env, GUARDS_CONF=stlib.conf_file(base, changes))

    # Правила с отрицательными пробами требуют строгий тестовый профиль независимо от
    # поставляемого профиля; отдельно проверяется, что штатный профиль принимает сообщение без подписи.
    env["GUARDS_CONF"] = stlib.conf_file(base, {"COMMIT_SIGNOFF": "required"})

    def shipped_policy_allows_no_signoff():
        e = dict(env, GUARDS_CONF=stlib.CONF)
        stlib.expect(run("Plain subject\n", "message", env=e), 0, "ок: осмотрено 1 сообщений")

    def policy_off():
        e = with_conf({"COMMIT_SIGNOFF": "off", "COMMIT_ASCII_ONLY": "no", "COMMIT_FORBIDDEN_TRAILERS": "none",
                       "COMMIT_AUTHOR_EMAIL_CHECK": "no"})
        text = CYR + " subject\n\nCo-Authored-By: Bot <b@example.test>\n"
        stlib.expect(run(text, "message", env=e), 0, "ок: осмотрено 1 сообщений")
        env2 = dict(env0, **{stlib.NAMES_FILE_VAR: names})
        repo2 = stlib.make_repo(base, env2, {"a.txt": "x\n"}, name="noset3")
        stlib.expect(run(text, "message", repo=repo2, env=with_conf({"COMMIT_AUTHOR_EMAIL_CHECK": "no"}, env2)), 1,
                     "FAIL: guard-commit-message")
        stlib.expect(run(good(), "message", repo=repo2, env=with_conf({"COMMIT_AUTHOR_EMAIL_CHECK": "no"}, env2)), 0,
                     "ок: осмотрено 1 сообщений")

    def policy_off_keeps_private():
        e = with_conf({"COMMIT_SIGNOFF": "off", "COMMIT_ASCII_ONLY": "no", "COMMIT_FORBIDDEN_TRAILERS": "none",
                       "COMMIT_AUTHOR_EMAIL_CHECK": "no"})
        proc = run("Subject " + P1 + " and " + WIN + "\n", "message", env=e)
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 2 нарушений")
        assert stlib.has_line(proc, "machine-path") and stlib.has_line(proc, "forbidden-name"), proc.out

    def other_trailer_list():
        e = with_conf({"COMMIT_FORBIDDEN_TRAILERS": "Reviewed-by Change-Id"})
        stlib.expect(run(good() + "Co-Authored-By: Bot <b@example.test>\n", "message", env=e), 0, "ок: осмотрено 1 сообщений")
        proc = run(good() + "Change-Id: I123\n", "message", env=e)
        stlib.expect(proc, 1, "FAIL: guard-commit-message: 1 нарушений")
        assert stlib.has_line(proc, "forbidden-trailer: трейлер Change-Id"), proc.out

    def policy_key_missing():
        for key in ("COMMIT_SIGNOFF", "COMMIT_FORBIDDEN_TRAILERS", "COMMIT_ASCII_ONLY", "COMMIT_AUTHOR_EMAIL_CHECK"):
            proc = run(good(), "message", env=with_conf({key: None}))
            stlib.expect(proc, 1, "FAIL: предпосылка")
            assert "нет обязательного ключа " + key in proc.out, (key, proc.out)
        proc = run(good(), "message", env=with_conf({"COMMIT_SIGNOFF": "maybe"}))
        stlib.expect(proc, 1, "FAIL: предпосылка")
        assert "required | off" in proc.out, proc.out

    sign = good()
    pr.probe("законное", "правильное сообщение, режим message", legit(sign, "message"))
    pr.probe("законное", "правильное сообщение, режим editor", legit(sign, "editor"))
    pr.probe("законное", "CRLF в файле сообщения", crlf_message_file)
    pr.probe("законное", "редактор: комментарии и diff за ножницами не судятся", editor_good_with_template_and_diff)
    pr.probe("законное", "строка на «>» с кириллицей без приватных данных", quote_line_name_red_both_cyrillic_ok)
    pr.probe("законное", "# с именем: message — красный, editor — не судится", hash_line_in_message_mode_red_editor_ok)
    pr.probe("законное", "# с кириллицей: message — красный, editor — проходит", hash_cyrillic_message_red_editor_ok)
    pr.probe("законное", "commit.verbose: хвост за ножницами при -F отрезан", scissors_with_verbose_config_cut)
    pr.probe("законное", "режим --commit: правильный коммит", commit_good)
    pr.probe("законное", "режим --ci: адрес не сверяется, подпись равна автору", commit_ci_signoff_matches_author)
    pr.probe("законное", "режим --ci без настройки: судить нечего по правилу адреса", ci_no_setting_nothing_to_judge)
    pr.probe("законное", "поставляемая политика принимает сообщение без Signed-off-by", shipped_policy_allows_no_signoff)
    pr.probe("красная", "нет Signed-off-by", red("Subject only\n", "message", "signoff-missing"))
    pr.probe("красная", "подпись не автора (имя)", red("S\n\nSigned-off-by: Other Name <%s>\n" % EMAIL, "message", "signoff-author"))
    pr.probe("красная", "подпись не автора (адрес)", red("S\n\nSigned-off-by: %s <x@example.test>\n" % NAME, "message", "signoff-author"))
    pr.probe("красная", "запрещённый трейлер Co-Authored-By", red(good() + "Co-Authored-By: Bot <b@example.test>\n", "message", "forbidden-trailer", line=6))
    pr.probe("красная", "запрещённый трейлер строчными буквами", red(good() + "co-authored-by: Bot <b@example.test>\n", "message", "forbidden-trailer", line=6))
    pr.probe("красная", "не ASCII в теме", red(good(CYR + " title"), "message", "non-ascii", line=1))
    pr.probe("красная", "путь машины в теле", red(good("Fix " + WIN), "message", "machine-path", line=1))
    pr.probe("красная", "запрещённое имя в теме", red(good("Mention " + P1), "message", "forbidden-name", line=1))
    pr.probe("красная", "пустое сообщение", empty_message)
    pr.probe("красная", "в редакторе остались одни комментарии", empty_editor_only_comments)
    pr.probe("красная", "нет настройки установщика (в том числе при CI=true)", no_email_setting)
    pr.probe("красная", "адрес автора не равен настройке", email_mismatch)
    pr.probe("красная", "нет списка запрещённых имён", no_names_list)
    pr.probe("красная", "режим --commit: нет подписи", commit_no_signoff)
    pr.probe("красная", "режим --commit: подпись не автора", commit_other_signoff)
    pr.probe("красная", "режим --commit: запрещённый трейлер", commit_coauthor)
    pr.probe("красная", "режим --commit: путь машины и имя в теме", commit_private_in_message)
    pr.probe("красная", "поиск значения в выводе: 0 с положительным контролем", positive_control)
    pr.probe("иной-синтаксис", "режим с diff: имя в самом сообщении — красный", verbose_diff_name_in_message_red)
    pr.probe("иной-синтаксис", "-F без режима с diff: имя за ножницами судится", scissors_with_f_no_verbose_tail_judged)
    pr.probe("иной-синтаксис", "набранная руками ножницы без служебной строки судятся", typed_scissors_without_service_line_judged)
    pr.probe("иной-синтаксис", "режим --commit --ci: автор и подпись с разными адресами", commit_ci_author_vs_signoff)
    pr.probe("законное", "политика выключена: подпись, ASCII, трейлеры и адрес не судятся", policy_off)
    pr.probe("красная", "политика выключена: путь машины и имя из списка судятся всегда", policy_off_keeps_private)
    pr.probe("иной-синтаксис", "свой перечень запрещённых трейлеров", other_trailer_list)
    pr.probe("мишень", "в guards.conf нет ключа политики или значение не из допустимых", policy_key_missing)
    pr.probe("мишень", "не указан ни файл сообщения, ни коммит; нет режима", missing_arguments)
    return pr.done()


if __name__ == "__main__":
    sys.exit(main())
