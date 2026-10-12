# -*- coding: utf-8 -*-
"""Параметры проекта для стражей: чтение и проверка файла guards.conf.

Зачем: всё, что зависит от проекта (имена переменных списка запрещённых имён, целевая ветка, раскладка
    папок, политика сообщений коммитов, форматы документов), задаётся в одном файле; без него каждый
    страж держал бы своё значение, и новый проект молча получал бы чужие имена и чужой формат.
Проверяет: синтаксис файла (КЛЮЧ=значение, решётка первым знаком — комментарий), неизвестные ключи,
    повтор ключа, который не бывает списком, наличие обязательных ключей и форму каждого значения
    (имя переменной, относительный путь, регулярное выражение, перечень допустимых слов). Нарушение —
    исключение Unavailable с подсказкой, какой ключ и что в нём писать; страж печатает его как
    «FAIL: предпосылка».
Не проверяет: смысл значений для проекта (что формат документов верен, что ветка существует).
Правило: README комплекта, «Параметры проекта»: отсутствие обязательного ключа — красный вердикт
    с подсказкой, а не подстановка чужого значения.

Где файл: переменная окружения GUARDS_CONF (полный путь; ею пользуются самотесты), иначе guards.conf
в папке стражей (на уровень выше этой библиотеки). Вызов из оболочки: python conf.py get <КЛЮЧ>
печатает значение (у списка — по строке на значение) или пишет «FAIL: предпосылка: ...» в stderr с
кодом 1; python conf.py check проверяет весь файл.
"""
import sys

sys.dont_write_bytecode = True

import os
import re

try:
    from guardlib import Unavailable
except ImportError:  # вызов из оболочки: библиотека лежит рядом
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from guardlib import Unavailable

README = "все ключи описаны в README комплекта, раздел «Параметры проекта»"
KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
VAR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9._][A-Za-z0-9._/-]*$")
GIT_KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9-]*\.[A-Za-z][A-Za-z0-9.-]*$")
WORD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9-]*$")
TASK_KINDS = ("first-line", "every-line", "unique")


def _path(value):
    if not value or value.startswith(("/", "\\")) or ":" in value or "\\" in value:
        return "нужен относительный путь от корня репозитория через косую черту"
    if value.endswith("/") or any(part in ("", ".", "..") for part in value.split("/")):
        return "в пути нет пустых частей, «.» и «..» и косой черты в конце"
    return None


def _home_path(value):
    if not value:
        return "нужен путь к файлу (можно начать с ~)"
    return None


def _var(value):
    return None if VAR_RE.match(value) else "нужно имя переменной окружения (буквы, цифры, подчёркивание)"


def _branch(value):
    return None if BRANCH_RE.match(value) else "нужно имя ветки git"


def _git_key(value):
    return None if GIT_KEY_RE.match(value) else "нужен ключ git config вида раздел.имя"


def _choice(*allowed):
    def check(value):
        return None if value in allowed else "допустимо: " + " | ".join(allowed)
    return check


def _words(value):
    if value == "none":
        return None
    words = value.split()
    bad = [w for w in words if not WORD_RE.match(w)]
    return "слова через пробел или none; не слово: " + ", ".join(bad) if bad or not words else None


def _regex(value, allow_off=False):
    if allow_off and value == "off":
        return None
    try:
        re.compile(value)
    except re.error as exc:
        return "регулярное выражение не разбирается (%s)" % exc
    return None if value else "нужно регулярное выражение"


def parse_task_rule(value):
    """Правило формата документа: (вид, образец пути, образец строки) или ValueError с причиной."""
    parts = value.split(None, 2)
    if len(parts) != 3:
        raise ValueError("нужно «<вид> <образец пути> <образец строки>», вид — " + ", ".join(TASK_KINDS))
    kind, path_re, line_re = parts
    if kind not in TASK_KINDS:
        raise ValueError("вид «%s» неизвестен; допустимо: %s" % (kind, ", ".join(TASK_KINDS)))
    try:
        compiled = (re.compile(path_re), re.compile(line_re))
    except re.error as exc:
        raise ValueError("регулярное выражение не разбирается (%s)" % exc)
    return kind, compiled[0], compiled[1]


RATCHET_GUARD_RE = re.compile(r"^check-[A-Za-z0-9_-]+\.(py|sh)$")


