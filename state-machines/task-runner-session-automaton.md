# Запуск сессии: код автомата

Стейт-машина запуска одной сессии агента — ворота профиля и цены (В2), проверка объёма (ОБЪЁМ, В1), вызов вложенной машины «Шаг агента» (СЕССИЯ), разбор итога сессии (РАЗБОР_ИТОГА) и ворота сбоя (В13), — записанная кодом на Нове как реализация протокола `Автомат` движка [state-machine-engine-automaton.md](state-machine-engine-automaton.md): данные машины, перечисления `Состояние` и `Событие`, переход `перейти(состояние, событие)` как `match`, роли (входы и результаты вызова шага агента и обращений к человеку на воротах), работа операции РАЗБОР_ИТОГА, ответ по концу по контракту машины. Всё общее — конверт запроса и ответа, исполнитель, снимок и хранилище, общие события «стоп/продолжить/отмена», цикл, фиксации — в движке и здесь не повторяется. Нормы — [task-runner.md](../task-runner.md) (словарь, ворота В1, В2, В13, профили запуска, форматы файлов) и [task-sessions.md](../task-sessions.md) (коды сессий). Идентификаторы кода английские, словарь — [state-machine-glossary.md](state-machine-glossary.md); русские имена — в описаниях и комментариях.

**Первоисточник — [task-runner-session-states.md](task-runner-session-states.md)** (машина «Запуск сессии»: таблицы состояний, общие события, «Контракт машины», «Решения при переводе»); правила формы — [state-machine-spec.md](state-machine-spec.md). Этот файл — производная запись того же автомата, не второй источник истины: при расхождении верен первоисточник, этот файл правится вслед за ним. Язык записи — Нова, https://github.com/nv-lang/nova. **Код не компилировался и не проверялся компилятором Нова:** это псевдокод в синтаксисе Нова; соглашения записи, помеченные места (`// псевдокод:`), подтверждённое и неподтверждённое спецификацией — в [state-machine-engine-automaton.md](state-machine-engine-automaton.md), здесь только относящееся к запуску сессии. Опытный статус и отличия от ранее написанной схемы — в шапке первоисточника; раннером эта машина не исполняется (раннер исполняет [task-runner-pseudocode.md](task-runner-pseudocode.md), помеченный устаревшим). Вызывают эту машину верхняя машина раннера — [task-runner-automaton.md](task-runner-automaton.md) (первоисточник — [task-runner-states.md](task-runner-states.md); состояние ЗАПУСК_СЕССИИ) и проверка цикла — [task-runner-review-automaton.md](task-runner-review-automaton.md) (первоисточник — [task-runner-review-states.md](task-runner-review-states.md); то же состояние). Оба вызова идут по контракту вызова движка (`Вызываемое`, эффект `Связь`: запрос уходит как `ЗапросРоли`, ответ приходит сообщением), не прямым вызовом функций; сама машина из состояния СЕССИЯ так же зовёт вложенную машину шага агента — [archive/state-machine-agent-step-automaton.md](archive/state-machine-agent-step-automaton.md) (первоисточник — [archive/state-machine-agent-step-states.md](archive/state-machine-agent-step-states.md)); общие типы (`ИтогСессии`, `Находка`, `Свод`, `ВходЗапускаСессии`, `ИтогЗапускаСессии`, `ЗапросАгента`, `ОтветАгента`, `ВидВызывающего`, `ПрофильАгента`, `ПределыАгента`) объявлены в слое методики — [state-machine-methodology-automaton.md](state-machine-methodology-automaton.md). Имя файла — по `AGENTS.md`, «Вынесенные алгоритмы», форма `automaton`.

## Соглашения записи

