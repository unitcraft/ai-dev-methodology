#!/usr/bin/env python3
"""Пробы ScriptedHost (задача 111, стадия 1) против спецификации host-spec.md.

Прогон из корня репозитория:
    python -m unittest discover -s doc/tasks/111-tonkiy-hozyain-stadiya-1-karkas-17-primi -p "test_*.py" -t .
или непосредственно:
    python doc/tasks/111-tonkiy-hozyain-stadiya-1-karkas-17-primi/test_scripted_host.py
"""
import io
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

from scripted_host import ScriptedHost, StepFailure  # noqa: E402

REGISTRY = os.path.join(ROOT, "alula-machines", "registry.md")

# 17 примитивов каркаса: имя -> (параметры, результат, класс) как в реестре.
# release_lock — действующая строка раннера; версия с токеном войдёт на стадии 4.
EXPECTED = {
    "read_file": ("path: text", "text", "volatile"),
    "write_file": ("path: text; content: text", "—", "acting"),
    "move_file": ("from: text; to: text", "—", "acting"),
    "delete_file": ("path: text", "—", "acting"),
    "file_exists": ("path: text", "bool", "volatile"),
    "list_dir": ("path: text", "[]text", "volatile"),
    "start_process": ("command: text; dir: text; log_path: text", "int>=1", "acting"),
    "stop_process": ("pid: int>=1", "—", "acting"),
    "process_running": ("pid: int>=1", "bool", "volatile"),
    "run_command": ("command: text; dir: text", "ExecResult", "acting"),
    "acquire_lock": ("path: text; token: text", "bool", "acting"),
    "release_lock": None,  # действующий без параметров; с токеном — стадия 4
    "parse_agent": ("instruction: text; input: text", "text", "volatile"),
    "sha256": ("text: text", "text", "pure"),
    "issue_token": ("task_dir: text; area: text; state: text", "text", "acting"),
    "verify_token": ("task_dir: text; token: text", "?Opening", "volatile"),
    "journal_write": ("event: JournalEvent", "—", "acting"),
}


def split_row(line):
    cells = re.split(r"(?<!\\)\|", line.strip())
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [c.strip().replace("\\|", "|") for c in cells]


