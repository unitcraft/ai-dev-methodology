#!/usr/bin/env python3
"""Страж универсальности внешних функций хозяина (задача 103, правило 14б `state-machine-spec.md`).

Норма (правило 14б): внешняя функция хозяина — универсальный примитив среды исполнения
(чтение файла, запись файла, запуск команды и т. п.), а не предметный вызов под конкретный
документ или действие машины; предметная функция допустима, только если не раскладывается
на универсальные примитивы без потери смысла; причина — что теряется при разложении —
называется при её объявлении. Проверка правила: поиском по реестру хозяина у каждой
предметной функции стоит названная причина исключения. Уточнение критерия (интегратор,
2026-11-06): каждая внешняя функция — примитив: не раскладывается на другие внешние
функции без потери смысла; у каждой функции есть записанное доказательство, что она
не реализуется через существующие примитивы; раскладываемая — красный с указанием,
на какие примитивы.

Что проверяет:
  1. собирает все объявленные внешние функции — строки таблицы раздела «## Primitives»
     реестра хозяина (`alula-machines/registry.md`; столбцы — раздел 7 спецификации Алулы);
  2. функция из списка универсальных примитивов (УНИВЕРСАЛЬНЫЕ ниже) — зелёная;
     иначе она предметная и зелёная только с непустой причиной: из столбца `reason`
     таблицы «Primitives» или из отдельной таблицы раздела «## Reasons» (заголовок
     `| tool | reason |`; столбец в таблице «Primitives» не бывает — загрузчик реестра
     `parse_registry_table` читает строку примитива ровно из шести ячеек, задача 110);
     пустая ячейка и `—` — причины нет;
  3. красный на каждую предметную функцию без записанной причины: имя функции и причина
     находки; красный и тогда, когда записанная причина сама называет другие функции
     реестра (слово целиком), — декларация признаёт разложение: в находке перечисляются
     эти примитивы; код возврата 1.

Список универсальных примитивов закрытый: примеры правила 14б (чтение файла, запись
файла, запуск команды) и примитивы языка (`time_now`, `new_id` — шапка реестра, раздел 7а,
AL-113). Расширение списка — решение методики, не стража. Действующий реестр методики
норме не следует (строка реестра норм задачи 102): прогон по нему красный ожидаемо.

Запуск: из корня репозитория `python doc/tasks/103-strazh-universalnosti-vneshnih-funkciy/check_host_universality.py`
(`--registry <путь>` — другой реестр; `--selftest` — самопроверка); код возврата 1 при находках.
"""
import argparse
import io
import os
import re
import sys

# Универсальные примитивы среды исполнения (закрытый перечень, см. документацию выше).
UNIVERSAL_PRIMITIVES = frozenset({
    "read_file",
    "write_file",
    "run_command",
    "time_now",
    "new_id",
})

DEFAULT_REGISTRY = os.path.join("alula-machines", "registry.md")
REASON_COLUMN = "reason"
REASONS_SECTION = "## Reasons"
EMPTY_CELL = "—"

REASON_MISSING = "предметная функция без записанной причины нераскладываемости"


class Finding(object):
    """Одна находка: имя функции и причина."""

    def __init__(self, name, reason):
        self.name = name
        self.reason = reason

    def __str__(self):
        return "КРАСНЫЙ: {0} — {1} (правило 14б)".format(self.name, self.reason)


def split_row(line):
    """Ячейки строки таблицы: деление по каждому `|` без обратной косой перед ним (как GitHub)."""
    cells = re.split(r"(?<!\\)\|", line.strip())
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [c.strip().replace("\\|", "|") for c in cells]