1. **Типы и идентификаторы** — по [движку](state-machine-engine-automaton.md), пункты 1–3: английские имена по [словарю](state-machine-glossary.md). Общие типы данных (`ИтогСессии`, `Находка`, `Свод`, `ВходЗапускаСессии`, `ИтогЗапускаСессии`, `ЗапросАгента`, `ОтветАгента`, `ВидВызывающего`, `ПрофильАгента`, `ПределыАгента`) объявлены один раз в слое методики [state-machine-methodology-automaton.md](state-machine-methodology-automaton.md) и подключены здесь; их таблица соответствия именам блока «Типы на Нове» — там же. Вход паузы (`ВходПаузы`) и сигнатуры `объём_запуска`, `остановить_группу_агента` — тоже из слоя; вариант `ВходРоли` для входа паузы — `ВходПаузыРоли`. Собственных типов данных у этой машины нет. Запись автомата `РазборСессии` — итог разбора артефакта сессии для операции РАЗБОР_ИТОГА. **Значения перечислений** с совпадающими именами в разных перечнях (`План`, `Требования`, `Вопрос`, `Готово`) пишутся с именем типа (`ИтогСессии.План`).
2. **Данные события.** Поля варианта события берутся образцом в `match`: `Сбой { причина } => …`; при совпадении имени поля с переменной машины поле переименовывается: `Ответ_сессии { итог_сессии: итог }`. «Сторона события» и идентификатор события — `событие.сторона`, `событие.идентификатор` (конверт `Входящее` движка, правила 13 и 31). Служебные операции переходу даёт `среда` (журнал, слова человека, сигналы вложенным, данные движка `открытые_запросы`, `предыдущее`, `запрос_вызова`).
3. **Строка таблицы — ветка кода.** Перед каждой строкой первоисточника (условие или событие, «Что меняется», «Куда») стоит комментарий `// <СОСТОЯНИЕ> #<номер строки>: …` с её текстом; у обращения в скобках — данные события; порядок строк как в первоисточнике. «Куда» записано как `Куда(<СОСТОЯНИЕ>)`; «запуск заново» — `Заново(<СОСТОЯНИЕ>)`; «Куда: предыдущее» — у ПАУЗЫ в движке (`Куда(@машина.состояние_по_имени(предыдущее))`). Строка «иначе» развилки — последняя ветка, ведёт в `ОШИБКА` через `среда.ошибка_машины(…)`. Строки «Вход», «Выход», «При входе», «Сторона» и одна строка простыми словами на состояние — комментарии `//` у состояния. Общие события (две строки «стоп» и четыре строки «отмена_запроса») записаны в движке (`общие_события`); `общее` машины сводит к ним её события. Состояние ПАУЗА и его четыре строки подключены фрагментом «Пауза» ([state-machine-pause-states.md](state-machine-pause-states.md)): события паузы разбирает движок (`общие_события`), у машины остаются ветка `ПАУЗА => НеЖдёт`, хуки `состояние_паузы`, `причина_остановки_в_паузе`, `состояние_по_имени` и сведение событий паузы в `общее`.
4. **Строки `// псевдокод:`** и перечень подтверждённого спецификацией — в [движке](state-machine-engine-automaton.md), пункт 5. Здесь дополнительно: функции без тела (сигнатуры механики и чтения внешних объектов); алиас `type Окружение alias Среда[…]` (как в машине проверки цикла); импорт `use` общих типов из слоя методики — разрешение вне записи; значения перечислений с именем типа. Неподтверждённое спецификацией Нова, используемое здесь (как и в машине проверки цикла): объявление `module`, `ro` на уровне модуля (константы), `return` внутри `if` в теле функции. Срок бездействия не задан: у обращений этой машины `0` (исполнитель «нет ответа» не порождает).
5. **Уточнения записи автомата сверх первоисточника:** (а) метод `событие_ответа` — метод протокола `Автомат`: отображение результата роли в событие; (б) вложенная сторона — поле `вложенная` описания обращения (`Одна`): у СЕССИИ `true` (вложенная машина шага агента), у остальных обращений `false`; число возвратов ответа не по форме — поле `возвратов_формы`: `0` у всех (форму проверяет и исправляет шаг агента); метод `при_возобновлении` — заглушка (подготовки при возобновлении нет); (в) `ЗапросАгентаРоли` — вариант `ВходРоли` для обращения СЕССИЯ: запрос вложенной машины шага агента (`ЗапросАгента`, его собирает `вход_запроса` по входу СЕССИИ); код сессии — поле `сессия` (Текст); по коду ветвятся запуск сессии, профиль и промпт — механика исполнителя («Реализация на файлах» первоисточника), машина по нему не ветвится (правило 6), суммы по видам сессий не заводятся; (г) `запрос_вызова` — всегда `запрос.идентификатор_запроса` (решение о `""` у верхнего уровня открыто, см. движок, пункт 6); (д) `состояние_по_имени` записано полным `match` по именам обращений; (е) необязательные поля входа вызова (`источник_запуска`, `фаза`, `заход_запуска`) — `Option`: тип входа один на раннер и проверку цикла.
6. **Данные машины — поля типа `Машина`**: поля названы как переменные раздела «Данные» первоисточника (правило 25), начальные значения — в `Машина.new()`, по входу запуска — `Машина.из_входа` (код сессии, источник, фаза, номер захода и задание приходят в запросе). Данные движка (конверт, очереди запросов, журнал, слова человека, тексты сбоев) — в `СостояниеДвижка` движка. Внешние объекты: `свод` и `находки_проверки` — поля (их пишет операция РАЗБОР_ИТОГА в `выполнить_операцию`, правило 29), остальные читаются через `Объекты` (`объём_запуска()`). **Именование читателей по ключу:** читатель элемента поля называется по полю (`@свод(номер)`, `@находки_проверки(номер)`). **Поле и метод с одним именем** (`свод`, `находки_проверки`) — сознательное решение: в Нове допустимо (`spec/decisions/03-syntax.md`, правило `@name`), правило 25 соблюдено (имя одной сущности одно).
7. **`недостижимо(текст)`** (определено в движке, пункт 8): в реализации стоит: у концов КОНЕЦ, ОСТАНОВЛЕНО, ОШИБКА в `перейти` (переходов нет); в `ответ_по_концу` (значение `остановка` вне таблицы; ответ не из конца; итог сессии пуст в КОНЦЕ); в `выполнить_операцию` (состояние без операции); в `вход_запроса` и `следующая_попытка` (состояние не обращение; сторона вне «шаг_агента», «вратарь», «человек»); в `состояние_по_имени`, `сторона_обращения` (имя вне перечня).

Соответствие типов и полей (общие типы данных — таблица в [state-machine-methodology-automaton.md](state-machine-methodology-automaton.md); здесь только добавленное и принятое из других файлов):

| Первоисточник | Русское имя (описания, таблицы) | Код и блок «Типы на Нове» (латиница) |
|---|---|---|
| Число, Текст | `int`, `str` | `int`, `str` (стандартные имена Нова) |
| Свод, ВходЗапускаСессии, ИтогЗапускаСессии, ИтогСессии, Находка | те же имена, объявлены в [state-machine-methodology-automaton.md](state-machine-methodology-automaton.md) | `Summary`, `SessionLaunchInput`, `SessionLaunchResult`, `SessionResult`, `Finding` (значения — там же) |
| ЗапросАгента, ОтветАгента, ВидВызывающего, ПрофильАгента, ПределыАгента | те же имена, объявлены в [state-machine-methodology-automaton.md](state-machine-methodology-automaton.md) | `AgentRequest`, `AgentReply`, `CallerKind`, `AgentProfile`, `AgentLimits` (поля — там же) |
| Запрос: идентификатор_запроса, номер_попытки, сторона, вход, срок_бездействия, трасса, номер_шага | `Запрос[Вход]`: `идентификатор_запроса`, `номер_попытки`, `сторона`, `вход`, `срок_бездействия`, `трасса`, `номер_шага` | `Request[T]`: `id`, `attempt`, `party`, `input`, `idle_term`, `trace`, `step` |
| Ответ (с результатом): запрос, сторона, результат, трасса, номер_шага | `ОтветСРезультатом[Результат]`: `запрос`, `сторона`, `результат`, `трасса`, `номер_шага` | `Reply[R]`: `request`, `party`, `result`, `trace`, `step` |
| Ответ (отказ): запрос, сторона, причина, текст, трасса, номер_шага | `ОтветОтказ`: `запрос`, `сторона`, `причина`, `текст`, `трасса`, `номер_шага` | `Rejection`: `request`, `party`, `reason`, `text`, `trace`, `step` |
| Ответ: с результатом, отказ | `Исход[Результат]`: `СРезультатом(ОтветСРезультатом[Результат])`, `Отказ(ОтветОтказ)` | `Response[R]`: `Answer(Reply[R])`, `Refusal(Rejection)` |
| КодСбоя: нет результата, отказ модели, соединение оборвалось, форма не исправлена, нет ответа в срок, остановлено человеком, потолок заходов с открытыми находками, отменено родителем, предел токенов, предел запросов хода | `КодСбоя`: `НетРезультата`, `ОтказМодели`, `СоединениеОборвалось`, `ФормаНеИсправлена`, `НетОтветаВСрок`, `ОстановленоЧеловеком`, `ПотолокЗаходов`, `ОтмененоРодителем`, `ПредельТокенов`, `ПредельЗапросовХода` | `FailCode`: `NoResult`, `ModelRefused`, `ConnectionLost`, `FormNotFixed`, `Timeout`, `StoppedByHuman`, `CeilingReached`, `Cancelled`, `MaxTokens`, `MaxTurnRequests` |
| Записи автомата (не из первоисточника): состояние, событие, вид состояния, сообщение, входящее событие, переход | `Состояние`, `Событие`, `Вид`, `Сообщение`, `Входящее`, `РезультатРоли`, `ВходРоли`, `ОшибкаХранилища`, `Переход`: `Куда`, `Заново`, `Остаться`, `НеЖдёт` | `State`, `Event`, `Kind`, `Incoming`, `Transition`: `Go`, `Rerun`, `Stay`, `NotAwaited`; `RoleResult`, `RoleInput` — запись автомата; `Message`, `StoreError` — типы движка; `SessionParsing` — запись автомата; в блоке «Типы на Нове» их нет |
| Функции записи автомата: функция переходов, недостижимая ветка | `перейти`, `недостижимо` | `step`, `unreachable` |
| Параметры типов: вход запроса, результат роли | `Вход`, `Результат` | `T`, `R` |

