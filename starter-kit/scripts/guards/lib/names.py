# -*- coding: utf-8 -*-
"""Список запрещённых имён: чтение из файла вне репозитория или из секрета, поиск образцов.

Зачем: имена приватных репозиториев, проектов и заказчиков нельзя хранить в публичном репозитории
    ни в каком виде; поэтому список лежит у владельца в файле, а в CI приходит секретом. Здесь он
    читается одинаково с концами строк LF и CRLF и с BOM, а его отсутствие — красный, не тишина.
Проверяет: наличие, читаемость и непустоту списка; ищет образцы подстрокой без учёта регистра.
Не проверяет: сами файлы репозитория (это check-private-names.py и guard-commit-message.py).
Правило: README комплекта, «Запрещённые имена».

Источники по приоритету (имена переменных и путь — параметры guards.conf): переменная
PRIVATE_NAMES_VAR (в CI — из секрета с тем же именем), затем файл из переменной
PRIVATE_NAMES_FILE_VAR, затем файл PRIVATE_NAMES_FILE. Формат: образец на строку, строка с решёткой
первым знаком — комментарий, пустые строки пропускаются. Номер образца — порядковый среди образцов
(без комментариев и пустых строк), с единицы. Значения образцов не попадают ни в вывод, ни в тексты
исключений.
"""
import sys

sys.dont_write_bytecode = True

import os

from guardlib import Unavailable
import conf as confmod


def _hint(var, file_var, default):
    return ("Заведите список: файл %s (путь переопределяет переменная %s), образец на строку, "
            "решётка — комментарий; в CI — секрет %s (заводится в настройках CI хостинга кода)."
            % (default, file_var, var))


def parse(text):
    """Образцы из текста списка; регистр свёрнут, CRLF и LF одинаковы."""
    patterns = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line.casefold())
    return patterns


def _decode(data, hint):
    if data.startswith((b"\xff\xfe", b"\xfe\xff")) or b"\x00" in data:
        raise Unavailable("список запрещённых имён сохранён в UTF-16 или с нулевыми байтами; "
                          "сохраните его как UTF-8. " + hint)
    return data.decode("utf-8-sig", "replace")


def load_names(conf=None):
    """Образцы списка запрещённых имён или Unavailable с подсказкой, как завести недостающее."""
    conf = conf or confmod.Conf()
    var = conf.get("PRIVATE_NAMES_VAR")
    file_var = conf.get("PRIVATE_NAMES_FILE_VAR")
    default = conf.get("PRIVATE_NAMES_FILE")
    hint = _hint(var, file_var, default)
    env = os.environ.get(var)
    env_empty = False
    if env is not None:
        patterns = parse(env.lstrip("﻿"))
        if patterns:
            return patterns
        env_empty = True
    path = os.environ.get(file_var) or os.path.expanduser(default)
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError:
        if env_empty:
            raise Unavailable("секрет или переменная %s пусты. %s" % (var, hint))
        raise Unavailable("нет списка запрещённых имён (файл не найден или не читается). " + hint)
    patterns = parse(_decode(data, hint))
    if not patterns:
        raise Unavailable("список запрещённых имён пуст. " + hint)
    return patterns


def find_names(text, patterns):
    """Номера (с единицы) образцов, которые встречаются в тексте подстрокой без учёта регистра."""
    folded = text.casefold()
    return [number for number, pattern in enumerate(patterns, 1) if pattern in folded]
