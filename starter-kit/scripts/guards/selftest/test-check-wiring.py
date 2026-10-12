# -*- coding: utf-8 -*-
"""Самотест мета-проверки check-wiring.py: параметры, шапка, самотест, подключение стражей и хука агента.

Зачем: страж без вызова или без самотеста выглядит надёжно и ничего не держит; мета-проверка должна
    краснеть именно на этом и называть страж.
Проверяет: на синтетическом дереве, которое собирается в прогоне (раскладка — из guards.conf комплекта):
    зелёное дерево; красные - у стража нет шапки (метка за меткой), нет самотеста, страж вне маски не назван
    в своём хуке, у нового guard-*.py нет внешнего вызывающего, нет хука git или он не исполняемый, задание
    CI не вызывает нужный скрипт, не передаёт секрет списка имён или отсутствует; запись хука агента
    покрывает только Bash или только PowerShell, команда зовёт python3, скрипт из команды не существует,
    команда не передаёт --conf, интерпретатор не запускается; в guards.conf нет обязательного ключа или
    значение не по форме, файла параметров нет в репозитории; самотест на .sh принимается; хук не из HOOKS
    не требуется; нет папки стражей - мишень потеряна.
Не проверяет: содержание настоящих стражей (это их самотесты).
Правило: README комплекта, «Страж с самотестом и вызывающим».
"""
import sys

sys.dont_write_bytecode = True

import json
import os

import stlib

PY_HEADER = '"""Title.\n\nЗачем: a\nПроверяет: b\nНе проверяет: c\nПравило: README\n"""\n'
SH_HEADER = "#!/bin/sh\n# Зачем: a\n# Проверяет: b\n# Не проверяет: c\n# Правило: README\n"
G = stlib.GUARDS_DIR
H = stlib.GITHOOKS_DIR
A = stlib.AGENT_HOOKS_DIR
WF = stlib.CI_WORKFLOW
ST = stlib.AGENT_SETTINGS
SETTINGS_TEXT = open(os.path.join(stlib.REPO, *ST.split("/")), encoding="utf-8").read()


def full(*names):
    return " ".join("%s/%s" % (G, n) for n in names)


def good_tree():
    files = {
        G + "/guards.conf": "# параметры\n",
        G + "/check-a.py": PY_HEADER,
        G + "/selftest/test-check-a.py": "pass\n",
        G + "/guard-secrets.py": PY_HEADER,
        G + "/selftest/test-guard-secrets.py": "pass\n",
        G + "/guard-commit-message.py": PY_HEADER,
        G + "/selftest/test-guard-commit-message.py": "pass\n",
        G + "/check-private-names.py": PY_HEADER,
        G + "/selftest/test-check-private-names.py": "pass\n",
        G + "/check-text-hygiene.py": PY_HEADER,
        G + "/selftest/test-check-text-hygiene.py": "pass\n",
        G + "/run-all.sh": SH_HEADER,
        G + "/selftest/test-run-all.py": "pass\n",
        G + "/commit-range.sh": SH_HEADER,
        G + "/selftest/test-commit-range.py": "pass\n",
        A + "/guard-git.py": PY_HEADER,
        G + "/selftest/test-guard-git.py": "pass\n",
        H + "/pre-commit": SH_HEADER + full("guard-secrets.py", "run-all.sh") + "\n",
        G + "/selftest/test-pre-commit.py": "pass\n",
        H + "/commit-msg": SH_HEADER + full("guard-commit-message.py") + "\n",
        G + "/selftest/test-commit-msg.py": "pass\n",
        H + "/pre-push": SH_HEADER + full("guard-secrets.py", "check-private-names.py", "check-text-hygiene.py",
                                          "check-ratchet.py", "guard-commit-message.py", "commit-range.sh") + "\n",
        G + "/selftest/test-pre-push.py": "pass\n",
        WF: full("run-all.sh", "selftest/run-selftests.sh", "prove-red.sh", "probe-empty-root.sh", "check-wiring.py",
                 "guard-secrets.py", "guard-commit-message.py", "commit-range.sh", "ci-mask.sh") + " " + stlib.NAMES_VAR + "\n",
        ST: SETTINGS_TEXT,
    }
    return files


