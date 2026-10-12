# -*- coding: utf-8 -*-
"""Самотест стража рукописных таблиц статусов check-no-status-table.py.

Зачем: таблица «задача — статус», набранная руками, расходится с правдой; страж, который краснит
    реестр решений или таблицу частей в README корня, будут обходить, а тот, что пропускает настоящую
    таблицу, бесполезен.
Проверяет: на временном guards.conf с образцом папки задач: красные — строка таблицы с колонкой
    «Статус»/«Status»/«State» и ссылкой на папку задачи в первой ячейке (одна строка достаточна, любой
    статус словом или фразой, ссылка относительно файла); зелёные — реестр решений (ссылки на файлы),
    таблица частей корня (ссылка на задачу не в первой ячейке), таблица без колонки состояния, таблица в
    блоке кода, список задач без таблицы; свой заголовок колонки (STATUS_TABLE_COLUMN);
    STATUS_TABLE_TASK_PATH=off — «судить нечего» с причиной; нет ключа или битое выражение — красная
    предпосылка; нет ни одного .md — мишень потеряна.
Не проверяет: списки задач без таблицы, содержимое ячеек статуса.
Правило: docs/guards.md (README комплекта), «Список задач руками не ведётся».

Фикстура таблицы собирается при прогоне; папка задач в пробах — tasks/.
"""
import sys

sys.dont_write_bytecode = True

import stlib

TICK3 = "`" * 3
SEP = "|---|---|\n"
TASK_PATH = r"^tasks/[0-9]+[^/]*/?$"


def main():
    pr = stlib.Probes("check-no-status-table")
    base = pr.mkdtemp()
    env0 = stlib.isolated_env(base)
    env = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"STATUS_TABLE_TASK_PATH": TASK_PATH}))
    counter = [0]

    def fresh(files):
        counter[0] += 1
        return stlib.make_repo(base, env, files, name="r%d" % counter[0])

    def check(repo, *args, **kw):
        return stlib.guard("check-no-status-table.py", repo, kw.get("env", env), *args)

    folder = {"tasks/001-x/spec.md": "x\n", "tasks/README.md": "x\n"}

    def red(readme, where, path="tasks/README.md", e=None):
        def fn():
            files = dict(folder)
            files[path] = readme
            proc = check(fresh(files), env=e or env)
            stlib.expect(proc, 1, "FAIL: check-no-status-table: 1 нарушений")
            assert stlib.has_line(proc, "FAIL %s:%s: status-table:" % (path, where)), proc.out
        return fn

    def green(readme, files=None, path="tasks/README.md"):
        def fn():
            f = dict(folder)
            f.update(files or {})
            f[path] = readme
            stlib.expect(check(fresh(f)), 0, "ок: осмотрено")
        return fn

    def legit_decision_registry():
        files = {"doc/decisions/README.md": "| № | Решение | Статус |\n|---|---|---|\n"
                 "| [0001](0001-x.md) | Работа по методике | принято |\n",
                 "doc/decisions/0001-x.md": "x\n"}
        stlib.expect(check(fresh(files)), 0, "ок: осмотрено")

    def legit_parts_table():
        text = ("| Папка | Что | State |\n|---|---|---|\n"
                "| `service/` | сервис ([задача](tasks/001-x/)) | planned |\n"
                "| [plugin/](plugin/) | расширение | in use |\n")
        stlib.expect(check(fresh({"README.md": text, "tasks/001-x/spec.md": "x\n", "plugin/a.txt": "x\n"})), 0, "ок: осмотрено")

    def off_is_nothing_to_judge():
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"STATUS_TABLE_TASK_PATH": "off"}))
        files = dict(folder)
        files["tasks/README.md"] = "| Задача | Статус |\n" + SEP + "| [001](001-x/) | идёт |\n"
        proc = check(fresh(files), env=e)
        stlib.expect(proc, 0, "судить нечего: папка задач не задана проектом (STATUS_TABLE_TASK_PATH=off")

    def key_missing_or_broken():
        for value, words in ((None, "нет обязательного ключа STATUS_TABLE_TASK_PATH"), ("^tasks/(", "не разбирается")):
            e = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"STATUS_TABLE_TASK_PATH": value}))
            proc = check(fresh(dict(folder)), env=e)
            stlib.expect(proc, 1, "FAIL: предпосылка")
            assert words in proc.out, (value, proc.out)

    own_column = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"STATUS_TABLE_TASK_PATH": TASK_PATH,
                                                                "STATUS_TABLE_COLUMN": "этап"}))

    pr.probe("законное", "реестр решений: ссылки на файлы", legit_decision_registry)
    pr.probe("законное", "таблица частей корня: задача в колонке State, не в первой ячейке", legit_parts_table)
    pr.probe("законное", "таблица со ссылками на папки задач, но без колонки состояния",
             green("| Задача | Кто |\n" + SEP + "| [001](001-x/) | владелец |\n"))
    pr.probe("законное", "таблица в огороженном блоке кода",
             green("пример:\n" + TICK3 + "\n| Задача | Статус |\n" + SEP + "| [001](001-x/) | идёт |\n" + TICK3 + "\n"))
    pr.probe("законное", "список задач без таблицы этот страж не судит", green("- [001](001-x/) — идёт\n"))
    pr.probe("законное", "STATUS_TABLE_TASK_PATH=off: судить нечего с причиной", off_is_nothing_to_judge)
    pr.probe("красная", "колонка «Статус», слово статуса",
             red("# Задачи\n\n| Задача | Статус |\n" + SEP + "| [001 — x](001-x/) | РАЗБОР |\n", "5"))
    pr.probe("красная", "статус фразой с запятыми",
             red("| Задача | Статус |\n" + SEP + "| [001](001-x/) | РАЗБОР: С1 сделана, идёт С2 |\n", "3"))
    pr.probe("красная", "заголовок Status", red("| Task | Status |\n" + SEP + "| [001](001-x) | open |\n", "3"))
    pr.probe("красная", "заголовок State и жирный шрифт", red("| Task | **State** |\n" + SEP + "| [001](001-x/) | open |\n", "3"))
    pr.probe("красная", "одна строка среди нескольких законных",
             red("| Что | Статус |\n" + SEP + "| [Обзор](../README.md) | ок |\n| [001](001-x/) | идёт |\n", "4"))
    pr.probe("красная", "свой заголовок колонки из STATUS_TABLE_COLUMN",
             red("| Задача | Этап |\n" + SEP + "| [001](001-x/) | разбор |\n", "3", e=own_column))
    pr.probe("иной-синтаксис", "ссылка от другого файла: ../tasks/001-x/",
             red("| Задача | Статус |\n" + SEP + "| [001](../tasks/001-x/) | идёт |\n", "3", path="doc/list.md"))
    pr.probe("иной-синтаксис", "ссылка на папку от корня: tasks/001-x",
             red("| Задача | Статус |\n" + SEP + "| [001](tasks/001-x) | идёт |\n", "3", path="README.md"))
    pr.probe("мишень", "нет ключа или битое выражение — красная предпосылка", key_missing_or_broken)
    pr.probe("мишень", "нет ни одного .md — мишень потеряна",
             lambda: stlib.expect(check(fresh({"a.txt": "x\n"})), 1, "FAIL: мишень потеряна"))
    return pr.done()


if __name__ == "__main__":
    sys.exit(main())
