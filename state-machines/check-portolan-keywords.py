#!/usr/bin/env python3
"""Проверка таблицы ключевых слов Портолана (`portolan-keywords.tsv`) и сверка с ней образцов машины.

Зачем: таблица слов — единый нормативный источник ключевых слов обоих языков Портолана (спецификация, раздел 1а);
образцы `state-machine-agent-step.portolan.md` (русский) и `state-machine-agent-step.en.portolan.md` (английский) записаны на разных
языках, и расхождение слов образца с таблицей молчит до первой реализации разбора.
Что проверяет:
  1. таблица: первая строка — заголовок `kind<TAB>ru<TAB>en`; в каждой строке три колонки без пустых ячеек;
     `kind` — из закрытого перечня (header, section, column, kind_state, key, kind_party, event, destination, decl, type, expr,
     action, operator, readable, catalog, enum_value), каждый вид представлен; в пределах вида слова `ru` не повторяются и слова `en` не повторяются;
  2. русский образец: структурные слова (имена шапки и ключи шапки, заголовки разделов `##`, строки-ключи `- Ключ:` и `Начальное состояние:`,
     заголовки столбцов таблиц, виды состояний в заголовках `###` (скобки с именем JSON необязательны), значение `нет`/`none`
     строки `Вход`) есть в таблице в колонке `ru` своего вида;
     английское структурное слово (есть в колонке `en`, нет в `ru`) в русском образце — ошибка;
  3. английский образец: те же структурные слова по колонке `en` (`Initial state:` вместо `Начальное состояние:`);
     русское структурное слово (есть в колонке `ru`, нет в `en`) в нём — ошибка; строка шапки `- language: en` обязательна
     (в русском образце допустима `- language: ru` или её отсутствие, иной язык — ошибка);
  4. самопроверка мутацией (`--selftest`): порча структурного слова в копии каждого образца даёт ошибку, исправный образец — нет.
Пропускает: блоки кода, справочный раздел `## Раскрытие фрагмента …` (`## Fragment expansion …`), прозу, имена, значения и содержимое
ячеек таблиц (кроме заголовков).
Чего не проверяет: слова внутри выражений и действий, соответствие английских слов JSON-схеме.
Запуск: из корня репозитория `python state-machines/check-portolan-keywords.py` (`--selftest` — с самопроверкой); код возврата 1 при расхождениях.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = 'portolan-keywords.tsv'
SAMPLES = [('state-machine-agent-step.portolan.md', 'ru'), ('state-machine-agent-step.en.portolan.md', 'en')]
KINDS = ['header', 'section', 'column', 'kind_state', 'key', 'kind_party', 'event', 'destination', 'decl', 'type', 'expr',
         'action', 'operator', 'readable', 'catalog', 'enum_value']


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


def structural(text, lang='ru'):
    """Структурные слова образца: список (номер строки, вид, слово)."""
    expansion = 'Раскрытие фрагмента' if lang == 'ru' else 'Fragment expansion'
    initial = r'^(Начальн[^:]*):' if lang == 'ru' else r'^(Initial[^:]*):'
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
            skip = title.startswith(expansion)
            word = expansion if skip else title
            out.append((n, 'section', word))
            continue
        if skip:
            continue
        if in_header:
            m = re.match(r'^- ([a-z_]+):', line)
            if m:
                out.append((n, 'header', m.group(1)))
            continue
        m = re.match(r'^### \S+ — (\S+)(?: \(|\s*$|\s+//)', line)  # скобки с именем JSON необязательны (спецификация 4.1)
        if m:
            out.append((n, 'kind_state', m.group(1)))
            continue
        m = re.match(r'^- ([^:`\n]+):', line)
        if m:
            out.append((n, 'key', m.group(1)))
            v = re.match(r'^- (?:Вход|Input):\s*(нет|none)\s*$', line)
            if v:  # значение «нет входа» — слово вида enum_value
                out.append((n, 'enum_value', v.group(1)))
            continue
        m = re.match(initial, line)
        if m:
            out.append((n, 'key', m.group(1)))
            continue
        if line.startswith('|') and n < len(lines) and re.match(r'^\|[-:| ]+\|\s*$', lines[n]):
            for c in line.strip().strip('|').split('|'):
                out.append((n, 'column', c.strip()))
    return out


def check_sample(text, words, name, lang):
    errs = []
    own = {k: v[0 if lang == 'ru' else 1] for k, v in words.items()}
    other = {k: v[1 if lang == 'ru' else 0] for k, v in words.items()}
    declared = re.search(r'^- language: (\w+)\s*$', text, re.M)
    if lang == 'en' and not (declared and declared.group(1) == 'en'):
        errs.append('%s:1: в английском образце нет строки шапки `- language: en`' % name)
    if lang == 'ru' and declared and declared.group(1) != 'ru':
        errs.append('%s:1: в русском образце объявлен `- language: %s`' % (name, declared.group(1)))
    for n, kind, word in structural(text, lang):
        if word in own[kind]:
            continue
        if word in other[kind]:
            errs.append('%s:%d: %s слово `%s` (вид `%s`) в %s образце' % (
                name, n, 'английское' if lang == 'ru' else 'русское', word, kind, 'русском' if lang == 'ru' else 'английском'))
        else:
            errs.append('%s:%d: слова `%s` (вид `%s`) нет в таблице, колонка %s' % (name, n, word, kind, lang))
    return errs


MUTATIONS = {
    'ru': [  # (описание, что заменить, на что)
        ('заголовок раздела', '\n## Состояния\n', '\n## Статусы\n'),
        ('английский раздел', '\n## Данные\n', '\n## Data\n'),
        ('строка-ключ', '- Срок тишины:', '- Срок тишыны:'),
        ('столбец таблицы состояний', '| № | Событие | Условие | Действия | Куда |', '| № | Событие | Условия | Действия | Куда |'),
        ('вид состояния', '### СТАРТ — операция (Start)', '### СТАРТ — операция2 (Start)'),
        ('английское значение входа', '- Вход: нет', '- Вход: none'),
        ('начальное состояние', 'Начальное состояние: СТАРТ', 'Начальное состоянье: СТАРТ'),
        ('ключ шапки', '- machine_version:', '- machine_ver:'),
    ],
    'en': [
        ('заголовок раздела', '\n## States\n', '\n## Statuses\n'),
        ('русский раздел', '\n## Data\n', '\n## Данные\n'),
        ('строка-ключ', '- Idle term:', '- Idle terms:'),
        ('русская строка-ключ', '- Party: agent', '- Сторона: agent'),
        ('столбец таблицы состояний', '| № | Event | Condition | Actions | To |', '| № | Event | Conditions | Actions | To |'),
        ('вид состояния', '### Start — operation', '### Start — operation2'),
        ('русское значение входа', '- Input: none', '- Input: нет'),
        ('начальное состояние', 'Initial state: Start', 'Initial stat: Start'),
        ('ключ шапки', '- machine_version:', '- machine_ver:'),
        ('нет строки language', '- language: en\n', ''),
    ],
}


def selftest(sample, words, name, lang):
    errs = check_sample(sample, words, name, lang)
    if errs:
        return ['самопроверка (%s): исправный образец не прошёл: %s' % (lang, errs[0])]
    bad = []
    for what, a, b in MUTATIONS[lang]:
        if a not in sample:
            bad.append('самопроверка (%s): образец не содержит заменяемого (%s)' % (lang, what))
            continue
        if not check_sample(sample.replace(a, b, 1), words, name, lang):
            bad.append('самопроверка (%s): порча не замечена (%s)' % (lang, what))
    return bad


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    errs, words = check_table(read(TABLE))
    for name, lang in SAMPLES:
        sample = read(name)
        errs += check_sample(sample, words, name, lang)
        if '--selftest' in sys.argv:
            errs += selftest(sample, words, name, lang)
    for e in errs:
        print(e)
    rows = sum(len(w[0]) for w in words.values())
    print('таблица слов: %d строк, %d видов; образцов: %d; расхождений: %d' % (rows, len(KINDS), len(SAMPLES), len(errs)))
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
