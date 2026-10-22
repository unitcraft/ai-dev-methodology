#!/usr/bin/env python3
"""Проверка таблицы ключевых слов Алулы (`alula-keywords.tsv`) и сверка с ней образцов машины.

Зачем: таблица слов — единый нормативный источник ключевых слов обоих языков Алулы (спецификация, раздел 1а);
образцы `state-machine-agent-step.alula.md` (русский), `state-machine-agent-step.en.alula.md` (английский) и запись
«Совещания» `task-runner-meeting.alula.md` (русская) записаны на разных языках, и расхождение слов образца с таблицей
молчит до первой реализации разбора.
Что проверяет:
  1. таблица: первая строка — заголовок `kind<TAB>ru<TAB>en`; в каждой строке три колонки без пустых ячеек;
     `kind` — из закрытого перечня (header, section, column, kind_state, key, kind_party, kind_param, event, destination, decl, type,
     expr, action, operator, readable, catalog, enum_value), каждый вид представлен; в пределах вида слова `ru` не повторяются и слова `en`
     не повторяются (в разных видах слово может повторяться); вид `kind_param` (виды параметров фрагмента, раздел 9, AL-63) — ровно
     `сигнал`, `текст`, `[]машина`, `поведение`, `примечание` с английскими словами ровно `signal`, `text`, `[]machine`, `behavior`, `note`
     (по парам), и из них в виде `type` стоит только `текст` (виды параметров — не типы данных);
  2. русский образец: структурные слова (имена шапки и ключи шапки, заголовки разделов `##`, строки-ключи `- Ключ:` и `Начальное состояние:`,
     заголовки столбцов таблиц, виды состояний в заголовках `###`) есть в таблице в колонке `ru` своего вида;
     английское структурное слово (есть в колонке `en`, нет в `ru`) в русском образце — ошибка;
  3. английский образец: те же структурные слова по колонке `en` (`Initial state:` вместо `Начальное состояние:`);
     русское структурное слово (есть в колонке `ru`, нет в `en`) в нём — ошибка; строка шапки `- language: en` обязательна
     (в русском образце допустима `- language: ru` или её отсутствие, иной язык — ошибка);
  4. знаки операторов (спецификация, 1а, AL-42): в блоках кода, строках таблиц и строках-ключах нет знаков `≥`, `≤`, `≠`, `→`, `⇒`, `∈`
     (только ASCII: `>=`, `<=`, `!=`, `->`, `=>`, `in`); в прозе знак `→` допустим; прежняя запись (до 2.18, AL-67…AL-69) — ошибка:
     в заголовке определения `определение имя(…) -> Тип` (`define`) первый знак `=` после типа результата — не `=>` (тело
     пишется после `=>`; `==`, `<=`, `>=`, `!=` знаком `=` не считаются); любой знак `->`, кроме типа результата после списка
     параметров определения и в `разбор: примитив[("роль")] -> Тип` (`parse:`), — ветка `выбор` или лямбда, они пишутся через `=>`;
     а также тип `да/нет` (с 2.18 — `булево`, AL-66);
  4а. убранное событие (AL-38): в строках таблиц нет события `слово(…)` (`word(…)`) — только `сигнал(…)`;
  5. JSON-имена (спецификация, 1а, «JSON-имя», AL-53, AL-58…AL-60) у объявленных имён, которые выходят из машины, — заголовок
     состояния `###`, первый столбец таблиц `## Вход`, `## Данные`, `## Примитивы` (кроме пути поля `имя[*].поле` и данных
     контракта из вида `readable` таблицы слов), объявления блока кода `## Типы` (тип, элемент перечисления, вариант, поле),
     сигналы сторон в столбце `сигналы` «Сторон» (сигнал и его поля) и имя настройки вратаря в виде стороны
     `human или agent по настройке <имя>`: скобок после имени нет (убраны, AL-60); JSON-имя — строка раздела `## Имена`
     (`| имя | JSON-имя |`; уточнённое имя `Тип.Вариант.поле`, `сторона.сигнал` сильнее простого), иначе автоматическое
     (латинское имя — оно само; иначе запись словаря методики `state-machine-glossary.md` для всего имени; иначе
     транслитерация с правилом регистра; функции `load_glossary`, `auto_name`); итоговое JSON-имя латинское; строка `## Имена`,
     которая ничего не меняет, — ошибка «лишняя строка»; строка для имени, которого среди объявлений файла нет, — ошибка;
     имя повторено в таблице; JSON-имя строки не латинское; JSON-имена одного пространства (состояния, вместе с состоянием
     подключённого фрагмента «Пауза»; данные; поля входа; типы; поля одной записи или варианта; варианты одного типа;
     элементы одного перечисления; сигналы одной стороны; поля одного сигнала; примитивы; имена настроек) различны; JSON-имена
     данных контракта и фрагмента «Пауза» (`previous`, `call_request_id`, `open_requests`, `stop_reason`, `to_send`, `human_words`)
     заняты в пространстве данных; константы и параметры (пространство 10) скрипт не сверяет — это проверка переводчика продукта;
     разные пространства друг другу не мешают (AL-58); слово имени (часть между `_` и пробелами) — только кириллица или
     только латиница (AL-59);
  5а. словарь (AL-62): хеш нормативной части словаря (функция `dictionary_hash`) равен закреплённому форматом (`DICT_HASH`),
     и спецификация (русская и английская) называет тот же хеш;
  6. самопроверка мутацией (`--selftest`): порча структурного слова, знака оператора (в том числе прежняя запись тела
     определения, ветки `выбор` и лямбды), JSON-имени (лишняя строка `## Имена`,
     строка для необъявленного, внутреннего или читаемого имени, повтор имени в таблице, нелатинское JSON-имя, скобки
     в объявлении, имя без латинского JSON-имени, два состояния, два данных, два поля одной записи с одним JSON-именем,
     состояние с JSON-именем состояния фрагмента, смешанное слово) в копии образцов «Шага агента» и изменённая запись
     словаря дают ошибку, исправный образец — нет; одно JSON-имя в разных пространствах и смешение письменностей через `_`
     ошибки не дают; в копии таблицы слов вид параметра фрагмента, перенесённый обратно в `type`, испорченное английское слово
     вида `kind_param` (`сигнал sgnl`) и таблица без вида `kind_param`
     дают ошибку, исправная таблица — нет.
Пропускает: прозу, имена и значения (кроме проверки 5) и содержимое ячеек таблиц (кроме заголовков и проверок 4, 5).
Чего не проверяет: слова внутри выражений и действий, соответствие английских слов JSON-схеме, правило стиля «имя поля
не совпадает с названием его типа» (спецификация, раздел 2, AL-54; предупреждение — позже), выражение `—` таблицы
«Запрос» (AL-56) и исчерпание развилок по типу (AL-57) — это проверки переводчика продукта.
Функции `load_glossary`, `auto_name`, `declarations`, `json_names` берёт и `check-alula-samples.py` (сверка JSON-имён двух образцов).
Запуск: из корня репозитория `python state-machines/check-alula-keywords.py` (`--selftest` — с самопроверкой); код возврата 1 при расхождениях.
"""
import hashlib, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = 'alula-keywords.tsv'
GLOSSARY = 'state-machine-glossary.md'
SPECS = [('state-machine-alula-spec.md', 'хеш словаря'), ('state-machine-alula-spec.en.md', 'glossary hash')]
DICT_HASH = '60383c370415'  # хеш нормативной части словаря, закреплённый форматом 2.16 и тем же в 2.17 и 2.18 (спецификация, 1а, AL-62)
GLOSSARY_VERSION = 11  # версия словаря (для людей), при которой закреплён хеш; проверка сверяет хеш, а не номер
NORMATIVE_TABLES = ['2.%d' % i for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 16)]  # разделы-таблицы словаря; 2.10 — записи
SAMPLES = [('state-machine-agent-step.alula.md', 'ru'), ('state-machine-agent-step.en.alula.md', 'en'),
           ('task-runner-meeting.alula.md', 'ru')]