Имена, которых нет в первоисточнике и которые завела запись автомата (не данные машины): `РезультатРоли`, `ВходРоли`, `Окружение`, `Необратимое`, варианты `Событие` с префиксом ворот (`В13_повторить`, …; один вариант на слово ворот строки первоисточника), `Ответ_сессии`, `Сразу_РАЗБОР_ИТОГА`, `Машина.из_входа`, методы машины для протокола `Автомат` (`начальное`, `общее`, `обращение`, `следующая_попытка`, `событие_ответа` и др.), функции раздела «Механика машины» (`слово_итога`, `свод_запуска`, `находки_запуска`, `профиль_запуска`, `контекст_сессии`, `разобрать_артефакт_сессии`, `трасса_вызова`, `номер_шага_вызова`). Типы и функции движка (`Исполнитель`, `Снимок`, `Хранилище`, `Автомат`, `Среда`, `Входящее`, `Переход`, `Куда`, `Заново`, `Остаться`, `НеЖдёт`, `перейти` и др.) — в [state-machine-engine-automaton.md](state-machine-engine-automaton.md).

## Типы

```nova
module session_launch

// псевдокод: общие типы и сигнатуры операций из слоя методики; импорт модулей — вне записи (соглашения, п. 4)
use methodology.{Finding, SessionResult, Summary, SessionLaunchInput, SessionLaunchResult, CallerKind, AgentProfile, AgentLimits, AgentRequest, AgentReply, PauseInput, launch_scope, stop_agent_group}

/// Запись автомата: итог разбора артефакта сессии (операция РАЗБОР_ИТОГА): итог сессии; свод и находки захода — только у сессий проверки
type SessionParsing { result SessionResult, summary Option[Summary], findings Option[[]Finding] }

/// Запись автомата: результат роли — по варианту на обращение первоисточника, где сторона возвращает результат (раздел «Состояния»: Выход);
/// у ворот человека результата роли нет: слово человека приходит событием, а не исходом запроса.
type RoleResult enum
  | AgentStepOutcome(AgentReply)                  // СЕССИЯ: ответ_агента (ответ вложенной машины «Шаг агента»)

/// Запись автомата: вход запроса — по варианту на обращение первоисточника; поля — строки таблицы «Вход» состояния, читаемые стороной
/// (у ворот без столбца «Кто читает» — вся таблица); необязательное поле — Option. Режим «показывать и продолжать» (исход по умолчанию даёт исполнитель) — на стороне исполнителя.
type RoleInput enum
  | RoleAgentRequest(AgentRequest)                                                                                            // СЕССИЯ (вложенная машина «Шаг агента»); остальные строки «Вход» СЕССИИ исполнитель подставляет в `контекст`
  | Gate2Input { session str, phase Option[str] }                                                                                   // В2
  | Gate1Input { session str }                                                                                                     // В1
  | Gate13SessionInput { session str, refusal_text str }                                                                                              // В13_СЕССИЯ
  | RolePauseInput(PauseInput)                                                                                                  // ПАУЗА

/// Необратимое действие во внешнем мире: последний этап фиксации, повторяемый без вреда (правило 13).
type Irreversible enum
  | StopAgentGroup        // ОСТАНОВЛЕНО, ОШИБКА: группа процессов агента останавливается целиком, проверяется, что в ней не осталось процессов

/// Окружение перехода запуска сессии: `Среда` движка с типами запуска.
type MachineEnvironment alias Environment[State, Event, Irreversible]
```

## Данные

