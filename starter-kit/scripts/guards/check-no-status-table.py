# -*- coding: utf-8 -*-
"""Страж рукописных таблиц статусов: список задач с состоянием руками не ведётся.

Зачем: таблица «задача — статус», набранная руками в .md, расходится с папками задач и их журналами
    и становится ложью; правду о задачах дают сами папки задач.
Проверяет: в отслеживаемых .md строку таблицы, у которой первая ячейка — ссылка на папку задачи (цель,
    разрешённая от файла, подходит под образец STATUS_TABLE_TASK_PATH из guards.conf), если у таблицы
    есть колонка состояния (заголовок подходит под STATUS_TABLE_COLUMN без учёта регистра). Одной такой
    строки достаточно. Слово статуса не перечисляется: признак — колонка.
Не проверяет: реестры, где ссылки ведут на файлы, а не на папки задач (например, реестр ADR), таблицы,
    где ссылка на задачу стоит не в первой ячейке, таблицы внутри блоков кода, списки задач без таблицы.
    STATUS_TABLE_TASK_PATH=off — «судить нечего» с этой причиной.
Правило: docs/guards.md (README комплекта), «Список задач руками не ведётся».

Пометок-исключений у этого стража нет.
"""
import sys

sys.dont_write_bytecode = True

import os
import posixpath
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import conf as confmod  # noqa: E402
import guardlib  # noqa: E402

SEPARATOR = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
FIRST_LINK = re.compile(r"^[*_ ]*!?\[[^\]]*\]\(\s*<?([^)>\s]+)>?(?:\s+[\"'][^)]*)?\)")


def split_row(line):
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", body)]


def find_status_tables(path, text, task_folder, status_column):
    """Строки таблиц статусов: список (номер строки) для файла path."""
    lines = guardlib.strip_fenced(text).split("\n")
    found = []
    i = 0
    while i + 1 < len(lines):
        if lines[i].lstrip().startswith("|") and SEPARATOR.match(lines[i + 1]) and "|" in lines[i + 1]:
            header = split_row(lines[i])
            has_status = any(status_column.match(cell) for cell in header)
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                if has_status:
                    cells = split_row(lines[j])
                    m = FIRST_LINK.match(cells[0]) if cells else None
                    if m:
                        target = m.group(1).split("#")[0]
                        if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                            joined = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
                            if task_folder.match(joined):
                                found.append(j + 1)
                j += 1
            i = j
        else:
            i += 1
    return found


def judge(source, args, rep):
    conf = confmod.Conf()
    task_path = conf.get("STATUS_TABLE_TASK_PATH")
    if task_path == "off":
        return guardlib.Outcome(nothing="папка задач не задана проектом (STATUS_TABLE_TASK_PATH=off в guards.conf)")
    task_folder = re.compile(task_path)
    status_column = re.compile(r"^[*_ ]*(?:%s)[*_ ]*$" % conf.get("STATUS_TABLE_COLUMN"), re.I)
    count = 0
    for entry in source.changed():
        if not entry.path.lower().endswith(".md") or entry.mode == "160000":
            continue
        data = source.read(entry)
        if data is None:
            continue
        count += 1
        text = data.decode("utf-8", "replace").lstrip("\ufeff")
        for number in find_status_tables(entry.path, text, task_folder, status_column):
            rep.add(entry.path, number, "status-table",
                    "рукописная таблица статусов задач: список задач — сами папки задач")
    return guardlib.Outcome(count=count)


if __name__ == "__main__":
    sys.exit(guardlib.run("check-no-status-table", "файлов .md", judge, lost="нет ни одного .md в репозитории"))