def main():
    pr = stlib.Probes("check-wiring")
    base = pr.mkdtemp()
    env = stlib.isolated_env(base)
    counter = [0]
    EXEC = (H + "/pre-commit", H + "/commit-msg", H + "/pre-push")

    def build(change=None, drop=(), execs=EXEC):
        files = good_tree()
        files.update(change or {})
        for key in drop:
            files.pop(key, None)
        counter[0] += 1
        repo = stlib.make_repo(base, env, files, name="w%d" % counter[0])
        present = [p for p in execs if p in files]
        if present:
            stlib.git(repo, env, "update-index", "--chmod=+x", "--", *present)
            stlib.git(repo, env, "commit", "-q", "-m", "exec bits")
        return repo

    def check(repo, *args, **kw):
        return stlib.guard("check-wiring.py", repo, kw.get("env", env), *args)

    def red(repo, rule, where, count=1, *args):
        proc = check(repo, *args)
        stlib.expect(proc, 1, "FAIL: check-wiring: %d нарушений" % count)
        assert stlib.has_line(proc, "FAIL %s" % where) and stlib.has_line(proc, ": %s:" % rule), proc.out

    def legit_good_tree():
        stlib.expect(check(build()), 0, "ок: осмотрено 11 стражей")

    def legit_sh_selftest():
        files = {G + "/check-b.sh": SH_HEADER, G + "/selftest/test-check-b.sh": "echo ok\n"}
        stlib.expect(check(build(files)), 0, "ок: осмотрено 12 стражей")

    def legit_matcher_regex():
        data = json.loads(SETTINGS_TEXT)
        data["hooks"]["PreToolUse"][0]["matcher"] = ".*"
        stlib.expect(check(build({ST: json.dumps(data)})), 0, "ок: осмотрено 11 стражей")

    def legit_two_entries():
        data = json.loads(SETTINGS_TEXT)
        entry = data["hooks"]["PreToolUse"][0]
        second = json.loads(json.dumps(entry))
        entry["matcher"] = "Bash"
        second["matcher"] = "PowerShell"
        data["hooks"]["PreToolUse"] = [entry, second]
        stlib.expect(check(build({ST: json.dumps(data)})), 0, "ок: осмотрено 11 стражей")

    def legit_hooks_subset():
        # проект подключил только pre-commit и commit-msg: pre-push не требуется
        e = dict(env, GUARDS_CONF=stlib.conf_file(base, {"HOOKS": "pre-commit commit-msg"}))
        repo = build(drop=(H + "/pre-push", G + "/selftest/test-pre-push.py"))
        stlib.expect(check(repo, env=e), 0, "ок: осмотрено 10 стражей")

    def header_missing_each_label():
        for label in ("Зачем:", "Проверяет:", "Не проверяет:", "Правило:"):
            text = PY_HEADER.replace(label, "X:") if label != "Проверяет:" else PY_HEADER.replace("Проверяет: b\n", "")
            if label == "Не проверяет:":
                text = PY_HEADER.replace("Не проверяет: c\n", "")
            repo = build({G + "/check-a.py": text})
            proc = check(repo)
            stlib.expect(proc, 1, "FAIL: check-wiring: 1 нарушений")
            assert stlib.has_line(proc, "FAIL %s/check-a.py:1: no-header:" % G) and label.rstrip(":") in proc.out, (label, proc.out)

    def selftest_missing():
        repo = build({G + "/check-new.py": PY_HEADER})
        red(repo, "no-selftest", G + "/check-new.py")

    def selftest_missing_for_hook():
        repo = build(drop=(G + "/selftest/test-pre-push.py",))
        red(repo, "no-selftest", H + "/pre-push")

    def outofmask_not_named():
        repo = build({H + "/pre-commit": SH_HEADER + full("run-all.sh") + "\n"})
        red(repo, "not-wired", H + "/pre-commit")

    def new_guard_without_caller():
        repo = build({G + "/guard-extra.py": PY_HEADER, G + "/selftest/test-guard-extra.py": "pass\n"})
        red(repo, "not-wired", G + "/guard-extra.py")

    def hook_missing():
        repo = build(drop=(H + "/commit-msg", G + "/selftest/test-commit-msg.py"))
        red(repo, "hook-missing", H + "/commit-msg")

    def hook_not_executable():
        repo = build(execs=(H + "/pre-commit", H + "/pre-push"))
        red(repo, "hook-not-executable", H + "/commit-msg")

    def workflow_lacks_script():
        text = good_tree()[WF].replace(G + "/prove-red.sh", "")
        red(build({WF: text}), "not-wired", WF)

    def workflow_lacks_secret():
        text = good_tree()[WF].replace(stlib.NAMES_VAR, "")
        red(build({WF: text}), "not-wired", WF)

    def workflow_missing():
        red(build(drop=(WF,)), "not-wired", WF)

    def settings_variant(mutate, rule_text):
        def fn():
            data = json.loads(SETTINGS_TEXT)
            mutate(data)
            repo = build({ST: json.dumps(data)})
            proc = check(repo)
            stlib.expect(proc, 1, "FAIL: check-wiring")
            assert stlib.has_line(proc, rule_text), proc.out
        return fn

    def only_bash(d):
        d["hooks"]["PreToolUse"][0]["matcher"] = "Bash"

    def only_powershell(d):
        d["hooks"]["PreToolUse"][0]["matcher"] = "PowerShell"

    def python3_command(d):
        cmd = d["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        d["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = cmd.replace("exec python ", "exec python3 ")

    def other_script(d):
        cmd = d["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        d["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = cmd.replace("guard-git.py", "no-such-guard.py")

    def no_conf_arg(d):
        cmd = d["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        d["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = cmd.replace(G + "/guards.conf", "elsewhere.conf")

    def settings_missing():
        repo = build(drop=(ST,))
        red(repo, "agent-hook", ST)

    def interpreter_does_not_start():
        repo = build()
        proc = check(repo, "--python-cmd", "no-such-python-binary")
        stlib.expect(proc, 1, "FAIL: check-wiring: 1 нарушений")
        assert stlib.has_line(proc, "не запускается"), proc.out

    def conf_key_missing():
        repo = build()
        e = dict(env, GUARDS_CONF=stlib.conf_file(base, {"MAIN_BRANCH": None}))
        proc = check(repo, env=e)
        stlib.expect(proc, 1, "FAIL: check-wiring: 1 нарушений")
        assert stlib.has_line(proc, ": conf: в") and "нет обязательного ключа MAIN_BRANCH" in proc.out, proc.out
        assert "README" in proc.out, "нет подсказки, где описаны ключи"

    def conf_bad_values():
        repo = build()
        e = dict(env, GUARDS_CONF=stlib.conf_file(base, {"COMMIT_ASCII_ONLY": "maybe", "STATUS_TABLE_TASK_PATH": "(unclosed"}))
        proc = check(repo, env=e)
        stlib.expect(proc, 1, "FAIL: check-wiring: 2 нарушений")
        assert "COMMIT_ASCII_ONLY" in proc.out and "STATUS_TABLE_TASK_PATH" in proc.out, proc.out

    def conf_unknown_key():
        repo = build()
        path = stlib.conf_file(base)
        with open(path, "a", encoding="utf-8", newline="\n") as handle:
            handle.write("MAIN_BRANH=main\n")
        proc = check(repo, env=dict(env, GUARDS_CONF=path))
        stlib.expect(proc, 1, "FAIL: предпосылка")
        assert "неизвестный ключ MAIN_BRANH" in proc.out, proc.out

    def conf_not_in_repo():
        red(build(drop=(G + "/guards.conf",)), "conf", G + "/guards.conf")

    def no_guards_dir():
        repo = stlib.make_repo(base, env, {"README.md": "x\n"}, name="noguards")
        stlib.expect(check(repo), 1, "FAIL: мишень потеряна")

    pr.probe("законное", "зелёное дерево: 11 стражей и хуков", legit_good_tree)
    pr.probe("законное", "самотест на .sh принимается", legit_sh_selftest)
    pr.probe("законное", "matcher регулярным выражением", legit_matcher_regex)
    pr.probe("законное", "две записи: одна на Bash, другая на PowerShell", legit_two_entries)
    pr.probe("законное", "HOOKS без pre-push: хук не требуется", legit_hooks_subset)
    pr.probe("красная", "нет каждой из четырёх меток шапки", header_missing_each_label)
    pr.probe("красная", "нет самотеста у check-*", selftest_missing)
    pr.probe("красная", "нет самотеста у хука git", selftest_missing_for_hook)
    pr.probe("красная", "страж вне маски не назван в хуке", outofmask_not_named)
    pr.probe("красная", "новый guard-*.py без внешнего вызывающего", new_guard_without_caller)
    pr.probe("красная", "нет хука git", hook_missing)
    pr.probe("красная", "хук git не исполняемый", hook_not_executable)
    pr.probe("красная", "задание CI не вызывает prove-red.sh", workflow_lacks_script)
    pr.probe("красная", "задание CI не передаёт секрет списка имён", workflow_lacks_secret)
    pr.probe("красная", "нет задания CI", workflow_missing)
    pr.probe("красная", "хук агента только на Bash",
             settings_variant(only_bash, "не покрывает инструмент PowerShell"))
    pr.probe("красная", "хук агента только на PowerShell",
             settings_variant(only_powershell, "не покрывает инструмент Bash"))
    pr.probe("красная", "в guards.conf нет обязательного ключа", conf_key_missing)
    pr.probe("красная", "в guards.conf значения не по форме", conf_bad_values)
    pr.probe("иной-синтаксис", "команда хука агента зовёт python3 (заглушка)",
             settings_variant(python3_command, "не явным интерпретатором python"))
    pr.probe("иной-синтаксис", "скрипт из команды хука агента не существует",
             settings_variant(other_script, "скрипт хука агента из команды не существует"))
    pr.probe("иной-синтаксис", "команда хука агента не передаёт guards.conf",
             settings_variant(no_conf_arg, "не передаёт --conf"))
    pr.probe("иной-синтаксис", "нет записи настроек агента", settings_missing)
    pr.probe("иной-синтаксис", "интерпретатор python из команды не запускается", interpreter_does_not_start)
    pr.probe("иной-синтаксис", "неизвестный ключ в guards.conf (опечатка)", conf_unknown_key)
    pr.probe("мишень", "файла параметров нет в репозитории", conf_not_in_repo)
    pr.probe("мишень", "нет папки стражей - мишень потеряна", no_guards_dir)
    return pr.done()


if __name__ == "__main__":
    sys.exit(main())