```nova
/// Предел одновременных запросов: у запуска запрос один (правило 21); движку отдаёт метод `предел_запросов`
// псевдокод: `ro` на уровне модуля — не подтверждено спецификацией Нова
ro REQUEST_LIMIT int = 1

/// Срок бездействия обращений запуска не задан (task-runner.md, «Срок бездействия роли»): `0`, исполнитель «нет ответа» не порождает;
/// шагу агента запуск сессии передаёт срок тишины `нет` и бюджеты `нет` (решение 12 первоисточника)
ro IDLE_TERM int = 0

/// Машина запуска сессии: данные запуска в одной записи (раздел «Данные» первоисточника); поля названы как переменные первоисточника.
/// Машина — данные и логика запуска: методы этого типа с ресивером `@` читают и пишут только эти поля; данные движка и служебные операции — через `среда`.
/// Машина реализует `Автомат[Состояние, Событие, ВходЗапускаСессии, ИтогЗапускаСессии, ВходРоли, РезультатРоли, Необратимое]` структурно.
type MachineData {
  // Переменные машины (состояние машины); сохраняются целиком вместе со снимком (правило 22); данные движка (конверт, очереди запросов, журнал) — в `СостояниеДвижка`
  session str,                                  // код запускаемой сессии; из запроса вызова, не меняется
  launch_source str,                        // источник правок для запускаемой сессии; `""` — источника нет; из запроса вызова, не меняется
  launch_pass Option[int],                   // номер захода сессии проверки цикла; None у вызова из раннера; из запроса вызова, не меняется
  phase Option[str],                            // фаза цикла задачи для профиля; None у вызова из проверки цикла; из запроса вызова, не меняется
  route str,                                 // маршрут задачи: у быстрого хвост промптов получает строку про постановку вместо plan.md; из запроса вызова, не меняется
  source_list Option[str],             // перечень источников из постановки (быстрый маршрут): читать только его и то, что нужно для правки; None — перечня нет; из запроса вызова, не меняется
  delivery_short bool,                            // сжата ли сдача: подставляется в промпты С7, С7п и С8; из запроса вызова, не меняется
  agent_reply Option[AgentReply],            // ответ вложенной машины «Шаг агента»: текст или артефакт сессии и запись расхода; None — ответа ещё не было
  result Option[SessionResult],              // чем кончилась сессия; None — сессия ещё не кончалась
  stop_reason str,                               // почему запуск останавливается: исход ворот
  refusal_text str,                            // текст отказа вложенной машины «Шаг агента»; показывается человеку у В13; на ветвление не влияет (решение 15 первоисточника)
  step_attempt int,                            // счётчики попыток одноадресных обращений: к вложенной машине «Шаг агента», к вратарю, к усиленному вратарю (правило 15)
  gatekeeper_attempt int,
  enhanced_attempt int,
  // Внешние объекты (хранилище и задание): пишет операция РАЗБОР_ИТОГА при входе (правило 29); роль и переходы их не пишут
  summary HashMap[int, Summary],                     // [заход_запуска]; итоговая строка файла проверки захода; в заходе без неё итога нет (записи нет)
  findings HashMap[int, []Finding],    // [заход_запуска]; находки файла проверки захода; данные прежних заходов не смешиваются
  // Задание и вход вызова: из запроса, не меняются
  task_dir str,
  repo_dir str,
  delivery_mode str,
}

/// Начальные значения данных машины — раздел «Данные» первоисточника; поля «из запроса» заполняет `Машина.из_входа`.
fn MachineData.new() -> MachineData => {
  session: "",
  launch_source: "",
  launch_pass: None,
  phase: None,
  route: "",
  source_list: None,
  delivery_short: false,
  agent_reply: None,
  result: None,
  stop_reason: "",
  refusal_text: "",
  step_attempt: 0,
  gatekeeper_attempt: 0,
  enhanced_attempt: 0,
  summary: HashMap[int, Summary].new(),
  findings: HashMap[int, []Finding].new(),
  task_dir: "",
  repo_dir: "",
  delivery_mode: "",
}

/// Машина по входу запуска: код сессии, источник правок, фаза, номер захода, маршрут, перечень источников, сдача_сжата и задание.
fn MachineData.from_input(input SessionLaunchInput) -> MachineData {
  mut machine = MachineData.new()
  machine.session = input.session
  machine.launch_source = input.launch_source ?? ""
  machine.launch_pass = input.launch_pass
  machine.phase = input.phase
  machine.route = input.route
  machine.source_list = input.source_list
  machine.delivery_short = input.delivery_short
  machine.task_dir = input.task_dir
  machine.repo_dir = input.repo_dir
  machine.delivery_mode = input.delivery_mode
  machine
}
```

## Инварианты

```nova
// 1. Шаг повышенного внимания: решает человек (по умолчанию) или агент по настройке проекта «исполнитель шагов повышенного внимания» (`исполнитель_повышенного_внимания`); ворота В14, В15, В5, В10а–г, В12, продолжение после «стоп человека» и решения закрытого списка раздела 4 — дорогие: их решает человек (по умолчанию) или усиленный вратарь — только по разрешению владельца в настройке проекта `усиленный_вратарь` (по умолчанию «нет») и с усиленными требованиями (`methodology.md`, раздел 18, «Вратарь»). Повышенное внимание — свойство шага: решение требует осознанного выбора и записи основания; основание пишется всегда, а в журнале — кто решил на самом деле (`решил`: «человек» или «агент») — на воротах В1, В2, В13, ПАУЗА, а сигналом «стоп человека» — в любой момент; исполнитель считает, переключает состояния
//    и пишет журнал. Исключение — ворота В2, которые человек перевёл в режим «показывать и продолжать»: исход по умолчанию даёт исполнитель и пишет его в журнал.
//    В коде: события ворот приходят от стороны «вратарь» (ворота, на которые вправе ответить вратарь) или «усиленный» (дорогие ворота и ПАУЗА: отвечает усиленный вратарь по разрешению, иначе человек) — имя роли ворот, кто исполняет её на деле, пишет `решил` (у вызванной машины в ПАУЗЕ — «от родителя»); перейти их не порождает.
//    Не убывающих счётчиков у запуска сессии нет: метка инварианта движка пуста.
```

## Состояния

```nova
type State enum
  // развилки
  | Scope
  // операции
  | ResultParsing
  // обращения
  | Gate2 | Gate1 | Session | Gate13Session | Pause
  // концы
  | End | Halted | Errored

/// Начальное состояние — В2. Вид состояния (обращение, операция, развилка, конец) по первоисточнику, раздел «Состояния».
fn MachineData @kind(state State) -> Kind => match state {
  Gate2 | Gate1 | Session | Gate13Session | Pause => Appeal
  ResultParsing => Operation
  Scope => Fork
  End | Halted | Errored => Final
}

/// Имя состояния — текст для переменной «предыдущее» и журнала (правило 24).
fn MachineData @state_name(state State) -> str => match state {
  Gate2 => "Gate2"
  Scope => "Scope"
  Gate1 => "Gate1"
  Session => "Session"
  ResultParsing => "ResultParsing"
  Gate13Session => "Gate13Session"
  Pause => "Pause"
  End => "End"
  Halted => "Halted"
  Errored => "Errored"
}

/// «Куда: предыдущее» (правило 24): значение переменной — имя состояния-обращения, не конца и не ПАУЗЫ.
fn MachineData @state_by_name(name str) -> State => match name {
  "Gate2" => Gate2
  "Gate1" => Gate1
  "Session" => Session
  "Gate13Session" => Gate13Session
  _ => unreachable(""previous" holds the name of an appeal state, not of an end or Pause (rule 24)")
}

/// Сторона обращения: «шаг_агента» (СЕССИЯ, вложенная машина «Шаг агента»), «вратарь» (ворота В2, В1, В13_СЕССИЯ: человек по умолчанию, агент по настройке) или «усиленный» (ПАУЗА).
fn appeal_party(appeal State) -> str => match appeal {
  Session => "agent_step"
  Gate2 | Gate1 | Gate13Session => "gatekeeper"
  Pause => "enhanced"
  _ => unreachable("only appeals have a party")
}
```

## События

