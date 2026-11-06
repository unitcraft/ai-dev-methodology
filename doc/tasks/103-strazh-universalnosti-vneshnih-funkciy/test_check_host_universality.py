#!/usr/bin/env python3
"""Пробы стража универсальности внешних функций (задача 103).

Позитивные: универсальная функция и предметная с записанной причиной — зелёные.
Негативные: предметная без столбца причины, с пустой причиной и с «—» — красные,
в находке имя функции и причина. Характеризация: действующий реестр методики
(`alula-machines/registry.md`) норме не следует (задача 102), страж на нём красный
по всем объявленным функциям. Запуск из папки задачи: `python -m unittest -v test_check_host_universality`.
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
        self.assertEqual(70, len(rows))
        names = [r["name"] for r in rows]
        self.assertIn("verify_owner_route_decision", names)
        self.assertIn("show_human", names)
        self.assertEqual(len(set(names)), len(names))

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


class SelftestTest(unittest.TestCase):
    """Самотест стража."""

    def test_selftest_flag_is_green(self):
        p = subprocess.run([sys.executable, GUARD, "--selftest"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(0, p.returncode, p.stdout + p.stderr)
        self.assertIn("самотест: ИТОГ зелёный", p.stdout)


class CurrentRegistryTest(unittest.TestCase):
    """Характеризация: действующий реестр норме 14б не следует (строка реестра норм
    задачи 102), поэтому прогон по нему красный ожидаемо. Когда реестр пересмотрят,
    эта проба переворачивается."""

    def test_current_registry_is_red_with_all_names(self):
        p = subprocess.run([sys.executable, GUARD, "--registry", REGISTRY],
                           capture_output=True, text=True, encoding="utf-8", cwd=REPO)
        self.assertEqual(1, p.returncode, p.stdout + p.stderr)
        self.assertIn("внешних функций 70", p.stdout)
        self.assertIn("предметных без причины 70", p.stdout)
        self.assertIn("ИТОГ: КРАСНЫЙ", p.stdout)
        self.assertIn("stop_agent_group", p.stdout)


if __name__ == "__main__":
    unittest.main()