def _ratchet_guards(values):
    if values == ["off"]:
        return None
    if "off" in values:
        return "off допустим только как единственное значение"
    bad = [v for v in values if not RATCHET_GUARD_RE.match(v) or v == "check-ratchet.py"]
    if bad:
        return "нужно имя файла стража check-* из папки стражей (не сам храповик); не годится: " + ", ".join(bad)
    if len(set(values)) != len(values):
        return "страж назван дважды"
    return None


def _task_rules(values):
    if values == ["off"]:
        return None
    if "off" in values:
        return "off допустим только как единственное значение"
    for number, value in enumerate(values, 1):
        try:
            parse_task_rule(value)
        except ValueError as exc:
            return "правило №%d: %s" % (number, exc)
    return None


# ключ: (обязателен ли, значение по умолчанию, проверка формы, что это)
SPEC = {
    "GUARDS_DIR": (False, "scripts/guards", _path, "папка стражей от корня репозитория"),
    "GITHOOKS_DIR": (False, "scripts/githooks", _path, "папка хуков git (её пишет установщик в core.hooksPath)"),
    "HOOKS": (False, "pre-commit commit-msg pre-push", _words, "набор подключаемых хуков git через пробел"),
    "AGENT_HOOKS_DIR": (False, "scripts/agent-hooks", _path, "папка хука агента"),
    "AGENT_SETTINGS": (False, ".claude/settings.json", _path, "файл настроек агента с записью хука"),
    "CI_WORKFLOW": (False, ".github/workflows/guards.yml", _path, "файл задания CI со стражами"),
    "INSTALLER": (False, "scripts/install-hooks.sh", _path, "установщик хуков"),
    "EXPECTED_EMAIL_KEY": (False, "guards.expectedEmail", _git_key,
                           "ключ git config, куда установщик пишет ожидаемый адрес автора"),
    "MAIN_BRANCH": (True, None, _branch, "целевая (основная) ветка проекта, например main"),
    "PRIVATE_NAMES_VAR": (True, None, _var,
                          "имя переменной окружения и секрета CI со списком запрещённых имён, например GUARDS_PRIVATE_NAMES"),
    "PRIVATE_NAMES_FILE_VAR": (True, None, _var,
                               "имя переменной окружения с путём к файлу списка, например GUARDS_PRIVATE_NAMES_FILE"),
    "PRIVATE_NAMES_FILE": (True, None, _home_path,
                           "файл списка запрещённых имён вне репозитория, например ~/.config/guards/private-names.txt"),
    "COMMIT_SIGNOFF": (True, None, _choice("required", "off"), "подпись Signed-off-by автора: required или off"),
    "COMMIT_FORBIDDEN_TRAILERS": (True, None, _words,
                                  "запрещённые трейлеры сообщения через пробел (например Co-authored-by) или none"),
    "COMMIT_ASCII_ONLY": (True, None, _choice("yes", "no"), "сообщение коммита только ASCII (кроме строк цитаты): yes или no"),
    "COMMIT_AUTHOR_EMAIL_CHECK": (True, None, _choice("yes", "no"),
                                  "сверять адрес автора с записанным установщиком: yes или no"),
    "AGENT_HOOK_RULES": (True, None, _words, "правила хука агента через пробел или none"),
    "TASK_DOC_RULE": (True, None, _task_rules,
                      "правило формата документа задачи «<вид> <образец пути> <образец строки>» (ключ повторяется) или off"),
    "STATUS_TABLE_TASK_PATH": (True, None, lambda v: _regex(v, True),
                               "образец пути папки задачи для стража таблиц статусов или off"),
    "STATUS_TABLE_COLUMN": (False, "статус|status|state", _regex, "образец заголовка колонки состояния (без учёта регистра)"),
    "TEST_FILES": (True, None, lambda v: _regex(v, True), "образец пути файла теста для стража пустых тестов или off"),
    "TEST_CHECK": (True, None, _regex, "образец проверки в тексте теста (нужен, если TEST_FILES не off)"),
    "TEST_COMMENT": (True, None, lambda v: None if v == "none" else _regex(v),
                     "образец комментария, вырезаемого перед поиском проверок, или none (нужен, если TEST_FILES не off)"),
    "RATCHET_GUARD": (True, None, _ratchet_guards,
                      "страж check-* под храповиком долга, имя файла (ключ повторяется) или off"),
    "RATCHET_BASELINE": (False, "scripts/guards/ratchet.txt", _path, "файл базы храповика долга от корня репозитория"),
}
LISTS = ("TASK_DOC_RULE", "RATCHET_GUARD")
# ключ нужен, только если другой ключ не выключен
CONDITIONAL = {"TEST_CHECK": ("TEST_FILES", "off"), "TEST_COMMENT": ("TEST_FILES", "off")}