def registry_primitives():
    with io.open(REGISTRY, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"^## Primitives\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    rows = [ln for ln in m.group(1).splitlines() if ln.strip().startswith("|")]
    header = split_row(rows[0])
    out = {}
    for ln in rows[2:]:
        cells = split_row(ln)
        out[cells[header.index("name")]] = (
            cells[header.index("parameters")],
            cells[header.index("result")],
            cells[header.index("class")],
        )
    return out


class RegistryContractTest(unittest.TestCase):
    """Каркас из 17 примитивов есть в реестре, сигнатуры совпадают с эталоном."""

    def test_all_17_present(self):
        reg = registry_primitives()
        for name in EXPECTED:
            self.assertIn(name, reg, "в реестре нет примитива {0}".format(name))

    def test_signatures_match(self):
        reg = registry_primitives()
        for name, sig in EXPECTED.items():
            if sig is None:
                continue
            self.assertEqual(sig, reg[name],
                             "сигнатура {0}: реестр {1}, эталон {2}".format(name, reg[name], sig))


class FilesystemTest(unittest.TestCase):
    def setUp(self):
        self.host = ScriptedHost()

    def test_write_read_exists_list_move_delete(self):
        self.host.write_file("a/b.txt", "привет")
        self.assertEqual(self.host.read_file("a/b.txt"), "привет")
        self.assertTrue(self.host.file_exists("a/b.txt"))
        self.assertEqual(self.host.list_dir("a"), ["b.txt"])
        self.host.move_file("a/b.txt", "c/d.txt")
        self.assertFalse(self.host.file_exists("a/b.txt"))
        self.assertEqual(self.host.read_file("c/d.txt"), "привет")
        self.host.delete_file("c/d.txt")
        self.assertFalse(self.host.file_exists("c/d.txt"))

    def test_path_outside_tree_fails(self):
        with self.assertRaises(StepFailure):
            self.host.read_file("../outside.txt")
        with self.assertRaises(StepFailure):
            self.host.write_file("/abs/path.txt", "x")

    def test_missing_file_is_step_failure(self):
        with self.assertRaises(StepFailure):
            self.host.read_file("no/such.txt")
        with self.assertRaises(StepFailure):
            self.host.delete_file("no/such.txt")
        with self.assertRaises(StepFailure):
            self.host.list_dir("no/such")


class ProcessTest(unittest.TestCase):
    def test_scripted_process_lifecycle(self):
        host = ScriptedHost({
            "process:build .:work": 42,
            "running:42": True,
            "command:git status:work": (0, "clean"),
        })
        pid = host.start_process("build .", "work", "logs/build.log")
        self.assertEqual(pid, 42)
        self.assertTrue(host.process_running(pid))
        host.stop_process(pid)
        host.stop_process(pid)  # идемпотентно: повтор — no-op
        with self.assertRaises(StepFailure):
            host.stop_process(777)  # неизвестный pid — сбой шага
        self.assertEqual(host.run_command("git status", "work"),
                         {"code": 0, "stdout": "clean"})

    def test_missing_scripted_answer_fails(self):
        host = ScriptedHost()
        with self.assertRaises(StepFailure):
            host.start_process("x", "d", "l.log")
        with self.assertRaises(StepFailure):
            host.process_running(1)
        with self.assertRaises(StepFailure):
            host.run_command("x", "d")


class LockTest(unittest.TestCase):
    def test_acquire_release_with_token(self):
        host = ScriptedHost()
        self.assertTrue(host.acquire_lock("locks/a", "токен-1"))
        self.assertFalse(host.acquire_lock("locks/a", "токен-2"))  # чужой — ложь
        self.assertTrue(host.acquire_lock("locks/a", "токен-1"))   # свой — истина
        with self.assertRaises(StepFailure):
            host.release_lock("locks/a", "токен-2")                # чужой — сбой шага
        host.release_lock("locks/a", "токен-1")
        host.release_lock("locks/a", "токен-1")                    # нет замка — no-op
        self.assertTrue(host.acquire_lock("locks/a", "токен-2"))   # свободен снова

    def test_lock_file_written(self):
        host = ScriptedHost()
        host.acquire_lock("locks/a", "токен-1")
        self.assertEqual(host.read_file("locks/a"), "токен-1")


class ParseAndHashTest(unittest.TestCase):
    def test_parse_agent_validates_json(self):
        host = ScriptedHost({"agent:инстр:вход": '{"итог": true}'})
        self.assertEqual(host.parse_agent("инстр", "вход"), '{"итог": true}')
        bad = ScriptedHost({"agent:и:в": "не json"})
        with self.assertRaises(StepFailure):
            bad.parse_agent("и", "в")

    def test_sha256_known_answer(self):
        host = ScriptedHost()
        self.assertEqual(
            host.sha256("abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertRegex(host.sha256(""), r"^[0-9a-f]{64}$")
        self.assertEqual(host.sha256("текст"), host.sha256("текст"))  # pure


class TrustedCoreTest(unittest.TestCase):
    def test_tokens_idempotent_and_non_consuming(self):
        host = ScriptedHost({
            "token:taskA:ворота:открыто": "токен-9",
            "opening:taskA:токен-9": {"author": "владелец", "date": "2026-11-06",
                                      "source": "чат", "content": "открыто"},
        })
        t1 = host.issue_token("taskA", "ворота", "открыто")
        t2 = host.issue_token("taskA", "ворота", "открыто")
        self.assertEqual(t1, t2)  # идемпотентно по паре «папка, область»
        opening = host.verify_token("taskA", t1)
        self.assertEqual(opening["author"], "владелец")
        self.assertIsNotNone(host.verify_token("taskA", t1))  # чтение не погашает

    def test_verify_unknown_token_none(self):
        host = ScriptedHost({"opening:taskA:чужой": None})
        self.assertIsNone(host.verify_token("taskA", "чужой"))

    def test_journal_write_appends_and_validates(self):
        host = ScriptedHost()
        host.journal_write({"code": "открытие", "params": [["ворота", "В2"]]})
        self.assertEqual(host.journal(), [{"code": "открытие", "params": [["ворота", "В2"]]}])
        with self.assertRaises(StepFailure):
            host.journal_write({"code": "", "params": []})
        with self.assertRaises(StepFailure):
            host.journal_write({"code": "x", "params": ["не-пара"]})


if __name__ == "__main__":
    unittest.main()
