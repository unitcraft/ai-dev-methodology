# Шаг агента: код автомата

> **Архив (2026-10-19).** Файл не обновляется: машина записана на Алуле — [nova-alula: spec/samples/agent-step.alula.md](https://github.com/nv-lang/nova-alula/blob/main/spec/samples/agent-step.alula.md) и [английская версия](https://github.com/nv-lang/nova-alula/blob/main/spec/samples/agent-step.en.alula.md). Решение владельца методики: «всё, что не касается Портолана, — в архив».

Стейт-машина одного вызова агента — линзы, запуска сессии цикла, хода чата, вратаря: типизированный запрос (`ЗапросАгента`), ход к транспорту агента (обращение ХОД_АГЕНТА), повтор временной ошибки, продолжение обрезанного выхода, проверка формы ответа с одним ходом исправления, запросы разрешений (развилка ПОЛИТИКА и ворота РАЗРЕШЕНИЕ), проверка бюджета (БЮДЖЕТ), сбор единой записи расхода (УЧЁТ) и ответ `ОтветАгента` либо отказ с кодом из закрытого списка, — записанная кодом на языке Нова как реализация протокола `Автомат` движка [state-machine-engine-automaton.md](state-machine-engine-automaton.md): данные машины, перечисления `Состояние` и `Событие`, переход `перейти(состояние, событие)` как `match`, роли (входы и результаты обращений к транспорту агента и к человеку на воротах), работа операций, ответ по концу. Всё общее — конверт запроса и ответа, исполнитель, снимок и хранилище, общие события «стоп/продолжить/отмена», цикл, фиксации — в движке. Нормы — [task-runner.md](../../task-runner.md) (словарь, профили запуска, форматы файлов). Идентификаторы кода английские, словарь — [state-machine-glossary.md](../state-machine-glossary.md); русские имена — в описаниях и комментариях.

**Первоисточник — [state-machine-agent-step-states.md](state-machine-agent-step-states.md)** (машина «Шаг агента»: таблицы состояний, общие события, «Контракт машины», «Решения при переводе»); правила формы — [state-machine-spec.md](../state-machine-spec.md). Файл — производная запись того же автомата, а не второй источник истины: при расхождении верен первоисточник, файл правится вслед за ним. Язык записи — Нова, https://github.com/nv-lang/nova. **Код не компилировался и не проверялся компилятором Нова:** это псевдокод в синтаксисе Нова; соглашения записи, помеченные места (`// псевдокод:`), подтверждённое и неподтверждённое спецификацией — в [state-machine-engine-automaton.md](state-machine-engine-automaton.md), здесь только то, что относится к шагу агента. Опытный статус — в шапке первоисточника; раннером эта машина не исполняется. Вызывает эту машину запуск сессии — [task-runner-session-automaton.md](task-runner-session-automaton.md) (первоисточник — [task-runner-session-states.md](task-runner-session-states.md); состояние СЕССИЯ) по контракту вызова движка (`Вызываемое`, эффект `Связь`: запрос уходит как `ЗапросРоли`, ответ приходит сообщением), а не прямым вызовом функции; общие типы (соглашения, пункт 1) объявлены в слое методики — [state-machine-methodology-automaton.md](state-machine-methodology-automaton.md). Совещание — [task-runner-meeting-automaton.md](task-runner-meeting-automaton.md) (первоисточник — [task-runner-meeting-states.md](task-runner-meeting-states.md); состояния ЛИНЗЫ, СВИДЕТЕЛЬ, ПРАВКА и ВОПРОС) — зовёт эту машину так же, вложенными вызовами для линз, свидетеля и автора (первоисточник, решение 13). Имя файла — по `AGENTS.md`, «Вынесенные алгоритмы», форма `automaton` (документ `state-machine`, часть `agent-step`).

## Соглашения записи

1. **Типы и идентификаторы** — по [движку](state-machine-engine-automaton.md), пункты 1–3: английские имена по [словарю](../state-machine-glossary.md). Общие типы данных (`ВидВызывающего`, `МодельАгента`, `Токены`, `Использование`, `ПрофильАгента`, `ПределыАгента`, `ЗапросАгента`, `ОтветАгента`) объявлены один раз в слое методики [state-machine-methodology-automaton.md](state-machine-methodology-automaton.md) и подключены здесь; их таблица соответствия именам блока «Типы на Нове» — там же. Вход паузы (`ВходПаузы`) — тоже из слоя; вариант `ВходРоли` для входа паузы — `ВходПаузыРоли`. Собственные типы данных этой машины (первоисточник, «Типы»): `РасходТранспорта`, `ВидДействия`, `ЗапросРазрешения`, `ПроверкаОтвета`, `ИтогХода`. Записи автомата, которых в первоисточнике нет: `РезультатРоли`, `ВходРоли`, `Окружение`, `Необратимое`. **Значения перечислений** с совпадающими именами в разных перечнях пишутся с именем типа (`ВидВызывающего.Линза`, `ПроверкаОтвета.Верна`, `ВидДействия.Удаление`).
2. **Данные события.** Поля варианта события берутся образцом в `match`: `Сбой { причина } => …`; при совпадении имени поля с переменной машины поле переименовывается: `Ответ_закончен { текст, артефакт, расход: полученный }`. «Сторона события» и идентификатор события — `событие.сторона`, `событие.идентификатор` (конверт `Входящее` движка, правила 13 и 31). Служебные операции переходу даёт `среда` (журнал, слова человека, сигналы вложенным, данные движка `открытые_запросы`, `предыдущее`, `запрос_вызова`).
3. **Строка таблицы — ветка кода.** Перед каждой строкой первоисточника (условие или событие, «Что меняется», «Куда») стоит комментарий `// <СОСТОЯНИЕ> #<номер строки>: …` с её текстом; у обращения в скобках — данные события; порядок строк как в первоисточнике. «Куда» записано как `Куда(<СОСТОЯНИЕ>)`; «Куда: предыдущее» — у ПАУЗЫ в движке (`Куда(@машина.состояние_по_имени(предыдущее))`). Строка «иначе» развилки — последняя ветка, ведёт в `ОШИБКА` через `среда.ошибка_машины(…)`. Строки «Вход», «Выход», «При входе», «Сторона» и одна строка простыми словами на состояние — комментарии `//` у состояния. Общие события записаны в движке (`общие_события`); `общее` машины сводит к ним её события. Состояние ПАУЗА и его четыре строки подключены фрагментом «Пауза» ([state-machine-pause-states.md](state-machine-pause-states.md)): события паузы разбирает движок, у машины остаются ветка `ПАУЗА => НеЖдёт`, хуки `состояние_паузы`, `причина_остановки_в_паузе`, `состояние_по_имени` и сведение событий паузы в `общее`.
4. **Строки `// псевдокод:`** и перечень подтверждённого спецификацией — в [движке](state-machine-engine-automaton.md), пункт 5. Здесь дополнительно: функции без тела (сигнатуры механики и чтения внешних объектов: `проверка_ответа`, `закрыть_ход_агента`); алиас `type Окружение alias Среда[…]` (как у запуска сессии); импорт `use` общих типов из слоя методики — разрешение вне записи; значения перечислений с именем типа; таблицы параметров проекта (`политика_проекта`, `требует_повышенного_внимания`) записаны функциями с `match`. Неподтверждённое спецификацией Нова, используемое здесь (как и в других машинах): объявление `module`, `ro` на уровне модуля (константы), `return` внутри `if` в теле функции, `+=` на целом поле, `Time.now()` как целое число миллисекунд эпохи.
5. **Уточнения записи автомата сверх первоисточника:** (а) метод `событие_ответа` — метод протокола `Автомат`: отображение результата роли в событие; (б) число возвратов ответа не по форме в запросе — поле `возвратов_формы` описания обращения (`Одна`): у ХОД_АГЕНТА `0`, потому что исправление формы идёт не возвратом в том же запросе движка, а ходом «исправить» — новым запросом по строкам ПРОВЕРКИ_ОТВЕТА; вложенных сторон у этой машины нет (`вложенная: false`); метод `при_возобновлении` — заглушка (подготовки при возобновлении нет); (в) `ИтогХода` — результат роли ХОД_АГЕНТА: по варианту на строку «ответ: …» первоисточника; (г) `проверка_ответа` — объект, измеренный исполнителем (функция без тела, как `объём_запуска` у запуска сессии); (д) `запрос_вызова` — всегда `запрос.идентификатор_запроса` (решение о `""` у верхнего уровня открыто, см. движок, пункт 6); (е) `состояние_по_имени` записано полным `match` по именам обращений; (ж) срок бездействия запроса к агенту (`срок_хода`) считает метод `обращение` по данным машины: срок тишины запроса, плюс пауза повтора при ходе «повторить».
6. **Данные машины — поля типа `Машина`**: поля названы как переменные раздела «Данные» первоисточника (правило 25), начальные значения — в `Машина.new()`, по входу шага — `Машина.из_входа` (запрос агента приходит в запросе целиком). Данные движка (конверт, очереди запросов, журнал, слова человека, тексты сбоев) — в `СостояниеДвижка` движка. Внешний объект `проверка_ответа` читается через `Объекты` (`проверка_ответа()`): его измеряет исполнитель перед развилкой ПРОВЕРКА_ОТВЕТА.
7. **`недостижимо(текст)`** (определено в движке, пункт 8): в реализации стоит: у концов КОНЕЦ, ОСТАНОВЛЕНО, ОШИБКА в `перейти` (переходов нет); в `ответ_по_концу` (значение `остановка` вне таблицы; ответ не из конца; использование пусто в КОНЦЕ); в `выполнить_операцию` (состояние без операции); в `вход_запроса` и `следующая_попытка` (состояние не обращение; сторона вне «агент», «вратарь», «человек»); в `состояние_по_имени`, `сторона_обращения` (имя вне перечня); через `обязательное` движка — в `ПОЛИТИКА`, `РАЗРЕШЕНИЕ`, `вход_запроса` (запрос разрешения пуст) и `ответ_по_концу` (использование пусто в КОНЦЕ); `решение_по_политике` и `собрать_использование` `недостижимо` не зовут.

Соответствие типов и полей (общие типы данных — таблица в [state-machine-methodology-automaton.md](state-machine-methodology-automaton.md); здесь только добавленное и принятое из других файлов):

| Первоисточник | Русское имя (описания, таблицы) | Код и блок «Типы на Нове» (латиница) |
|---|---|---|
| Число, Текст, Дробное | `int`, `str`, `f64` | `int`, `str`, `f64` (стандартные имена Нова) |
| ВидВызывающего: линза, сессия цикла, ход чата, вратарь | `ВидВызывающего`: `Линза`, `СессияЦикла`, `ХодЧата`, `Вратарь` | `CallerKind`: `Lens`, `CycleSession`, `ChatTurn`, `Gatekeeper` |
| МодельАгента: идентификатор, поставщик, вариант | `МодельАгента`: `идентификатор`, `поставщик`, `вариант` | `AgentModel`: `id`, `provider`, `variant` |
| Токены: вход, выход, рассуждение, кэш_чтение, кэш_запись | `Токены`: `вход`, `выход`, `рассуждение`, `кэш_чтение`, `кэш_запись` | `TokenUsage`: `input`, `output`, `reasoning`, `cache_read`, `cache_write` |
| ПрофильАгента: семья, модель, усилие | `ПрофильАгента`: `семья`, `модель`, `усилие` | `AgentProfile`: `family`, `model`, `effort` |
| ПределыАгента: срок_тишины, бюджет_токенов, бюджет_стоимости | `ПределыАгента`: `срок_тишины`, `бюджет_токенов`, `бюджет_стоимости` | `AgentLimits`: `silence_term`, `token_budget`, `cost_budget` |
| ЗапросАгента: вид, профиль, сессия, контекст, пределы, трасса, номер_шага | `ЗапросАгента`: те же имена | `AgentRequest`: `kind`, `profile`, `session`, `context`, `limits`, `trace`, `step` |
| РасходТранспорта: модель, токены, стоимость, занято_контекста | `РасходТранспорта`: те же имена | `TransportUsage`: `model`, `tokens`, `cost`, `context_used` |
| Использование: сессия, результат, семья, модель, токены, стоимость, создано, обновлено, занято_контекста, трасса, номер_шага | `Использование`: те же имена | `Usage`: `session`, `result`, `family`, `model`, `tokens`, `cost`, `created`, `updated`, `context_used`, `trace`, `step` |
| ОтветАгента: текст, артефакт, использование | `ОтветАгента`: те же имена | `AgentReply`: `text`, `artifact`, `usage` |
| ВидДействия: чтение, запись, удаление, перенос, поиск, исполнение, сеть, мышление, смена режима, другое | `ВидДействия`: `Чтение`, `Запись`, `Удаление`, `Перенос`, `Поиск`, `Исполнение`, `Сеть`, `Мышление`, `СменаРежима`, `Другое` | `ActionKind`: `Read`, `Write`, `Delete`, `Move`, `Search`, `Execute`, `Network`, `Think`, `SwitchMode`, `Other` |
| ЗапросРазрешения: вид_действия, описание | `ЗапросРазрешения`: `вид_действия`, `описание` | `PermissionRequest`: `action`, `description` |
| ПроверкаОтвета: верна, нарушена, пуста | `ПроверкаОтвета`: `Верна`, `Нарушена`, `Пуста` | `ReplyCheck`: `Valid`, `Violated`, `Empty` |
| ИтогХода: закончен (текст, артефакт, расход), обрезан, предел_запросов, отказ_модели, отменён, временная_ошибка, постоянная_ошибка, нужно_разрешение | `ИтогХода`: `Закончен { текст, артефакт, расход }`, `Обрезан`, `ПределЗапросов`, `МодельОтказалась`, `Отменён`, `ВременнаяОшибка`, `ПостояннаяОшибка`, `НужноРазрешение`; поле `расход` у вариантов с расходом | `TurnResult`: `Finished(text, artifact, usage)`, `Truncated`, `TurnRequestLimit`, `ModelRefusal`, `Stopped`, `TransientError`, `PermanentError`, `NeedsPermission`; латинское `usage` — поле `расход` (тип `TransportUsage`), не `Usage` |
| Запрос: идентификатор_запроса, номер_попытки, сторона, вход, срок_бездействия, трасса, номер_шага | `Запрос[Вход]`: `идентификатор_запроса`, `номер_попытки`, `сторона`, `вход`, `срок_бездействия`, `трасса`, `номер_шага` | `Request[T]`: `id`, `attempt`, `party`, `input`, `idle_term`, `trace`, `step` |
| Ответ (с результатом): запрос, сторона, результат, трасса, номер_шага | `ОтветСРезультатом[Результат]`: `запрос`, `сторона`, `результат`, `трасса`, `номер_шага` | `Reply[R]`: `request`, `party`, `result`, `trace`, `step` |
| Ответ (отказ): запрос, сторона, причина, текст, трасса, номер_шага | `ОтветОтказ`: `запрос`, `сторона`, `причина`, `текст`, `трасса`, `номер_шага` | `Rejection`: `request`, `party`, `reason`, `text`, `trace`, `step` |
| Ответ: с результатом, отказ | `Исход[Результат]`: `СРезультатом(ОтветСРезультатом[Результат])`, `Отказ(ОтветОтказ)` | `Response[R]`: `Answer(Reply[R])`, `Refusal(Rejection)` |
| КодСбоя: нет результата, отказ модели, соединение оборвалось, форма не исправлена, нет ответа в срок, остановлено человеком, потолок заходов с открытыми находками, отменено родителем, предел токенов, предел запросов хода | `КодСбоя`: `НетРезультата`, `ОтказМодели`, `СоединениеОборвалось`, `ФормаНеИсправлена`, `НетОтветаВСрок`, `ОстановленоЧеловеком`, `ПотолокЗаходов`, `ОтмененоРодителем`, `ПредельТокенов`, `ПредельЗапросовХода` | `FailCode`: `NoResult`, `ModelRefused`, `ConnectionLost`, `FormNotFixed`, `Timeout`, `StoppedByHuman`, `CeilingReached`, `Cancelled`, `MaxTokens`, `MaxTurnRequests` |
| Записи автомата (не из первоисточника): состояние, событие, вид состояния, сообщение, входящее событие, переход | `Состояние`, `Событие`, `Вид`, `Сообщение`, `Входящее`, `РезультатРоли`, `ВходРоли`, `ОшибкаХранилища`, `Переход`: `Куда`, `Заново`, `Остаться`, `НеЖдёт` | `State`, `Event`, `Kind`, `Incoming`, `Transition`: `Go`, `Rerun`, `Stay`, `NotAwaited`; `RoleResult`, `RoleInput` — запись автомата; `Message`, `StoreError` — типы движка; в блоке «Типы на Нове» их нет |
| Функции записи автомата: функция переходов, недостижимая ветка | `перейти`, `недостижимо` | `step`, `unreachable` |
| Параметры типов: вход запроса, результат роли | `Вход`, `Результат` | `T`, `R` |

Имена, которых нет в первоисточнике и которые завела запись автомата (кроме названных в соглашениях, пункт 1): варианты `Событие` с префиксом ворот (`РАЗРЕШЕНИЕ_разрешить`, …; один вариант на слово ворот строки первоисточника), `Ответ_закончен` и другие варианты «ответ: …» (по варианту `ИтогХода`), `Сразу_СТАРТ`, `Сразу_УЧЁТ`, `Машина.из_входа`, методы машины для протокола `Автомат` (`начальное`, `общее`, `обращение`, `следующая_попытка`, `событие_ответа` и др.), функции раздела «Механика машины» (`сложить_расход`, `израсходовано_токенов`, `решение_по_политике`, `пауза_повтора` и др.; все — термины первоисточника). Типы и функции движка (`Исполнитель`, `Снимок`, `Хранилище`, `Автомат`, `Среда`, `Входящее`, `Переход`, `Куда`, `Остаться`, `НеЖдёт`, `перейти` и др.) — в [state-machine-engine-automaton.md](state-machine-engine-automaton.md).

## Типы

```nova
module agent_step

// псевдокод: общие типы и сигнатуры слоя методики; импорт модулей — вне записи (соглашения, п. 4)
use methodology.{CallerKind, AgentModel, TokenUsage, Usage, AgentProfile, AgentLimits, AgentRequest, AgentReply, PauseInput}

/// РасходТранспорта: расход, который сообщил транспорт за ход; модель — та, что ответила (если протокол не сообщает, транспорт берёт её из профиля)
type TransportUsage { model AgentModel, tokens TokenUsage, cost Option[f64], context_used Option[int], request_started int }

/// ВидДействия: вид действия, которое просит разрешить агент; по виду ветвится политика (`политика_проекта`, `требует_повышенного_внимания`)
type ActionKind enum
  | Read
  | Write
  | Delete
  | Move
  | Search
  | Execute
  | Network
  | Think
  | SwitchMode
  | Other

/// ЗапросРазрешения: что агент просит разрешить; описание читает человек на воротах РАЗРЕШЕНИЕ
type PermissionRequest { action ActionKind, description str }

/// ПроверкаОтвета: измерено исполнителем: форма ответа верна, нарушена или ответ пуст (первоисточник, Термины, «Пустой ответ»: у сессии цикла нужен артефакт, у линзы и хода чата — текст или артефакт, у вратаря — текст со словом ворот, основанием и уверенностью)
type ReplyCheck enum
  | Valid
  | Violated
  | Empty

/// ИтогХода: итог одного хода у транспорта; по варианту на строку «ответ: …» первоисточника (раздел «Состояния», ХОД_АГЕНТА)
type TurnResult enum
  | Finished { text Option[str], artifact Option[str], usage TransportUsage }   // конец хода
  | Truncated { usage TransportUsage }                                            // выход остановлен пределом токенов ответа
  | TurnRequestLimit { usage TransportUsage }                                     // исчерпан предел запросов модели за ход
  | ModelRefusal { usage TransportUsage }                                   // отказ модели
  | Stopped { usage TransportUsage }                                            // ход остановлен агентом или транспортом
  | TransientError                                                                // лимит частоты, перегрузка, сбой поставщика: повтор оправдан
  | PermanentError                                                               // повтор не лечит
  | NeedsPermission { permission_request PermissionRequest }                         // агент просит разрешение; транспорт держит ход открытым до решения

/// Запись автомата: результат роли — по варианту на обращение первоисточника, где сторона возвращает результат (раздел «Состояния»: Выход);
/// у ворот человека результата роли нет: слово человека приходит событием, а не исходом запроса.
type RoleResult enum
  | TurnOutcome(TurnResult)                      // ХОД_АГЕНТА: итог_хода

/// Запись автомата: вход запроса — по варианту на обращение первоисточника; поля — строки таблицы «Вход» состояния, читаемые стороной
/// (у ворот без столбца «Кто читает» — вся таблица); необязательное поле — Option.
type RoleInput enum
  | TurnInput { agent_request AgentRequest, turn str, retry_count int, turn_before_retry Option[str], permission_decision Option[str] }   // ХОД_АГЕНТА (агент)
  | PermissionInput { agent_request AgentRequest, permission_request PermissionRequest }                      // РАЗРЕШЕНИЕ
  | RolePauseInput(PauseInput)                                                                               // ПАУЗА

/// Необратимое действие во внешнем мире: последний этап фиксации, повторяемый без вреда (правило 13).
type Irreversible enum
  | CloseAgentTurn        // ОСТАНОВЛЕНО, ОШИБКА: транспорту сообщается об отмене открытого хода, в том числе удержанного до решения о разрешении

/// Окружение перехода шага агента: `Среда` движка с типами шага.
type MachineEnvironment alias Environment[State, Event, Irreversible]
```

## Данные

```nova
/// Предел одновременных запросов: у шага запрос один (правило 21); движку отдаёт метод `предел_запросов`
// псевдокод: `ro` на уровне модуля — не подтверждено спецификацией Нова
ro REQUEST_LIMIT int = 1

/// Сколько раз повторяется запрос после временной ошибки (`run` псевдокода: «до 3 раз»)
ro RETRIES int = 3

/// Пауза перед первым повтором, миллисекунды; перед каждым следующим удваивается; параметр проекта, значение — этой записи (решение 4 первоисточника)
ro RETRY_PAUSE int = 2000

/// Сколько раз продолжается обрезанный выход
ro CONTINUATIONS int = 1

/// Сколько раз ответ не по форме возвращается агенту в том же диалоге
ro FORM_RETURNS int = 1

/// Сколько ходов шаг отправляет, если запрос не задал предел ходов; принято: владелец, 2026-10-18, «по рекомендации» (решение 16 первоисточника)
ro TURN_LIMIT int = 20

/// Машина шага агента: данные шага в одной записи (раздел «Данные» первоисточника); поля названы как переменные первоисточника.
/// Машина — данные и логика шага: методы этого типа с ресивером `@` читают и пишут только эти поля; данные движка и служебные операции — через `среда`.
/// Машина реализует `Автомат[Состояние, Событие, ЗапросАгента, ОтветАгента, ВходРоли, РезультатРоли, Необратимое]` структурно.
type MachineData {
  // Переменные машины (состояние машины); сохраняются целиком вместе со снимком (правило 22); данные движка (конверт, очереди запросов, журнал) — в `СостояниеДвижка`
  agent_request AgentRequest,                  // запрос вызова: вид, профиль, сессия, контекст, пределы, трасса и номер_шага вызывающего; из запроса вызова, не меняется
  turn str,                                     // какой ход отправляется транспорту: «первый», «повторить», «продолжить», «исправить», «разрешение»; по значению машина не ветвится
  retry_count int,                          // сколько раз повторён запрос после временной ошибки
  continuation_count int,                       // сколько раз отправлено «продолжи с места обрыва»
  return_count int,                         // сколько раз отправлено «исправь форму файла»
  turn_count int,                             // сколько ходов отправлено шагом: 1 после СТАРТА, растёт в БЮДЖЕТЕ
  turn_before_retry Option[str],                  // ход, который повторяется после временной ошибки; None — повторов не было
  transport_usage Option[TransportUsage],             // расход транспорта, сложенный по всем ходам шага; None — транспорт расхода не дал
  reply_text Option[str],                    // текст ответа агента из последнего закончившегося хода
  reply_artifact Option[str],                 // ссылка на артефакт ответа агента из последнего закончившегося хода
  permission_request Option[PermissionRequest],  // запрос агента на разрешение, ждущий решения
  permission_decision Option[str],              // «разрешить» или «отказать»: решение, которое получит агент
  started Option[int],                          // момент начала шага, миллисекунды эпохи; пишет СТАРТ
  usage Option[Usage],         // собранная запись расхода; пишет УЧЁТ
  stop_reason str,                               // почему шаг кончается отказом; `""`, пока отказа нет
  agent_attempt int,                          // счётчики попыток одноадресных обращений (правило 15): к агенту, к вратарю, к человеку
  gatekeeper_attempt int,
  enhanced_attempt int,
}

/// Начальные значения данных машины — раздел «Данные» первоисточника; запрос агента заполняет `Машина.из_входа`.
fn MachineData.new(request AgentRequest) -> MachineData => {
  agent_request: request,
  turn: "first",
  retry_count: 0,
  continuation_count: 0,
  return_count: 0,
  turn_count: 0,
  turn_before_retry: None,
  transport_usage: None,
  reply_text: None,
  reply_artifact: None,
  permission_request: None,
  permission_decision: None,
  started: None,
  usage: None,
  stop_reason: "",
  agent_attempt: 0,
  gatekeeper_attempt: 0,
  enhanced_attempt: 0,
}

/// Машина по входу шага: запрос агента целиком.
fn MachineData.from_input(input AgentRequest) -> MachineData => MachineData.new(input)
```

## Инварианты

```nova
// 1. Шаг повышенного внимания: решает человек (по умолчанию) или агент по настройке проекта «исполнитель шагов повышенного внимания» (`исполнитель_повышенного_внимания`); ворота В14, В15, В5, В10а–г, В12, продолжение после «стоп человека» и решения закрытого списка раздела 4 — дорогие: их решает человек (по умолчанию) или усиленный вратарь — только по разрешению владельца в настройке проекта `усиленный_вратарь` (по умолчанию «нет») и с усиленными требованиями (`methodology.md`, раздел 18, «Вратарь»). Повышенное внимание — свойство шага: решение требует осознанного выбора и записи основания; основание пишется всегда, а в журнале — кто решил на самом деле (`решил`: «человек» или «агент») — на воротах РАЗРЕШЕНИЕ, ПАУЗА и на воротах вызывающей машины (у запуска сессии В1, В2, В13); «стоп человека» — в любой момент, от человека (владелец, 2026-10-18, «по рекомендации»);
//    исполнитель считает, переключает состояния и пишет журнал. Исключение — запросы разрешений, на которые отвечает политика проекта (ПОЛИТИКА): исход даёт
//    исполнитель и пишет его в журнал; виды из `требует_повышенного_внимания` автоматически не разрешаются никогда, а у вызова без человека (виды «линза» и «вратарь») «спросить» превращается в «отказать».
//    В коде: события ворот приходят от стороны «вратарь» (ворота, на которые вправе ответить вратарь) или «усиленный» (дорогие ворота и ПАУЗА: отвечает усиленный вратарь по разрешению, иначе человек) — имя роли ворот, кто исполняет её на деле, пишет `решил` (у вызванной машины в ПАУЗЕ — «от родителя»); перейти их не порождает.
//
// 2. Шаг конечен: счётчики число_повторов, число_продолжений, число_возвратов и число_ходов не убывают и ограничены, ход после предела ходов не отправляется:
//    движок после каждого перехода шага сверяет `метка_инварианта` с её значением до шага.
//
// 3. Вратарь-агент (вид `Вратарь`): человека у вызова нет — `интерактивный(Вратарь)` ложно, политика даёт ему «отказать» вместо «спросить»; ответ годен при слове из перечня ворот,
//    непустом основании и уверенности «высокая» или «низкая» (форма — один ход исправления); ворота В14, В15, В5, В10а–г, В12, продолжение после «стоп человека» и решения закрытого списка
//    обычному вратарю не отдаются, усиленному — по разрешению владельца; ни одно состояние не направляет их шагу с этим видом напрямую, запрос собирает исполнитель ворот по стороне «усиленный». Выбор исполнителя слова — механика исполнителя ворот, состояния не меняются (решение 19).
```

## Состояния

```nova
type State enum
  // развилки
  | Retry | Continuation | ReplyValidation | Policy | Budget | StepOutcome
  // операции
  | Start | Accounting
  // обращения
  | AgentTurn | Permission | Pause
  // концы
  | End | Halted | Errored

/// Начальное состояние — СТАРТ. Вид состояния (обращение, операция, развилка, конец) по первоисточнику, раздел «Состояния».
fn MachineData @kind(state State) -> Kind => match state {
  AgentTurn | Permission | Pause => Appeal
  Start | Accounting => Operation
  Retry | Continuation | ReplyValidation | Policy | Budget | StepOutcome => Fork
  End | Halted | Errored => Final
}

/// Имя состояния — текст для переменной «предыдущее» и журнала (правило 24).
fn MachineData @state_name(state State) -> str => match state {
  Start => "Start"
  AgentTurn => "AgentTurn"
  Retry => "Retry"
  Continuation => "Continuation"
  ReplyValidation => "ReplyValidation"
  Policy => "Policy"
  Permission => "Permission"
  Budget => "Budget"
  Accounting => "Accounting"
  StepOutcome => "StepOutcome"
  Pause => "Pause"
  End => "End"
  Halted => "Halted"
  Errored => "Errored"
}

/// «Куда: предыдущее» (правило 24): значение переменной — имя состояния-обращения, не конца и не ПАУЗЫ.
fn MachineData @state_by_name(name str) -> State => match name {
  "AgentTurn" => AgentTurn
  "Permission" => Permission
  _ => unreachable(""previous" holds the name of an appeal state, not of an end or Pause (rule 24)")
}

/// Сторона обращения: «агент» (ХОД_АГЕНТА), «вратарь» (ворота РАЗРЕШЕНИЕ: человек по умолчанию, агент по настройке) или «усиленный» (ПАУЗА).
fn appeal_party(appeal State) -> str => match appeal {
  AgentTurn => "agent"
  Permission => "gatekeeper"
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
  // исходы запроса стороны (правила 16, 26); у каждого есть событие.сторона; ХОД_АГЕНТА: «ответ» по варианту итога хода
  | RepliedFinished { text Option[str], artifact Option[str], usage TransportUsage }   // «ответ: закончен»
  | RepliedTruncated { usage TransportUsage }                                              // «ответ: обрезан»
  | RepliedTurnRequestLimit { usage TransportUsage }                                      // «ответ: предел_запросов»
  | RepliedModelRefusal { usage TransportUsage }                                         // «ответ: отказ_модели»
  | RepliedStopped { usage TransportUsage }                                              // «ответ: отменён»
  | RepliedTransientError                                                                 // «ответ: временная_ошибка»
  | RepliedPermanentError                                                                // «ответ: постоянная_ошибка»
  | RepliedNeedsPermission { permission_request PermissionRequest }                          // «ответ: нужно_разрешение»
  | Failure { reason FailCode }                                                               // «сбой»
  // исход операции (операций с данными две: СТАРТ и УЧЁТ; у развилки событие без данных)
  | Immediate                                          // «сразу»
  | ImmediateStart { started int }                     // «сразу» с данными СТАРТА: миллисекунды эпохи
  | ImmediateAccounting { usage Usage }     // «сразу» с данными УЧЁТА: собранная запись
  // слова ворот человека
  | PermissionAllow                           // «РАЗРЕШЕНИЕ: «разрешить»»
  | PermissionDeny                            // «РАЗРЕШЕНИЕ: «отказать»»
  | PauseWordContinue { human_word str, author str, source str }   // «ПАУЗА: «продолжить»»
  | PauseWordHalt                               // «ПАУЗА: «остановить»»
  | PauseWordContinueFromParent { id str }          // «ПАУЗА: «продолжить от родителя»»
  | PauseWordHaltFromParent { id str }         // «ПАУЗА: «остановить от родителя»»
```

## Механика машины

```nova
// Раздел записывает механику шага агента: свободные функции и методы `Машина`; методы `Исполнитель` и общие функции — в движке.
// псевдокод: функции без тела — сигнатуры; тело пишет реализация, в Нове внешняя реализация здесь не показана

// Свободные функции: чтение внешних объектов и операции над ними
// измерено исполнителем перед развилкой ПРОВЕРКА_ОТВЕТА по `текст_ответа` и `артефакт_ответа`: форма верна, нарушена или ответа нет
fn reply_validation() Objects -> ReplyCheck
// транспорту сообщается об отмене открытого хода (в том числе удержанного до решения о разрешении); повторяемо без вреда
fn close_agent_turn() Objects -> Result[(), ObjectError]

// Свободные функции: термины первоисточника (чистые)
// сумма необязательных целых: нет только если нет обоих
fn sum_ints(first Option[int], second Option[int]) -> Option[int] => match first {
  Some(value) => match second {
    Some(other) => Some(value + other)
    None => Some(value)
  }
  None => second
}
// сумма необязательных дробных: нет только если нет обоих
fn sum_floats(first Option[f64], second Option[f64]) -> Option[f64] => match first {
  Some(value) => match second {
    Some(other) => Some(value + other)
    None => Some(value)
  }
  None => second
}
// токены по полям: сумма имеющихся значений
fn add_tokens(previous_tokens TokenUsage, new_tokens TokenUsage) -> TokenUsage => TokenUsage {
  input: sum_ints(previous_tokens.input, new_tokens.input), output: sum_ints(previous_tokens.output, new_tokens.output),
  reasoning: sum_ints(previous_tokens.reasoning, new_tokens.reasoning),
  cache_read: sum_ints(previous_tokens.cache_read, new_tokens.cache_read), cache_write: sum_ints(previous_tokens.cache_write, new_tokens.cache_write) }
// «предел токенов» и «предел ходов»: предел_ходов — поле запроса или `ПРЕДЕЛ_ХОДОВ`; «предел ходов исчерпан» — число_ходов не меньше него
fn turn_limit_reached(request AgentRequest, turn_count int) -> bool => turn_count >= (request.limits.turn_limit ?? TURN_LIMIT)
// «сложить_расход(a, b)»: нет и b — b; иначе токены и стоимость — суммы, модель, занято_контекста и начало_запроса — из b
fn add_usage(previous_usage_option Option[TransportUsage], new_usage TransportUsage) -> TransportUsage => match previous_usage_option {
  Some(previous_usage) => TransportUsage {
    model: new_usage.model, tokens: add_tokens(previous_usage.tokens, new_usage.tokens),
    cost: sum_floats(previous_usage.cost, new_usage.cost), context_used: new_usage.context_used, request_started: new_usage.request_started }
  None => new_usage
}
// «израсходовано_токенов»: вход, выход и рассуждение; кэш в бюджет токенов не входит; нет-расход — 0
fn tokens_spent(usage Option[TransportUsage]) -> int => match usage {
  Some(found_item) => (found_item.tokens.input ?? 0) + (found_item.tokens.output ?? 0) + (found_item.tokens.reasoning ?? 0)
  None => 0
}
// «израсходовано_стоимости»: поле стоимость; нет и нет-расход — 0
fn cost_spent(usage Option[TransportUsage]) -> f64 => match usage {
  Some(found_item) => found_item.cost ?? 0.0
  None => 0.0
}
// «предел токенов исчерпан»: бюджет задан и израсходовано не меньше него
fn token_limit_reached(request AgentRequest, usage Option[TransportUsage]) -> bool => match request.limits.token_budget {
  Some(limit) => tokens_spent(usage) >= limit
  None => false
}
// «предел стоимости исчерпан»: бюджет задан и израсходовано не меньше него
fn cost_limit_reached(request AgentRequest, usage Option[TransportUsage]) -> bool => match request.limits.cost_budget {
  Some(limit) => cost_spent(usage) >= limit
  None => false
}
// «интерактивный вызов»: у видов «линза» и «вратарь» человека нет
fn interactive(kind CallerKind) -> bool => match kind {
  CallerKind.Lens => false
  CallerKind.CycleSession => true
  CallerKind.ChatTurn => true
  CallerKind.Gatekeeper => false
}
// закрытый перечень видов действий повышенного внимания, на которые автоматически не разрешается никогда (`ВИДЫ_ПОВЫШЕННОГО_ВНИМАНИЯ` первоисточника)
fn needs_elevated_attention(action ActionKind) -> bool => match action {
  ActionKind.Delete | ActionKind.Move | ActionKind.Execute | ActionKind.Network | ActionKind.SwitchMode => true
  _ => false
}
// таблица `ПОЛИТИКА_РАЗРЕШЕНИЙ` первоисточника: параметр проекта; здесь значения по умолчанию методики — «спросить» для всех видов
// псевдокод: таблица параметров проекта записана функцией; проект подставляет свои значения
fn project_policy(action ActionKind) -> str => match action {
  ActionKind.Read => "ask"
  ActionKind.Write => "ask"
  ActionKind.Delete => "ask"
  ActionKind.Move => "ask"
  ActionKind.Search => "ask"
  ActionKind.Execute => "ask"
  ActionKind.Network => "ask"
  ActionKind.Think => "ask"
  ActionKind.SwitchMode => "ask"
  ActionKind.Other => "ask"
}
// «решение_по_политике(вид_действия, вид)»: «спросить», «разрешить» или «отказать»
fn decision_by_policy(action ActionKind, kind CallerKind) -> str {
  if needs_elevated_attention(action) {
    if interactive(kind) { return "ask" }
    return "deny"
  }
  ro by_table = project_policy(action)
  if by_table == "ask" && !interactive(kind) { return "deny" }
  by_table
}
// «пауза_повтора(число_повторов)»: ПАУЗА_ПОВТОРА, умноженная на 2 в степени (число_повторов − 1)
fn retry_pause(retry_count int) -> int {
  mut pause = RETRY_PAUSE
  mut pass_number = 1
  while pass_number < retry_count {
    pause = pause * 2
    pass_number += 1
  }
  pause
}
// код вида действия — значение параметра события журнала; русское слово — по таблице слов значений в state-machine-journal.md
fn action_kind_word(action ActionKind) -> str => match action {
  ActionKind.Read => "read"
  ActionKind.Write => "write"
  ActionKind.Delete => "delete"
  ActionKind.Move => "move"
  ActionKind.Search => "search"
  ActionKind.Execute => "execute"
  ActionKind.Network => "network"
  ActionKind.Think => "think"
  ActionKind.SwitchMode => "switch_mode"
  ActionKind.Other => "other"
}
// число или `none` (значения нет) — значение параметра события журнала расхода
fn number_word(value Option[int]) -> str => match value {
  Some(number_value) => "${number_value}"
  None => "none"
}
// дробное или `none` (значения нет) — значение параметра события журнала расхода
fn float_word(value Option[f64]) -> str => match value {
  Some(number_value) => "${number_value}"
  None => "none"
}

// Методы Машины: данные автомата
// событие журнала расхода: `none` — транспорт значения не дал (одно событие на шаг, правило 31 даёт конверт)
fn usage_event(collected Usage) -> JournalEvent => journal_event("agent_usage", [
  param("session", "${collected.session}"), param("result", "${collected.result}"), param("model", "${collected.model.id}"),
  param("input", "${number_word(collected.tokens.input)}"), param("output", "${number_word(collected.tokens.output)}"),
  param("reasoning", "${number_word(collected.tokens.reasoning)}"), param("cache_read", "${number_word(collected.tokens.cache_read)}"),
  param("cache_write", "${number_word(collected.tokens.cache_write)}"), param("cost", "${float_word(collected.cost)}")])
// расход на пути, минующем УЧЁТ (общие события, дефект): запись собирается и пишется при входе в конец; на пути через УЧЁТ строка уже написана
fn MachineData @record_end_usage(environment MachineEnvironment) Journal Time -> () => match @usage {
  Some(_) => ()
  None => environment.write_journal(usage_event(@collect_usage(Time.now())))
}
// запись для диагностики: все переменные и хранилища (Вход ОШИБКИ)
fn MachineData mut @journal_machine_data(environment MachineEnvironment) Journal Time -> ()
// срок бездействия запроса к агенту: срок тишины запроса, плюс пауза повтора при ходе «повторить»; `0` значит «срока нет» (`нет` даёт `0`)
fn MachineData @turn_term() -> int => match @agent_request.limits.silence_term {
  Some(term) => term + (if @turn == "retry" { retry_pause(@retry_count) } else { 0 })
  None => 0
}
// запись расхода: собирается из того, что вернул транспорт (поля без значения — None); `обновлено` — момент записи
fn MachineData @collect_usage(updated int) -> Usage {
  ro request = @agent_request
  ro result = if @stop_reason == "" { "reply" } else { @stop_reason }
  ro model = match @transport_usage {
    Some(received) => received.model
    None => AgentModel { id: request.profile.model, provider: "", variant: request.profile.effort }
  }
  ro tokens = match @transport_usage {
    Some(received) => received.tokens
    None => TokenUsage { input: None, output: None, reasoning: None, cache_read: None, cache_write: None }
  }
  ro cost = match @transport_usage {
    Some(received) => received.cost
    None => None
  }
  ro context_used = match @transport_usage {
    Some(received) => received.context_used
    None => None
  }
  Usage {
    session: request.session, result, family: request.profile.family, model, tokens, cost,
    created: @started ?? updated, updated, context_used,
    trace: request.trace, step: request.step }
}

// Методы Машины для движка (протокол `Автомат`): состояния и события машины
fn MachineData @initial() -> State => Start
fn MachineData @pause_state() -> State => Pause
// значение «остановка» при «остановить» у ПАУЗЫ: «ПАУЗА: <слово остановки>»; слово остановки — параметр подключения фрагмента «Пауза» (раздел «Общие события» первоисточника), значение есть в таблице «конец → ответ»
fn MachineData @pause_stop_reason() -> str => "pause_halt"
fn MachineData @halted_state() -> State => Halted
fn MachineData @error_state() -> State => Errored
fn MachineData @immediate_event() -> Event => Immediate
fn MachineData @failure_event(reason FailCode) -> Event => Failure { reason }
// метка инварианта: четыре счётчика, которые не убывают (число_повторов, число_продолжений, число_возвратов, число_ходов); движок сравнивает покомпонентно после каждого перехода шага
fn MachineData @invariant_mark() -> []int => [@retry_count, @continuation_count, @return_count, @turn_count]
// «остановка» — причина остановки шага; пишут общие события движка и строки состояний
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
// как состояние-обращение обращается к сторонам: у шага всегда одна сторона (агент, вратарь или человек), вложенных машин нет;
// у ХОД_АГЕНТА срок бездействия — срок тишины запроса (`срок_хода`), у ворот вратаря и человека срока нет; возвратов формы в запросе движка нет:
// исправление формы идёт ходом «исправить» (строки ПРОВЕРКИ_ОТВЕТА)
fn MachineData @appeal(current State) -> Option[AppealDescription] => match @kind(current) {
  Appeal => Some(Single {
    party: appeal_party(current), idle_term: if current == AgentTurn { @turn_term() } else { 0 },
    nested: false,                                              // вложенных машин у шага нет: агент, вратарь и человек — стороны запросов
    form_returns: 0 })
  _ => None
}
// номер новой попытки одноадресной стороны: счётчик попыток (правило 15)
fn MachineData mut @next_attempt(party str) -> int => match party {
  "agent" => {
    @agent_attempt += 1
    @agent_attempt
  }
  "gatekeeper" => {
    @gatekeeper_attempt += 1
    @gatekeeper_attempt
  }
  "enhanced" => {
    @enhanced_attempt += 1
    @enhanced_attempt
  }
  _ => unreachable("party outside "agent", "gatekeeper", "enhanced"")
}
// рабочей копии попытки у роли «агент» нет: агент правит файлы задачи сразу, проверка «объект не менялся с начала попытки» не применяется
fn MachineData @object_changed_since_attempt(current State) Objects -> bool => false
// принимать файл попытки нечего (см. выше): повторяемо без вреда
fn MachineData mut @accept_attempt_file(id str) Objects -> () => ()
// последний, повторяемый без вреда этап: отмена открытого хода у транспорта (правило 13)
fn MachineData mut @execute(action Irreversible) Objects -> () => match action {
  CloseAgentTurn => object_ok(close_agent_turn(), "закрыть ход агента не удалось")
}
// предел одновременных запросов: у шага один (правило 21)
fn MachineData @request_limit() -> int => REQUEST_LIMIT
// вход, результат и событие стороны — в строку и обратно: через `Связь` ходят конкретные типы, а не типы машины
fn MachineData @encode_input(input RoleInput) -> PartyInput
fn MachineData @decode_result(result PartyResult) -> RoleResult
fn MachineData @decode_event(event PartyEvent) -> Event
fn MachineData @encode_output(output AgentReply) -> PartyOutput
// данные машины в строку снимка и обратно; формат — за реализацией хранилища
fn MachineData @capture() -> str
fn MachineData mut @restore(data str)
// подготовки при возобновлении у шага агента нет: сохранённое состояние входится сразу
fn MachineData mut @on_resume(saved State, environment MachineEnvironment) Journal Objects Time -> Option[Transition[State]] => None
// событие с данными по результату принятого ответа роли (метод протокола `Автомат`)
fn MachineData @reply_event(current State, role_result RoleResult) -> Event => match role_result {
  TurnOutcome(outcome) => match outcome {
    TurnResult.Finished { text, artifact, usage } => RepliedFinished { text, artifact, usage }
    TurnResult.Truncated { usage } => RepliedTruncated { usage }
    TurnResult.TurnRequestLimit { usage } => RepliedTurnRequestLimit { usage }
    TurnResult.ModelRefusal { usage } => RepliedModelRefusal { usage }
    TurnResult.Stopped { usage } => RepliedStopped { usage }
    TurnResult.TransientError => RepliedTransientError
    TurnResult.PermanentError => RepliedPermanentError
    TurnResult.NeedsPermission { permission_request } => RepliedNeedsPermission { permission_request }
  }
}

/// Вход запроса по таблице «Вход» обращения: строки «сторона» (и вся таблица ворот); строки «исполнитель» в запрос не входят.
fn MachineData @request_input(appeal State, party str, environment MachineEnvironment) Objects -> RoleInput => match appeal {
  AgentTurn => TurnInput {
    agent_request: @agent_request, turn: @turn, retry_count: @retry_count, turn_before_retry: @turn_before_retry, permission_decision: @permission_decision }
  Permission => PermissionInput {
    agent_request: @agent_request,
    permission_request: required(@permission_request, "Permission: the permission request is recorded in AgentTurn") }
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

  // ===================== СТАРТ — операция =====================
  Start => match event_body {
    // СТАРТ #1: сразу (начато: Число — миллисекунды эпохи)
    ImmediateStart { started: moment } => {
      @started = Some(moment)
      @turn_count = 1
      Go(AgentTurn)
    }
    _ => NotAwaited
  }

  // ===================== ХОД_АГЕНТА — обращение =====================
  AgentTurn => match event_body {
    // ХОД_АГЕНТА #1: ответ: закончен (текст: Текст или нет; артефакт: Текст или нет; расход: РасходТранспорта)
    RepliedFinished { text, artifact, usage: received } => {
      @transport_usage = Some(add_usage(@transport_usage, received))
      @reply_text = text
      @reply_artifact = artifact
      Go(ReplyValidation)
    }
    // ХОД_АГЕНТА #2: ответ: обрезан (расход: РасходТранспорта)
    RepliedTruncated { usage: received } => {
      @transport_usage = Some(add_usage(@transport_usage, received))
      Go(Continuation)
    }
    // ХОД_АГЕНТА #3: ответ: предел_запросов (расход: РасходТранспорта)
    RepliedTurnRequestLimit { usage: received } => {
      @transport_usage = Some(add_usage(@transport_usage, received))
      @stop_reason = "max_turn_requests"
      environment.write_journal(journal_event("turn_requests_exhausted", []JournalParam.new()))
      Go(Accounting)
    }
    // ХОД_АГЕНТА #4: ответ: отказ_модели (расход: РасходТранспорта)
    RepliedModelRefusal { usage: received } => {
      @transport_usage = Some(add_usage(@transport_usage, received))
      @stop_reason = "model_refused"
      environment.write_journal(journal_event("model_refused", []JournalParam.new()))
      Go(Accounting)
    }
    // ХОД_АГЕНТА #5: ответ: отменён (расход: РасходТранспорта)
    RepliedStopped { usage: received } => {
      @transport_usage = Some(add_usage(@transport_usage, received))
      @stop_reason = "stopped_by_agent"
      environment.write_journal(journal_event("turn_cancelled", []JournalParam.new()))
      Go(Accounting)
    }
    // ХОД_АГЕНТА #6: ответ: временная_ошибка
    RepliedTransientError => Go(Retry)
    // ХОД_АГЕНТА #7: ответ: постоянная_ошибка
    RepliedPermanentError => {
      @stop_reason = "no_result"
      environment.write_journal(journal_event("agent_permanent_error", []JournalParam.new()))
      Go(Accounting)
    }
    // ХОД_АГЕНТА #8: ответ: нужно_разрешение (запрос_разрешения: ЗапросРазрешения)
    RepliedNeedsPermission { permission_request: request } => {
      @permission_request = Some(request)
      Go(Policy)
    }
    // ХОД_АГЕНТА #9: сбой (причина: КодСбоя — у этого обращения: соединение оборвалось, нет ответа в срок или нет результата)
    Failure { reason } => {
      @stop_reason = fail_code_word(reason)
      environment.write_journal(journal_event("turn_failed", [param("reason", "${fail_code_word(reason)}")]))
      Go(Accounting)
    }
    _ => NotAwaited
  }

  // ===================== ПОВТОР — развилка =====================
  Retry => {
    // ПОВТОР #1: число_повторов меньше ЧИСЛО_ПОВТОРОВ, и ход не равен «повторить»
    if @retry_count < RETRIES && @turn != "retry" {
      @retry_count += 1
      @turn_before_retry = Some(@turn)
      @turn = "retry"
      environment.write_journal(journal_event("agent_transient_error", [param("retry", "${@retry_count}")]))
      return Go(Budget)
    }
    // ПОВТОР #2: число_повторов меньше ЧИСЛО_ПОВТОРОВ, и ход = «повторить»
    if @retry_count < RETRIES && @turn == "retry" {
      @retry_count += 1
      environment.write_journal(journal_event("agent_transient_error", [param("retry", "${@retry_count}")]))
      return Go(Budget)
    }
    // ПОВТОР #3: число_повторов не меньше ЧИСЛО_ПОВТОРОВ
    if @retry_count >= RETRIES {
      @stop_reason = "no_result"
      environment.write_journal(journal_event("agent_transient_error_exhausted", [param("retries", "${RETRIES}")]))
      return Go(Accounting)
    }
    // ПОВТОР #4: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "Retry")]))
  }

  // ===================== ПРОДОЛЖЕНИЕ — развилка =====================
  Continuation => {
    // ПРОДОЛЖЕНИЕ #1: число_продолжений меньше ЧИСЛО_ПРОДОЛЖЕНИЙ
    if @continuation_count < CONTINUATIONS {
      @continuation_count += 1
      @turn = "continue"
      environment.write_journal(journal_event("output_truncated_continue", []JournalParam.new()))
      return Go(Budget)
    }
    // ПРОДОЛЖЕНИЕ #2: число_продолжений не меньше ЧИСЛО_ПРОДОЛЖЕНИЙ
    if @continuation_count >= CONTINUATIONS {
      @stop_reason = "max_tokens"
      environment.write_journal(journal_event("output_truncated_again", []JournalParam.new()))
      return Go(Accounting)
    }
    // ПРОДОЛЖЕНИЕ #3: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "Continuation")]))
  }

  // ===================== ПРОВЕРКА_ОТВЕТА — развилка =====================
  ReplyValidation => {
    ro validation = reply_validation()
    // ПРОВЕРКА_ОТВЕТА #1: проверка_ответа = «верна»
    if validation == ReplyCheck.Valid { return Go(Accounting) }
    // ПРОВЕРКА_ОТВЕТА #2: проверка_ответа = «пуста»
    if validation == ReplyCheck.Empty {
      @stop_reason = "no_result"
      environment.write_journal(journal_event("agent_no_result", []JournalParam.new()))
      return Go(Accounting)
    }
    // ПРОВЕРКА_ОТВЕТА #3: проверка_ответа = «нарушена», и число_возвратов меньше ЧИСЛО_ВОЗВРАТОВ_ФОРМЫ
    if validation == ReplyCheck.Violated && @return_count < FORM_RETURNS {
      @return_count += 1
      @turn = "fix"
      environment.write_journal(journal_event("reply_form_violated", []JournalParam.new()))
      return Go(Budget)
    }
    // ПРОВЕРКА_ОТВЕТА #4: проверка_ответа = «нарушена», и число_возвратов не меньше ЧИСЛО_ВОЗВРАТОВ_ФОРМЫ
    if validation == ReplyCheck.Violated && @return_count >= FORM_RETURNS {
      @stop_reason = "form_not_fixed"
      environment.write_journal(journal_event("reply_form_not_fixed", []JournalParam.new()))
      return Go(Accounting)
    }
    // ПРОВЕРКА_ОТВЕТА #5: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "ReplyValidation")]))
  }

  // ===================== ПОЛИТИКА — развилка =====================
  Policy => {
    ro request = required(@permission_request, "Policy: the permission request is recorded in AgentTurn")
    ro decision = decision_by_policy(request.action, @agent_request.kind)
    // ПОЛИТИКА #1: решение_по_политике(вид_действия, вид) = «разрешить»
    if decision == "allow" {
      @permission_decision = Some("allow")
      @turn = "permission"
      environment.write_journal(journal_event("permission_auto_allowed", [param("action", "${action_kind_word(request.action)}")]))
      return Go(Budget)
    }
    // ПОЛИТИКА #2: решение_по_политике(вид_действия, вид) = «отказать»
    if decision == "deny" {
      @permission_decision = Some("deny")
      @turn = "permission"
      environment.write_journal(journal_event("permission_auto_denied", [param("action", "${action_kind_word(request.action)}")]))
      return Go(Budget)
    }
    // ПОЛИТИКА #3: решение_по_политике(вид_действия, вид) = «спросить»
    if decision == "ask" { return Go(Permission) }
    // ПОЛИТИКА #4: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "Policy")]))
  }

  // ===================== РАЗРЕШЕНИЕ — обращение =====================
  Permission => match event_body {
    // РАЗРЕШЕНИЕ #1: РАЗРЕШЕНИЕ: «разрешить»
    PermissionAllow => {
      ro request = required(@permission_request, "Permission: the permission request is recorded in AgentTurn")
      @permission_decision = Some("allow")
      @turn = "permission"
      environment.write_journal(journal_event("permission_human_allowed", [param("action", "${action_kind_word(request.action)}")]))
      Go(Budget)
    }
    // РАЗРЕШЕНИЕ #2: РАЗРЕШЕНИЕ: «отказать»
    PermissionDeny => {
      ro request = required(@permission_request, "Permission: the permission request is recorded in AgentTurn")
      @permission_decision = Some("deny")
      @turn = "permission"
      environment.write_journal(journal_event("permission_human_denied", [param("action", "${action_kind_word(request.action)}")]))
      Go(Budget)
    }
    _ => NotAwaited
  }

  // ===================== БЮДЖЕТ — развилка =====================
  Budget => {
    ro tokens_exhausted = token_limit_reached(@agent_request, @transport_usage)
    ro cost_exhausted = cost_limit_reached(@agent_request, @transport_usage)
    ro turns_exhausted = turn_limit_reached(@agent_request, @turn_count)
    // БЮДЖЕТ #1: предел токенов исчерпан
    if tokens_exhausted {
      @stop_reason = "max_tokens"
      environment.write_journal(journal_event("token_limit", [param("spent", "${tokens_spent(@transport_usage)}")]))
      return Go(Accounting)
    }
    // БЮДЖЕТ #2: предел токенов не исчерпан, и предел стоимости исчерпан
    if !tokens_exhausted && cost_exhausted {
      @stop_reason = "cost_limit"
      environment.write_journal(journal_event("cost_limit", [param("spent", "${cost_spent(@transport_usage)}")]))
      return Go(Accounting)
    }
    // БЮДЖЕТ #3: предел токенов не исчерпан, предел стоимости не исчерпан, и предел ходов исчерпан
    if !tokens_exhausted && !cost_exhausted && turns_exhausted {
      @stop_reason = "max_turn_requests"
      environment.write_journal(journal_event("turn_limit", [param("sent", "${@turn_count}")]))
      return Go(Accounting)
    }
    // БЮДЖЕТ #4: ни один предел не исчерпан
    if !tokens_exhausted && !cost_exhausted && !turns_exhausted {
      @turn_count += 1
      return Go(AgentTurn)
    }
    // БЮДЖЕТ #5: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "Budget")]))
  }

  // ===================== УЧЁТ — операция =====================
  Accounting => match event_body {
    // УЧЁТ #1: сразу (использование: Использование)
    ImmediateAccounting { usage: collected } => {
      @usage = Some(collected)
      environment.write_journal(usage_event(collected))
      Go(StepOutcome)
    }
    _ => NotAwaited
  }

  // ===================== ИТОГ_ШАГА — развилка =====================
  StepOutcome => {
    // ИТОГ_ШАГА #1: остановка = `""`
    if @stop_reason == "" { return Go(End) }
    // ИТОГ_ШАГА #2: остановка не равна `""`
    if @stop_reason != "" { return Go(Halted) }
    // ИТОГ_ШАГА #3: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "StepOutcome")]))
  }

  // ===================== ПАУЗА — обращение =====================
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
/// Работа операций при входе (в одном шаге с переходом; отказа и «нет ответа» у операции нет). Результат — событие: у СТАРТА — `Сразу_СТАРТ`, у УЧЁТА — `Сразу_УЧЁТ` с данными.
fn MachineData mut @run_operation(operation State, environment MachineEnvironment) Journal Objects Time -> Event => match operation {
  Start => ImmediateStart { started: Time.now() }
  Accounting => ImmediateAccounting { usage: @collect_usage(Time.now()) }
  _ => unreachable("the other states have no operation work")
}
```

## Приём ответа и запись результата

```nova
/// При приёме (правило 14): у обращений шага записи стороны нет (счётчики попыток ведёт механика контракта).
fn MachineData mut @on_accept(current State, response Response[RoleResult]) => ()

/// Запись принятого результата в хранилище (правила 8, 14): роль возвращает результат, в хранилище машины не пишет.
/// У шага результат ХОД_АГЕНТА идёт событием (расход, текст и артефакт машина запишет в переходе); у ворот результата роли нет.
fn MachineData mut @record_result(current State, response Response[RoleResult]) => ()
```

## Концы и ответ

```nova
/// Работа концов при входе (в последнем, повторяемом без вреда этапе фиксации) и ответ вызвавшей стороне.
/// Вход в любой конец отменяет все открытые запросы (правило 22); машина отвечает ровно один раз (правило 35).
fn MachineData mut @on_end_entry(end_state State, environment MachineEnvironment) Journal Time -> () => match end_state {
  // ОСТАНОВЛЕНО: открытый ход агента закрывается — транспорту сообщается об отмене, в том числе ходу, удержанному до решения о разрешении; если `использование` — `нет` (вход по
  //   общему событию, УЧЁТ не проходился), пишется строка расхода; в журнал — «шаг агента остановлен: <остановка>»; вызывающая машина получает `Refusal` (таблица «конец → ответ»).
  Halted => {
    environment.add_irreversible(Irreversible.CloseAgentTurn)
    @record_end_usage(environment)
    environment.write_journal(journal_event("agent_step_stopped", [param("reason", "${@stop_reason}")]))
  }
  // ОШИБКА: открытый ход агента закрывается; если `использование` — `нет`, пишется строка расхода; в журнал — запись из перехода и данные машины; вызывающая машина
  //   получает `Refusal` с текстом «дефект шага агента: <запись из перехода>»; решает человек вне машины.
  Errored => {
    environment.add_irreversible(Irreversible.CloseAgentTurn)
    @record_end_usage(environment)
    environment.write_journal(environment.transition_note())
    @journal_machine_data(environment)
  }
  // КОНЕЦ: ответ `Answer` с `ОтветАгента` уходит вызывающей машине; строка расхода в журнал уже записана состоянием УЧЁТ — своей строки у конца нет.
  End => ()
  _ => ()
}
// запись для диагностики: все переменные и хранилища (Вход ОШИБКИ) — сигнатура объявлена в разделе «Механика машины»

/// Таблица «конец → ответ» первоисточника (раздел «Контракт машины»): каждый конец и каждое значение остановка — одна строка.
fn MachineData @end_response(call_request Request[AgentRequest], end_state State, environment MachineEnvironment) -> Response[AgentReply] {
  match end_state {
    // КОНЕЦ, условие входа: всегда → СРезультатом: текст, артефакт и использование
    End => Answer(Reply {
      request: call_request.id, party: call_request.party, trace: call_request.trace, step: call_request.step,
      result: AgentReply {
        text: @reply_text, artifact: @reply_artifact,
        usage: required(@usage, "End: the usage is recorded in Accounting"),
        request_started: match @transport_usage {
          Some(received) => Some(received.request_started)
          None => None
        } } })
    // ОШИБКА, условие входа: всегда (дефект машины) → Отказ, НетРезультата; текст — запись из перехода
    Errored => refuse_with(call_request, NoResult, "дефект шага агента: ${environment.transition_note().code}")
    Halted => match @stop_reason {
      // ОСТАНОВЛЕНО: остановка = «нет результата» → Отказ, НетРезультата
      "no_result" => refuse_with(call_request, NoResult, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «отказ модели» → Отказ, ОтказМодели
      "model_refused" => refuse_with(call_request, ModelRefused, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «соединение оборвалось» → Отказ, СоединениеОборвалось
      "connection_lost" => refuse_with(call_request, ConnectionLost, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «форма не исправлена» → Отказ, ФормаНеИсправлена
      "form_not_fixed" => refuse_with(call_request, FormNotFixed, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «нет ответа в срок» → Отказ, НетОтветаВСрок
      "timeout" => refuse_with(call_request, Timeout, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «предел токенов» → Отказ, ПредельТокенов
      "max_tokens" => refuse_with(call_request, MaxTokens, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «предел стоимости» → Отказ, ПредельТокенов (отдельного кода для стоимости нет, решение 7 первоисточника)
      "cost_limit" => refuse_with(call_request, MaxTokens, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «предел запросов хода» → Отказ, ПредельЗапросовХода
      "max_turn_requests" => refuse_with(call_request, MaxTurnRequests, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «отменён агентом» → Отказ, ОтмененоРодителем
      "stopped_by_agent" => refuse_with(call_request, Cancelled, @stop_reason)
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
/// (обработчик `Связь` запуска сессии при запросе `ЗапросРоли` с входом `ЗапросАгента`).
fn start_agent_step(request Request[AgentRequest]) Time -> Response[AgentReply] =>
  with Store = store_handler, Journal = journal_handler, Link = link_handler, Objects = objects_handler {   // псевдокод: обработчики (база, файл поверх Fs/Db, очередь сообщений) — любые, вне файла
    mut engine_instance = Engine.new(MachineData.from_input(request.input))
    engine_instance.call(request)
  }
```

## Что движок не покрыл

Список мест, где шагу агента нужно то, чего движок [state-machine-engine-automaton.md](state-machine-engine-automaton.md) не давал: записано обходом внутри этой машины или функцией без тела. Номера пунктов в каждом файле свои: здесь открыты 1–9.

| № | Что нужно шагу агента | Что в движке | Обход в этом файле | Предлагаемое решение |
|---|---|---|---|---|
| 1 | Запрос стороны посреди запроса: агент просит разрешение, пока ход не закончен | Исходов запроса два: ответ и сбой (правила 16, 26); другого события у обращения роли нет | Результат `НужноРазрешение`: ход остаётся открытым, решение уходит новым запросом хода «разрешение» | Контракт: исход «вопрос стороны» с продолжением того же запроса |
| 2 | Ожидание измерения: форма ответа проверяется исполнителем (`verify_formats` по коду сессии или виду вызывающего) | Нет понятия «измеренный исполнителем объект»; у запуска сессии то же (`объём_запуска`) | Функция без тела `проверка_ответа` с эффектом `Объекты` | Слой методики: эффект `ОбъектыЗадачи` (измерение объёма, формата) |
| 3 | Необратимое действие «закрыть ход агента» (отмена удержанного хода) | Эффект `Объекты` — закрыть и открыть для записи, перенести в архив, прочитать байты, принять файл попытки | Функция без тела `закрыть_ход_агента` в этой машине | Движок: расширяемый `Объекты`; слой методики: `ОбъектыЗадачи` |
| 4 | Время начала и конца шага, миллисекунды эпохи (`создано`, `обновлено`) | `Time.now()`; тип результата принят как целое число | `Time.now()` как `int` в `выполнить_операцию` | Движок: подтвердить тип времени; для записи — `Timestamp` и преобразование |
| 5 | Конверт вызова в запросе `ЗапросАгента` (`трасса`, `номер_шага` вызывающего для записи расхода) | `Среда` не отдаёт машине трассу и номер шага; их знает только исполнитель | Поля `запрос.трасса`, `запрос.номер_шага` берутся из запроса (у вызывающей — функции без тела, запуск сессии, пункт 12) | Движок: методы `трасса()` и `номер_шага()` в `Среда` либо исключить поля из `ЗапросАгента` |
| 6 | Ворота человека — 2 состояния (РАЗРЕШЕНИЕ, ПАУЗА) и столько же вариантов `ВходРоли`, слова ворот — варианты `Событие` | `ВходРоли` и `Событие` — перечисления машины | Вариант на ворота и на слово ворот | Слой методики: тип «Ворота» (имя, показываемые данные, слова ворот как данные), одно событие «слово ворот» |
| 7 | Каркас вложенной машины (ПАУЗА вынесена фрагментом «Пауза»): ОСТАНОВЛЕНО, ОШИБКА, таблица «конец → ответ», `общее`, `записать_остановку` — те же, что у раннера, проверки цикла, запуска сессии и совещания | Движок даёт только протокол `Автомат`, реализации у него нет | Копия | Слой методики: базовая реализация каркаса |
| 8 | Рабочая копия попытки и проверка «объект не менялся с начала попытки»: у шага их нет, а протокол требует методы `объект_менялся_с_начала_попытки`, `принять_файл_попытки` | Оба метода обязательны в протоколе | Пустые методы | Движок: необязательный протокол «Рабочая копия попытки» |
| 9 | Запись расхода на пути, минующем УЧЁТ (общие события ведут прямо в ОСТАНОВЛЕНО): запись собирается при входе в конец | Конец не может менять данные машины (правило 29); `при_входе_в_конец` — механика исполнителя | Метод `записать_расход_конца`: собирает запись и пишет строку журнала, данные машины не меняет (решение 8 первоисточника) | Слой методики: запись расхода — необратимое действие конца, повторяемое без вреда |
