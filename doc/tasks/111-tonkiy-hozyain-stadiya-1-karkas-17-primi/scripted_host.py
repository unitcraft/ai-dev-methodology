#!/usr/bin/env python3
"""ScriptedHost — тестовый исполнитель 17 примитивов тонкого хозяина (стадия 1).

Эталон контракта по спецификации `host-spec.md` (папка задачи 111). Реально
исполняет файловую систему, замки, хеш и журнал внутри дерева хозяина; ответы
сценарных примитивов (процессы, разбор агентом, токены) скриптует вызывающий.
Путь вне дерева и любая недоступность — сбой шага (StepFailure), а не значение.
"""
import hashlib
import json
import os
import re
import tempfile


class StepFailure(Exception):
    """Сбой шага: путь вне дерева, недоступность среды, чужой токен, нет ответа."""


class ScriptedHost(object):
    """Исполнитель примитивов хозяина для тестов машин (тонкий хозяин, стадия 1)."""

    HEX64 = re.compile(r"^[0-9a-f]{64}$")

    def __init__(self, answers=None):
        """answers: {ключ: значение} для сценарных примитивов.

        Ключи: ``process:<command>:<dir>`` -> pid (int>=1),
        ``running:<pid>`` -> bool, ``command:<command>:<dir>`` -> (code, stdout),
        ``agent:<instruction>:<input>`` -> JSON-текст,
        ``token:<task_dir>:<area>:<state>`` -> текст токена,
        ``opening:<task_dir>:<token>`` -> dict(author,date,source,content) или None.
        """
        self._tmp = tempfile.TemporaryDirectory(prefix="scripted-host-")
        self.tree = self._tmp.name
        self._answers = dict(answers or {})
        self._pids = set()          # живые scripted pid
        self._stopped = set()       # корректно остановленные (повтор — no-op)
        self._journal = []

    # -- общие правила ------------------------------------------------------

    def _resolve(self, path):
        """Путь внутри дерева хозяина или StepFailure."""
        full = os.path.realpath(os.path.join(self.tree, path))
        root = os.path.realpath(self.tree)
        if full != root and not full.startswith(root + os.sep):
            raise StepFailure("путь вне дерева хозяина: {0}".format(path))
        return full

    def _answer(self, key, what):
        if key not in self._answers:
            raise StepFailure("нет scripted-ответа: {0}".format(what))
        return self._answers[key]

    # -- файловая система (6) ----------------------------------------------

    def read_file(self, path):
        full = self._resolve(path)
        if not os.path.isfile(full):
            raise StepFailure("нет файла: {0}".format(path))
        with open(full, encoding="utf-8") as f:
            return f.read()

    def write_file(self, path, content):
        full = self._resolve(path)
        parent = os.path.dirname(full)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

    def move_file(self, frm, to):
        src, dst = self._resolve(frm), self._resolve(to)
        if not os.path.isfile(src):
            raise StepFailure("нет файла: {0}".format(frm))
        parent = os.path.dirname(dst)
        if parent:
            os.makedirs(parent, exist_ok=True)
        os.replace(src, dst)

    def delete_file(self, path):
        full = self._resolve(path)
        if not os.path.isfile(full):
            raise StepFailure("нет файла: {0}".format(path))
        os.remove(full)

    def file_exists(self, path):
        return os.path.isfile(self._resolve(path))

    def list_dir(self, path):
        full = self._resolve(path)
        if not os.path.isdir(full):
            raise StepFailure("нет папки: {0}".format(path))
        return sorted(os.listdir(full))

    # -- процессы (4, сценарные) -------------------------------------------

    def start_process(self, command, dir, log_path):
        self._resolve(log_path)
        pid = int(self._answer("process:{0}:{1}".format(command, dir),
                               "start_process({0})".format(command)))
        if pid < 1:
            raise StepFailure("pid меньше 1: {0}".format(pid))
        self._pids.add(pid)
        return pid

    def stop_process(self, pid):
        if pid in self._stopped:
            return  # идемпотентно: повторная остановка — no-op
        if pid not in self._pids:
            raise StepFailure("неизвестный pid: {0}".format(pid))
        self._pids.discard(pid)
        self._stopped.add(pid)

    def process_running(self, pid):
        return bool(self._answer("running:{0}".format(pid),
                                 "process_running({0})".format(pid)))

    def run_command(self, command, dir):
        code, stdout = self._answer("command:{0}:{1}".format(command, dir),
                                    "run_command({0})".format(command))
        return {"code": int(code), "stdout": stdout}

    # -- замки (2) -----------------------------------------------------------

    def acquire_lock(self, path, token):
        full = self._resolve(path)
        if os.path.exists(full):
            with open(full, encoding="utf-8") as f:
                owner = f.read()
            return owner == token  # свой токен — истина, чужой — ложь
        parent = os.path.dirname(full)
        if parent:
            os.makedirs(parent, exist_ok=True)
        # O_EXCL: атомарное создание; гонки двух хозяев не дают двух замков
        try:
            fd = os.open(full, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            with open(full, encoding="utf-8") as f:
                return f.read() == token
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(token)
        return True

    def release_lock(self, path, token):
        full = self._resolve(path)
        if not os.path.exists(full):
            return  # замка нет — no-op
        with open(full, encoding="utf-8") as f:
            owner = f.read()
        if owner != token:
            raise StepFailure("чужой токен замка: {0}".format(path))
        os.remove(full)

    # -- разбор и хеш (2) ----------------------------------------------------

    def parse_agent(self, instruction, input):
        text = self._answer("agent:{0}:{1}".format(instruction, input),
                            "parse_agent({0})".format(instruction))
        try:
            json.loads(text)  # механическая валидация: ответ — JSON-текст
        except ValueError:
            raise StepFailure("ответ parse_agent не JSON-текст")
        return text

    def sha256(self, text):
        # hashlib — стандартная библиотека Python, поверх системной криптобиблиотеки ОС
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if not self.HEX64.match(digest):  # самопроверка формата 64 hex
            raise StepFailure("sha256: не 64 hex")
        return digest

    # -- доверенное ядро (3) -------------------------------------------------

    def issue_token(self, task_dir, area, state):
        self._resolve(task_dir)
        return self._answer("token:{0}:{1}:{2}".format(task_dir, area, state),
                            "issue_token({0},{1})".format(task_dir, area))

    def verify_token(self, task_dir, token):
        opening = self._answer("opening:{0}:{1}".format(task_dir, token),
                               "verify_token({0})".format(task_dir))
        if opening is None:
            return None  # чтение не погашает открытие
        return dict(opening)

    def journal_write(self, event):
        code = event.get("code")
        params = event.get("params")
        if not code:
            raise StepFailure("journal_write: пустой код события")
        if (not isinstance(params, list)
                or any(not (isinstance(p, (list, tuple)) and len(p) == 2) for p in params)):
            raise StepFailure("journal_write: параметры не пары")
        self._journal.append({"code": code, "params": [list(p) for p in params]})

    def journal(self):
        return list(self._journal)