def default_path():
    env = os.environ.get("GUARDS_CONF")
    if env:
        return env
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "guards.conf")


class Conf(object):
    """Разобранный файл параметров; ошибки синтаксиса — сразу, ошибки ключа — при обращении."""

    def __init__(self, path=None):
        self.path = path or default_path()
        self.name = os.path.basename(self.path)
        self.values = {}
        try:
            with open(self.path, "rb") as handle:
                data = handle.read()
        except OSError:
            raise Unavailable("нет файла параметров %s; скопируйте его из комплекта и заполните (%s)"
                              % (self.name, README))
        text = data.decode("utf-8-sig", "replace").replace("\r\n", "\n")
        for number, raw in enumerate(text.split("\n"), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if not sep or not KEY_RE.match(key):
                raise Unavailable("%s:%d: строка не вида КЛЮЧ=значение (%s)" % (self.name, number, README))
            if key not in SPEC:
                raise Unavailable("%s:%d: неизвестный ключ %s (%s)" % (self.name, number, key, README))
            if key in self.values and key not in LISTS:
                raise Unavailable("%s:%d: ключ %s задан второй раз" % (self.name, number, key))
            self.values.setdefault(key, []).append(value)

    def _needed(self, key):
        cond = CONDITIONAL.get(key)
        return not (cond and self.values.get(cond[0]) == [cond[1]])

    def problem(self, key):
        """Причина, по которой ключ не годится, или None."""
        required, default, check, what = SPEC[key]
        if key not in self.values:
            if required and self._needed(key):
                return "в %s нет обязательного ключа %s — %s; %s" % (self.name, key, what, README)
            return None
        values = self.values[key]
        if key in LISTS:
            reason = check(values)
        else:
            reason = check(values[0]) if values[0] != "" else "пустое значение"
        if reason:
            return "в %s ключ %s: %s (%s — %s)" % (self.name, key, reason, key, what)
        return None

    def get(self, key):
        """Значение ключа (у списка — список строк); нет обязательного или форма неверна — Unavailable."""
        reason = self.problem(key)
        if reason:
            raise Unavailable(reason)
        if key in self.values:
            return list(self.values[key]) if key in LISTS else self.values[key][0]
        default = SPEC[key][1]
        return [default] if key in LISTS and default is not None else default

    def words(self, key):
        value = self.get(key)
        return [] if value in (None, "none") else value.split()

    def validate(self):
        """Все причины по всем ключам (пустой список — файл годен)."""
        return [reason for reason in (self.problem(key) for key in SPEC) if reason]

    def task_rules(self):
        """Правила формата документов задач или None, если выключено (off)."""
        values = self.get("TASK_DOC_RULE")
        if values == ["off"]:
            return None
        return [parse_task_rule(v) for v in values]


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        sys.stderr.reconfigure(encoding="utf-8", newline="\n")
    except Exception:
        pass
    try:
        conf = Conf()
        if len(argv) == 2 and argv[0] == "get" and argv[1] in SPEC:
            value = conf.get(argv[1])
            for item in value if isinstance(value, list) else [value]:
                sys.stdout.write(item + "\n")
            return 0
        if argv == ["check"]:
            problems = conf.validate()
            for reason in problems:
                sys.stdout.write("FAIL %s\n" % reason)
            if problems:
                sys.stdout.write("FAIL: параметры: %d нарушений\n" % len(problems))
                return 1
            sys.stdout.write("ок: осмотрено %d ключей\n" % len(SPEC))
            return 0
    except Unavailable as exc:
        sys.stderr.write("FAIL: предпосылка: %s\n" % exc)
        return 1
    sys.stderr.write("FAIL: предпосылка: вызов conf.py get <КЛЮЧ> или conf.py check\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
