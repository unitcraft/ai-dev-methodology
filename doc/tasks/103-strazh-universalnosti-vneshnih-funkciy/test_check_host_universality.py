#!/usr/bin/env python3
"""Пробы стража универсальности внешних функций (задача 103; причины отдельной
таблицей «## Reasons» — задача 110).

Позитивные: универсальная функция и предметная с записанной причиной — зелёные
(причина — столбец `reason` таблицы «Primitives» или таблица «## Reasons»).
Негативные: предметная без столбца причины, с пустой причиной и с «—» — красные,
в находке имя функции и причина. Характеризация: действующий реестр методики
(`alula-machines/registry.md`) после задачи 110 норме 14б следует: у каждого из 71
предметного инструмента записана причина нераскладываемости, страж на нём зелёный.
Запуск из папки задачи: `python -m unittest -v test_check_host_universality`.
"""
import io
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GUARD = os.path.join(HERE, "check_host_universality.py")
REGISTRY = os.path.join(REPO, "alula-machines", "registry.md")

sys.path.insert(0, HERE)
import check_host_universality as guard

HEADER = "| name | parameters | result | class | reads | writes |"
SEP = "|---|---|---|---|---|---|"


def table(rows, reason_column=False, reasons=None):
    head, sep = HEADER, SEP
    if reason_column:
        head += " reason |"
        sep = sep[:-1] + "---|"
    lines = ["## Primitives", "", head, sep]
    for i, row in enumerate(rows):
        if reason_column:
            row = row + " | " + (reasons[i] if reasons else "")
        lines.append("| " + row + " |")
    return "\n".join(lines) + "\n"


class CollectTest(unittest.TestCase):
    """Шаг 1 критерия: собрать все объявленные внешние функции."""

    def test_all_declared_functions_collected(self):
        with io.open(REGISTRY, encoding="utf-8") as f:
            text = f.read()
        rows = guard.parse_primitives(text)
        self.assertEqual(87, len(rows))
        names = [r["name"] for r in rows]
        self.assertIn("verify_owner_route_decision", names)
        self.assertIn("show_human", names)
        self.assertIn("issue_token", names)
        self.assertEqual(len(set(names)), len(names))

    def test_reasons_collected_for_every_declared_function(self):
        with io.open(REGISTRY, encoding="utf-8") as f:
            text = f.read()
        rows = guard.parse_primitives(text)
        reasons = guard.parse_reasons(text)
        for row in rows:
            if row["name"].strip("`") in guard.UNIVERSAL_PRIMITIVES:
                continue
            reason = reasons.get(row["name"], "")
            self.assertTrue(reason and reason != guard.EMPTY_CELL,
                            "у {0} нет причины в таблице «## Reasons»".format(row["name"]))

    def test_universal_primitives_of_thin_host_are_declared(self):
        """Каркас тонкого хозяина (задача 111): универсальные примитивы эпика есть в реестре."""
        with io.open(REGISTRY, encoding="utf-8") as f:
            text = f.read()
        names = set(r["name"] for r in guard.parse_primitives(text))
        for name in ("read_file", "write_file", "move_file", "delete_file", "file_exists",
                     "list_dir", "start_process", "stop_process", "process_running",
                     "run_command", "acquire_lock", "parse_agent", "sha256"):
            self.assertIn(name, names)

    def test_registry_without_primitives_section_is_red(self):
        with self.assertRaises(ValueError):
            guard.parse_primitives("# Реестр без раздела\n")


class PositiveProbeTest(unittest.TestCase):
    """Позитивные пробы: страж зелёный."""

    def test_universal_primitive_is_green(self):
        counts, findings = guard.check_registry(
            table(["read_file | path: text | text | volatile | — | —"]))
        self.assertEqual(1, counts["universal"])
        self.assertEqual([], findings)

    def test_domain_function_with_recorded_reason_is_green(self):
        counts, findings = guard.check_registry(table(
            ["verify_owner_route_decision | task_dir: text | text | volatile | — | —"],
            reason_column=True,
            reasons=["решение владельца не раскладывается на примитивы без потери доверия"]))
        self.assertEqual(1, counts["justified"])
        self.assertEqual([], findings)
    def test_domain_function_with_reason_in_reasons_section_is_green(self):
        """Задача 110: причина в отдельной таблице раздела «## Reasons» — зелёная."""
        text = table(
            ["verify_owner_route_decision | task_dir: text | text | volatile | — | —"])
        text += ("## Reasons\n\n| tool | reason |\n|---|---|\n"
                 "| verify_owner_route_decision | решение владельца не раскладывается "
                 "на примитивы без потери доверия |\n")
        counts, findings = guard.check_registry(text)
        self.assertEqual(1, counts["justified"])
        self.assertEqual([], findings)