def parse_primitives(text):
    """Строки таблицы «## Primitives»: список словарей {имя столбца: ячейка}.

    Без раздела или таблицы — ValueError: страж не работает молча.
    """
    m = re.search(r"^## Primitives\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        raise ValueError("в реестре нет раздела «## Primitives»")
    rows = [ln for ln in m.group(1).splitlines() if ln.strip().startswith("|")]
    if len(rows) < 2:
        raise ValueError("в разделе «## Primitives» нет таблицы")
    header = split_row(rows[0])
    if "name" not in header:
        raise ValueError("в таблице «Primitives» нет столбца «name»")
    if not re.match(r"^:?-+:?$", split_row(rows[1])[0].replace(" ", "")):
        raise ValueError("вторая строка таблицы «Primitives» — не разделитель")
    out = []
    for ln in rows[2:]:
        cells = split_row(ln)
        if len(cells) < len(header):
            cells = cells + [""] * (len(header) - len(cells))
        out.append(dict(zip(header, cells)))
    return out


def parse_reasons(text):
    """Таблица раздела «## Reasons»: {имя инструмента: причина}.

    Отдельная таблица — потому что строка примитива читается загрузчиком реестра
    ровно из шести ячеек и седьмого столбца в «Primitives» не бывает (задача 110).
    Заголовок таблицы — с первой ячейкой «tool» (не «name»: иначе это таблица
    примитивов). Раздела или таблицы нет — пустой словарь: причины необязательны.
    """
    m = re.search(r"^## Reasons\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return {}
    rows = [ln for ln in m.group(1).splitlines() if ln.strip().startswith("|")]
    if len(rows) < 2:
        return {}
    header = split_row(rows[0])
    if len(header) < 2 or header[1] != REASON_COLUMN:
        raise ValueError("в таблице «## Reasons» второй столбец — «reason»")
    out = {}
    for ln in rows[2:]:
        cells = split_row(ln)
        if len(cells) < 2:
            continue
        out[cells[0].strip("`")] = cells[1]
    return out


def referenced_functions(reason, names, own):
    """Имена других функций реестра, названные в записанной причине (слово целиком).

    Декларация, называющая другие функции, сама признаёт разложение на них.
    """
    found = []
    for n in sorted(names):
        if n != own and re.search(r"(?<![\w])" + re.escape(n) + r"(?![\w])", reason):
            found.append(n)
    return found


def check_registry(text):
    """Сверка реестра с правилом 14б. Возвращает (числа, находки)."""
    rows = parse_primitives(text)
    reasons = parse_reasons(text)
    names = set(row.get("name", "").strip("`") for row in rows)
    universal, justified = 0, 0
    findings = []
    for row in rows:
        name = row.get("name", "").strip("`")
        if name in UNIVERSAL_PRIMITIVES:
            universal += 1
            continue
        reason = row.get(REASON_COLUMN, "").strip()
        if not reason or reason == EMPTY_CELL:
            reason = reasons.get(name, "").strip()
        if not reason or reason == EMPTY_CELL:
            findings.append(Finding(name, REASON_MISSING))
            continue
        decomposed = referenced_functions(reason, names, name)
        if decomposed:
            findings.append(Finding(
                name,
                "раскладывается на примитивы: {0}: записанная причина сама называет "
                "реализацию через них".format(", ".join(decomposed))))
        else:
            justified += 1
    counts = {
        "total": len(rows),
        "universal": universal,
        "justified": justified,
        "unjustified": len(findings),
    }
    return counts, findings


def report(path, counts, findings, out):
    for f in findings:
        out.write(str(f) + "\n")
    out.write(
        "реестр {0}: внешних функций {1}; универсальных {2}; предметных с причиной {3}; "
        "предметных без причины {4}\n".format(
            path, counts["total"], counts["universal"], counts["justified"], counts["unjustified"]))
    out.write("ИТОГ: {0}\n".format("КРАСНЫЙ" if findings else "зелёный"))


def selftest(out):
    """Самопроверка стража на встроенных реестрах: список не пуст и находки ловятся."""
    ok = True

    def expect(label, cond):
        nonlocal ok
        out.write("самотест: {0} — {1}\n".format(label, "ок" if cond else "ПРОВАЛ"))
        ok = ok and cond

    expect("список универсальных примитивов не пуст", len(UNIVERSAL_PRIMITIVES) > 0)

    table_universal = (
        "## Primitives\n\n| name | parameters | result | class | reads | writes |\n"
        "|---|---|---|---|---|---|\n| read_file | path: text | text | volatile | — | — |\n")
    counts, findings = check_registry(table_universal)
    expect("универсальная функция зелёная", counts["total"] == 1 and not findings)

    table_reason = (
        "## Primitives\n\n| name | parameters | result | class | reads | writes | reason |\n"
        "|---|---|---|---|---|---|---|\n"
        "| verify_owner_route_decision | task_dir: text | text | volatile | — | — | решение владельца не раскладывается на примитивы без потери доверия |\n")
    counts, findings = check_registry(table_reason)
    expect("предметная с записанной причиной зелёная", counts["justified"] == 1 and not findings)

    table_reasons_section = (
        table_reason +
        "## Reasons\n\n| tool | reason |\n|---|---|\n"
        "| verify_owner_route_decision | решение владельца не раскладывается на примитивы без потери доверия |\n")
    counts, findings = check_registry(table_reasons_section)
    expect("причина из отдельной таблицы «## Reasons» зелёная",
           counts["justified"] == 1 and not findings)

    table_bare = table_universal.replace(
        "| read_file | path: text | text | volatile | — | — |",
        "| stop_agent_group | — | — | acting | — | — |")
    counts, findings = check_registry(table_bare)
    expect(
        "предметная без причины красная с именем и причиной",
        len(findings) == 1 and findings[0].name == "stop_agent_group"
        and findings[0].reason == REASON_MISSING)

    table_dash = table_reason.replace(
        "решение владельца не раскладывается на примитивы без потери доверия", EMPTY_CELL)
    counts, findings = check_registry(table_dash)
    expect("причина «—» — причины нет", len(findings) == 1)

    table_bare_with_reasons = (
        table_bare +
        "## Reasons\n\n| tool | reason |\n|---|---|\n| stop_agent_group | — |\n")
    counts, findings = check_registry(table_bare_with_reasons)
    expect("причина «—» в таблице «## Reasons» — причины нет", len(findings) == 1)

    table_decomposed = (
        "## Primitives\n\n| name | parameters | result | class | reads | writes | reason |\n"
        "|---|---|---|---|---|---|---|\n"
        "| read_file | path: text | text | volatile | — | — | — |\n"
        "| proposal_with_fingerprint | — | text | volatile | — | — | читает файл read_file и считает отпечаток |\n")
    counts, findings = check_registry(table_decomposed)
    expect(
        "причина, называющая другую функцию, — красный с перечнем примитивов",
        len(findings) == 1 and findings[0].name == "proposal_with_fingerprint"
        and "read_file" in findings[0].reason)

    out.write("самотест: ИТОГ {0}\n".format("зелёный" if ok else "КРАСНЫЙ"))
    return ok


def main(argv):
    ap = argparse.ArgumentParser(description="Страж универсальности внешних функций хозяина (правило 14б).")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY,
                    help="реестр хозяина (по умолчанию %(default)s, запуск из корня репозитория)")
    ap.add_argument("--selftest", action="store_true", help="самопроверка без чтения реестра")
    args = ap.parse_args(argv)

    if args.selftest:
        return 0 if selftest(sys.stdout) else 1

    with io.open(args.registry, encoding="utf-8") as f:
        text = f.read()
    try:
        counts, findings = check_registry(text)
    except ValueError as e:
        sys.stdout.write("КРАСНЫЙ: {0}: {1}\n".format(args.registry, e))
        return 1
    report(args.registry, counts, findings, sys.stdout)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
