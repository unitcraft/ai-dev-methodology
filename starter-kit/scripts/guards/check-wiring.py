# -*- coding: utf-8 -*-
"""Мета-проверка стражей: каждый документирован, подключён и проверен самотестом; параметры годны.

Зачем: страж, который никто не вызывает, или проверка без самотеста выглядят надёжно и ничего не
    держат; такую дыру не видно, пока нарушение не пройдёт. Мета-проверка делает подключение
    свойством, которое проверяется машиной, а не вниманием.
Проверяет: раскладку берёт из ключей guards.conf (по умолчанию раскладка комплекта); (1) файл параметров
    годен (обязательные ключи на месте, формы значений верны) и лежит в папке стражей под git (conf);
    (2) у каждого стража (check-*, guard-*, хук агента, хуки git из HOOKS, запускающие скрипты папки
    стражей, установщик) есть шапка с метками «Зачем:», «Проверяет:», «Не проверяет:», «Правило:»
    (no-header); (3) есть самотест selftest/test-<имя>.py или .sh (no-selftest); (4) у каждого стража
    есть внешний вызывающий: guard-* и скрипты .sh папки стражей названы полным путём в задании CI
    или в хуке git из HOOKS, check-* подключены маской через run-all.sh, который назван в задании CI,
    хук агента назван в записи настроек агента (not-wired); хуки из HOOKS лежат в папке хуков под
    своими именами, исполняемые и зовут своих стражей (hook-missing, hook-not-executable, not-wired);
    задание CI называет переменную списка запрещённых имён (not-wired); (5) запись хука агента
    покрывает инструменты Bash и PowerShell, зовёт существующий скрипт из папки хука агента явным
    интерпретатором python (не python3), передаёт ему путь к guards.conf, и этот интерпретатор
    запускается (agent-hook).
Не проверяет: содержание самих проверок и самотестов (это делают самотесты и «доказательство
    красного»), стражей вне перечисленных папок, смысл значений параметров для проекта.
Правило: README комплекта, «Страж с самотестом и вызывающим».

Пометок-исключений у этого стража нет. Стражи по маске check-* подключаются построением (run-all.sh).
"""
import sys

sys.dont_write_bytecode = True

import json
import os
import re
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import conf as confmod  # noqa: E402
import guardlib  # noqa: E402

LABELS = ("Зачем:", "Проверяет:", "Не проверяет:", "Правило:")
# стражи, которых зовёт каждый хук комплекта (у чужого хука из HOOKS требований нет)
HOOK_NAMES = {
    "pre-commit": ("guard-secrets.py", "run-all.sh"),
    "commit-msg": ("guard-commit-message.py",),
    "pre-push": ("guard-secrets.py", "check-private-names.py", "check-text-hygiene.py",
                 "guard-commit-message.py", "commit-range.sh"),
}
# что обязано быть в задании CI (пути относительно папки стражей)
WORKFLOW_SCRIPTS = ("run-all.sh", "selftest/run-selftests.sh", "prove-red.sh", "probe-empty-root.sh",
                    "check-wiring.py", "guard-secrets.py", "guard-commit-message.py", "commit-range.sh",
                    "ci-mask.sh")


class Layout(object):
    def __init__(self, conf):
        self.guards = conf.get("GUARDS_DIR")
        self.githooks = conf.get("GITHOOKS_DIR")
        self.hooks = conf.words("HOOKS")
        self.agent = conf.get("AGENT_HOOKS_DIR")
        self.settings = conf.get("AGENT_SETTINGS")
        self.workflow = conf.get("CI_WORKFLOW")
        self.installer = conf.get("INSTALLER")
        self.names_var = conf.get("PRIVATE_NAMES_VAR")
        g, h, a = (re.escape(x) for x in (self.guards, self.githooks, self.agent))
        hooks = "|".join(re.escape(x) for x in self.hooks) or "(?!)"
        self.guard_path = re.compile(
            r"^(%s/(?:check-[^/]+\.(?:py|sh)|guard-[^/]+\.py|[^/]+\.sh)|%s/[^/]+\.py|%s/(?:%s)|%s)$"
            % (g, a, h, hooks, re.escape(self.installer)))


def check_header(path, text, rep):
    head = "\n".join(text.split("\n")[:80])
    missing = [label for label in LABELS if not re.search(r"(?m)^[#\s\"']*" + re.escape(label), head)]
    if missing:
        rep.add(path, 1, "no-header", "в шапке нет меток: " + ", ".join(missing))


def stem_of(path):
    name = path.rsplit("/", 1)[-1]
    return os.path.splitext(name)[0] if "." in name else name


def check_selftest(path, entry_paths, lay, rep):
    stem = stem_of(path)
    tests = ["%s/selftest/test-%s.%s" % (lay.guards, stem, ext) for ext in ("py", "sh")]
    if not any(t in entry_paths for t in tests):
        rep.add(path, None, "no-selftest", "нет самотеста selftest/test-%s.py или .sh" % stem)


def read_text(source, by_path, path):
    if path not in by_path:
        return None
    return (source.read(by_path[path]) or b"").decode("utf-8", "replace")