KINDS = ['header', 'section', 'column', 'kind_state', 'key', 'kind_party', 'kind_param', 'event', 'destination', 'decl', 'type',
         'expr', 'action', 'operator', 'readable', 'catalog', 'enum_value']
# виды параметров фрагмента (раздел 9, AL-63): закрытый перечень вида `kind_param`; из них тип данных — только `текст`
KIND_PARAM = ('сигнал', 'текст', '[]машина', 'поведение', 'примечание')
KIND_PARAM_ALSO_TYPE = ('текст',)
# пары «русское слово -> английское слово» вида `kind_param`: английская колонка проверяется так же строго, как русская
KIND_PARAM_PAIRS = (('сигнал', 'signal'), ('текст', 'text'), ('[]машина', '[]machine'), ('поведение', 'behavior'),
                    ('примечание', 'note'))
FRAGMENT_STATE = 'Pause'  # JSON-имя состояния, которое приносит подключённый фрагмент «Пауза» (раздел 9)
# данные контракта и фрагмента «Пауза» — читаемые имена таблицы слов: их JSON-имена (слово `en`) занимают пространство данных (AL-58)
CONTRACT_DATA = ('предыдущее', 'запрос_вызова', 'открытые_запросы', 'остановка', 'к_отправке', 'слова_человека')


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
    pairs = []
    kp_pairs = set()
    for n, line in enumerate(lines[1:], 2):
        cells = line.split('\t')
        if len(cells) != 3:
            errs.append('%s:%d: колонок %d, нужно 3' % (TABLE, n, len(cells)))
            continue
        kind, ru, en = cells
        if kind == 'readable':
            pairs.append((ru, en))
        if kind == 'kind_param':
            kp_pairs.add((ru, en))
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
    kp = words['kind_param'][0]
    if kp and kp != set(KIND_PARAM):
        errs.append('%s: вид `kind_param` — ровно виды параметров фрагмента %s, а в таблице %s (AL-63)' % (
            TABLE, ', '.join(KIND_PARAM), ', '.join(sorted(kp))))
    elif kp and kp_pairs != set(KIND_PARAM_PAIRS):
        errs.append('%s: вид `kind_param` — ровно пары %s, а в таблице %s (AL-63)' % (
            TABLE, ', '.join('%s/%s' % p for p in KIND_PARAM_PAIRS), ', '.join('%s/%s' % p for p in sorted(kp_pairs))))
    for w in sorted((words['type'][0] & set(KIND_PARAM)) - set(KIND_PARAM_ALSO_TYPE)):
        errs.append('%s: `%s` — вид параметра фрагмента, не тип данных: его вид `kind_param`, не `type` (AL-63)' % (TABLE, w))
    words['readable_pairs'] = pairs
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
        m = re.match(r'^### \S+ — (\S+)(?: \(|\s*$|\s+//)', line)
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


