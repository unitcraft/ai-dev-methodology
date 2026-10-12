# -*- coding: utf-8 -*-
"""Страж формата документов задач: машинные места документов по правилам проекта из guards.conf.

Зачем: программа цикла задач и сами сессии читают из документов задач машинные места (статус в
    первой строке, итог захода проверки, номера требований, строки журнала хода); молча испорченное
    место запускает проверку заново поверх утверждённого документа или теряет заход, и в обзоре
    этого не видно.
Проверяет: каждый отслеживаемый файл, путь которого подходит под образец пути хотя бы одного правила
    TASK_DOC_RULE, по видам правил: first-line — первая строка (без BOM и CR в конце) подходит под
    образец строки (first-line); если у образца пути и образца строки есть группа (?P<n>...), числа в
    них равны (first-line, «номер захода как в имени файла»); every-line — каждая непустая строка
    (деление по LF, один CR в конце снимается) подходит под образец (line-form); unique — значение,
    найденное образцом в начале строки (группа id или всё совпадение), не повторяется в файле (dup-id).
    Образец строки прикладывается с начала строки; чтобы требовать строку целиком, закончите его $.
Не проверяет: содержание документов, файлы вне образцов путей, честность строк журнала (это дело
    приёмки). Формат комплект не выдумывает: TASK_DOC_RULE=off — «судить нечего» с этой причиной.
Правило: README комплекта, «Формат документов задач».

Пометок-исключений у этого стража нет.
"""
import sys

sys.dont_write_bytecode = True

import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import conf as confmod  # noqa: E402
import guardlib  # noqa: E402


def split_lines(data):
    """Байты → строки: UTF-8 с заменой, BOM снят, деление только по LF, один CR в конце снимается."""
    parts = data.decode("utf-8", "replace").lstrip("﻿").split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    return [p[:-1] if p.endswith("\r") else p for p in parts]


def check_first_line(path, path_match, line_re, lines, number, rep):
    first = lines[0] if lines else ""
    m = line_re.match(first)
    if not m:
        rep.add(path, 1, "first-line", "первая строка не по образцу правила TASK_DOC_RULE №%d" % number)
        return
    want = path_match.groupdict().get("n")
    got = m.groupdict().get("n")
    if want is not None and got is not None and int(want) != int(got):
        rep.add(path, 1, "first-line", "номер в первой строке (%s) не равен номеру в имени файла (%s), "
                "правило №%d" % (got, want, number))


def check_every_line(path, line_re, lines, number, rep):
    for lineno, line in enumerate(lines, 1):
        if line == "":
            continue
        if not line_re.match(line):
            rep.add(path, lineno, "line-form", "строка не по образцу правила TASK_DOC_RULE №%d" % number)


def check_unique(path, line_re, lines, number, rep):
    seen = {}
    for lineno, line in enumerate(lines, 1):
        m = line_re.match(line)
        if not m:
            continue
        key = m.groupdict().get("id") or m.group(0)
        if key in seen:
            rep.add(path, lineno, "dup-id", "повтор %s (первое объявление в строке %d), правило №%d"
                    % (key, seen[key], number))
        else:
            seen[key] = lineno


def judge(source, args, rep):
    rules = confmod.Conf().task_rules()
    if rules is None:
        return guardlib.Outcome(nothing="формат документов задач не задан проектом (TASK_DOC_RULE=off в guards.conf)")
    count = 0
    for entry in source.changed():
        if entry.mode == "160000":
            continue
        matched = [(number, kind, path_re.match(entry.path), line_re)
                   for number, (kind, path_re, line_re) in enumerate(rules, 1)]
        matched = [m for m in matched if m[2]]
        if not matched:
            continue
        data = source.read(entry)
        if data is None:
            continue
        count += 1
        lines = split_lines(data)
        for number, kind, path_match, line_re in matched:
            if kind == "first-line":
                check_first_line(entry.path, path_match, line_re, lines, number, rep)
            elif kind == "every-line":
                check_every_line(entry.path, line_re, lines, number, rep)
            else:
                check_unique(entry.path, line_re, lines, number, rep)
    return guardlib.Outcome(count=count)


if __name__ == "__main__":
    sys.exit(guardlib.run("check-task-docs", "файлов задач", judge,
                          lost="нет ни одного файла под образцами путей TASK_DOC_RULE"))