def check_callers(source, by_path, lay, rep):
    """Хуки из HOOKS на месте и зовут своих стражей; у guard-* и .sh папки стражей есть вызывающий."""
    workflow = read_text(source, by_path, lay.workflow)
    callers = [workflow or ""]
    for hook in lay.hooks:
        path = "%s/%s" % (lay.githooks, hook)
        if path not in by_path:
            rep.add(path, None, "hook-missing", "нет хука git %s в %s (он назван в HOOKS)" % (hook, lay.githooks))
            continue
        if by_path[path].mode != "100755":
            rep.add(path, None, "hook-not-executable", "хук git не исполняемый (режим %s)" % by_path[path].mode)
        text = read_text(source, by_path, path)
        callers.append(text)
        for needed in HOOK_NAMES.get(hook, ()):
            if "%s/%s" % (lay.guards, needed) not in text:
                rep.add(path, None, "not-wired", "хук не вызывает %s/%s" % (lay.guards, needed))
    if workflow is None:
        rep.add(lay.workflow, None, "not-wired", "нет задания CI " + lay.workflow)
    else:
        for script in WORKFLOW_SCRIPTS:
            if "%s/%s" % (lay.guards, script) not in workflow:
                rep.add(lay.workflow, None, "not-wired", "задание CI не вызывает %s/%s" % (lay.guards, script))
        if lay.names_var not in workflow:
            rep.add(lay.workflow, None, "not-wired",
                    "задание CI не передаёт секрет %s (PRIVATE_NAMES_VAR)" % lay.names_var)
    own = re.compile(r"^%s/(guard-[^/]+\.py|(?!check-)[^/]+\.sh)$" % re.escape(lay.guards))
    for path in sorted(by_path):
        if own.match(path) and not any(path in text for text in callers):
            rep.add(path, None, "not-wired", "нет внешнего вызывающего: не назван ни в задании CI, ни в хуке из HOOKS")


def _covers(matcher, tool):
    if matcher in ("", "*", None):
        return True
    try:
        return re.fullmatch(matcher, tool) is not None
    except re.error:
        return False


def check_agent_hook(source, by_path, lay, rep, python_cmd):
    settings = lay.settings
    if settings not in by_path:
        rep.add(settings, None, "agent-hook", "нет записи хука агента (%s)" % settings)
        return
    try:
        data = json.loads((source.read(by_path[settings]) or b"").decode("utf-8-sig"))
        entries = data["hooks"]["PreToolUse"]
        assert isinstance(entries, list)
    except Exception:
        rep.add(settings, None, "agent-hook", "в %s нет hooks.PreToolUse или файл не JSON" % settings)
        return
    covered = set()
    good_commands = []
    for entry in entries:
        for tool in ("Bash", "PowerShell"):
            if _covers(entry.get("matcher"), tool):
                covered.add(tool)
        for hook in entry.get("hooks", []):
            command = hook.get("command", "")
            if lay.agent + "/" in command:
                good_commands.append(command)
    for tool in ("Bash", "PowerShell"):
        if tool not in covered:
            rep.add(settings, None, "agent-hook", "запись хука агента не покрывает инструмент %s" % tool)
    if not good_commands:
        rep.add(settings, None, "agent-hook", "команда хука не зовёт скрипт из %s" % lay.agent)
        return
    agent_scripts = [p for p in by_path if re.match(r"^%s/[^/]+\.py$" % re.escape(lay.agent), p)]
    for path in agent_scripts:
        if not any(path in command for command in good_commands):
            rep.add(path, None, "not-wired", "скрипт хука агента не назван в %s" % settings)
    for command in good_commands:
        script = re.search(re.escape(lay.agent) + r"/[A-Za-z0-9_.-]+\.py", command)
        if not script or script.group(0) not in by_path:
            rep.add(settings, None, "agent-hook", "скрипт хука агента из команды не существует")
        if "%s/guards.conf" % lay.guards not in command:
            rep.add(settings, None, "agent-hook", "команда хука агента не передаёт --conf %s/guards.conf" % lay.guards)
        m = re.search(r"\bexec\s+(\S+)\s+\"?\$", command) or re.search(r"\b(python[0-9.]*)\b", command)
        word = m.group(1) if m else ""
        if word != "python":
            rep.add(settings, None, "agent-hook", "хук агента запускается не явным интерпретатором python (на машине python3 бывает заглушкой)")
            continue
        try:
            ok = subprocess.run([python_cmd, "-c", "pass"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        except OSError:
            ok = False
        if not ok:
            rep.add(settings, None, "agent-hook", "интерпретатор python из команды хука агента не запускается")


def judge(source, args, rep):
    conf = confmod.Conf()
    problems = conf.validate()
    for reason in problems:
        rep.add(conf.name, None, "conf", reason)
    if problems:
        return guardlib.Outcome(count=1)
    lay = Layout(conf)
    entries = source.entries()
    by_path = dict((e.path, e) for e in entries)
    if not any(p.startswith(lay.guards + "/") for p in by_path):
        return guardlib.Outcome(count=0)
    conf_path = "%s/guards.conf" % lay.guards
    if conf_path not in by_path:
        rep.add(conf_path, None, "conf", "файла параметров нет в репозитории (он должен быть под git)")
    count = 0
    for entry in entries:
        if not lay.guard_path.match(entry.path):
            continue
        text = (source.read(entry) or b"").decode("utf-8", "replace")
        count += 1
        check_header(entry.path, text, rep)
        check_selftest(entry.path, by_path, lay, rep)
    check_callers(source, by_path, lay, rep)
    check_agent_hook(source, by_path, lay, rep, args.python_cmd)
    return guardlib.Outcome(count=count)


def extra(parser):
    parser.add_argument("--python-cmd", default="python")


if __name__ == "__main__":
    sys.exit(guardlib.run("check-wiring", "стражей", judge, extra=extra,
                          lost="нет папки стражей (GUARDS_DIR): стражи потеряны"))