UNICODE_OPS = '≥≤≠→⇒∈'
DEF_HEAD = re.compile(r'^\s*(?:определение|define|definition)\s+[^\s(]+\(')  # начало заголовка определения
PARSE_ARROW = re.compile(r'(?:разбор|parse):\s*[\w.]+\s*(?:\([^()]*\))?\s*(->)')  # `разбор: примитив[("роль")] -> Тип`
ASSIGN_EQ = re.compile(r'(?<![=<>!])=(?!=)')  # знак `=` вне `==`, `<=`, `>=`, `!=`; `=>` — тело (AL-67)


def def_result_arrow(line):
    """Позиция `->` типа результата в заголовке определения (`определение имя(…) -> Тип`) или None."""
    m = DEF_HEAD.match(line)
    if not m:
        return None
    depth, i = 1, m.end()
    while i < len(line) and depth:
        depth += {'(': 1, ')': -1}.get(line[i], 0)
        i += 1
    a = re.match(r'\s*->', line[i:]) if not depth else None
    return i + a.end() - 2 if a else None


def old_records(line):
    """Прежняя запись (до 2.18) в строке кода, таблицы или строке-ключе: (тело через `=`, лишние `->`).
    `->` допустим только как тип результата — после списка параметров определения и в `разбор: … -> Тип`;
    любой другой `->` — ветка `выбор` или лямбда (AL-68, AL-69). Тело определения: первый знак `=` после типа
    результата должен быть `=>` (AL-67)."""
    allowed = {m.start(1) for m in PARSE_ARROW.finditer(line)}
    res = def_result_arrow(line)
    old_body = False
    if res is not None:
        allowed.add(res)
        eq = ASSIGN_EQ.search(line, res + 2)
        old_body = bool(eq) and line[eq.start() + 1:eq.start() + 2] != '>'
    arrows = [m.start() for m in re.finditer('->', line) if m.start() not in allowed]
    return old_body, arrows
LATIN = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

# Транслитерация (спецификация, 1а, AL-53): строчная буква кириллицы -> латиница; ъ и ь опускаются.
TRANSLIT = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y',
            'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
            'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'}


def dictionary_pairs(text):
    """Нормативная часть словаря (спецификация, 1а, AL-62): пары «русское -> английское» в порядке файла — строки таблиц
    разделов 2.1–2.9, 2.11, 2.12, 2.16 (`| `рус` | `англ` | …`) и записи `` `рус` → `англ` `` раздела 2.10."""
    pairs, sec = [], None
    for line in text.replace('\r\n', '\n').split('\n'):
        m = re.match(r'^#{2,4} (\d+(?:\.\d+)*)\.? ', line)
        if m:
            sec = m.group(1)
            continue
        if sec in NORMATIVE_TABLES:
            pairs += re.findall(r'^\| `([^`]+)` \| `([^`]+)` \|', line)
        elif sec == '2.10':
            pairs += re.findall(r'`([^`]+)` → `([^`]+)`', line)
    return pairs


def dictionary_hash(text):
    """Хеш словаря: первые 12 знаков SHA-256 строк `рус → англ` нормативной части, соединённых LF (без LF в конце), UTF-8."""
    body = '\n'.join('%s → %s' % p for p in dictionary_pairs(text))
    return hashlib.sha256(body.encode('utf-8')).hexdigest()[:12]


def load_glossary(text):
    """Словарь «русское имя -> английское» (1а, AL-53): нормативная часть (`dictionary_pairs`); имя, которому она даёт два
    разных английских имени, в поиск не входит. Возвращает (словарь, версия словаря из шапки или None)."""
    m = re.search(r'\*\*Версия словаря: (\d+)', text)
    seen = {}
    for ru, en in dictionary_pairs(text):
        seen.setdefault(ru, set()).add(en)
    return {ru: next(iter(en)) for ru, en in seen.items() if len(en) == 1}, (int(m.group(1)) if m else None)


def check_dictionary(gtext, specs):
    """Хеш словаря равен закреплённому форматом, и спецификация называет его (AL-62); `specs` — список (имя, текст, слово)."""
    errs = []
    h = dictionary_hash(gtext)
    if h != DICT_HASH:
        errs.append('%s: хеш нормативной части словаря %s, формат закрепил %s: словарь изменён без смены формата (AL-62)' % (
            GLOSSARY, h, DICT_HASH))
    for name, text, word in specs:
        if ('%s `%s`' % (word, DICT_HASH)) not in text:
            errs.append('%s: нет записи «%s `%s`» (раздел 1а, AL-62)' % (name, word, DICT_HASH))
    return errs