class NegativeProbeTest(unittest.TestCase):
    """Негативные пробы: красный с названием функции и причиной."""

    def test_domain_function_without_reason_is_red(self):
        counts, findings = guard.check_registry(
            table(["stop_agent_group | — | — | acting | — | —"]))
        self.assertEqual(1, counts["unjustified"])
        self.assertEqual(1, len(findings))
        self.assertEqual("stop_agent_group", findings[0].name)
        self.assertEqual(guard.REASON_MISSING, findings[0].reason)
        self.assertIn("stop_agent_group", str(findings[0]))
        self.assertIn("без записанной причины", str(findings[0]))

    def test_empty_reason_is_red(self):
        _, findings = guard.check_registry(table(
            ["stop_agent_group | — | — | acting | — | —"], reason_column=True, reasons=[""]))
        self.assertEqual(1, len(findings))

    def test_dash_reason_is_red(self):
        _, findings = guard.check_registry(table(
            ["stop_agent_group | — | — | acting | — | —"], reason_column=True, reasons=["—"]))
        self.assertEqual(1, len(findings))

    def test_reason_naming_other_function_is_red_with_primitives(self):
        """Уточнение критерия: декларация, называющая другие функции реестра, сама
        признаёт разложение — красный с перечнем этих примитивов."""
        _, findings = guard.check_registry(table(
            ["read_file | path: text | text | volatile | — | —",
             "proposal_with_fingerprint | — | text | volatile | — | —"],
            reason_column=True,
            reasons=["—", "читает файл read_file и считает отпечаток"]))
        self.assertEqual(1, len(findings))
        self.assertEqual("proposal_with_fingerprint", findings[0].name)
        self.assertIn("раскладывается на примитивы: read_file", findings[0].reason)

    def test_reason_mentioning_undeclared_name_is_green(self):
        """Имя не из реестра — не разложение на существующие примитивы."""
        _, findings = guard.check_registry(table(
            ["verify_owner_route_decision | task_dir: text | text | volatile | — | —"],
            reason_column=True,
            reasons=["доверие теряется при разложении на чтение read_dir и сверку"]))
        self.assertEqual([], findings)

    def test_reason_naming_itself_is_green(self):
        _, findings = guard.check_registry(table(
            ["verify_owner_route_decision | task_dir: text | text | volatile | — | —"],
            reason_column=True,
            reasons=["verify_owner_route_decision не раскладывается без потери доверия"]))
        self.assertEqual([], findings)


class SelftestTest(unittest.TestCase):
    """Самотест стража."""

    def test_selftest_flag_is_green(self):
        p = subprocess.run([sys.executable, GUARD, "--selftest"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)
        self.assertIn("самотест: ИТОГ зелёный", p.stdout)


class CurrentRegistryTest(unittest.TestCase):
    """Характеризация после задачи 110: действующий реестр норме 14б следует —
    у каждого из 71 предметного инструмента записана причина нераскладываемости
    в таблице «## Reasons», страж на нём зелёный (бывшая красная проба задачи 103
    перевёрнута этой правкой)."""

    def test_current_registry_is_green_with_all_reasons(self):
        p = subprocess.run([sys.executable, GUARD, "--registry", REGISTRY],
                           capture_output=True, text=True, encoding="utf-8", cwd=REPO)
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)
        self.assertIn("внешних функций 87", p.stdout)
        self.assertIn("предметных с причиной 74", p.stdout)
        self.assertIn("предметных без причины 0", p.stdout)
        self.assertIn("ИТОГ: зелёный", p.stdout)


if __name__ == "__main__":
    unittest.main()
