# -*- coding: utf-8 -*-
"""Страж пустых тестов: файл теста без единой проверки.

Зачем: тест без проверок всегда зелёный и создаёт ощущение покрытия; он появляется при копировании
    заготовки или незаконченной правке и не виден в обзоре.
Проверяет: каждый отслеживаемый файл, путь которого подходит под TEST_FILES из guards.conf, содержит
    хотя бы одно совпадение с образцом проверки TEST_CHECK после того, как из текста вырезаны
    комментарии по образцу TEST_COMMENT (режим многострочный: ^ и $ — границы строки). Что внутри
    проверки (в том числе литерал true), не судится.
Не проверяет: качество проверок, покрытие кода, файлы вне образца TEST_FILES, результат прогона
    тестов. TEST_FILES=off — «судить нечего» с этой причиной.
Правило: README комплекта, «Тест без проверок».

Пометок-исключений у этого стража нет.
"""
import sys

sys.dont_write_bytecode = True

import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import conf as confmod  # noqa: E402
import guardlib  # noqa: E402


def count_checks(text, check, comment):
    """Число проверок в тексте теста: совпадения образца проверки вне комментариев."""
    if comment is not None:
        text = comment.sub("", text)
    return len(check.findall(text))


def judge(source, args, rep):
    conf = confmod.Conf()
    files = conf.get("TEST_FILES")
    if files == "off":
        return guardlib.Outcome(nothing="файлы тестов не заданы проектом (TEST_FILES=off в guards.conf)")
    test_file = re.compile(files)
    check = re.compile(conf.get("TEST_CHECK"), re.M)
    comment_re = conf.get("TEST_COMMENT")
    comment = None if comment_re == "none" else re.compile(comment_re, re.M)
    count = 0
    for entry in source.changed():
        if not test_file.match(entry.path) or entry.mode == "160000":
            continue
        data = source.read(entry)
        if data is None:
            continue
        count += 1
        if count_checks(data.decode("utf-8", "replace"), check, comment) == 0:
            rep.add(entry.path, None, "empty-test", "в тесте нет ни одной проверки (образец TEST_CHECK)")
    return guardlib.Outcome(count=count)


if __name__ == "__main__":
    sys.exit(guardlib.run("check-tests-have-checks", "файлов тестов", judge,
                          lost="нет ни одного файла под образцом TEST_FILES"))
