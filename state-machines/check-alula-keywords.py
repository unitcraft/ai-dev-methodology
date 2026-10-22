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
  4. знаки операторов (спецификация, 1а, AL-42): в блоках кода, строках таблиц и строках-ключах нет знаков `≥`, `≤`, `≠`, `→`, `⇒`, `∈`, `‥`
     (только ASCII: `>=`, `<=`, `!=`, `->`, `=>`, `in`, `..`); в прозе знак `→` допустим; прежняя запись (до 2.18, AL-67…AL-69) — ошибка:
     в заголовке определения `определение имя(…) -> Тип` (`define`) первый знак `=` после типа результата — не `=>` (тело
     пишется после `=>`; `==`, `<=`, `>=`, `!=` знаком `=` не считаются); любой знак `->`, кроме типа результата после списка
     параметров определения и в `разбор: примитив[("роль")] -> Тип` (`parse:`), — ветка `выбор` или лямбда, они пишутся через `=>`;
     а также тип `да/нет` (с 2.18 — `булево`, AL-66); после `то`/`then` условного действия или выражения и после
     `иначе`/`else` его ветки — не блок `{ … }` или пустой блок (AL-70, AL-71); `если` с блоком без `то` (без `то`
     допустим только страж ветки `выбор`, до `=>`); `для каждого`/`for each` без блока `{ … }` после выражения
     коллекции, в том числе с двоеточием (AL-72); `пусть`/`let`, после которого до конца привязки (`;`, конец ячейки,
     конец группы, пустая строка) на глубине 0 стоит слово `в`/`in`, — прежние действие и выражение `пусть … в`
     (AL-73, AL-75); блоки проверяются только в местах кода (`code_segments`): блок кода целиком, ячейки столбцов кода
     (`CODE_COLUMNS`; не «примечание»/`note`, не имена и типы), значения строк-ключей кода и вложенный список «При входе»;
     слова внутри строковых литералов не читаются; прежняя запись до 2.19 (AL-76…AL-80, функция `check_v219`): знак `‥`
     вместо `..`; в участках кода — вызов `диапазон(…)` (в английском файле `range(…)`; диапазон пишется `a..b`), макрос
     каталога (`MACROS`), вызванный функцией, а не методом после точки (`фильтр(xs, …)` вместо `xs.фильтр(…)`), и `in {`;
     в ячейке события (столбцы «Событие»/«событие», `Event`/`event`; `event_cells`) — `in {`, образец `ответ: Вар(` и
     сигнал с полями `сигнал(с(`; в участках кода и строках таблиц — пустая `${}` и незакрытая вставка в текстовом
     литерале, литерал со вставкой рядом со знаком набора литералов (`|`, в таблице `\\|`) или внутри `in […]`; литерал
     читается с экранированием `\\` и вложенными литералами во вставке (`string_end`); `in` после `for each <имя>` —
     слово цикла, а не множество (`loop_in`); типы выражений во вставке не проверяются (это проверка переводчика
     продукта); пространство вызовов (AL-81, `check_calls`): имя определения (как написано и английское имя по 1а,
     `auto_name`) и примитива (как написано и JSON-имя) не совпадает со словом функции каталога и с `range`, а имя
     определения — с именем примитива (AL-58); прежняя запись до 2.20 (AL-82, функция `check_v220`): в столбце
     «сигналы»/`signals` таблицы «Сторон» — круглая скобка сразу после имени сигнала `засчитан(находки []Находка)`
     (скобки кортежа внутри полей `{ пара (число, текст) }` не в счёт; с 2.20 —
     `засчитан { находки []Находка }`; скобки JSON-имени `имя (X)` ловит проверка 5); в участках кода — альтернатива
     `выбор`/`match` по варианту с полями в круглых скобках: имя варианта с заглавной (или `Тип.Вар`), за ним `(…)` и
     `=>`, `|` или страж `если`/`if` (`Закончен(текст) =>`; с 2.20 — `Закончен { текст } =>`); вызовы функций
     (`Ответ(…)`, `Отказ(…)`, `Пауза(…)`, функции каталога, определения) этими признаками не ловятся;
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
     определения, ветки `выбор` и лямбды; прежние `диапазон(…)`, макрос функцией, образец события и сигнал с полями в
     круглых скобках, `in {…}`, знак `‥`; пустая и незакрытая вставка, вставка в наборе литералов и в `in […]`; объявление
     сигнала с полями и альтернатива `выбор` в круглых скобках, AL-82), JSON-имени
     (лишняя строка `## Имена`,
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
DICT_HASH = '60383c370415'  # хеш нормативной части словаря, закреплённый форматом 2.16 и тем же в 2.17–2.20 (спецификация, 1а, AL-62)
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


UNICODE_OPS = '≥≤≠→⇒∈‥'
DEF_HEAD = re.compile(r'^\s*(?:определение|define|definition)\s+[^\s(]+\s*\(')  # начало заголовка определения
PARSE_ARROW = re.compile(r'(?:разбор|parse):\s*[\w.]+\s*(?:\([^()]*\))?\s*(->)')  # `разбор: примитив[("роль")] -> Тип`
ASSIGN_EQ = re.compile(r'(?<![=<>!])=(?!=)')  # знак `=` вне `==`, `<=`, `>=`, `!=`; `=>` — тело (AL-67)


class DefHeader:
    """Заголовок определения в блоке кода, в том числе перенесённый на несколько строк (AL-67): пока скобка параметров
    не закрыта, считается глубина скобок по строкам; стрелка `->` сразу после закрывающей скобки — на той же строке или
    в начале следующей — тип результата; первый знак `=` после неё (не `==`, `<=`, `>=`, `!=`) обязан быть `=>`."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.depth, self.seek = 0, None  # seek: None, 'arrow' (скобка закрыта, ждём `->`), 'eq' (ждём `=>`)

    def line(self, line):
        """Возвращает (позиция стрелки типа результата в строке или None, тело записано через `=`)."""
        pos, arrow, old_body = 0, None, False
        m = DEF_HEAD.match(line)
        if m:
            self.depth, self.seek, pos = 1, None, m.end()
        if self.depth:
            i = pos
            while i < len(line) and self.depth:
                self.depth += {'(': 1, ')': -1}.get(line[i], 0)
                i += 1
            if self.depth:
                return None, False
            self.seek, pos = 'arrow', i
        if self.seek == 'arrow':
            r = re.match(r'\s*->', line[pos:])
            if r:
                arrow, pos, self.seek = pos + r.end() - 2, pos + r.end(), 'eq'
            elif line[pos:].strip():
                self.reset()  # после параметров не `->`: не заголовок с типом результата
        if self.seek == 'eq':
            eq = ASSIGN_EQ.search(line, pos)
            if eq:
                old_body = line[eq.start() + 1:eq.start() + 2] != '>'
                self.reset()
        return arrow, old_body


def old_records(line, header=None):
    """Прежняя запись (до 2.18) в строке кода, таблицы или строке-ключе: (тело через `=`, лишние `->`).
    `->` допустим только как тип результата — после списка параметров определения (`header`, см. `DefHeader`)
    и в `разбор: … -> Тип`; любой другой `->` — ветка `выбор` или лямбда (AL-68, AL-69)."""
    allowed = {m.start(1) for m in PARSE_ARROW.finditer(line)}
    res, old_body = (header or DefHeader()).line(line)
    if res is not None:
        allowed.add(res)
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


CELL_PIPE = re.compile(r'(?<!\\)\|')
# столбцы таблиц, где стоит код (выражения и действия); прочие столбцы (имена, типы, «примечание»/`note`, «Куда»,
# «читает», «пишет», сигналы) — не код, проверка блоков их не читает
CODE_COLUMNS = {'значение', 'value', 'по умолчанию', 'default', 'начальное', 'initial', 'не убывает', 'non_decreasing',
                'профиль', 'profile', 'условие', 'condition', 'действия', 'actions', 'выражение', 'expression',
                'когда', 'when', 'ответ', 'response'}
# строки-ключи, значение которых — код; «При входе» без значения открывает вложенный список действий
CODE_KEYS = re.compile(r'^- (?:При входе|On entry|Инвариант|Invariant|Предел запросов|Request limit|Срок тишины|Idle term|'
                       r'Кроме|Except):\s*(.*)$')
ENTRY_KEY = re.compile(r'^- (?:При входе|On entry):\s*$')
WORD_CH = re.compile(r'\w')


def word_at(s, i, w):
    """Слово `w` в позиции i, не часть другого слова."""
    if not s.startswith(w, i):
        return False
    before = s[i - 1] if i else ' '
    after = s[i + len(w)] if i + len(w) < len(s) else ' '
    return not WORD_CH.match(before) and not WORD_CH.match(after)


def string_end(s, i, errs=None):
    """Позиция после строкового литерала, который начинается кавычкой в позиции i: знак `\\` экранирует следующий знак,
    вставка `${ … }` (AL-80) читается до своей `}` с вложенными литералами; нет закрывающей кавычки — конец строки.
    В `errs` (список) кладутся (позиция, метка): `EMPTY_INS` — пустая вставка `${}`, `OPEN_INS` — незакрытая вставка."""
    j = i + 1
    while j < len(s):
        ch = s[j]
        if ch == '\\':
            j += 2
            continue
        if ch == '"':
            return j + 1
        if s.startswith('${', j):
            depth, k = 1, j + 2
            while k < len(s) and depth:
                if s[k] == '"':
                    k = string_end(s, k, errs)
                    continue
                depth += {'{': 1, '}': -1}.get(s[k], 0)
                k += 1
            if depth:
                if errs is not None:
                    errs.append((j, 'OPEN_INS'))
                return len(s)
            if errs is not None and not s[j + 2:k - 1].strip():
                errs.append((j, 'EMPTY_INS'))
            j = k
            continue
        j += 1
    return len(s)


def scan_top(s, i, stop):
    """Первая позиция на глубине 0 начиная с i, где `stop(s, j)` истинно; -1 при выходе из группы или в конце.
    Строковые литералы пропускаются."""
    depth = 0
    while i < len(s):
        ch = s[i]
        if ch == '"':
            i = string_end(s, i)
            continue
        if ch in '([{':
            if depth == 0 and stop(s, i):
                return i
            depth += 1
        elif ch in ')]}':
            depth -= 1
            if depth < 0:
                return -1
        elif depth == 0 and stop(s, i):
            return i
        i += 1
    return -1


def outside_strings(s):
    """Позиции вне строковых литералов `"…"`."""
    out, i = [], 0
    while i < len(s):
        if s[i] == '"':
            i = string_end(s, i)
            continue
        out.append(i)
        i += 1
    return out


def block_close(s, j):
    """Позиция `}`, закрывающей `{` в позиции j (строки пропускаются)."""
    depth, x = 0, j
    while x < len(s):
        if s[x] == '"':
            x = string_end(s, x)
            continue
        depth += {'{': 1, '(': 1, '[': 1, '}': -1, ')': -1, ']': -1}.get(s[x], 0)
        if depth == 0:
            return x
        x += 1
    return len(s)


def branch_errors(seg, k):
    """Ветка с позиции k (после `то`/`иначе`): блок `{ … }`, не пустой. Возвращает (метка ошибки или None, конец)."""
    rest = seg[k:].lstrip()
    if not rest.startswith('{'):
        return 'AL-71', k
    j = k + len(seg[k:]) - len(rest)
    x = block_close(seg, j)
    if not seg[j + 1:x].strip():
        return 'EMPTY', x
    return None, x


def block_errors(seg):
    """Прежняя запись блоков (до 2.18) в участке кода: позиции и метки.
    (а) условное действие и выражение: после `то`/`then` и `иначе`/`else` — непустой блок `{ … }` (AL-70, AL-71);
    `если` без `то` допустим только как страж ветки `выбор` (до `=>`); блок без `то` — ошибка;
    (б) `для каждого`/`for each`: после выражения коллекции — блок `{ … }`, без двоеточия (AL-72);
    (в) `пусть`/`let` со словом `в`/`in` до конца привязки (AL-73, AL-75).
    Слова внутри строковых литералов не читаются."""
    out = []
    for i in outside_strings(seg):
        for w_if, w_then, w_else in (('если', 'то', 'иначе'), ('if', 'then', 'else')):
            if not word_at(seg, i, w_if):
                continue
            k = i + len(w_if)
            t = scan_top(seg, k, lambda s, j: word_at(s, j, w_then) or s[j] in ';|' or s.startswith('=>', j)
                         or s.startswith('\n\n', j))
            if t < 0 or not word_at(seg, t, w_then):
                # страж ветки `выбор` кончается `=>`; без `то` блок `{` на глубине 0 — ошибка
                if t >= 0 and seg.startswith('=>', t):
                    continue
                b = scan_top(seg, k, lambda s, j: s[j] in '{;|' or s.startswith('\n\n', j))
                if b >= 0 and seg[b] == '{':
                    out.append((i, 'NO_THEN'))
                continue
            label, x = branch_errors(seg, t + len(w_then))
            if label:
                out.append((i, label))
                if label == 'AL-71':
                    continue
            tail = seg[x + 1:].lstrip()
            if word_at(tail, 0, w_else) and not tail[len(w_else):].lstrip().startswith('=>'):
                e0 = x + 1 + (len(seg[x + 1:]) - len(tail)) + len(w_else)
                label, _ = branch_errors(seg, e0)
                if label:
                    out.append((i, label))
        for w_for, w_in in (('для каждого', 'в'), ('for each', 'in')):
            if word_at(seg, i, w_for):
                c = scan_top(seg, i + len(w_for), lambda s, j: s[j] in ':{;|' or s.startswith('\n\n', j))
                if c < 0 or seg[c] != '{':
                    out.append((i, 'AL-72'))
        for w_let, w_in in (('пусть', 'в'), ('let', 'in')):
            if word_at(seg, i, w_let):
                # привязка кончается `;`, концом ячейки, концом группы или пустой строкой; слово `в`/`in` до конца —
                # прежние `пусть … в выр` и `пусть … в действия` (AL-73, AL-75)
                c = scan_top(seg, i + len(w_let),
                             lambda s, j: s[j] in ';|' or s.startswith('\n\n', j) or word_at(s, j, w_in))
                if c >= 0 and word_at(seg, c, w_in):
                    out.append((i, 'AL-75'))
    return out


BLOCK_MSG = {'AL-71': 'ветки `если` пишутся блоками: `то { … } иначе { … }` (AL-70, AL-71)',
             'NO_THEN': 'у `если` с блоком нет `то`: `если выр то { … }`; `если` без `то` — только страж ветки `выбор` (AL-70)',
             'EMPTY': 'ветка `если` не пустая: блок `{ }` без содержимого не пишется, ненужную ветку `иначе` опускают (AL-70)',
             'AL-72': 'тело `для каждого` пишется блоком: `для каждого x в xs { … }`, без двоеточия (AL-72)',
             'AL-75': 'у `пусть` нет слова `в`: привязка — `пусть имя = выр;` в блоке `{ …; выр }` или `{ …; действия }` (AL-73, AL-75)'}


def check_operators(text, name):
    """Знаки операторов только ASCII в блоках кода, строках таблиц и строках-ключах (AL-42); прежняя запись тела
    определения, ветки `выбор` и лямбды (`=`, `->` до 2.18, AL-67…AL-69) и тип `да/нет` (AL-66) — ошибка."""
    errs, in_code, header = [], False, DefHeader()
    for n, line in enumerate(text.split('\n'), 1):
        if line.startswith('```'):
            in_code = not in_code
            header.reset()
            continue
        if not (in_code or line.startswith('|') or line.lstrip().startswith('- ')):
            continue
        if any(ch in line for ch in UNICODE_OPS):
            errs.append('%s:%d: знак оператора не ASCII (%s)' % (name, n, ''.join(ch for ch in UNICODE_OPS if ch in line)))
        old_body, arrows = old_records(line, header if in_code else None)
        if old_body:
            errs.append('%s:%d: тело определения пишется после `=>`, а не `=` (AL-67)' % (name, n))
        if arrows:
            errs.append('%s:%d: ветка `выбор` и лямбда пишутся через `=>`, `->` — только перед типом результата (AL-68, AL-69)' % (name, n))
        if 'да/нет' in line:
            errs.append('%s:%d: тип `да/нет` с 2.18 пишется `булево` (AL-66)' % (name, n))
    errs += [e for e in segment_errors(text, name) if e not in errs]
    return errs


def code_segments(text):
    """Участки кода для проверки блоков: (номер первой строки с 0, текст). Блок кода — целиком (заголовки и ветки
    переносятся на несколько строк); в таблице — ячейки столбцов кода (`CODE_COLUMNS`) по заголовку таблицы;
    значение строки-ключа кода (`CODE_KEYS`) и элементы вложенного списка «При входе». Проза — столбцы
    «примечание»/`note`, имена, типы, абзацы и прочие строки списка — не читается."""
    lines = text.split('\n')
    segs, start, cols, prev_table, entry = [], None, [], False, False
    for n, line in enumerate(lines):
        if line.startswith('```'):
            if start is None:
                start = n + 1
            else:
                segs.append((start, '\n'.join(lines[start:n])))
                start = None
            continue
        if start is not None:
            continue
        is_table = line.startswith('|')
        if is_table:
            cells = [c.strip() for c in CELL_PIPE.split(line.strip())[1:-1]]
            if not prev_table:
                cols = [i for i, c in enumerate(cells) if c.lower() in CODE_COLUMNS]
            elif not re.match(r'^\|[-:| ]+\|$', line):
                segs += [(n, cells[i]) for i in cols if i < len(cells)]
        prev_table = is_table
        m = CODE_KEYS.match(line)
        if m:
            segs.append((n, m.group(1)))
        if ENTRY_KEY.match(line):
            entry = True
        elif entry and re.match(r'^\s+- ', line):
            segs.append((n, line.strip()[2:]))
        elif line.strip():
            entry = False
    return segs


def segment_errors(text, name):
    """Проверка блоков `{ … }` (AL-70…AL-75) по участкам кода (`code_segments`)."""
    errs = []
    for first, seg in code_segments(text):
        for pos, label in block_errors(seg):
            e = '%s:%d: %s' % (name, first + seg.count('\n', 0, pos) + 1, BLOCK_MSG[label])
            if e not in errs:
                errs.append(e)
    return errs


# макросы каталога (раздел 12): с 2.19 — методы списка `xs.фильтр(…)`, вызов функцией — ошибка (AL-78)
MACROS = {'ru': ('фильтр', 'отобразить', 'любой', 'все', 'количество', 'первый_где', 'свёртка', 'словарь'),
          'en': ('filter', 'map', 'any', 'all', 'count', 'first_where', 'fold', 'dict')}
RANGE_WORD = {'ru': 'диапазон', 'en': 'range'}  # с 2.19 — оператор `a..b`, слова в файле нет (AL-76)
EVENT_COLUMNS = {'событие', 'event'}  # ячейка события: строки перехода, общие события, «При приёме»
OLD_RESPONSE = re.compile(r'(?:ответ|response):\s*[\w.]+\s*\(')  # прежний образец `ответ: Вар(…)` (AL-77)
OLD_SIGNAL = re.compile(r'(?:сигнал|signal)\(\s*[^(){}"]+?\(')  # прежний сигнал с полями `сигнал(с(…))` (AL-77)
IN_BRACE = re.compile(r'(?<!\w)in\s*\{')  # прежнее множество `in {…}` (AL-79)
IN_LIST = re.compile(r'(?<!\w)in\s*\[')
V219_MSG = {
    'RANGE': 'диапазон пишется `a..b`, вызова `диапазон(…)`/`range(…)` нет (AL-76)',
    'MACRO': 'макрос каталога вызывается методом списка `xs.%s(…)`, а не функцией (AL-78)',
    'IN': 'множество после `in` пишется литералом списка `in […]`, а не `in {…}` (AL-79)',
    'EVENT': 'образец события с полями пишется в фигурных скобках: `ответ: Вар { поле }`, `сигнал(с { поле })` (AL-77)',
    'EMPTY_INS': 'пустая вставка `${}` в текстовом литерале (AL-80)',
    'OPEN_INS': 'незакрытая вставка `${…` в текстовом литерале (AL-80)',
    'SET_INS': 'литерал со вставкой `${…}` — текст, а не значение набора литералов `"a" | "b"` (AL-80)',
    'IN_INS': 'литерал со вставкой `${…}` не стоит в множестве `in […]` (AL-80)',
}


def event_cells(text):
    """Ячейки событий: (номер строки с 0, текст) столбцов «Событие»/«событие» (`Event`/`event`) таблиц вне блоков кода."""
    out, in_code, cols, prev = [], False, [], False
    for n, line in enumerate(text.split('\n')):
        if line.startswith('```'):
            in_code = not in_code
            continue
        is_table = not in_code and line.startswith('|')
        if is_table:
            cells = [c.strip() for c in CELL_PIPE.split(line.strip())[1:-1]]
            if not prev:
                cols = [i for i, c in enumerate(cells) if c.lower() in EVENT_COLUMNS]
            elif not re.match(r'^\|[-:| ]+\|$', line):
                out += [(n, cells[i]) for i in cols if i < len(cells)]
        prev = is_table
    return out


LOOP_HEAD = re.compile(r'(?<!\w)for\s+each\s+\w+\s*$')  # `for each x` перед `in`: слово цикла, а не множество (AL-79)


def loop_in(seg, i):
    """Слово `in` в позиции i — слово цикла `for each <имя> in` (английский файл; в русском у цикла слово `в`)."""
    return LOOP_HEAD.search(seg, 0, i) is not None


def literal_errors(seg, table):
    """Вставки в текстовых литералах участка (AL-80): пустая и незакрытая вставка; литерал со вставкой рядом со знаком
    набора литералов (`|`; в строке таблицы — `\\|`) и внутри `in […]`. Возвращает список (позиция, метка)."""
    errs, spans, i = [], [], 0
    while i < len(seg):
        if seg[i] == '"':
            e = string_end(seg, i, errs)
            if '${' in seg[i:e].replace('\\$', ''):
                spans.append((i, e))
            i = e
            continue
        i += 1
    for a, b in spans:
        after = seg[b:].lstrip()
        before = seg[:a].rstrip()
        if table:
            near = after.startswith('\\|') or before.endswith('\\|')
        else:
            near = after.startswith('|') or before.endswith('|')
        if near:
            errs.append((a, 'SET_INS'))
    for m in IN_LIST.finditer(seg):
        if loop_in(seg, m.start()):
            continue
        x = block_close(seg, m.end() - 1)
        errs += [(a, 'IN_INS') for a, b in spans if m.end() <= a < x]
    return errs


def check_v219(text, name, lang):
    """Прежняя запись до 2.19 и вставки в литералах (AL-76…AL-80): вызов `диапазон(…)`, макрос каталога функцией и `in {`
    в участках кода (`code_segments`); `in {` и прежний образец в ячейке события; вставки — в участках кода и в строках таблиц."""
    found = []  # (номер строки с 0, позиция в участке, участок, метка, слово)
    macros = '|'.join(MACROS[lang])
    call = re.compile(r'(?<![\w.])(%s)\s*\(' % macros)
    rng = re.compile(r'(?<!\w)%s\s*\(' % RANGE_WORD[lang])
    segs = code_segments(text)
    for first, seg in segs:
        outside = set(outside_strings(seg))
        for m in rng.finditer(seg):
            if m.start() in outside:
                found.append((first, m.start(), seg, 'RANGE', ''))
        for m in call.finditer(seg):
            if m.start() in outside:
                found.append((first, m.start(), seg, 'MACRO', m.group(1)))
        for m in IN_BRACE.finditer(seg):
            if m.start() in outside and not loop_in(seg, m.start()):
                found.append((first, m.start(), seg, 'IN', ''))
    for first, cell in event_cells(text):
        outside = set(outside_strings(cell))
        if any(m.start() in outside for m in IN_BRACE.finditer(cell)):
            found.append((first, 0, cell, 'IN', ''))
        if OLD_RESPONSE.search(cell) or OLD_SIGNAL.search(cell):
            found.append((first, 0, cell, 'EVENT', ''))
    lines = text.split('\n')
    lit = [(f, s, False) for f, s in segs if not lines[f].startswith('|')]
    lit += [(n, l, True) for n, l in enumerate(lines) if l.startswith('|') and not re.match(r'^\|[-:| ]+\|\s*$', l)]
    for first, seg, table in lit:
        found += [(first, pos, seg, label, '') for pos, label in literal_errors(seg, table)]
    errs = []
    for first, pos, seg, label, word in found:
        msg = V219_MSG[label] % word if label == 'MACRO' else V219_MSG[label]
        e = '%s:%d: %s' % (name, first + seg.count('\n', 0, pos) + 1, msg)
        if e not in errs:
            errs.append(e)
    return errs


# прежняя альтернатива `выбор` по варианту с полями `Вар(поле, …) =>` (до 2.20, AL-82): имя варианта с заглавной
# (правило регистра, AL-64) или `Тип.Вар`, круглые скобки без вложенных, затем `=>`, `|` (в ячейке `\|`) или страж
OLD_ALT = re.compile(r'(?<![\w.])((?:\w+\.)?[A-ZА-ЯЁ]\w*)\s*\([^()]*\)\s*(?:=>|\\?\||(?:если|if)(?!\w))')
JSON_PARENS = re.compile(r' \([A-Za-z_][A-Za-z0-9_]*\)')  # скобки JSON-имени `имя (X)` (AL-60; их ловит проверка 5)
V220_MSG = {
    'SIG': 'сигнал с полями объявляется в фигурных скобках: `%s { поле Тип, … }`, а не `%s(…)` (AL-82)',
    'ALT': 'альтернатива `выбор` по варианту с полями пишется в фигурных скобках: `%s { поле, поле: имя } =>`, а не `%s(…)` (AL-82)',
}


def check_v220(text, name, lang):
    """Прежняя запись до 2.20 (AL-82): объявление сигнала с полями в круглых скобках в столбце «сигналы» таблицы
    «Сторон» и альтернатива `выбор` по варианту с полями в круглых скобках в участках кода (`code_segments`)."""
    parties = 'Стороны' if lang == 'ru' else 'Parties'
    col = 'сигналы' if lang == 'ru' else 'signals'
    errs, sec, in_code, header = [], None, False, None
    for n, line in enumerate(text.split('\n'), 1):
        if line.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r'^## (\S+)', line)
        if m:
            sec, header = m.group(1), None
            continue
        if not line.startswith('|'):
            header = None
            continue
        if re.match(r'^\|[-:| ]+\|\s*$', line):
            continue
        cells = [c.strip() for c in CELL_PIPE.split(line.strip())[1:-1]]
        if header is None:
            header = cells
            continue
        if sec != parties or col not in header or len(cells) <= header.index(col):
            continue
        for sig in split_top(cells[header.index(col)]):
            m = re.match(r'^([^({]+?)\s*\(', JSON_PARENS.sub('', sig))  # скобка сразу после имени сигнала, не внутри полей
            if m:
                nm = m.group(1).strip()
                errs.append('%s:%d: %s' % (name, n, V220_MSG['SIG'] % (nm, nm)))
    for first, seg in code_segments(text):
        outside = set(outside_strings(seg))
        for m in OLD_ALT.finditer(seg):
            if m.start() in outside:
                e = '%s:%d: %s' % (name, first + seg.count('\n', 0, m.start()) + 1, V220_MSG['ALT'] % (m.group(1), m.group(1)))
                if e not in errs:
                    errs.append(e)
    return errs


DEF_NAME = re.compile(r'^\s*(?:определение|define|definition)\s+([^\s(]+)\s*\(')


def check_calls(text, words, name, lang, gloss):
    """Пространство вызовов (1а, AL-81): имя определения (как написано и английское имя по 1а — словарь или
    транслитерация, `auto_name`) и имя примитива (как написано и JSON-имя, `json_names`) не совпадают со словом функции
    каталога ни в одном языке (вид `catalog` таблицы слов) и с `range` (имя вызова диапазона в дереве, AL-76); имена внутри
    пространства различны (AL-58): определение не совпадает с примитивом реестра (сверяются те же написания)."""
    cat = words['catalog'][0] | words['catalog'][1] | {'range'}
    errs, in_code, defs = [], False, []
    for n, line in enumerate(text.split('\n'), 1):
        if line.startswith('```'):
            in_code = not in_code
            continue
        m = DEF_NAME.match(line) if in_code else None
        if m:
            nm = m.group(1)
            defs.append((n, nm, {nm, auto_name(nm, False, gloss)}))
            hit = sorted(defs[-1][2] & cat)
            if hit:
                errs.append('%s:%d: определение `%s` совпадает с функцией каталога `%s` (пространство вызовов, AL-81)' % (
                    name, n, nm, hit[0]))
    readable = words['readable'][0 if lang == 'ru' else 1]
    prims = []
    for n, where, pascal, nm, path, js in json_names(text, lang, gloss, readable)[0]:
        if where != 'примитива':
            continue
        prims.append((n, nm, {nm, js}))
        hit = sorted({nm, js} & cat)
        if hit:
            errs.append('%s:%d: примитив `%s` совпадает с функцией каталога `%s` (пространство вызовов, AL-81)' % (
                name, n, nm, hit[0]))
    for n, nm, names in defs:
        for pn, pnm, pnames in prims:
            hit = sorted(names & pnames)
            if hit:
                errs.append('%s:%d: определение `%s` совпадает с примитивом реестра `%s` (строка %d) по имени `%s`: в пространстве '
                            'вызовов имена различны (AL-58, AL-81)' % (name, n, nm, pnm, pn, hit[0]))
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
    """Разбор сигнала стороны `имя[ { поля }]`: имя — всё до первой скобки, может быть из нескольких слов (`остановить
    совещание`); прежние поля в круглых скобках `имя(поля)` (до 2.20, AL-82) разбираются так же, ошибку даёт `check_v220`;
    скобки `имя (X)` убраны (AL-60)."""
    m = re.match(r'^(.+?) \(([A-Za-z_][A-Za-z0-9_]*)\)(.*)$', sig)
    if m:
        return m.group(1).strip(), m.group(2), m.group(3).strip()
    nm = re.split(r'[({]', sig)[0].strip()
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
                if (rest.startswith('{') and rest.endswith('}')) or (rest.startswith('(') and rest.endswith(')')):
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
    errs = check_operators(text, name) + check_v219(text, name, lang) + check_v220(text, name, lang) + check_calls(text, words, name, lang, gloss) + check_removed(text, name) + check_json_names(text, words, name, lang, gloss, contract)
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
        ('однострочное тело через `=` (до 2.18)', '-> число =>\n  (1..п)', '-> число = (1..п)'),
        ('вызов `диапазон(…)` (до 2.19)', '(1..п).свёртка(ПАУЗА_ПОВТОРА,', 'диапазон(1, п).свёртка(ПАУЗА_ПОВТОРА,'),
        ('знак `‥` вместо `..`', '(1..п).свёртка(', '(1‥п).свёртка('),
        ('макрос `свёртка` функцией (до 2.19)', '(1..п).свёртка(ПАУЗА_ПОВТОРА, (н, _) => н * 2)', 'свёртка(1..п, ПАУЗА_ПОВТОРА, (н, _) => н * 2)'),
        ('макросы `фильтр` и `количество` функцией в ячейке', '| число_ходов += 1 | ХОД_АГЕНТА |', '| число_ходов += количество(фильтр([1], x => x > 0), x => истина) | ХОД_АГЕНТА |'),
        ('образец ответа в круглых скобках (до 2.19)', 'ответ: Закончен { текст, артефакт, расход: полученный }', 'ответ: Закончен(текст, артефакт, расход: полученный)'),
        ('образец ответа с одним полем в круглых скобках', 'ответ: Обрезан { расход: полученный }', 'ответ: Обрезан(расход: полученный)'),
        ('сигнал с полями в круглых скобках (до 2.19)', '| 1 | сигнал(разрешить) |', '| 1 | сигнал(разрешить(решение: р)) |'),
        ('`in {…}` в ячейке события (до 2.19)', 'сбой(причина in [КодСбоя.СоединениеОборвалось, КодСбоя.НетОтветаВСрок, КодСбоя.НетРезультата])', 'сбой(причина in {КодСбоя.СоединениеОборвалось, КодСбоя.НетОтветаВСрок, КодСбоя.НетРезультата})'),
        ('`in {…}` в `Кроме` (до 2.19)', '- Кроме: остановка in [""]', '- Кроме: остановка in {""}'),
        ('объявление сигнала с полями в круглых скобках (до 2.20)', 'продолжить { слово_человека текст, автор текст, источник текст }', 'продолжить(слово_человека текст, автор текст, источник текст)'),
        ('объявление сигнала с одним полем в круглых скобках', '| разрешить, отказать |', '| разрешить(решение текст), отказать |'),
        ('объявление сигнала с полем-кортежем в круглых скобках', '| разрешить, отказать |', '| разрешить(пара (число, текст)), отказать |'),
        ('альтернатива `выбор` по варианту в круглых скобках (до 2.20)', 'выбор вид_действия { ВидДействия.Удаление |', 'выбор вид_действия { Удаление(вид) |'),
        ('альтернатива `выбор` в круглых скобках перед `=>`', 'ВидДействия.СменаРежима => истина;', 'ВидДействия.СменаРежима => истина; Сеть(адрес: а) => ложь;'),
        ('альтернатива `выбор` в круглых скобках со стражем', 'ВидДействия.СменаРежима => истина;', 'ВидДействия.СменаРежима => истина; ВидДействия.Сеть(адрес) если истина => ложь;'),
        ('альтернатива `выбор` в круглых скобках в ячейке', '| число_ходов += 1 | ХОД_АГЕНТА |', '| число_ходов += выбор ход_до_повтора { Закончен(текст) \\| Обрезан(текст) => 1; иначе => 0 } | ХОД_АГЕНТА |'),
        ('пустая вставка `${}`', '| число_ходов += 1 | ХОД_АГЕНТА |', '| текст_ответа = "ход ${}" | ХОД_АГЕНТА |'),
        ('незакрытая вставка', '| число_ходов += 1 | ХОД_АГЕНТА |', '| текст_ответа = "ход ${число_ходов" | ХОД_АГЕНТА |'),
        ('литерал со вставкой в наборе литералов', '| ход | "first" \\| "retry"', '| ход | "first${число_ходов}" \\| "retry"'),
        ('литерал со вставкой в `in […]`', '- Кроме: остановка in [""]', '- Кроме: остановка in ["${число_ходов}"]'),
        ('определение с английским именем функции каталога по словарю (`добавить` → `concat`)', 'определение пауза_повтора(п число>=0) -> число =>', 'определение добавить(а число) -> число =>\n  а\n\nопределение пауза_повтора(п число>=0) -> число =>'),
        ('определение с именем функции каталога', 'определение пауза_повтора(п число>=0) -> число =>', 'определение склеить(а текст, б текст) -> текст =>\n  а + б\n\nопределение пауза_повтора(п число>=0) -> число =>'),
        ('определение с именем примитива реестра образца', 'определение пауза_повтора(п число>=0) -> число =>', 'определение time_now(а число) -> число =>\n  а\n\nопределение пауза_повтора(п число>=0) -> число =>'),
        ('настоящее множество `in […]` со вставкой в условии', '| число_ходов += 1 | ХОД_АГЕНТА |', '| если остановка in ["a${число_ходов}"] то { число_ходов += 1 } | ХОД_АГЕНТА |'),
        ('ветка с текстовым образцом через `->`', 'ВидДействия.СменаРежима => истина;', 'ВидДействия.СменаРежима => истина; "ask" -> "ask";'),
        ('ветка со стражем через `->`', 'ВидДействия.СменаРежима => истина;', 'ВидДействия.СменаРежима если есть(вид_действия) -> истина;'),
        ('трёхместная лямбда через `->`', '(н, _) => н * 2', '(а, б, в) -> а * 2'),
        ('лямбда через `->` без пробела', '(н, _) => н * 2', '(н, _)-> н * 2'),
        ('многострочный заголовок, тело через `=`', 'пауза_повтора(п число>=0) -> число =>', 'пауза_повтора(\n  п число>=0\n) -> число ='),
        ('`->` на следующей строке, тело через `=`', 'пауза_повтора(п число>=0) -> число =>', 'пауза_повтора(п число>=0)\n  -> число ='),
        ('пробел перед скобкой, тело через `=`', 'пауза_повтора(п число>=0) -> число =>', 'пауза_повтора (п число>=0) -> число ='),
        ('условное действие с ветками в круглых скобках (до 2.18)', 'то { журнал(событие_расхода(собрать_использование(запрос_агента, остановка, расход, начато, сейчас))) };',
         'то (журнал(событие_расхода(собрать_использование(запрос_агента, остановка, расход, начато, сейчас))));'),
        ('условное действие в ячейке с веткой `иначе` в круглых скобках', '| число_ходов += 1 | ХОД_АГЕНТА |', '| если истина то { число_ходов += 1 } иначе (число_ходов += 2) | ХОД_АГЕНТА |'),
        ('условное выражение без блока в `то` (до 2.18)', 'то { (а ?? 0) + (б ?? 0) } иначе { а ?? б }', 'то (а ?? 0) + (б ?? 0) иначе а ?? б'),
        ('условное выражение без блока в `иначе`', 'то { (а ?? 0) + (б ?? 0) } иначе { а ?? б }', 'то { (а ?? 0) + (б ?? 0) } иначе а ?? б'),
        ('многострочное условное выражение, `то` на следующей строке без блока', '  то { пусть п = обязательно(прежний);', '  то (пусть п = обязательно(прежний);'),
        ('условное выражение в ячейке «Концов» без блока', 'то { обязательно(расход).начало_запроса } иначе { пусто }', 'то обязательно(расход).начало_запроса иначе пусто'),
        ('`для каждого` с двоеточием (до 2.18)', '| число_ходов += 1 | ХОД_АГЕНТА |', '| для каждого x в [1]: число_ходов += x | ХОД_АГЕНТА |'),
        ('действие `пусть … в` (до 2.18)', '| число_ходов += 1 | ХОД_АГЕНТА |', '| пусть x = 1 в (число_ходов += x) | ХОД_АГЕНТА |'),
        ('выражение `пусть … в` в ветке (до 2.18)', 'то { пусть п = обязательно(р); (п.токены.вход', 'то { пусть п = обязательно(р) в (п.токены.вход'),
        ('выражение `пусть … в` в теле определения (до 2.18)', '  пусть срок = з.пределы.срок_тишины;', '  пусть срок = з.пределы.срок_тишины в'),
        ('выражение `пусть … в` в ячейке', '| число_ходов += 1 | ХОД_АГЕНТА |', '| число_ходов += (пусть x = 1 в x) | ХОД_АГЕНТА |'),
        ('`для каждого` без блока, тело в круглых скобках', '| число_ходов += 1 | ХОД_АГЕНТА |', '| для каждого x в [1] (число_ходов += x) | ХОД_АГЕНТА |'),
        ('`для каждого` без блока', '| число_ходов += 1 | ХОД_АГЕНТА |', '| для каждого x в [1] число_ходов += x | ХОД_АГЕНТА |'),
        ('`если` с блоком без `то`', '| число_ходов += 1 | ХОД_АГЕНТА |', '| если истина { число_ходов += 1 } | ХОД_АГЕНТА |'),
        ('пустая ветка `иначе { }`', '| число_ходов += 1 | ХОД_АГЕНТА |', '| если истина то { число_ходов += 1 } иначе { } | ХОД_АГЕНТА |'),
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
        ('знак оператора не ASCII', '(1..n).fold(RETRY_PAUSE, (m, _) => m * 2)', '(1..n).fold(RETRY_PAUSE, (m, _) ⇒ m * 2)'),
        ('тело определения через `=` (до 2.18)', 'define retry_pause(n int>=0) -> int =>', 'define retry_pause(n int>=0) -> int ='),
        ('ветка `match` через `->` (до 2.18)', 'ActionKind.SwitchMode => true;', 'ActionKind.SwitchMode -> true;'),
        ('лямбда через `->` (до 2.18)', '(m, _) => m * 2', '(m, _) -> m * 2'),
        ('однострочное тело через `=` (до 2.18)', '-> int =>\n  (1..n)', '-> int = (1..n)'),
        ('вызов `range(…)` (до 2.19)', '(1..n).fold(RETRY_PAUSE,', 'range(1, n).fold(RETRY_PAUSE,'),
        ('знак `‥` вместо `..`', '(1..n).fold(', '(1‥n).fold('),
        ('макрос `fold` функцией (до 2.19)', '(1..n).fold(RETRY_PAUSE, (m, _) => m * 2)', 'fold(1..n, RETRY_PAUSE, (m, _) => m * 2)'),
        ('макросы `filter` и `count` функцией в ячейке', '| turn_count += 1 | AgentTurn |', '| turn_count += count(filter([1], x => x > 0), x => true) | AgentTurn |'),
        ('образец ответа в круглых скобках (до 2.19)', 'response: Finished { text, artifact, transport_usage: received }', 'response: Finished(text, artifact, transport_usage: received)'),
        ('сигнал с полями в круглых скобках (до 2.19)', '| 1 | signal(allow) |', '| 1 | signal(allow(decision: d)) |'),
        ('`in {…}` в ячейке события (до 2.19)', 'failure(reason in [FailCode.ConnectionLost, FailCode.Timeout, FailCode.NoResult])', 'failure(reason in {FailCode.ConnectionLost, FailCode.Timeout, FailCode.NoResult})'),
        ('`in {…}` в `Except` (до 2.19)', '- Except: stop_reason in [""]', '- Except: stop_reason in {""}'),
        ('объявление сигнала с полями в круглых скобках (до 2.20)', 'continue { human_word text, author text, source text }', 'continue(human_word text, author text, source text)'),
        ('объявление сигнала с полем-кортежем в круглых скобках', '| allow, deny |', '| allow(pair (int, text)), deny |'),
        ('альтернатива `match` по варианту в круглых скобках (до 2.20)', 'match action { ActionKind.Delete |', 'match action { Delete(path) |'),
        ('альтернатива `match` в круглых скобках со стражем', 'ActionKind.SwitchMode => true;', 'ActionKind.SwitchMode => true; ActionKind.Network(address) if true => false;'),
        ('пустая вставка `${}`', '| turn_count += 1 | AgentTurn |', '| reply_text = "turn ${}" | AgentTurn |'),
        ('незакрытая вставка', '| turn_count += 1 | AgentTurn |', '| reply_text = "turn ${turn_count" | AgentTurn |'),
        ('литерал со вставкой в наборе литералов', '| turn | "first" \\| "retry"', '| turn | "first${turn_count}" \\| "retry"'),
        ('литерал со вставкой в `in […]`', '- Except: stop_reason in [""]', '- Except: stop_reason in ["${turn_count}"]'),
        ('определение с именем функции каталога `concat`', 'define retry_pause(n int>=0) -> int =>', 'define concat(a int) -> int =>\n  a\n\ndefine retry_pause(n int>=0) -> int =>'),
        ('определение с именем вызова диапазона `range`', 'define retry_pause(n int>=0) -> int =>', 'define range(a int) -> int =>\n  a\n\ndefine retry_pause(n int>=0) -> int =>'),
        ('определение с именем примитива реестра образца', 'define retry_pause(n int>=0) -> int =>', 'define time_now(a int) -> int =>\n  a\n\ndefine retry_pause(n int>=0) -> int =>'),
        ('настоящее множество `in […]` со вставкой в условии', '| turn_count += 1 | AgentTurn |', '| if stop_reason in ["a${turn_count}"] then { turn_count += 1 } | AgentTurn |'),
        ('ветка с текстовым образцом через `->`', 'ActionKind.SwitchMode => true;', 'ActionKind.SwitchMode => true; "ask" -> "ask";'),
        ('ветка со стражем через `->`', 'ActionKind.SwitchMode => true;', 'ActionKind.SwitchMode if has(action) -> true;'),
        ('трёхместная лямбда через `->`', '(m, _) => m * 2', '(a, b, c) -> a * 2'),
        ('лямбда через `->` без пробела', '(m, _) => m * 2', '(m, _)-> m * 2'),
        ('многострочный заголовок, тело через `=`', 'retry_pause(n int>=0) -> int =>', 'retry_pause(\n  n int>=0\n) -> int ='),
        ('`->` на следующей строке, тело через `=`', 'retry_pause(n int>=0) -> int =>', 'retry_pause(n int>=0)\n  -> int ='),
        ('пробел перед скобкой, тело через `=`', 'retry_pause(n int>=0) -> int =>', 'retry_pause (n int>=0) -> int ='),
        ('условное действие с ветками в круглых скобках (до 2.18)', 'then { journal(usage_event(collect_usage(agent_request, stop_reason, transport_usage, started, now))) };',
         'then (journal(usage_event(collect_usage(agent_request, stop_reason, transport_usage, started, now))));'),
        ('условное действие в ячейке с веткой `else` в круглых скобках', '| turn_count += 1 | AgentTurn |', '| if true then { turn_count += 1 } else (turn_count += 2) | AgentTurn |'),
        ('условное выражение без блока в `then` (до 2.18)', 'then { (a ?? 0) + (b ?? 0) } else { a ?? b }', 'then (a ?? 0) + (b ?? 0) else a ?? b'),
        ('условное выражение без блока в `else`', 'then { (a ?? 0) + (b ?? 0) } else { a ?? b }', 'then { (a ?? 0) + (b ?? 0) } else a ?? b'),
        ('`for each` с двоеточием (до 2.18)', '| turn_count += 1 | AgentTurn |', '| for each x in [1]: turn_count += x | AgentTurn |'),
        ('действие `let … in` (до 2.18)', '| turn_count += 1 | AgentTurn |', '| let x = 1 in (turn_count += x) | AgentTurn |'),
        ('выражение `let … in` в ветке (до 2.18)', 'then { let p = require(tu); (p.tokens.input', 'then { let p = require(tu) in (p.tokens.input'),
        ('выражение `let … in` в теле определения (до 2.18)', '  let term = req.limits.silence_term;', '  let term = req.limits.silence_term in'),
        ('выражение `let … in` в ячейке', '| turn_count += 1 | AgentTurn |', '| turn_count += (let x = 1 in x) | AgentTurn |'),
        ('`for each` без блока, тело в круглых скобках', '| turn_count += 1 | AgentTurn |', '| for each x in [1] (turn_count += x) | AgentTurn |'),
        ('`for each` без блока', '| turn_count += 1 | AgentTurn |', '| for each x in [1] turn_count += x | AgentTurn |'),
        ('`if` с блоком без `then`', '| turn_count += 1 | AgentTurn |', '| if true { turn_count += 1 } | AgentTurn |'),
        ('пустая ветка `else { }`', '| turn_count += 1 | AgentTurn |', '| if true then { turn_count += 1 } else { } | AgentTurn |'),
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
        ('однострочное тело через `=>` с `пусть`, `>=` и `==`', '-> число =>\n  (1..п).свёртка(ПАУЗА_ПОВТОРА, (н, _) => н * 2)', '-> число => { пусть к = п >= 0; если к == истина то { (1..п).свёртка(ПАУЗА_ПОВТОРА, (н, _) => н * 2) } иначе { 0 } }'),
        ('вставки в действии и экранированный знак `\\${`', '| число_ходов += 1 | ХОД_АГЕНТА |', '| текст_ответа = "ход ${число_ходов} из ${ЧИСЛО_ПОВТОРОВ}, \\${x}"; число_ходов += 1 | ХОД_АГЕНТА |'),
        ('вложенный литерал со вставкой внутри вставки', '| число_ходов += 1 | ХОД_АГЕНТА |', '| текст_ответа = "${если истина то { "есть ${число_ходов}" } иначе { "нет" }}" | ХОД_АГЕНТА |'),
        ('диапазон и методы макросов в ячейке', '| число_ходов += 1 | ХОД_АГЕНТА |', '| число_ходов += (1..число_ходов + 1).фильтр(x => x > 0).количество(x => истина) | ХОД_АГЕНТА |'),
        ('метод `словарь` на литерале списка и поле записи после точки', '| число_ходов += 1 | ХОД_АГЕНТА |', '| число_ходов += длина([1, 2].словарь(x => x, x => x)) + расход.токены | ХОД_АГЕНТА |'),
        ('литерал без вставки в `in […]`, одиночный знак `$`', '- Кроме: остановка in [""]', '- Кроме: остановка in ["", "$5"]'),
        ('определение с именем, не совпадающим с функцией каталога', 'определение пауза_повтора(п число>=0) -> число =>', 'определение добавить_всё(а число) -> число =>\n  а\n\nопределение пауза_повтора(п число>=0) -> число =>'),
        ('определение с именем, не совпадающим с примитивом', 'определение пауза_повтора(п число>=0) -> число =>', 'определение убрать_несостоятельные_заново(а число) -> число =>\n  а\n\nопределение пауза_повтора(п число>=0) -> число =>'),
        ('`для каждого … в [ … ]` со вставками в элементах', '| число_ходов += 1 | ХОД_АГЕНТА |', '| для каждого x в ["a${число_ходов}", "b"] { число_ходов += 1 } | ХОД_АГЕНТА |'),
        ('многострочный заголовок с `) -> число =>`', 'пауза_повтора(п число>=0) -> число =>', 'пауза_повтора(\n  п число>=0\n) -> число =>'),
        ('`->` на следующей строке', 'пауза_повтора(п число>=0) -> число =>', 'пауза_повтора(п число>=0)\n  -> число =>'),
        ('пробел перед скобкой', 'пауза_повтора(п число>=0) -> число =>', 'пауза_повтора (п число>=0) -> число =>'),
        ('условное действие в ячейке с `иначе { … }`', '| число_ходов += 1 | ХОД_АГЕНТА |', '| если истина то { число_ходов += 1 } иначе { число_ходов += 2; журнал(x) } | ХОД_АГЕНТА |'),
        ('условное выражение с блоками в действии', '| число_ходов += 1 | ХОД_АГЕНТА |', '| число_ходов += если истина то { 1 } иначе { 2 } | ХОД_АГЕНТА |'),
        ('блок действий с `пусть` и `для каждого` с блоком', '| число_ходов += 1 | ХОД_АГЕНТА |', '| { пусть x = 1; для каждого y в [x] { число_ходов += y } } | ХОД_АГЕНТА |'),
        ('блок-выражение в действии и литерал записи в ветке', '| число_ходов += 1 | ХОД_АГЕНТА |', '| число_ходов += { пусть x = 1; x }; запрос_разрешения = если истина то { ЗапросРазрешения { вид_действия: ВидДействия.Сеть } } иначе { пусто } | ХОД_АГЕНТА |'),
        ('проза в столбце «примечание» со словами `если … то`, `для каждого …:`, `пусть … в`', '| вид | ВидВызывающего | вид вызывающего |',
         '| вид | ВидВызывающего | если есть, то сессия агента; для каждого хода: сессия; пусть свободно в цикле |'),
        ('слова в строковом литерале блока', '| число_ходов += 1 | ХОД_АГЕНТА |', '| { пусть s = "если a то b; для каждого x: y; пусть z в w"; число_ходов += 1 } | ХОД_АГЕНТА |'),
        ('страж ветки `выбор` без `то`', 'ВидДействия.СменаРежима => истина;', 'ВидДействия.СменаРежима если истина => истина;'),
        ('альтернатива `выбор` по варианту с полями в фигурных скобках', 'ВидДействия.СменаРежима => истина;', 'ВидДействия.СменаРежима => истина; Сеть { адрес, порт: п } если п > 0 => ложь; Удаление { путь } | Перенос { путь } => ложь;'),
        ('альтернатива в фигурных скобках в ячейке', '| число_ходов += 1 | ХОД_АГЕНТА |', '| число_ходов += выбор ход_до_повтора { Закончен { текст } \\| Обрезан { текст } => 1; иначе => 0 } | ХОД_АГЕНТА |'),
        ('объявление сигнала с одним полем в фигурных скобках', '| разрешить, отказать |', '| разрешить { решение текст }, отказать |'),
        ('объявление сигнала с полем-кортежем', '| разрешить, отказать |', '| разрешить { пара (число, текст) }, отказать |'),
        ('квалифицированная альтернатива `Тип.Вар { … }`', 'ВидДействия.СменаРежима => истина;', 'ВидДействия.СменаРежима => истина; ИтогХода.Закончен { текст } => ложь;'),
    ],
    'en': [
        ('однострочное тело через `=>` с `let`, `>=` и `==`', '-> int =>\n  (1..n).fold(RETRY_PAUSE, (m, _) => m * 2)', '-> int => { let k = n >= 0; if k == true then { (1..n).fold(RETRY_PAUSE, (m, _) => m * 2) } else { 0 } }'),
        ('вставки в действии и экранированный знак `\\${`', '| turn_count += 1 | AgentTurn |', '| reply_text = "turn ${turn_count} of ${RETRIES}, \\${x}"; turn_count += 1 | AgentTurn |'),
        ('вложенный литерал со вставкой внутри вставки', '| turn_count += 1 | AgentTurn |', '| reply_text = "${if true then { "has ${turn_count}" } else { "none" }}" | AgentTurn |'),
        ('диапазон и методы макросов в ячейке', '| turn_count += 1 | AgentTurn |', '| turn_count += (1..turn_count + 1).filter(x => x > 0).count(x => true) | AgentTurn |'),
        ('определение с именем, не совпадающим с функцией каталога', 'define retry_pause(n int>=0) -> int =>', 'define concat_all(a int) -> int =>\n  a\n\ndefine retry_pause(n int>=0) -> int =>'),
        ('определение с именем, не совпадающим с примитивом', 'define retry_pause(n int>=0) -> int =>', 'define time_now_twice(a int) -> int =>\n  a\n\ndefine retry_pause(n int>=0) -> int =>'),
        ('`for each … in [ … ]` со вставками в элементах', '| turn_count += 1 | AgentTurn |', '| for each x in ["a${turn_count}", "b"] { turn_count += [x] } | AgentTurn |'),
        ('многострочный заголовок с `) -> int =>`', 'retry_pause(n int>=0) -> int =>', 'retry_pause(\n  n int>=0\n) -> int =>'),
        ('`->` на следующей строке', 'retry_pause(n int>=0) -> int =>', 'retry_pause(n int>=0)\n  -> int =>'),
        ('пробел перед скобкой', 'retry_pause(n int>=0) -> int =>', 'retry_pause (n int>=0) -> int =>'),
        ('условное действие в ячейке с `else { … }`', '| turn_count += 1 | AgentTurn |', '| if true then { turn_count += 1 } else { turn_count += 2; journal(x) } | AgentTurn |'),
        ('условное выражение с блоками в действии', '| turn_count += 1 | AgentTurn |', '| turn_count += if true then { 1 } else { 2 } | AgentTurn |'),
        ('блок действий с `let` и `for each` с блоком', '| turn_count += 1 | AgentTurn |', '| { let x = 1; for each y in [x] { turn_count += y } } | AgentTurn |'),
        ('блок-выражение в действии', '| turn_count += 1 | AgentTurn |', '| turn_count += { let x = 1; x } | AgentTurn |'),
        ('проза в столбце `note` со словами `if … then`, `for each …:`, `let … in`', '| kind | CallerKind | the caller kind |',
         '| kind | CallerKind | the agent session if any, then reused; for each turn: a session; let free in the loop |'),
        ('слова в строковом литерале блока', '| turn_count += 1 | AgentTurn |', '| { let s = "if a then b; for each x: y; let z in w"; turn_count += 1 } | AgentTurn |'),
        ('страж ветки `match` без `then`', 'ActionKind.SwitchMode => true;', 'ActionKind.SwitchMode if true => true;'),
        ('альтернатива `match` по варианту с полями в фигурных скобках', 'ActionKind.SwitchMode => true;', 'ActionKind.SwitchMode => true; Network { address, port: p } if p > 0 => false;'),
        ('объявление сигнала с одним полем в фигурных скобках', '| allow, deny |', '| allow { decision text }, deny |'),
        ('объявление сигнала с полем-кортежем', '| allow, deny |', '| allow { pair (int, text) }, deny |'),
        ('квалифицированная альтернатива `Type.Var { … }`', 'ActionKind.SwitchMode => true;', 'ActionKind.SwitchMode => true; TurnResult.Finished { text } => false;'),
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