```nova
type Event enum
  // общие события: разбираются до строк состояний (раздел «Общие события» первоисточника, движок)
  | StopFromHuman { human_word str, author str, source str }
  | StopFromParent { id str }
  | CancelRequest { id str }
  // исходы запроса стороны (правила 16, 26); у каждого есть событие.сторона
  | SessionReplied { agent_reply AgentReply }     // СЕССИЯ: «ответ»
  | Failure { reason FailCode, refusal_text str }                       // «сбой»
  // исход операции (операция с данными одна: РАЗБОР_ИТОГА; «сразу» у развилки — событие без данных)
  | Immediate                                          // «сразу»
  | ImmediateResultParsing { result SessionResult }  // «сразу» с данными РАЗБОРА_ИТОГА
  // слова ворот человека (одно слово у нескольких ворот — один вариант)
  | Gate13Repeat                                  // В13_СЕССИЯ: «В13: «повторить»»
  | Gate13Halt                                 // В13_СЕССИЯ: «В13: «остановить»»
  | Gate2Confirm                                 // «В2: «подтвердить»»
  | Gate1Repeat                                   // «В1: «повторить»»
  | Gate1Halt                                  // «В1: «остановить»»
  | PauseWordContinue { human_word str, author str, source str }   // «ПАУЗА: «продолжить»»
  | PauseWordHalt                               // «ПАУЗА: «остановить»»
  | PauseWordContinueFromParent { id str }          // «ПАУЗА: «продолжить от родителя»»
  | PauseWordHaltFromParent { id str }         // «ПАУЗА: «остановить от родителя»»
```

## Механика машины

```nova
// Раздел записывает механику запуска сессии: свободные функции и методы `Машина`; методы `Исполнитель` и общие функции — в движке.
// псевдокод: функции без тела — сигнатуры; тело пишет реализация, в Нове внешняя реализация здесь не показана

// Свободные функции: механика запуска (служебные хранилища и объекты задачи; запрос к шагу агента)
// вид диалога: «сдача» для С7, С7п, С8, КОММИТ, ПУШ, иначе «основной» (по нему шаг агента проверяет кеш)
fn session_dialog_kind(session str) -> str => match session {
  "s7" | "s7_fix" | "s8" | "commit" | "push" => "delivery"
  _ => "main"
}
// профиль запуска, подтверждённый у В2 (выбор по умолчаниям фазы и подсказке; служебное хранилище)
fn launch_profile(session str) Objects -> AgentProfile
// контекст запроса: промпт сессии с подстановками (`<источник правок>`, `<способ сдачи>`, `<папка задачи>`, `<репозиторий>`, `<перечень источников>`, `<ветка из plan.md>`),
// строкой быстрого маршрута и строкой сжатой сдачи, и диалог (новый или ход живого диалога автора); `план_задачи` исполнитель читает сам
fn session_context(session str, source Option[str], launch_pass Option[int], delivery_mode str, task_dir str, repo_dir str, route str, source_list Option[str], delivery_short bool) Objects -> str
// разбор артефакта сессии из ответа агента: слово остановки последнего абзаца — итог; у сессий проверки — итоговая строка и находки захода (task-runner.md, «Машинные форматы»)
fn parse_session_artifact(session str, response AgentReply) Objects -> SessionParsing
// конверт этой машины для запроса агента: трасса и номер шага (`Среда` их не отдаёт: «Что движок не покрыл», пункт 12)
fn call_trace(environment MachineEnvironment) -> str
fn call_step(environment MachineEnvironment) -> int

// слово итога сессии — для журнала
fn outcome_word(outcome SessionResult) -> str => match outcome {
  SessionResult.Done => "done"
  SessionResult.Revision => "revision"
  SessionResult.Plan => "plan"
  SessionResult.Requirements => "requirements"
  SessionResult.Question => "question"
}

// Методы Машины: данные автомата
// свод[номер]; None, пока итоговой строки нет
fn MachineData @summary(pass_number int) -> Option[Summary] => @summary.get(pass_number)
// находки_проверки[номер]; None, пока файла проверки захода нет
fn MachineData @findings(pass_number int) -> Option[[]Finding] => @findings.get(pass_number)
// свод[заход_запуска]; None, пока итоговой строки нет или у вызова нет номера захода (раннер)
fn MachineData @launch_summary() -> Option[Summary] => match @launch_pass {
  Some(pass_number) => @summary(pass_number)
  None => None
}
// находки_проверки[заход_запуска]; None, пока файла проверки захода нет или у вызова нет номера захода (раннер)
fn MachineData @launch_findings() -> Option[[]Finding] => match @launch_pass {
  Some(pass_number) => @findings(pass_number)
  None => None
}
// запись для диагностики: все переменные и хранилища (Вход ОШИБКИ)
fn MachineData mut @journal_machine_data(environment MachineEnvironment) Journal Time -> ()

// Методы Машины для движка (протокол `Автомат`): состояния и события машины
fn MachineData @initial() -> State => Gate2
fn MachineData @pause_state() -> State => Pause
// значение «остановка» при «остановить» у ПАУЗЫ: «ПАУЗА: <слово остановки>»; слово остановки — параметр подключения фрагмента «Пауза» (раздел «Общие события» первоисточника), значение есть в таблице «конец → ответ»
fn MachineData @pause_stop_reason() -> str => "pause_halt"
fn MachineData @halted_state() -> State => Halted
fn MachineData @error_state() -> State => Errored
fn MachineData @immediate_event() -> Event => Immediate
// псевдокод: движок передаёт только код (`событие_сбоя(причина)`), текст отказа остаётся пустым, пока движок не понесёт его («Что движок не покрыл», пункт 13)
fn MachineData @failure_event(reason FailCode) -> Event => Failure { reason, refusal_text: "" }
// метка инварианта: не убывающих счётчиков у запуска сессии нет, компонентов нет (движок сравнивает покомпонентно после каждого перехода шага)
fn MachineData @invariant_mark() -> []int => []int.new()
// «остановка» — причина остановки запуска; пишут общие события движка и строки состояний
fn MachineData mut @record_stop(reason str) {
  @stop_reason = reason
}
// общие события: события машины, которые движок разбирает до строк состояний
fn MachineData @common(current State, event_body Event) -> Option[CommonEvent] => match event_body {
  StopFromHuman { human_word, author, source } => Some(HumanStop { human_word, author, source })
  StopFromParent { id } => Some(ParentStop { id })
  CancelRequest { id } => Some(RequestCancelled { id })
  PauseWordContinue { human_word, author, source } => Some(PauseContinue { human_word, author, source })
  PauseWordHalt => Some(PauseHalt)
  PauseWordContinueFromParent { id } => Some(PauseContinueFromParent { id })
  PauseWordHaltFromParent { id } => Some(PauseHaltFromParent { id })
  _ => None
}
// как состояние-обращение обращается к сторонам: у запуска всегда одна сторона (шаг агента или человек), срок бездействия не задан
fn MachineData @appeal(current State) -> Option[AppealDescription] => match @kind(current) {
  Appeal => Some(Single {
    party: appeal_party(current), idle_term: IDLE_TERM,
    nested: current == Session,                                  // вложенная машина одна — «Шаг агента» (СЕССИЯ): ей идут сигналы «стоп/продолжить/остановить/отмена»; вратарь и человек — стороны запросов
    form_returns: 0 })                                          // форму проверяет и исправляет шаг агента (один ход «исправь форму файла»); у запуска сессии возвратов нет
  _ => None
}
// номер новой попытки одноадресной стороны: счётчик попыток (правило 15)
fn MachineData mut @next_attempt(party str) -> int => match party {
  "agent_step" => {
    @step_attempt += 1
    @step_attempt
  }
  "gatekeeper" => {
    @gatekeeper_attempt += 1
    @gatekeeper_attempt
  }
  "enhanced" => {
    @enhanced_attempt += 1
    @enhanced_attempt
  }
  _ => unreachable("party outside "agent_step", "gatekeeper", "enhanced"")
}
// рабочей копии попытки нет: агент правит файлы задачи сразу, проверка «объект не менялся с начала попытки» не применяется
fn MachineData @object_changed_since_attempt(current State) Objects -> bool => false
// принимать файл попытки нечего (см. выше): повторяемо без вреда
fn MachineData mut @accept_attempt_file(id str) Objects -> () => ()
// последний, повторяемый без вреда этап: остановка группы процессов агента (правило 13)
fn MachineData mut @execute(action Irreversible) Objects -> () => match action {
  StopAgentGroup => object_ok(stop_agent_group(), "остановить группу процессов агента не удалось")
}
// предел одновременных запросов: у запуска один (правило 21)
fn MachineData @request_limit() -> int => REQUEST_LIMIT
// вход, результат и событие стороны — в строку и обратно: через `Связь` ходят конкретные типы, а не типы машины
fn MachineData @encode_input(input RoleInput) -> PartyInput
fn MachineData @decode_result(result PartyResult) -> RoleResult
fn MachineData @decode_event(event PartyEvent) -> Event
fn MachineData @encode_output(output SessionLaunchResult) -> PartyOutput
// данные машины в строку снимка и обратно; формат — за реализацией хранилища
fn MachineData @capture() -> str
fn MachineData mut @restore(data str)
// подготовки при возобновлении у запуска сессии нет: сохранённое состояние входится сразу
fn MachineData mut @on_resume(saved State, environment MachineEnvironment) Journal Objects Time -> Option[Transition[State]] => None
// событие с данными по результату принятого ответа роли (метод протокола `Автомат`)
fn MachineData @reply_event(current State, role_result RoleResult) -> Event => match role_result {
  AgentStepOutcome(response) => SessionReplied { agent_reply: response }
}

/// Вход запроса по таблице «Вход» обращения: строки «сторона» (и вся таблица ворот); строки «исполнитель» в запрос не входят.
fn MachineData @request_input(appeal State, party str, environment MachineEnvironment) Objects -> RoleInput => match appeal {
  Session => RoleAgentRequest(AgentRequest {
    kind: CallerKind.CycleSession, profile: launch_profile(@session), session: @session, dialog_kind: session_dialog_kind(@session),
    context: session_context(
      @session, if @launch_source == "" { None } else { Some(@launch_source) }, @launch_pass, @delivery_mode, @task_dir, @repo_dir,
      @route, @source_list, @delivery_short),
    limits: AgentLimits { silence_term: None, token_budget: None, cost_budget: None, turn_limit: None },     // решение 12 первоисточника
    trace: call_trace(environment), step: call_step(environment) })
  Gate2 => Gate2Input { session: @session, phase: @phase }
  Gate1 => Gate1Input { session: @session }
  Gate13Session => Gate13SessionInput { session: @session, refusal_text: @refusal_text }
  Pause => RolePauseInput(PauseInput { previous: environment.previous(), call_request_id: environment.call_request_id() })
  _ => unreachable("only appeals build a request input")
}
```

