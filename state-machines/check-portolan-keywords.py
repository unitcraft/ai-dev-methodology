#!/usr/bin/env python3
"""Проверка таблицы ключевых слов Портолана (`portolan-keywords.tsv`) и сверка с ней образцов машины.

Зачем: таблица слов — единый нормативный источник ключевых слов обоих языков Портолана (спецификация, раздел 1а);
образцы `state-machine-agent-step.portolan.md` (русский), `state-machine-agent-step.en.portolan.md` (английский) и запись
«Совещания» `task-runner-meeting.portolan.md` (русская) записаны на разных языках, и расхождение слов образца с таблицей
молчит до первой реализации разбора.
Что проверяет:
  1. таблица: первая строка — заголовок `kind<TAB>ru<TAB>en`; в каждой строке три колонки без пустых ячеек;
     `kind` — из закрытого перечня (header, section, column, kind_state, key, kind_party, event, destination, decl, type, expr,
     action, operator, readable, catalog, enum_value), каждый вид представлен; в пределах вида слова `ru` не повторяются и слова `en` не повторяются;
  2. русский образец: структурные слова (имена шапки и ключи шапки, заголовки разделов `##`, строки-ключи `- Ключ:` и `Начальное состояние:`,
     заголовки столбцов таблиц, виды состояний в заголовках `###` (скобки с JSON-именем необязательны)) есть в таблице в колонке
     `ru` своего вида;
     английское структурное слово (есть в колонке `en`, нет в `ru`) в русском образце — ошибка;
  3. английский образец: те же структурные слова по колонке `en` (`Initial state:` вместо `Начальное состояние:`);
     русское структурное слово (есть в колонке `ru`, нет в `en`) в нём — ошибка; строка шапки `- language: en` обязательна
     (в русском образце допустима `- language: ru` или её отсутствие, иной язык — ошибка);
  4. знаки операторов (спецификация, 1а, Я-42): в блоках кода, строках таблиц и строках-ключах нет знаков `≥`, `≤`, `≠`, `→`, `∈`
     (только ASCII: `>=`, `<=`, `!=`, `->`, `in`); в прозе знак `→` допустим;
  4а. убранное событие (Я-38): в строках таблиц нет события `слово(…)` (`word(…)`) — только `сигнал(…)`;
  5. JSON-имена (спецификация, 1а, «JSON-имя», Я-46): нелатинское имя, которое выходит из машины, несёт латинское JSON-имя в скобках
     при объявлении — заголовок состояния `###`, первый столбец таблиц `## Вход`, `## Данные`, `## Примитивы` (кроме пути поля `имя[*].поле`
     и данных контракта из вида `readable` таблицы слов), объявления блока кода `## Типы` (тип, элемент перечисления, вариант, поле)
     сигналы сторон в столбце `сигналы` «Сторон» (сигнал и его поля) и имя настройки вратаря в виде стороны
     `human или agent по настройке <имя>`; в скобках — латинское имя;
  6. самопроверка мутацией (`--selftest`): порча структурного слова, знака оператора или JSON-имени в копии образцов «Шага агента»
     даёт ошибку, исправный образец — нет.
Пропускает: прозу, имена и значения (кроме проверки 5) и содержимое ячеек таблиц (кроме заголовков и проверок 4, 5).
Чего не проверяет: слова внутри выражений и действий, соответствие английских слов JSON-схеме.
Запуск: из корня репозитория `python state-machines/check-portolan-keywords.py` (`--selftest` — с самопроверкой); код возврата 1 при расхождениях.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = 'portolan-keywords.tsv'
SAMPLES = [('state-machine-agent-step.portolan.md', 'ru'), ('state-machine-agent-step.en.portolan.md', 'en'),
           ('task-runner-meeting.portolan.md', 'ru')]
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
    initial = r'^(Начальн[^:]*):' if lang == 'ru' else r'^(Initial[^:]*):'
    out = []
    in_code = False
    in_header = True
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
            out.append((n, 'section', m.group(1)))
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
            continue
        m = re.match(initial, line)
        if m:
            out.append((n, 'key', m.group(1)))
            continue
        if line.startswith('|') and n < len(lines) and re.match(r'^\|[-:| ]+\|\s*$', lines[n]):
            for c in line.strip().strip('|').split('|'):
                out.append((n, 'column', c.strip()))
    return out


UNICODE_OPS = '≥≤≠→∈'
LATIN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def check_operators(text, name):
    """Знаки операторов только ASCII в блоках кода, строках таблиц и строках-ключах (Я-42)."""
    errs, in_code = [], False
    for n, line in enumerate(text.split('\n'), 1):
        if line.startswith('```'):
            in_code = not in_code
            continue
        if (in_code or line.startswith('|') or line.lstrip().startswith('- ')) and any(ch in line for ch in UNICODE_OPS):
            errs.append('%s:%d: знак оператора не ASCII (%s)' % (name, n, ''.join(ch for ch in UNICODE_OPS if ch in line)))
    return errs


def check_removed(text, name):
    """Убранное событие `слово(…)`/`word(…)` (Я-38) в строках таблиц."""
    return ['%s:%d: событие `слово(…)` убрано, пишется `сигнал(…)` (Я-38)' % (name, n)
            for n, line in enumerate(text.split('\n'), 1) if line.startswith('|') and re.search(r'\| (?:слово|word)\(', line)]


def split_top(s, sep=','):
    """Деление по разделителю вне скобок ()[]{}."""
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '([{':
            depth += 1
        elif ch in ')]}':
            depth -= 1
        if ch == sep and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]


def json_name(decl):
    """Разбор объявления `имя (JsonИмя) остальное`: (имя, JSON-имя или None, остальное); имя может быть из нескольких слов."""
    m = re.match(r'^([^({\["]+?) \(([^()\s]+)\)(.*)$', decl)
    if m:
        return m.group(1).strip(), m.group(2), m.group(3).strip()
    m = re.match(r'^([^({\["]+?)(?=\s*[({\["]|$)(.*)$', decl)
    head = m.group(1).strip()
    if ' ' in head and not decl.startswith(head + '('):  # `имя тип`: имя — первое слово
        head = head.split()[0]
    return head, None, decl[len(head):].strip()


def need(name, js, where, n, fname, errs, skip=()):
    if js is not None and not LATIN.match(js):
        errs.append('%s:%d: JSON-имя `%s` у %s `%s` не латинское' % (fname, n, js, where, name))
    elif js is None and name not in skip and not LATIN.match(name):
        errs.append('%s:%d: у %s `%s` нет JSON-имени в скобках' % (fname, n, where, name))


def fields(body, n, fname, errs):
    for f in split_top(body):
        fn, fj, _ = json_name(f)
        need(fn, fj, 'поля', n, fname, errs)


def check_json_names(text, words, name, lang):
    """JSON-имена нелатинских имён, которые выходят из машины (Я-46)."""
    errs = []
    readable = words['readable'][0 if lang == 'ru' else 1]
    names = ('Вход', 'Данные', 'Примитивы', 'Типы', 'Стороны') if lang == 'ru' else ('Input', 'Data', 'Primitives', 'Types', 'Parties')
    sec_input, sec_data, sec_prim, sec_types, sec_parties = names
    signals_col = 'сигналы' if lang == 'ru' else 'signals'
    sec, in_code, header, in_variant = None, False, None, False
    decls = []  # (номер строки, объявление, член варианта?) блока типов
    for n, line in enumerate(text.split('\n'), 1):
        if line.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            if sec == sec_types and line.strip():
                st = line.strip()
                if in_variant:
                    if st == '}':
                        in_variant = False
                    else:
                        decls.append((n, st, True))
                elif line[0] in ' \t' and decls:
                    decls[-1] = (decls[-1][0], decls[-1][1] + ' ' + st, False)
                else:
                    decls.append((n, st, False))
                    in_variant = st.endswith('{') and re.match(r'^(?:вариант|variant) ', st) is not None
            continue
        m = re.match(r'^## (\S+)', line)
        if m:
            sec, header = m.group(1), None
            continue
        m = re.match(r'^### (.+?) — \S+(?: \((\S+)\))?(?:\s|$)', line)
        if m:
            need(m.group(1), m.group(2), 'состояния', n, name, errs)
            continue
        if not line.startswith('|'):
            header = None
            continue
        if re.match(r'^\|[-:| ]+\|\s*$', line):
            continue
        cells = [c.strip() for c in re.split(r'(?<!\\)\|', line.strip())[1:-1]]
        if header is None:
            header = cells
            continue
        if sec in (sec_input, sec_data, sec_prim) and header[0] in ('имя', 'name'):
            nm, js, _ = json_name(cells[0])
            if '[*]' not in cells[0]:
                need(nm, js, {sec_input: 'поля входа', sec_data: 'данного', sec_prim: 'примитива'}[sec], n, name, errs, readable)
        kind_col = 'вид' if lang == 'ru' else 'kind'
        if sec == sec_parties and kind_col in header:
            m = re.search(r'(?:по настройке|by setting) (\S+?)(?: \(([^()\s]+)\))?\(', cells[header.index(kind_col)])
            if m:
                need(m.group(1), m.group(2), 'настройки вратаря', n, name, errs)
        if sec == sec_parties and signals_col in header and cells[header.index(signals_col)] != '—':
            for sig in split_top(cells[header.index(signals_col)]):
                nm, js, rest = json_name(sig)
                need(nm, js, 'сигнала', n, name, errs)
                if rest.startswith('(') and rest.endswith(')'):
                    fields(rest[1:-1], n, name, errs)
    for n, d, member in decls:
        if member:
            nm, js, rest = json_name(d)
            need(nm, js, 'варианта', n, name, errs)
            if rest.startswith('{') and rest.endswith('}'):
                fields(rest[1:-1], n, name, errs)
            continue
        m = re.match(r'^(?:перечисление|enum) (.+?) = (.*)$', d)
        if m:
            nm, js, _ = json_name(m.group(1))
            need(nm, js, 'типа', n, name, errs)
            for el in split_top(re.sub(r'"[^"]*"', '', m.group(2)), '|'):
                en_, ej, _ = json_name(el)
                need(en_, ej, 'элемента перечисления', n, name, errs)
            continue
        m = re.match(r'^(?:тип|type|вариант|variant) (.+?) \{(.*)$', d)
        if m:
            nm, js, _ = json_name(m.group(1))
            need(nm, js, 'типа', n, name, errs)
            body = m.group(2).strip()
            if body.endswith('}'):
                fields(body[:-1], n, name, errs)
    return errs


def check_sample(text, words, name, lang):
    errs = check_operators(text, name) + check_removed(text, name) + check_json_names(text, words, name, lang)
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
        ('английская строка-ключ чтений', '- Читает: число_повторов, ход', '- Reads: число_повторов, ход'),
        ('знак оператора не ASCII', '| 3 | число_повторов >= ЧИСЛО_ПОВТОРОВ |', '| 3 | число_повторов ≥ ЧИСЛО_ПОВТОРОВ |'),
        ('нет JSON-имени у данного', '| число_повторов (retry_count) |', '| число_повторов |'),
        ('нет JSON-имени у поля типа', 'вход (input) ?число', 'вход ?число'),
        ('нет JSON-имени у элемента перечисления', 'Пуста (Empty)', 'Пуста'),
        ('нет JSON-имени у варианта', 'ВременнаяОшибка (TransientError)', 'ВременнаяОшибка'),
        ('нет JSON-имени у сигнала', 'разрешить (allow), отказать (deny)', 'разрешить, отказать (deny)'),
        ('нет JSON-имени у поля сигнала', 'автор (author) текст', 'автор текст'),
        ('нелатинское JSON-имя', '(ReplyValidation)', '(ПроверкаОтвета)'),
        ('убранное событие слово', '| 1 | сигнал(разрешить) |', '| 1 | слово(разрешить) |'),
        ('нет JSON-имени у настройки вратаря', 'исполнитель_повышенного_внимания (elevated_attention_executor)(', 'исполнитель_повышенного_внимания('),
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
        ('русская строка-ключ чтений', '- Reads: retry_count, turn', '- Читает: retry_count, turn'),
        ('знак оператора не ASCII', 'fold(range(1, n), RETRY_PAUSE, (m, _) -> m * 2)', 'fold(range(1, n), RETRY_PAUSE, (m, _) → m * 2)'),
        ('убранное событие word', '| 1 | signal(allow) |', '| 1 | word(allow) |'),
        ('начальное состояние', 'Initial state: Start', 'Initial stat: Start'),
        ('ключ шапки', '- machine_version:', '- machine_ver:'),
        ('нет строки language', '- language: en\n', ''),
    ],
}


MUTATED = {'state-machine-agent-step.portolan.md', 'state-machine-agent-step.en.portolan.md'}


def selftest(sample, words, name, lang):
    errs = check_sample(sample, words, name, lang)
    if errs:
        return ['самопроверка (%s): исправный образец не прошёл: %s' % (lang, errs[0])]
    if name not in MUTATED:
        return []
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