def translit(word):
    """Побуквенная транслитерация; заглавная буква даёт латиницу с заглавной первой буквой (`Ж` -> `Zh`); латиница и цифры — как есть."""
    out = ''
    for ch in word:
        low = ch.lower()
        if low in TRANSLIT:
            t = TRANSLIT[low]
            out += (t[:1].upper() + t[1:]) if ch != low else t
        else:
            out += ch
    return out


def words_of(name):
    """Слова имени: части между `_` и пробелами."""
    return [w for w in re.split(r'[_ ]+', name) if w]


def mixed_words(name):
    """Слова имени, где смешаны кириллица и латиница (AL-59)."""
    return [w for w in words_of(name)
            if any('Ѐ' <= c <= 'ӿ' for c in w) and any(c.isascii() and c.isalpha() for c in w)]


def auto_name(name, pascal, gloss):
    """Автоматическое JSON-имя (1а, AL-53). `pascal` — имя-тип (состояние, тип, вариант, элемент перечисления): слова склеиваются,
    каждое с заглавной буквы (`ХОД_АГЕНТА` -> `KhodAgenta`); иначе имя-значение (данное, поле входа, поле, сигнал и его поле,
    примитив, имя настройки вратаря): слова строчными через `_` (`оставить правку` -> `ostavit_pravku`).
    Каждое слово транслитерируется отдельно, латинское слово остаётся (`запрос_Agent` -> `ZaprosAgent`, AL-59)."""
    if LATIN.match(name):
        return name
    if name in gloss:
        return gloss[name]
    words = words_of(name)
    if pascal:
        out = ''
        for w in words:
            if not any(c.islower() for c in w):  # слово заглавными (`ХОД`, `В3`): все буквы, кроме первой, — строчные
                w = w[:1] + w[1:].lower()
            t = translit(w)
            out += t[:1].upper() + t[1:]
        return out
    return '_'.join(translit(w.lower()) for w in words)


def check_operators(text, name):
    """Знаки операторов только ASCII в блоках кода, строках таблиц и строках-ключах (AL-42); прежняя запись тела
    определения, ветки `выбор` и лямбды (`=`, `->` до 2.18, AL-67…AL-69) и тип `да/нет` (AL-66) — ошибка."""
    errs, in_code = [], False
    for n, line in enumerate(text.split('\n'), 1):
        if line.startswith('```'):
            in_code = not in_code
            continue
        if not (in_code or line.startswith('|') or line.lstrip().startswith('- ')):
            continue
        if any(ch in line for ch in UNICODE_OPS):
            errs.append('%s:%d: знак оператора не ASCII (%s)' % (name, n, ''.join(ch for ch in UNICODE_OPS if ch in line)))
        old_body, arrows = old_records(line)
        if old_body:
            errs.append('%s:%d: тело определения пишется после `=>`, а не `=` (AL-67)' % (name, n))
        if arrows:
            errs.append('%s:%d: ветка `выбор` и лямбда пишутся через `=>`, `->` — только перед типом результата (AL-68, AL-69)' % (name, n))
        if 'да/нет' in line:
            errs.append('%s:%d: тип `да/нет` с 2.18 пишется `булево` (AL-66)' % (name, n))
    return errs