## Переходы

```nova
/// Переход по событию. тело_события — событие, которое ждёт состояние `текущее` (у развилки — Сразу без данных);
/// событие — исходное событие шага: его данные (сторона, идентификатор, тело) доступны всей цепочке до ближайшего обращения (правило 13).
/// Состояние пишется при фиксации; в «Что меняется» оно не повторяется.
fn MachineData mut @step(current State, event_body Event, event Incoming[Event], environment MachineEnvironment) Journal Objects Time -> Transition[State] {
  match current {

  // ===================== В2 — обращение =====================
  Gate2 => match event_body {
    // В2 #1: В2: «подтвердить»
    Gate2Confirm => Go(Scope)
    _ => NotAwaited
  }

  // ===================== ОБЪЁМ — развилка =====================
  Scope => {
    // ОБЪЁМ #1: объём_запуска = «помещается»
    if launch_scope() == "fits" { return Go(Session) }
    // ОБЪЁМ #2: объём_запуска = «не помещается»
    if launch_scope() == "does_not_fit" { return Go(Gate1) }
    // ОБЪЁМ #3: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "Scope")]))
  }

  // ===================== В1 — обращение =====================
  Gate1 => match event_body {
    // В1 #1: В1: «повторить»
    Gate1Repeat => Go(Gate2)
    // В1 #2: В1: «остановить»
    Gate1Halt => {
      @stop_reason = "gate1_halt"
      Go(Halted)
    }
    _ => NotAwaited
  }

  // ===================== СЕССИЯ — обращение =====================
  // Запись автомата: событие «ответ» несёт ответ шага агента (`Ответ_сессии`); итог сессии, свод и находки захода читает следующая операция РАЗБОР_ИТОГА.
  Session => match event_body {
    // СЕССИЯ #1: ответ (ответ_агента: ОтветАгента — текст или артефакт сессии и запись расхода)
    SessionReplied { agent_reply: response } => {
      @agent_reply = Some(response)
      Go(ResultParsing)
    }
    // СЕССИЯ #2: сбой (причина: КодСбоя)
    Failure { reason, refusal_text: text } => {
      @refusal_text = text
      environment.write_journal(journal_event("session_not_finished", [param("session", "${@session}"), param("reason", "${fail_code_word(reason)}")]))
      Go(Gate13Session)
    }
    _ => NotAwaited
  }

  // ===================== РАЗБОР_ИТОГА — операция =====================
  ResultParsing => match event_body {
    // РАЗБОР_ИТОГА #1: сразу (итог_сессии: ИтогСессии — готово, ревизия, план, требования или вопрос)
    ImmediateResultParsing { result: outcome } => {
      @result = Some(outcome)
      Go(End)
    }
    _ => NotAwaited
  }

  // ===================== В13_СЕССИЯ — обращение =====================
  Gate13Session => match event_body {
    // В13_СЕССИЯ #1: В13: «повторить»
    Gate13Repeat => Rerun(Session)
    // В13_СЕССИЯ #2: В13: «остановить»
    Gate13Halt => {
      @stop_reason = "gate13_halt"
      Go(Halted)
    }
    _ => NotAwaited
  }

  // ===================== ПАУЗА — обращение =====================
  // Подключено фрагментом «Пауза» (state-machine-pause-states.md): события ПАУЗЫ разбирает движок (`общие_события`), строк состояния у машины нет;
  //   остальные события ПАУЗА не ждёт.
  Pause => NotAwaited

  // ===================== КОНЕЦ — конец =====================
  End => unreachable("end state: no transitions; the work on entry is in "Ends and reply"")

  // ===================== ОСТАНОВЛЕНО — конец =====================
  Halted => unreachable("end state: no transitions; the work on entry is in "Ends and reply"")

  // ===================== ОШИБКА — конец =====================
  Errored => unreachable("end state: no transitions; the work on entry is in "Ends and reply"")

  }
}
```

