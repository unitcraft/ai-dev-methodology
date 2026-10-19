#!/usr/bin/env python3
"""Проверка таблицы ключевых слов Портолана (`portolan-keywords.tsv`) и сверка с ней образца машины.

Зачем: таблица слов — единый нормативный источник ключевых слов обоих языков Портолана (спецификация, раздел 1а);
образец `state-machine-agent-step.portolan.md` записан по-русски, и расхождение слов образца с таблицей молчит до первой реализации разбора.
Что проверяет:
  1. таблица: первая строка — заголовок `kind<TAB>ru<TAB>en`; в каждой строке три колонки без пустых ячеек;
     `kind` — из закрытого перечня (header, section, column, kind_state, key, kind_party, event, destination, decl, type, expr,
     action, readable, catalog, enum_value), каждый вид представлен; в пределах вида слова `ru` не повторяются и слова `en` не повторяются;
  2. образец: структурные слова (имена шапки и ключи шапки, заголовки разделов `##`, строки-ключи `- Ключ:` и `Начальное состояние:`,
     заголовки столбцов таблиц, виды состояний в заголовках `###`) есть в таблице в колонке `ru` своего вида;
     английское структурное слово (есть в колонке `en`, нет в `ru`) в русском образце — ошибка;
  3. самопроверка мутацией (`--selftest`): порча структурного слова в копии образца даёт ошибку, исправный образец — нет.
Пропускает: блоки кода, справочный раздел `## Раскрытие фрагмента …`, прозу, имена, значения и содержимое ячеек таблиц (кроме заголовков).
Чего не проверяет: слова внутри выражений и действий, соответствие английских слов JSON-схеме.
Запуск: из корня репозитория `python state-machines/check-portolan-keywords.py` (`--selftest` — с самопроверкой); код возврата 1 при расхождениях.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = 'portolan-keywords.tsv'
SAMPLE = 'state-machine-agent-step.portolan.md'
KINDS = ['header', 'section', 'column', 'kind_state', 'key', 'kind_party', 'event', 'destination', 'decl', 'type', 'expr',
         'action', 'readable', 'catalog', 'enum_value']


def read(name):
    return io.open(os.path.join(HERE, name), encoding='utf-8', newline='').read().replace('\r\n', '\n')


def check_table(text):
    """Возвращает (ошибки, словарь kind -> (ru-множество, en-множество))."""
    errs = []
    lines = text.split('\n')
    while lines and lines[-1] == '':
        lines.pop()
    if not lines or lines[0] != 'kind\tru\ten':
        errs.append('%s:1: первая строка должна быть заголовком `kind<TAB>ru<TAB>en`' % TABLE)
    words = {k: (set(), set()) for k in KINDS}
    for n, line in enumerate(lines[1:], 2):
        cells = line.split('\t')
        if len(cells) != 3:
            errs.append('%s:%d: колонок %d, нужно 3' % (TABLE, n, len(cells)))
            continue
        kind, ru, en = cells
        if '' in (kind.strip(), ru.strip(), en.strip()):
            errs.append('%s:%d: пустая ячейка' % (TABLE, n))
            continue
        if kind not in words:
            errs.append('%s:%d: вид `%s` вне закрытого перечня' % (TABLE, n, kind))
            continue
        for col, val, seen in (('ru', ru, words[kind][0]), ('en', en, words[kind][1])):
            if val in seen:
                errs.append('%s:%d: в виде `%s` слово %s `%s` повторено' % (TABLE, n, kind, col, val))
            seen.add(val)
    for k in KINDS:
        if not words[k][0]:
            errs.append('%s: вид `%s` не представлен' % (TABLE, k))
    return errs, words


def structural(text):
    """Структурные слова образца: список (номер строки, вид, слово)."""
    out = []
    in_code = False
    in_header = True
    skip = False  # справочный раздел «Раскрытие фрагмента»
    lines = text.split('\n')
    for n, line in enumerate(lines, 1):
        if line.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r'^# (\S+):', line)
        if m and n == 1:
            out.append((n, 'header', m.group(1)))
            continue
        m = re.match(r'^## (.+?)\s*$', line)
        if m:
            in_header = False
            title = m.group(1)
            skip = title.startswith('Раскрытие фрагмента')
            word = 'Раскрытие фрагмента' if skip else title
            out.append((n, 'section', word))
            continue
        if skip:
            continue
        if in_header:
            m = re.match(r'^- ([a-z_]+):', line)
            if m:
                out.append((n, 'header', m.group(1)))
            continue
        m = re.match(r'^### \S+ — (\S+) \(', line)
        if m:
            out.append((n, 'kind_state', m.group(1)))
            continue
        m = re.match(r'^- ([^:`\n]+):', line)
        if m:
            out.append((n, 'key', m.group(1)))
            continue
        m = re.match(r'^(Начальн[^:]*):', line)
        if m:
            out.append((n, 'key', m.group(1)))
            continue
        if line.startswith('|') and n < len(lines) and re.match(r'^\|[-:| ]+\|\s*$', lines[n]):
            for c in line.strip().strip('|').split('|'):
                out.append((n, 'column', c.strip()))
    return out


def check_sample(text, words):
    errs = []
    for n, kind, word in structural(text):
        ru, en = words[kind]
        if word in ru:
            continue
        if word in en:
            errs.append('%s:%d: английское слово `%s` (вид `%s`) в русском образце' % (SAMPLE, n, word, kind))
        else:
            errs.append('%s:%d: слова `%s` (вид `%s`) нет в таблице, колонка ru' % (SAMPLE, n, word, kind))
    return errs


def selftest(sample, words):
    errs = check_sample(sample, words)
    if errs:
        return ['самопроверка: исправный образец не прошёл: ' + errs[0]]
    mutations = [  # (описание, что заменить, на что)
        ('заголовок раздела', '\n## Состояния\n', '\n## Статусы\n'),
        ('английский раздел', '\n## Данные\n', '\n## Data\n'),
        ('строка-ключ', '- Срок тишины:', '- Срок тишыны:', ),
        ('столбец таблицы состояний', '| № | Событие | Условие | Действия | Куда |', '| № | Событие | Условия | Действия | Куда |'),
        ('вид состояния', '### СТАРТ — операция (Start)', '### СТАРТ — операция2 (Start)'),
        ('начальное состояние', 'Начальное состояние: СТАРТ', 'Начальное состоянье: СТАРТ'),
        ('ключ шапки', '- machine_version:', '- machine_ver:'),
    ]
    bad = []
    for what, a, b in mutations:
        if a not in sample:
            bad.append('самопроверка: образец не содержит заменяемого (%s)' % what)
            continue
        if not check_sample(sample.replace(a, b, 1), words):
            bad.append('самопроверка: порча не замечена (%s)' % what)
    return bad


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    errs, words = check_table(read(TABLE))
    sample = read(SAMPLE)
    errs += check_sample(sample, words)
    if '--selftest' in sys.argv:
        errs += selftest(sample, words)
    for e in errs:
        print(e)
    rows = sum(len(w[0]) for w in words.values())
    print('таблица слов: %d строк, %d видов; расхождений: %d' % (rows, len(KINDS), len(errs)))
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