def check_removed(text, name):
    """Убранное событие `слово(…)`/`word(…)` (AL-38) в строках таблиц."""
    return ['%s:%d: событие `слово(…)` убрано, пишется `сигнал(…)` (AL-38)' % (name, n)
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


def split_name(decl):
    """Разбор объявления `имя остальное`: (имя, скобки после имени или None, остальное); имя может быть из нескольких слов.
    Скобки `имя (X)` убраны из языка (AL-60): находка скобок — ошибка проверки."""
    m = re.match(r'^([^({\["]+?) \(([^()\s]+)\)(.*)$', decl)
    if m:
        return m.group(1).strip(), m.group(2), m.group(3).strip()
    m = re.match(r'^([^({\["]+?)(?=\s*[({\["]|$)(.*)$', decl)
    head = m.group(1).strip()
    if ' ' in head and not decl.startswith(head + '('):  # `имя тип`: имя — первое слово
        head = head.split()[0]
    return head, None, decl[len(head):].strip()


def split_signal(sig):
    """Разбор сигнала стороны `имя[(поля)]`: имя — всё до первой скобки, может быть из нескольких слов (`остановить совещание`);
    скобки `имя (X)` убраны (AL-60)."""
    m = re.match(r'^(.+?) \(([A-Za-z_][A-Za-z0-9_]*)\)(.*)$', sig)
    if m:
        return m.group(1).strip(), m.group(2), m.group(3).strip()
    nm = sig.split('(')[0].strip()
    return nm, None, sig[len(nm):].strip()


def declarations(text, lang, readable=()):
    """Объявленные имена, которые выходят из машины (1а): список (номер строки, где, имя-тип?, имя, путь, скобки или None);
    путь — уточнённое имя (`(Тип, Вариант, поле)`, `(сторона, сигнал, поле)`; у состояния, данного, поля входа, типа,
    примитива, настройки — `(имя,)`); сначала заголовки состояний и строки таблиц в порядке файла, затем объявления блока `## Типы`."""
    out = []
    names = ('Вход', 'Данные', 'Примитивы', 'Типы', 'Стороны') if lang == 'ru' else ('Input', 'Data', 'Primitives', 'Types', 'Parties')
    sec_input, sec_data, sec_prim, sec_types, sec_parties = names
    signals_col = 'сигналы' if lang == 'ru' else 'signals'
    kind_col = 'вид' if lang == 'ru' else 'kind'
    sec, in_code, header, in_variant = None, False, None, False
    decls = []  # (номер строки, объявление, член варианта?) блока типов

    def fields(body, n, where, path):
        for f in split_top(body):
            fn, fj, _ = split_name(f)
            out.append((n, where, False, fn, path + (fn,), fj))

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
            out.append((n, 'состояния', True, m.group(1), (m.group(1),), m.group(2)))
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
            nm, js, _ = split_name(cells[0])
            if '[*]' not in cells[0] and not (js is None and nm in readable):
                out.append((n, {sec_input: 'поля входа', sec_data: 'данного', sec_prim: 'примитива'}[sec], False, nm, (nm,), js))
        if sec == sec_parties and kind_col in header:
            m = re.search(r'(?:по настройке|by setting) (\S+?)(?: \(([^()\s]+)\))?\(', cells[header.index(kind_col)])
            if m:
                out.append((n, 'настройки вратаря', False, m.group(1), (m.group(1),), m.group(2)))
        if sec == sec_parties and signals_col in header and cells[header.index(signals_col)] != '—':
            party = cells[0]
            for sig in split_top(cells[header.index(signals_col)]):
                nm, js, rest = split_signal(sig)
                out.append((n, 'сигнала', False, nm, (party, nm), js))
                if rest.startswith('(') and rest.endswith(')'):
                    fields(rest[1:-1], n, 'поля сигнала', (party, nm))
    owner = None
    for n, d, member in decls:
        if member:
            nm, js, rest = split_name(d)
            out.append((n, 'варианта', True, nm, (owner, nm), js))
            if rest.startswith('{') and rest.endswith('}'):
                fields(rest[1:-1], n, 'поля', (owner, nm))
            continue
        m = re.match(r'^(?:перечисление|enum) (.+?) = (.*)$', d)
        if m:
            nm, js, _ = split_name(m.group(1))
            owner = nm
            out.append((n, 'типа', True, nm, (nm,), js))
            for el in split_top(re.sub(r'"[^"]*"', '', m.group(2)), '|'):
                en_, ej, _ = split_name(el)
                out.append((n, 'элемента перечисления', True, en_, (nm, en_), ej))
            continue
        m = re.match(r'^(?:тип|type|вариант|variant) (.+?) \{(.*)$', d)
        if m:
            nm, js, _ = split_name(m.group(1))
            owner = nm
            out.append((n, 'типа', True, nm, (nm,), js))
            body = m.group(2).strip()
            if body.endswith('}'):
                fields(body[:-1], n, 'поля', (nm,))
    return out


def names_table(text, lang):
    """Строки раздела `## Имена` (`## Names`): список (номер строки, имя или уточнённое имя, JSON-имя)."""
    title = 'Имена' if lang == 'ru' else 'Names'
    rows, sec, in_code, header = [], None, False, None
    for n, line in enumerate(text.split('\n'), 1):
        if line.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith('## '):
            sec, header = line[3:].strip(), None
            continue
        if sec != title or not line.startswith('|') or re.match(r'^\|[-:| ]+\|\s*$', line):
            continue
        cells = [c.strip() for c in re.split(r'(?<!\\)\|', line.strip())[1:-1]]
        if header is None:
            header = cells
            continue
        if len(cells) == 2:
            rows.append((n, cells[0], cells[1]))
    return rows


def json_names(text, lang, gloss, readable=()):
    """JSON-имена объявлений (1а, AL-60): (список (номер строки, где, имя-тип?, имя, путь, JSON-имя), ошибки таблицы `## Имена`
    списком (номер строки, текст)). Строка с уточнённым именем (путём) сильнее строки с простым именем; имя без строки —
    автоматическое JSON-имя."""
    decls = declarations(text, lang, readable)
    rows, errs = {}, []
    for n, key, js in names_table(text, lang):
        path = tuple(p.strip() for p in key.split('.'))
        if path in rows:
            errs.append((n, 'имя `%s` повторено в `## Имена` (строка %d)' % (key, rows[path][0])))
            continue
        rows[path] = (n, js)
        if not LATIN.match(js):
            errs.append((n, 'JSON-имя `%s` строки `## Имена` у `%s` не латинское' % (js, key)))
    without = {p: [] for p in rows}  # строка -> имена, которые её объявления получили бы без неё
    out = []
    for n, where, pascal, nm, path, _ in decls:
        auto = auto_name(nm, pascal, gloss)
        full, bare = rows.get(path), rows.get((nm,))
        if full is not None:
            without[path].append(bare[1] if bare is not None and len(path) > 1 else auto)
            final = full[1]
        elif bare is not None:
            without[(nm,)].append(auto)
            final = bare[1]
        else:
            final = auto
        out.append((n, where, pascal, nm, path, final))
    names = {d[3] for d in decls}
    paths = {d[4] for d in decls}
    for path, (n, js) in rows.items():
        known = (path[0] in names) if len(path) == 1 else (path in paths)
        if not known:
            errs.append((n, 'строка `## Имена` для `%s`: такого объявления в файле нет (внутренние и читаемые имена в таблицу '
                            'не пишутся, AL-60)' % '.'.join(path)))
        elif all(alt == js for alt in without[path]):
            errs.append((n, 'лишняя строка `## Имена` у `%s`: `%s` — имя, которое объявление получает без неё (AL-60)' % (
                '.'.join(path), js)))
    return out, errs


def namespace(where, path):
    """Пространство различимости JSON-имени (1а, AL-58): вид объявления и путь без последнего имени."""
    return (where,) + tuple(path[:-1])


def check_json_names(text, words, name, lang, gloss, contract=None):
    """JSON-имена имён, которые выходят из машины (AL-53, AL-58…AL-60); `contract` — JSON-имена данных контракта и фрагмента."""
    errs = []
    readable = words['readable'][0 if lang == 'ru' else 1]
    for n, where, pascal, nm, path, js in declarations(text, lang, readable):
        if js is not None:
            errs.append('%s:%d: скобки `(%s)` после имени %s `%s`: скобки убраны, JSON-имя пишется в `## Имена` (AL-60)' % (
                name, n, js, where, nm))
        for w in mixed_words(nm):
            errs.append('%s:%d: в слове `%s` имени %s `%s` смешаны кириллица и латиница: смешивать можно только через `_` '
                        'или пробел (AL-59)' % (name, n, w, where, nm))
    names, table_errs = json_names(text, lang, gloss, readable)
    errs += ['%s:%d: %s' % (name, n, e) for n, e in table_errs]
    for n, key, js in names_table(text, lang):
        for part in key.split('.'):
            for w in mixed_words(part):
                errs.append('%s:%d: в слове `%s` имени `%s` смешаны кириллица и латиница (AL-59)' % (name, n, w, key))
    spaces = {}
    if re.search(r'^(?:Пауза|Pause)\(', text, re.M):  # состояния фрагмента входят в пространство состояний машины (AL-58)
        spaces[('состояния',)] = {FRAGMENT_STATE: 'состояния фрагмента «Пауза»'}
    spaces[('данного',)] = {js: 'данного контракта или фрагмента' for js in (contract or ())}
    for n, where, pascal, nm, path, js in names:
        if not LATIN.match(js):
            errs.append('%s:%d: у %s `%s` JSON-имя `%s` не латинское: нужна строка в `## Имена` (AL-60)' % (name, n, where, nm, js))
        space = spaces.setdefault(namespace(where, path), {})
        if js in space:
            errs.append('%s:%d: JSON-имя `%s` у %s `%s` уже у %s: коллизия в одном пространстве (AL-58)' % (
                name, n, js, where, '.'.join(path), space[js]))
        space.setdefault(js, '%s `%s` (строка %d)' % (where, '.'.join(path), n))
    return errs


def check_sample(text, words, name, lang, gloss):
    contract = [en for ru, en in words['readable_pairs'] if ru in CONTRACT_DATA] if 'readable_pairs' in words else []
    errs = check_operators(text, name) + check_removed(text, name) + check_json_names(text, words, name, lang, gloss, contract)
    own = {k: v[0 if lang == 'ru' else 1] for k, v in words.items() if k in KINDS}
    other = {k: v[1 if lang == 'ru' else 0] for k, v in words.items() if k in KINDS}
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


ROW_RU = '| расход | transport_usage |\n'
MUTATIONS = {
    'ru': [  # (описание, что заменить, на что)
        ('заголовок раздела', '\n## Состояния\n', '\n## Статусы\n'),
        ('английский раздел', '\n## Данные\n', '\n## Data\n'),
        ('строка-ключ', '- Срок тишины:', '- Срок тишыны:'),
        ('столбец таблицы состояний', '| № | Событие | Условие | Действия | Куда |', '| № | Событие | Условия | Действия | Куда |'),
        ('столбец таблицы имён', '| имя | JSON-имя |', '| имя | JSON имя |'),
        ('вид состояния', '### СТАРТ — операция\n', '### СТАРТ — операция2\n'),
        ('английская строка-ключ чтений', '- Читает: число_повторов, ход', '- Reads: число_повторов, ход'),
        ('знак оператора не ASCII', '| 3 | число_повторов >= ЧИСЛО_ПОВТОРОВ |', '| 3 | число_повторов ≥ ЧИСЛО_ПОВТОРОВ |'),
        ('тело определения через `=` (до 2.18)', 'определение пауза_повтора(п число>=0) -> число =>', 'определение пауза_повтора(п число>=0) -> число ='),
        ('ветка `выбор` через `->` (до 2.18)', 'иначе => ложь }', 'иначе -> ложь }'),
        ('лямбда через `->` (до 2.18)', '(н, _) => н * 2', '(н, _) -> н * 2'),
        ('тип `да/нет` (до 2.18)', '-> булево =>', '-> да/нет =>'),
        ('однострочное тело через `=` (до 2.18)', '-> число =>\n  свёртка(', '-> число = свёртка('),
        ('ветка с текстовым образцом через `->`', 'ВидДействия.СменаРежима => истина;', 'ВидДействия.СменаРежима => истина; "ask" -> "ask";'),
        ('ветка со стражем через `->`', 'ВидДействия.СменаРежима => истина;', 'ВидДействия.СменаРежима если есть(вид_действия) -> истина;'),
        ('трёхместная лямбда через `->`', '(н, _) => н * 2', '(а, б, в) -> а * 2'),
        ('лямбда через `->` без пробела', '(н, _) => н * 2', '(н, _)-> н * 2'),
        ('лишняя строка `## Имена` у данного (словарь)', ROW_RU, ROW_RU + '| число_повторов | retry_count |\n'),
        ('лишняя строка `## Имена` у состояния (словарь)', ROW_RU, ROW_RU + '| СТАРТ | Start |\n'),
        ('лишняя строка `## Имена` у сигнала (словарь)', ROW_RU, ROW_RU + '| разрешить | allow |\n'),
        ('лишняя строка `## Имена` у поля (уточнённое имя, словарь)', ROW_RU, ROW_RU + '| Токены.вход | input |\n'),
        ('лишняя строка `## Имена` у латинского имени', ROW_RU, ROW_RU + '| time_now | time_now |\n'),
        ('строка `## Имена` для необъявленного имени', ROW_RU, ROW_RU + '| нет_такого | no_such |\n'),
        ('строка `## Имена` для внутреннего имени (константа)', ROW_RU, ROW_RU + '| ЧИСЛО_ПОВТОРОВ | RETRIES |\n'),
        ('строка `## Имена` для читаемого имени', ROW_RU, ROW_RU + '| остановка | stop |\n'),
        ('имя повторено в `## Имена`', ROW_RU, ROW_RU + '| расход | spend |\n'),
        ('нелатинское JSON-имя строки', ROW_RU, '| расход | расход_транспорта |\n'),
        ('скобки у состояния (убраны)', '### СТАРТ — операция\n', '### СТАРТ — операция (Begin)\n'),
        ('скобки у данного (убраны)', '| число_повторов | число>=0 |', '| число_повторов (retries) | число>=0 |'),
        ('скобки у сигнала (убраны)', '| разрешить, отказать |', '| разрешить (permit), отказать |'),
        ('JSON-имя не строится', '| начато | ?число |', '| начато§ | ?число |'),
        ('два состояния с одним JSON-именем', ROW_RU, ROW_RU + '| ПОВТОР | Continuation |\n'),
        ('два данных с одним JSON-именем', ROW_RU, ROW_RU + '| текст_ответа | reply_x |\n| артефакт_ответа | reply_x |\n'),
        ('два поля одной записи с одним JSON-именем', ROW_RU, ROW_RU + '| Токены.вход | output |\n'),
        ('состояние с JSON-именем состояния фрагмента', ROW_RU, ROW_RU + '| УЧЁТ | Pause |\n'),
        ('данное с JSON-именем данного фрагмента', ROW_RU, ROW_RU + '| начато | open_requests |\n'),
        ('данное с JSON-именем данного контракта', ROW_RU, ROW_RU + '| начато | stop_reason |\n'),
        ('смешанное слово (кириллица и латиница)', '| начато | ?число |', '| начатоAt | ?число |'),
        ('убранное событие слово', '| 1 | сигнал(разрешить) |', '| 1 | слово(разрешить) |'),
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
        ('знак оператора не ASCII', 'fold(range(1, n), RETRY_PAUSE, (m, _) => m * 2)', 'fold(range(1, n), RETRY_PAUSE, (m, _) ⇒ m * 2)'),
        ('тело определения через `=` (до 2.18)', 'define retry_pause(n int>=0) -> int =>', 'define retry_pause(n int>=0) -> int ='),
        ('ветка `match` через `->` (до 2.18)', 'ActionKind.SwitchMode => true;', 'ActionKind.SwitchMode -> true;'),
        ('лямбда через `->` (до 2.18)', '(m, _) => m * 2', '(m, _) -> m * 2'),
        ('однострочное тело через `=` (до 2.18)', '-> int =>\n  fold(', '-> int = fold('),
        ('ветка с текстовым образцом через `->`', 'ActionKind.SwitchMode => true;', 'ActionKind.SwitchMode => true; "ask" -> "ask";'),
        ('ветка со стражем через `->`', 'ActionKind.SwitchMode => true;', 'ActionKind.SwitchMode if has(action) -> true;'),
        ('трёхместная лямбда через `->`', '(m, _) => m * 2', '(a, b, c) -> a * 2'),
        ('лямбда через `->` без пробела', '(m, _) => m * 2', '(m, _)-> m * 2'),
        ('убранное событие word', '| 1 | signal(allow) |', '| 1 | word(allow) |'),
        ('начальное состояние', 'Initial state: Start', 'Initial stat: Start'),
        ('ключ шапки', '- machine_version:', '- machine_ver:'),
        ('нет строки language', '- language: en\n', ''),
        ('скобки у латинского имени (убраны)', '| retry_count | int>=0 |', '| retry_count (retry_count) | int>=0 |'),
        ('данное с JSON-именем данного фрагмента', '\n## Constants\n',
         '\n## Names\n\n| name | json_name |\n|---|---|\n| started | open_requests |\n\n## Constants\n'),
        ('лишняя строка `## Names`', '\n## Constants\n',
         '\n## Names\n\n| name | json_name |\n|---|---|\n| retry_count | retry_count |\n\n## Constants\n'),
    ],
}
CLEAN = {  # порча, которая ошибки давать не должна
    'ru': [
        ('одно JSON-имя в разных пространствах (поле записи и данное)', ROW_RU, ROW_RU + '| Токены.вход | retry_count |\n'),
        ('смешение письменностей через `_`', '| начато | ?число |', '| начато_at | ?число |'),
        ('однострочное тело через `=>` с `пусть`, `>=` и `==`', '-> число =>\n  свёртка(', '-> число => пусть к = п >= 0 в если к == истина то свёртка('),
    ],
    'en': [
        ('однострочное тело через `=>` с `let`, `>=` и `==`', '-> int =>\n  fold(', '-> int => let k = n >= 0 in if k == true then fold('),
    ],
}


MUTATED = {'state-machine-agent-step.alula.md', 'state-machine-agent-step.en.alula.md'}


def selftest(sample, words, name, lang, gloss):
    errs = check_sample(sample, words, name, lang, gloss)
    if errs:
        return ['самопроверка (%s): исправный образец не прошёл: %s' % (lang, errs[0])]
    if name not in MUTATED:
        return []
    bad = []
    for what, a, b in MUTATIONS[lang]:
        if a not in sample:
            bad.append('самопроверка (%s): образец не содержит заменяемого (%s)' % (lang, what))
            continue
        if not check_sample(sample.replace(a, b, 1), words, name, lang, gloss):
            bad.append('самопроверка (%s): порча не замечена (%s)' % (lang, what))
    for what, a, b in CLEAN[lang]:
        if a not in sample:
            bad.append('самопроверка (%s): образец не содержит заменяемого (%s)' % (lang, what))
            continue
        e = check_sample(sample.replace(a, b, 1), words, name, lang, gloss)
        if e:
            bad.append('самопроверка (%s): ложная ошибка (%s): %s' % (lang, what, e[0]))
    return bad


def selftest_table(text):
    """Вид параметра фрагмента в `type`, испорченное английское слово вида `kind_param` и таблица без `kind_param` — ошибка (AL-63)."""
    a = 'kind_param\tсигнал\tsignal\n'
    if a not in text:
        return ['самопроверка таблицы слов: нет заменяемой строки']
    if check_table(text)[0]:
        return ['самопроверка таблицы слов: исправная таблица не прошла']
    bad = []
    if not check_table(text.replace(a, 'type\tсигнал\tsignal\n', 1))[0]:
        bad.append('самопроверка таблицы слов: вид параметра в группе `type` не замечен')
    if not check_table(text.replace(a, 'kind_param\tсигнал\tsgnl\n', 1))[0]:
        bad.append('самопроверка таблицы слов: испорченное английское слово вида `kind_param` не замечено')
    if not check_table(''.join(l for l in text.splitlines(True) if not l.startswith('kind_param\t')))[0]:
        bad.append('самопроверка таблицы слов: таблица без `kind_param` не замечена')
    return bad


def selftest_dictionary(gtext, specs):
    """Изменённая запись словаря без смены формата — ошибка (AL-62)."""
    a = '| `число_повторов` | `retry_count` |'
    if a not in gtext:
        return ['самопроверка словаря: нет заменяемой записи']
    if check_dictionary(gtext, specs):
        return ['самопроверка словаря: исправный словарь не прошёл']
    if not check_dictionary(gtext.replace(a, '| `число_повторов` | `retries` |', 1), specs):
        return ['самопроверка словаря: изменённая запись не замечена']
    return []


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    table = read(TABLE)
    errs, words = check_table(table)
    gtext = read(GLOSSARY)
    gloss, version = load_glossary(gtext)
    specs = [(n, read(n), w) for n, w in SPECS]
    errs += check_dictionary(gtext, specs)
    for name, lang in SAMPLES:
        sample = read(name)
        errs += check_sample(sample, words, name, lang, gloss)
        if '--selftest' in sys.argv:
            errs += selftest(sample, words, name, lang, gloss)
    if '--selftest' in sys.argv:
        errs += selftest_dictionary(gtext, specs)
        errs += selftest_table(table)
    for e in errs:
        print(e)
    rows = sum(len(words[k][0]) for k in KINDS)
    print('таблица слов: %d строк, %d видов; словарь версии %s: %d имён, хеш %s; образцов: %d; расхождений: %d' % (
        rows, len(KINDS), version, len(gloss), dictionary_hash(gtext), len(SAMPLES), len(errs)))
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