## Работа операций

```nova
/// Работа операций при входе (в одном шаге с переходом; отказа и «нет ответа» у операции нет). Результат — событие: `Сразу_РАЗБОР_ИТОГА` с данными.
fn MachineData mut @run_operation(operation State, environment MachineEnvironment) Journal Objects Time -> Event => match operation {
  ResultParsing => {
    // слово остановки — итог; у сессий проверки итоговая строка и находки захода пишутся в хранилище (правило 29)
    ro parsing = parse_session_artifact(@session, required(@agent_reply, "ResultParsing: the agent reply is recorded in Session"))
    match parsing.summary {
      Some(found_item) => { @summary.insert(required(@launch_pass, "ResultParsing: the summary line arrives only for review sessions, which have a pass number"), found_item) }
      None => {}                                        // итога нет: записи в `свод` нет
    }
    match parsing.findings {
      Some(found_items) => { @findings.insert(required(@launch_pass, "ResultParsing: the findings arrive only for review sessions, which have a pass number"), found_items) }
      None => {}                                        // сессия правки или раннера: файла находок нет
    }
    ImmediateResultParsing { result: parsing.result }
  }
  _ => unreachable("the other states have no operation work")
}
```

## Приём ответа и запись результата

```nova
/// При приёме (правило 14): у обращений запуска записи стороны нет (счётчики попыток ведёт механика контракта).
fn MachineData mut @on_accept(current State, response Response[RoleResult]) => ()

/// Запись принятого результата в хранилище (правила 8, 14): роль возвращает результат, в хранилище машины не пишет.
/// Ответ шага агента идёт событием (`ответ_агента` запишет переход СЕССИИ); итоговую строку и находки захода сессии проверки пишет операция РАЗБОР_ИТОГА
/// (`выполнить_операцию`, правило 29); у ворот результата роли нет.
fn MachineData mut @record_result(current State, response Response[RoleResult]) => ()
```

## Концы и ответ

```nova
/// Работа концов при входе (в последнем, повторяемом без вреда этапе фиксации) и ответ вызвавшей стороне.
/// Вход в любой конец отменяет все открытые запросы (правило 22); машина отвечает ровно один раз (правило 35).
fn MachineData mut @on_end_entry(end_state State, environment MachineEnvironment) Journal Time -> () => match end_state {
  // ОСТАНОВЛЕНО: группа процессов агента останавливается целиком и проверяется, что в ней не осталось процессов; в журнал — «запуск сессии остановлен: <остановка>»;
  //   вызывающая машина получает `Refusal` (таблица «конец → ответ»).
  Halted => {
    environment.add_irreversible(Irreversible.StopAgentGroup)
    environment.write_journal(journal_event("session_launch_stopped", [param("reason", "${@stop_reason}")]))
  }
  // ОШИБКА: группа процессов агента останавливается; в журнал — запись из перехода и данные машины; вызывающая машина получает `Refusal`; решает человек вне машины.
  Errored => {
    environment.add_irreversible(Irreversible.StopAgentGroup)
    environment.write_journal(environment.transition_note())
    @journal_machine_data(environment)
  }
  // КОНЕЦ: в журнал — код сессии и итог сессии; ответ `Answer` с итогом запуска уходит вызывающей машине.
  End => {
    ro outcome = required(@result, "End: the session outcome is recorded in Session")
    environment.write_journal(journal_event("session_result", [param("session", "${@session}"), param("outcome", "${outcome_word(outcome)}")]))
  }
  _ => ()
}
// запись для диагностики: все переменные и хранилища (Вход ОШИБКИ) — сигнатура объявлена в разделе «Механика машины»

/// Таблица «конец → ответ» первоисточника (раздел «Контракт машины»): каждый конец и каждое значение остановка — одна строка.
fn MachineData @end_response(call_request Request[SessionLaunchInput], end_state State, environment MachineEnvironment) -> Response[SessionLaunchResult] {
  match end_state {
    // КОНЕЦ, условие входа: всегда → СРезультатом: итог сессии; у сессий проверки — свод и находки захода
    End => Answer(Reply {
      request: call_request.id, party: call_request.party, trace: call_request.trace, step: call_request.step,
      result: SessionLaunchResult {
        result: required(@result, "End: the session outcome is recorded in Session"),
        summary: @launch_summary(),
        findings: @launch_findings() } })
    // ОШИБКА, условие входа: всегда (дефект машины) → Отказ, НетРезультата; текст — запись из перехода
    Errored => refuse_with(call_request, NoResult, journal_event_text(environment.transition_note()))
    Halted => match @stop_reason {
      // ОСТАНОВЛЕНО: остановка = «В13: остановить» или «В1: остановить» → Отказ, ОстановленоЧеловеком
      "gate13_halt" | "gate1_halt" => refuse_with(call_request, StoppedByHuman, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «ПАУЗА: остановить» (слово человека; у вызванной машины — сигнал «остановить от родителя» в ПАУЗЕ) → Отказ, ОстановленоЧеловеком
      "pause_halt" => refuse_with(call_request, common_stop_fail_code(@stop_reason), @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «отмена_запроса» → Отказ, ОтмененоРодителем
      "cancel_request" => refuse_with(call_request, common_stop_fail_code(@stop_reason), @stop_reason)
      _ => unreachable("stop reason outside the table "end to reply": a new value adds a table row")
    }
    _ => unreachable("only end states give a reply")
  }
}

/// Точка подстановки эффектов: обработчики выбирает вызывающий код, один раз (`with`), и вне этого файла — любые (`Time` — стандартный, обработчик по умолчанию).
/// Все функции цепочки от `начать`, `возобновить`, `вызвать` объявляют эффекты в своей сигнатуре; здесь они подставлены. Машину по входу запроса создаёт вызывающий код
/// (обработчик `Связь` верхней машины — раннера или проверки цикла — при запросе `ЗапросРоли` с входом `ВходЗапускаСессии`).
fn start_session_launch(request Request[SessionLaunchInput]) Time -> Response[SessionLaunchResult] =>
  with Store = store_handler, Journal = journal_handler, Link = link_handler, Objects = objects_handler {   // псевдокод: обработчики (база, файл поверх Fs/Db, очередь сообщений) — любые, вне файла
    mut engine_instance = Engine.new(MachineData.from_input(request.input))
    engine_instance.call(request)
  }
```

