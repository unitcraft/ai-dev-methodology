# -*- coding: utf-8 -*-
"""Страж тонкости хозяина: машина не производит эффектов сама, хозяин не импортирует машину.

Зачем: решения машины (выбор перехода, условия развилок, какой эффект нужен) принимает только машина;
    логика, ушедшая в хозяина, не покрывается сверкой машины и при замене хозяина меняется молча, а прямой
    вызов эффекта из шага машины делает шаг неповторимым: повтор шага повторяет действие во внешнем мире.
Проверяет: в файлах машин (путь подходит под MACHINE_FILES из guards.conf) строки с прямым вызовом
    эффекта (строка подходит под MACHINE_EFFECT): шаг машины по состоянию и событию возвращает новое
    состояние и перечень эффектов, а выполняет эффекты хозяин; в файлах хозяев (путь подходит под
    HOST_FILES) строки импорта модуля машины (строка подходит под MACHINE_IMPORT): хозяин ведёт машину
    через исполнителя одинаково для любой машины. Включённый страж требует обеих мишеней: в дереве и в
    индексе ноль файлов машин или ноль файлов хозяев — красный с названной стороной, а не «ок» (пустота
    не бывает чистой). MACHINE_FILES=off — «судить нечего» с этой причиной.
Не проверяет: ветвление хозяина по данным машины и смысл эффектов (статически по строкам не отличить);
    динамическую половину правила (замена хозяина на тестового не меняет поведение машины — её проверяет
    приёмка прогоном); комментарии и литералы: язык проекта стражу неизвестен, образцы вызова и импорта
    проект подбирает так, чтобы они не ловили данные (например, закрывающей скобкой вызова).
Правило: docs/guards.md (README комплекта), «Хозяин машины минимален».

Исключение по строке — пометка с причиной в комментарии на той же строке: guard-allow(machine-effect):
<причина> или guard-allow(host-import): <причина>; для файла-образца нарушения — guard-fixture с теми же
именами правил. Пометка без причины — красный.
"""
import sys

sys.dont_write_bytecode = True

import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import conf as confmod  # noqa: E402
import guardlib  # noqa: E402


def judge(source, args, rep):
    conf = confmod.Conf()
    machines = conf.get("MACHINE_FILES")
    if machines == "off":
        return guardlib.Outcome(nothing="код машин и хозяев не задан проектом (MACHINE_FILES=off в guards.conf)")
    machine_path = re.compile(machines)
    effect = re.compile(conf.get("MACHINE_EFFECT"))
    host_path = re.compile(conf.get("HOST_FILES"))
    machine_import = re.compile(conf.get("MACHINE_IMPORT"))
    count = 0
    seen_machine = False
    seen_host = False
    for entry in source.changed():
        is_machine = machine_path.match(entry.path) is not None
        is_host = host_path.match(entry.path) is not None
        if not (is_machine or is_host) or entry.mode == "160000":
            continue
        name = entry.path.rsplit("/", 1)[-1]
        ext = name.rsplit(".", 1)[-1].lower() if "." in name.lstrip(".") else ""
        if ext in guardlib.BINARY_EXT:
            continue
        data = source.read(entry)
        if data is None:
            continue
        count += 1
        view = guardlib.FileView(entry.path, data)
        if is_machine:
            seen_machine = True
            for number, line in enumerate(view.lines, 1):
                if effect.search(line):
                    view.report(rep, "machine-effect", number,
                                "прямой вызов эффекта в машине: шаг возвращает перечень эффектов, выполняет их хозяин")
        if is_host:
            seen_host = True
            for number, line in enumerate(view.lines, 1):
                if machine_import.search(line):
                    view.report(rep, "host-import", number,
                                "хозяин импортирует машину: хозяин ведёт её через исполнителя одинаково для любой машины")
    if count and source.mode != "commit":
        if not seen_machine:
            rep.add(conf.name, None, "target",
                    "образцу MACHINE_FILES не соответствует ни один файл: машины потеряны (папку переименовали?)")
        if not seen_host:
            rep.add(conf.name, None, "target",
                    "образцу HOST_FILES не соответствует ни один файл: хозяева потеряны (папку переименовали?)")
    return guardlib.Outcome(count=count)


if __name__ == "__main__":
    sys.exit(guardlib.run("check-thin-host", "файлов машин и хозяев", judge,
                          lost="нет файлов под образцами MACHINE_FILES и HOST_FILES"))
