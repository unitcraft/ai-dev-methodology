#!/usr/bin/env python3
"""Сверка таблиц состояний (`*-states.md`) с кодом автомата (`*-automaton.md`).

Зачем: таблицы «Куда» — источник правды, код повторяет их вручную; расхождение молчит до первой реализации.
Что проверяет, для каждой пары файлов:
  1. каждому состоянию из раздела «Состояния» соответствует вариант `State` (имя — по словарю `state-machine-glossary.md`), и наоборот;
  2. вид состояния в заголовке («обращение», «операция», «развилка», «конец») совпадает с `@kind`;
  3. каждая ячейка «Куда» — имя состояния этой машины (или слово из ДОПУСТИМЫЕ_КУДА);
  4. все состояния достижимы из начального; у каждого не-конца есть выход;
  5. сторона в строке «Сторона:» совпадает с `appeal_party`.
Сверка журнала (`check_journal`: все `*-automaton.md` машин и движка и `state-machine-journal.md`):
  6. каждый код из `journal_event("…", …)` есть в таблице шаблонов `state-machine-journal.md`, и наоборот; машины строки таблицы — ровно те, где код пишется;
  7. имена параметров в вызове совпадают с `{…}` шаблона и со столбцом «Параметры»;
  8. в вызовах `write_journal(` и `machine_error(` нет строкового литерала (русский текст журнала живёт только в таблице шаблонов).
Чего не проверяет: данные событий, условия развилок, тела функций, значения параметров.
Запуск: из корня репозитория `python state-machines/check-tables.py`; код возврата 1 при расхождениях.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MACHINES = {  # файл состояний -> (файл автомата, сокращение «Где» в словаре)
    'task-runner-states.md': ('task-runner-automaton.md', 'раннер'),
    'task-runner-review-states.md': ('task-runner-review-automaton.md', 'проверка'),
    'task-runner-session-states.md': ('task-runner-session-automaton.md', 'сессия'),
    'task-runner-meeting-states.md': ('task-runner-meeting-automaton.md', 'совещание'),
    'state-machine-agent-step-states.md': ('state-machine-agent-step-automaton.md', 'шаг агента'),
}
# «Куда», которое не имя состояния: переменная (правило 24 спецификации) и слова без перехода
ДОПУСТИМЫЕ_КУДА = {'предыдущее', 'возврат_подготовки', 'не меняется', 'остаётся', 'остаётся в этом состоянии', 'то же', 'то же состояние'}
# строка имени состояния отличается от варианта намеренно: в раннере РАЗБОР — ещё и фаза (словарь, раздел «Коллизии»)
СТРОКА_ИНАЯ = {'ReviewParsing'}
SIDE = {'вратарь': 'gatekeeper', 'усиленный': 'enhanced'}
KIND = {'обращение': 'Appeal', 'операция': 'Operation', 'развилка': 'Fork', 'конец': 'Final'}


def read(name):
    return io.open(os.path.join(HERE, name), encoding='utf-8').read()


def glossary_states(machine):
    """Русское имя состояния -> вариант `State` по таблице идентификаторов словаря (имена заглавными)."""
    t = read('state-machine-glossary.md')
    out = {}
    for m in re.finditer(r'^\| `([А-ЯЁ][А-ЯЁ0-9_]*[а-я]?)` \| `([A-Z]\w*)` \| ([^|]+) \|', t, re.M):
        if machine in [w.strip() for w in m.group(3).split(',')]:
            out[m.group(1)] = m.group(2)
    return out


def parse_states(t):
    body = t[t.index('\n## Состояния'):]
    body = body[:body.index('\n## ', 5)] if '\n## ' in body[5:] else body
    initial = re.search(r'Начальное состояние — ([^.\n]+)', body)
    secs = {}
    for m in re.finditer(r'^### (\S+) — (\S+)\n(.*?)(?=^### |\Z)', body, re.M | re.S):
        name, kind, text = m.group(1), m.group(2), m.group(3)
        targets = []
        for tb in re.finditer(r'^\| (?:Событие|Условие) \|.*\n\|[-| ]+\|\n((?:\|.*\n?)+)', text, re.M):
            for row in tb.group(1).strip().split('\n'):
                cells = [c.strip() for c in row.strip().strip('|').split('|')]
                targets.append(cells[-1].strip('`').split(', запуск заново')[0])
        side = re.search(r'^Сторона: (\S+)', text, re.M)
        secs[name] = {'kind': kind, 'targets': targets, 'side': side.group(1) if side else None}
    return (initial.group(1).strip() if initial else None), secs


def parse_automaton(t):
    enum = re.search(r'type State enum\n(.*?)\n\n', t, re.S).group(1)
    variants = set(re.findall(r'[A-Z]\w*', re.sub(r'//.*', '', enum)))
    kinds = {}
    km = re.search(r'fn MachineData @kind\(.*?\) -> Kind => match state \{\n(.*?)\n\}', t, re.S)
    for arm in re.sub(r'\n\s*\|', ' |', km.group(1)).split('\n'):
        if '=>' not in arm:
            continue
        a, b = arm.split('=>')
        for v in re.findall(r'\w+', a):
            kinds[v] = b.strip()
    sides = {}
    sm = re.search(r'fn appeal_party\(.*?\) -> str => match appeal \{\n(.*?)\n\}', t, re.S)
    if sm:
        for line in re.sub(r'\n\s*\|', ' |', sm.group(1)).split('\n'):
            if '=>' not in line or line.strip().startswith('_'):
                continue
            a, b = line.split('=>')
            for v in re.findall(r'\w+', a):
                sides[v] = b.strip().strip('"')
    names = {}
    nm = re.search(r'fn MachineData @state_name\(.*?\) -> str => match state \{\n(.*?)\n\}', t, re.S)
    if nm:
        for arm in nm.group(1).split('\n'):
            if '=>' in arm:
                a, b = arm.split('=>')
                for v in re.findall(r'\w+', a):
                    names[v] = b.strip().strip('"')
    return variants, kinds, sides, names


def check(states_file, automaton_file, machine):
    errs = []
    gl = glossary_states(machine)
    initial, secs = parse_states(read(states_file))
    variants, kinds, sides, names = parse_automaton(read(automaton_file))
    for v, s in names.items():
        if v != s and v not in СТРОКА_ИНАЯ:
            errs.append('`state_name`: вариант %s даёт строку %r (правило: строка равна имени варианта)' % (v, s))
    eng = {}
    for ru in secs:
        if ru not in gl:
            errs.append('нет в словаре строк состояний: %s' % ru)
        else:
            eng[ru] = gl[ru]
    mapped = set(eng.values())
    for ru, en in eng.items():
        if en not in variants:
            errs.append('состояние %s (%s) есть в таблицах, нет в `State`' % (ru, en))
    for v in sorted(variants - mapped):
        errs.append('вариант `State.%s` есть в коде, нет раздела состояния' % v)
    for ru, s in secs.items():
        en = eng.get(ru)
        if en in kinds and KIND.get(s['kind']) != kinds[en]:
            errs.append('вид %s: таблицы «%s», код %s' % (ru, s['kind'], kinds[en]))
        if s['side'] in SIDE and en in sides and sides[en] != SIDE[s['side']]:
            errs.append('сторона %s: таблицы «%s», код %s' % (ru, s['side'], sides[en]))
        if s['kind'] != 'конец' and ru != 'ПАУЗА' and not s['targets']:
            errs.append('у %s нет ни одной строки «Куда»' % ru)
        for tg in s['targets']:
            if tg not in secs and tg not in ДОПУСТИМЫЕ_КУДА:
                errs.append('%s: «Куда» = %r — не состояние этой машины' % (ru, tg))
    if initial in secs:
        seen, stack = set(), [initial]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack += [tg for tg in secs[x]['targets'] if tg in secs]
        for ru in secs:
            if ru not in seen and ru != 'ПАУЗА':
                errs.append('%s недостижимо из начального %s' % (ru, initial))
    else:
        errs.append('начальное состояние %r не найдено среди разделов' % initial)
    return errs, len(secs)


JOURNAL_FILE = 'state-machine-journal.md'
JOURNAL_AUTOMATA = {  # файл автомата -> имя машины в столбце «Машина» таблицы шаблонов
    'state-machine-engine-automaton.md': 'движок',
    'state-machine-agent-step-automaton.md': 'шаг агента',
    'task-runner-automaton.md': 'раннер',
    'task-runner-review-automaton.md': 'проверка',
    'task-runner-session-automaton.md': 'сессия',
    'task-runner-meeting-automaton.md': 'совещание',
}
CODE_RE = re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$')
CALL_RE = re.compile(r'journal_event\("([^"]*)"\s*,\s*(\[\]JournalParam\.new\(\)|\[(.*?)\]\))', re.S)
LITERAL_RE = re.compile(r'(?:write_journal|machine_error)\(\s*"')
CYR_RE = re.compile('[А-Яа-яЁё]')


def journal_table():
    """Таблица шаблонов: код -> (машины, шаблон, параметры); дубли и неразборчивые строки — в ошибки."""
    t = read(JOURNAL_FILE)
    body = t[t.index('\n## 2. Таблица шаблонов'):]
    end = body.find('\n### ', 5)
    body = body[:end] if end >= 0 else body
    table, errs = {}, []
    for line in body.split('\n'):
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not line.startswith('|') or len(cells) != 4 or cells[0] == 'Машина' or set(cells[0]) <= set('-'):
            continue
        m = re.fullmatch(r'`([^`]*)`', cells[1])
        if not m:
            errs.append('таблица шаблонов: код события не в обратных кавычках: %r' % cells[1])
            continue
        code = m.group(1)
        params = [] if cells[3] == '—' else re.findall(r'`(\w+)`', cells[3])
        if code in table:
            errs.append('таблица шаблонов: код %s повторяется' % code)
        table[code] = ({x.strip() for x in cells[0].split(',')}, cells[2], params)
    return table, errs


def check_journal():
    errs = []
    table, e = journal_table()
    errs += e
    used = {}  # код -> машины, где он пишется
    for af, machine in JOURNAL_AUTOMATA.items():
        t = read(af)
        for m in LITERAL_RE.finditer(t):
            errs.append('%s:%d: в `write_journal(`/`machine_error(` строковый литерал: событие строится `journal_event(...)`' % (af, t.count('\n', 0, m.start()) + 1))
        for m in CALL_RE.finditer(t):
            code = m.group(1)
            where = '%s:%d' % (af, t.count('\n', 0, m.start()) + 1)
            if code == '':
                continue  # пустое событие — начальное значение `transition_note`
            if not CODE_RE.match(code):
                errs.append('%s: код события %r — не латинский snake_case' % (where, code))
                continue
            names = re.findall(r'param\("([^"]*)"', m.group(3) or '')
            if any(CYR_RE.search(n) for n in names):
                errs.append('%s: имя параметра с кириллицей в событии %s' % (where, code))
            if len(set(names)) != len(names):
                errs.append('%s: имена параметров события %s повторяются' % (where, code))
            used.setdefault(code, set()).add(machine)
            if code not in table:
                errs.append('%s: кода %s нет в таблице шаблонов' % (where, code))
                continue
            params = table[code][2]
            if set(names) != set(params):
                errs.append('%s: параметры вызова %s события %s не равны столбцу «Параметры» %s' % (where, sorted(names), code, sorted(params)))
    for code, (machines, tpl, params) in table.items():
        if code not in used:
            errs.append('код %s есть в таблице шаблонов, в автоматах не пишется' % code)
            continue
        if machines != used[code]:
            errs.append('код %s: машины таблицы %s, в автоматах %s' % (code, sorted(machines), sorted(used[code])))
        placeholders = re.findall(r'\{(\w+)\}', tpl)
        if set(placeholders) != set(params):
            errs.append('код %s: подстановки шаблона %s не равны столбцу «Параметры» %s' % (code, sorted(set(placeholders)), sorted(params)))
        if not CYR_RE.search(tpl):
            errs.append('код %s: в шаблоне нет русского текста' % code)
    return errs, len(table)


def main():
    bad = 0
    for sf, (af, machine) in MACHINES.items():
        errs, n = check(sf, af, machine)
        print('%s: %d состояний, расхождений %d' % (sf, n, len(errs)))
        for e in errs:
            print('  - ' + e)
        bad += len(errs)
    errs, n = check_journal()
    print('%s: %d кодов событий, расхождений %d' % (JOURNAL_FILE, n, len(errs)))
    for e in errs:
        print('  - ' + e)
    bad += len(errs)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