## Что движок не покрыл

Места, где запуску сессии нужно то, чего движок [state-machine-engine-automaton.md](state-machine-engine-automaton.md) не давал: записано обходом внутри этой машины или функцией без тела. Номера пунктов в каждом файле свои: здесь открыты 3–5, 7–13. Цепочка запуска сессии закрыта самой этой машиной (в раннере — пункт 10, в проверке цикла — пункт 6). Пункт 12 — обращение к агенту как вызов вложенной машины «Шаг агента» ([archive/state-machine-agent-step-automaton.md](archive/state-machine-agent-step-automaton.md)); пункт 13 — текст отказа в событии «сбой» и хук «при входе в ПАУЗУ». Вызовы ролей совещания на «Шаг агента» переведены отдельным заходом ([task-runner-meeting-automaton.md](task-runner-meeting-automaton.md)).

| № | Что нужно запуску сессии | Что в движке | Обход в этом файле | Предлагаемое решение |
|---|---|---|---|---|
| 3 | Чтение объёма запуска, остановка группы процессов агента | Эффект `Объекты`: закрыть и открыть для записи, перенести в архив, прочитать байты, принять файл попытки | Функции без тела с эффектом `Объекты` (`объём_запуска`, `остановить_группу_агента`) — в слое методики (эффект `Объекты` движка не расширен) | Движок: расширяемый `Объекты`; слой методики: эффект `ОбъектыЗадачи` (группа процессов, измерение объёма) |
| 4 | Режим ворот «показывать и продолжать» (В2): исполнитель сам даёт исход по умолчанию | У движка нет понятия исхода ворот по умолчанию | Нет (режим — на стороне исполнителя и обработчика `Связь`) | Слой методики: хук `исход_по_умолчанию(состояние) -> Option[Событие]` с записью в журнал |
| 5 | Запуск сессии: группа процессов агента, диалог автора, сборка промпта | `Объекты` не расширен; сборка промпта — не движок | Функции без тела `профиль_запуска`, `контекст_сессии`; группа процессов — `остановить_группу_агента` слоя | Слой методики: описание запуска сессии (формат артефакта, профиль, диалог) как данные роли |
| 7 | Ворота человека — 4 состояния (В2, В1, В13_СЕССИЯ, ПАУЗА) и столько же вариантов `ВходРоли`, слова ворот — варианты `Событие` | `ВходРоли` и `Событие` — перечисления машины | Вариант на ворота и на слово ворот | Слой методики: тип «Ворота» (имя, показываемые данные, слова ворот как данные), одно событие «слово ворот» |
| 8 | Каркас вложенной машины (ПАУЗА вынесена фрагментом «Пауза», шаг 5): ОСТАНОВЛЕНО, ОШИБКА, таблица «конец → ответ», `общее`, `записать_остановку` — те же, что у раннера, проверки цикла, совещания и шага агента | Движок даёт только протокол `Автомат`, реализации у него нет | Копия | Слой методики: базовая реализация каркаса |
| 9 | Рабочая копия попытки и проверка «объект не менялся с начала попытки»: у запуска их нет, а протокол требует методы `объект_менялся_с_начала_попытки`, `принять_файл_попытки` | Оба метода обязательны в протоколе | Пустые методы | Движок: необязательный протокол «Рабочая копия попытки» |
| 10 | Создание исполнителя вложенной машины по запросу родителя (`Машина.из_входа(запрос.вход)`) | «Машину по входу запроса создаёт вызывающий код»; у родителя нет способа создать вложенную | Нет: обработчик `Связь` создаёт исполнителя вложенной машины вне файла | Движок: протокол `Фабрика[Вход]` для вложенных машин |
| 11 | Вход вызова с необязательными полями (`источник_запуска`, `фаза`, `заход_запуска`, `перечень_источников`): раннер не передаёт номер захода, проверка цикла — фазу | `Запрос[Вход]` — один тип входа на машину | Поля `Option` | Слой методики: сумма входов по вызывающей машине вместо одной записи |
| 12 | Конверт этой машины в запросе вложенной (`ЗапросАгента.трасса`, `номер_шага`): `Среда` не отдаёт машине трассу и номер шага | Конверт знает только исполнитель | Функции без тела `трасса_вызова`, `номер_шага_вызова` | Движок: методы `трасса()` и `номер_шага()` в `Среда` либо исключить поля из `ЗапросАгента` |
| 13 | (а) Текст отказа вложенной машины в событии «сбой» (`текст_отказа` для ворот В13); (б) хук «при входе в ПАУЗУ» — остановить группу процессов агента (прежнее поведение паузы) | (а) `событие_сбоя(причина)` несёт только код, текст остаётся в `тексты_сбоев`; (б) общие события не вызывают хук машины | (а) Поле `текст_отказа` пусто, пока движок не передаёт текст; (б) нет | Движок: `событие_сбоя(причина, текст)` и необязательный хук `при_входе_в_паузу` |
