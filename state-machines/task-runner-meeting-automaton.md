# Совещание агентов: код автомата

Стейт-машина совещания, записанная кодом на языке Нова как реализация протокола `Автомат` движка [state-machine-engine-automaton.md](state-machine-engine-automaton.md): данные машины, перечисления `Состояние` и `Событие`, переход `перейти(состояние, событие)` как `match`, вызовы вложенной машины «Шаг агента» и ворота человека (входы и результаты), ответ по концу по контракту машины, константы совещания. Всё общее — конверт запроса и ответа, исполнитель, снимок и хранилище, общие события «стоп/продолжить/отмена», цикл, фиксации — в движке. Нормы — [methodology.md](../methodology.md), раздел 18, «Согласование решения несколькими агентами». Идентификаторы кода английские, словарь — [state-machine-glossary.md](state-machine-glossary.md); русские имена — в описаниях и комментариях.

**Первоисточник — [task-runner-meeting-states.md](task-runner-meeting-states.md)** (таблицы состояний, общие события, «Контракт машины»); правила формы — [state-machine-spec.md](state-machine-spec.md). Этот файл — производная запись того же автомата: при расхождении верен первоисточник, а этот файл правится вслед за ним. Язык записи — Нова, https://github.com/nv-lang/nova. **Код не компилировался и не проверялся компилятором Нова:** это псевдокод в синтаксисе Нова; соглашения записи, помеченные места (`// псевдокод:`), подтверждённое и неподтверждённое спецификацией — в [state-machine-engine-automaton.md](state-machine-engine-automaton.md), здесь только относящееся к совещанию. Расширения, отличия от псевдокода раннера и опытный статус описаны в шапке первоисточника; раннером машина не исполняется. Схема раннера ([task-runner-pseudocode.md](task-runner-pseudocode.md), [task-runner-meeting-pseudocode.md](task-runner-meeting-pseudocode.md)) — другая форма записи, помечена устаревшей и этим файлом не заменяется. Модельные вызовы совещания — линзы, свидетель и автор (состояния ЛИНЗЫ, СВИДЕТЕЛЬ, ПРАВКА и ВОПРОС) — идут вложенными вызовами машины «Шаг агента» — [state-machine-agent-step-automaton.md](state-machine-agent-step-automaton.md) (первоисточник — [state-machine-agent-step-states.md](state-machine-agent-step-states.md)) — по контракту вызова движка (`Вызываемое`, эффект `Связь`: запрос уходит как `ЗапросРоли`, ответ приходит сообщением), как у запуска сессии; общие типы запроса и ответа (`ЗапросАгента`, `ОтветАгента`, `ВидВызывающего`, `ПрофильАгента`, `ПределыАгента`) объявлены в слое методики. Имя файла — по `AGENTS.md`, «Вынесенные алгоритмы», форма `automaton`.

## Соглашения записи

1. **Типы и идентификаторы** — по [движку](state-machine-engine-automaton.md), пункты 1–3: английские имена по [словарю](state-machine-glossary.md), таблица соответствия именам блока «Типы на Нове» первоисточника — ниже. Новых типов данных нет (вход паузы `ВходПаузы` и типы вызова агента `ВидВызывающего`, `ПрофильАгента`, `ПределыАгента`, `ЗапросАгента`, `ОтветАгента` — из [слоя методики](state-machine-methodology-automaton.md); вариант `ВходРоли` для входа паузы — `ВходПаузыРоли`, для запроса агента — `ЗапросАгентаРоли`); записи автомата совещания — `ИтогЛинзы` (то, что возвращает линза после разбора артефакта: находки и пробы), `РезультатРоли`, `ВходРоли`, `КонтекстРоли`, `Окружение`, `Необратимое`.
2. **Данные события.** Поля варианта события берутся образцом в `match`: `Сбой { причина } => …`; при совпадении имени поля с переменной машины поле переименовывается: `В7_ответил { ответ_человека: слово_ответа }`. «Сторона события» и идентификатор события — `событие.сторона`, `событие.идентификатор` (конверт `Входящее` движка, правила 13 и 31). Шаблон строки журнала «<сторона события>» — `${событие.сторона}`. Служебные операции переходу даёт `среда` (журнал, слова человека, сигналы вложенным, данные движка `к_отправке`, `открытые_запросы`, `предыдущее`, `запрос_вызова`).
3. **Строка таблицы — ветка кода.** Перед каждой строкой первоисточника (условие или событие, «Что меняется», «Куда») стоит комментарий `// <СОСТОЯНИЕ> #<номер строки>: …` с её текстом; порядок строк как в первоисточнике. Строка «иначе» каждой развилки — последняя ветка, ведёт в `ОШИБКА`. Строки «Вход», «Выход», «При входе», «Сторона» и строка простыми словами — комментарии `//` у состояния. Шесть строк «ОБЩ …» общих событий записаны в движке (`общие_события`); `общее` машины сводит к ним её события. Состояние ПАУЗА и его четыре строки подключены фрагментом «Пауза» ([state-machine-pause-states.md](state-machine-pause-states.md)): события паузы разбирает движок (`общие_события`), у машины остаются ветка `ПАУЗА => НеЖдёт`, хуки `состояние_паузы`, `причина_остановки_в_паузе`, `состояние_по_имени` и сведение событий паузы в `общее`.
4. **Строки `// псевдокод:`** и перечень подтверждённого спецификацией — в [движке](state-machine-engine-automaton.md), пункт 5. Здесь дополнительно: значения констант совещания (параметры проекта); функции без тела (сигнатуры механики); алиас `type Окружение alias Среда[…]` (в спецификации — `type StringMap[V] alias HashMap[str, V]`; алиас протокола с параметрами — вывод, не цитата); ключ-кортеж `HashMap[(str, int), …]` у `находки_линзы` — в Нове он пока ломает кодогенерацию (запись M-hashmap-tuple-key-mono, открыта), поэтому в Нове пока вложенное отображение `HashMap[str, HashMap[int, V]]` или составной ключ-строка. **Отображения.** У `HashMap` нет `[]` и `get_mut`: чтение — `get(ключ) -> Option[V]` (в `линзы`, `свод`, `аннулирований`), запись — `insert(ключ, значение)`; поле записи линзы меняется вставкой изменённой копии (`установить_потери`, `установить_пробы`, `установить_попытку`). **Именование читателей по ключу:** читатель элемента поля называется по полю (`@свод(номер)`, `@аннулирований(номер)`, `@линзы(идентификатор)`) — форма чтения свойства по слову владельца, 2026-10-18; поле и метод с одним именем на одном типе в Нове допустимы (`spec/decisions/03-syntax.md`, правило `@name`: «`@name` без `()` — поле, `@name()` — вызов метода»; прецедент — `Vec`, поле `len` и метод `len()` в `std/src/collections/vec/core.nv`; проверено оркестратором проекта, 2026-10-18). Неподтверждённое спецификацией Нова, используемое здесь: объявление `module` и импорт `use` слоя методики, `const` на уровне модуля, `return` внутри `if` в ветке `match` и в теле функции, `while` не используется.
5. **Уточнения записи автомата сверх первоисточника:** ветка `None` у `копия` в ВОЗВРАТЕ пишет строку журнала «ВОЗВРАТ: копии нет» (недостижима: копию пишет ЗАМОК); `РезультатРоли` — сумма разобранных результатов вызовов шага агента по обращениям первоисточника (`РезультатСвидетеля`, `РезультатЛинзы`, `РезультатПравки`; исполнитель разбирает артефакт `ОтветАгента` при приёме, `разобрать_ответ_агента`); `ВходРоли` — сумма входов запроса: `ЗапросАгентаРоли` у четырёх обращений к шагу агента и по варианту на ворота человека (девять вариантов); `КонтекстРоли` — сумма данных, из которых исполнитель собирает `контекст` запроса агента (по варианту на обращение, поля — строки «Вход» со значением «сторона»); у ворот человека результата роли нет — слово приходит событием; `ВходВ3.свод` — `Option`: свод есть всегда, итог внутри него может отсутствовать (РАЗБОР #3 ведёт в В3). Метод `событие_ответа` — отображение результата роли в событие (`Ответ`, `Ответ_закончена`, `Ответ_вопрос`); `при_возобновлении` — заглушка (подготовки при возобновлении нет). Отличие от первоисточника: `запрос_вызова` — всегда `запрос.идентификатор_запроса` (решение о `""` у верхнего уровня открыто, см. движок, пункт 6). Вложенная сторона — поле `вложенная` описания обращения: `true` у ЛИНЗ, СВИДЕТЕЛЯ, ПРАВКИ и ВОПРОСА (вызов шага агента), `false` у ворот человека; срок бездействия запроса — `0` у всех (у вызова вложенной машины срока нет, правило 35, пункт 5), срок тишины агента — `пределы_роли`; `возвратов_формы` — у СВИДЕТЕЛЯ `1`: возврат сверки выдержки идёт новым запросом той же стороны (решение 6 первоисточника), у остальных `0`: общую форму возвращает шаг агента.
6. **Данные машины — поля типа `Машина`**, а не переменные модуля: поля названы как переменные раздела «Данных» первоисточника (правило 25), начальные значения — в `Машина.new()`, по входу совещания — `Машина.из_входа`. Данные движка (конверт, очереди запросов, журнал, слова человека) — в `СостояниеДвижка` движка. Методы `Машина` читают и пишут только свои поля; данные движка и служебные операции — через `среда`. Имя `Машина`: `Состояние` занято перечнем состояний; имя русское, как имена данных.
7. **`недостижимо(текст)`** (определено в движке, пункт 8): в реализации стоит: у концов ОСТАНОВЛЕНО, ОШИБКА, КОНЕЦ в `перейти` (переходов нет); в `ответ_по_концу` (значение `остановка` вне таблицы; ответ не из конца); в `выполнить_операцию` (состояние без операции); в `при_приёме` и `записать_результат` (вариант результата роли не соответствует состоянию); в `вход_запроса` (обязательное поле входа пусто — `обязательное` движка; состояние не обращение); в `счётчик_попыток` и `увеличить_счётчик_попыток` (сторона вне «свидетель», «автор», «вратарь», «человек»); в `линзы` (записи линзы нет).

Соответствие типов и полей:

| Первоисточник | Русское имя (описания, таблицы) | Код и блок «Типы на Нове» (латиница) |
|---|---|---|
| Число, Текст | `int`, `str` | `int`, `str` (стандартные имена Нова) |
| Линза: идентификатор, потери_подряд, пробы, попытка | `Линза`: `идентификатор`, `потери_подряд`, `пробы`, `попытка` | `Lens`: `id`, `lost`, `probes`, `attempt` |
| Запрос: идентификатор_запроса, номер_попытки, сторона, вход, срок_бездействия, трасса, номер_шага | `Запрос[Вход]`: `идентификатор_запроса`, `номер_попытки`, `сторона`, `вход`, `срок_бездействия`, `трасса`, `номер_шага` | `Request[T]`: `id`, `attempt`, `party`, `input`, `idle_term`, `trace`, `step` |
| Ответ (с результатом): запрос, сторона, результат, трасса, номер_шага | `ОтветСРезультатом[Результат]`: `запрос`, `сторона`, `результат`, `трасса`, `номер_шага` | `Reply[R]`: `request`, `party`, `result`, `trace`, `step` |
| Ответ (отказ): запрос, сторона, причина, текст, трасса, номер_шага | `ОтветОтказ`: `запрос`, `сторона`, `причина`, `текст`, `трасса`, `номер_шага` | `Rejection`: `request`, `party`, `reason`, `text`, `trace`, `step` |
| Ответ: с результатом, отказ | `Исход[Результат]`: `СРезультатом(ОтветСРезультатом[Результат])`, `Отказ(ОтветОтказ)` | `Response[R]`: `Answer(Reply[R])`, `Refusal(Rejection)` |
| КодСбоя: нет результата, отказ модели, соединение оборвалось, форма не исправлена, нет ответа в срок, остановлено человеком, потолок заходов с открытыми находками, отменено родителем, предел токенов, предел запросов хода | `КодСбоя`: `НетРезультата`, `ОтказМодели`, `СоединениеОборвалось`, `ФормаНеИсправлена`, `НетОтветаВСрок`, `ОстановленоЧеловеком`, `ПотолокЗаходов`, `ОтмененоРодителем`, `ПредельТокенов`, `ПредельЗапросовХода` | `FailCode`: `NoResult`, `ModelRefused`, `ConnectionLost`, `FormNotFixed`, `Timeout`, `StoppedByHuman`, `CeilingReached`, `Cancelled`, `MaxTokens`, `MaxTurnRequests` |
| ОтветСвидетеля: с утверждением, не измерено | `ОтветСвидетеля`: `СУтверждением(Утверждение)`, `НеИзмерено(str)` | `WitnessAnswer`: `Answered(Claim)`, `NotMeasured(str)` |
| Утверждение: вид, утверждение, источник, выдержка, сверка | `Утверждение`: `вид`, `утверждение`, `источник`, `выдержка`, `сверка` | `Claim`: `kind`, `statement`, `source`, `excerpt`, `check` |
| Сверка: подтверждено, искажение канала, не подтверждено | `Сверка`: `Подтверждено`, `ИскажениеКанала`, `НеПодтверждено` | `Check`: `Confirmed`, `ChannelDistortion`, `NotConfirmed` |
| ИтогПравки: закончена, вопрос | `ИтогПравки`: `Закончена(str)`, `Вопрос(ВопросПравки)` | `EditResult`: `Done(str)`, `Asked(Asking)` |
| ИтогПравки (вопрос): предложение, вопрос | `ВопросПравки`: `предложение`, `вопрос` | `Asking`: `proposal`, `question` |
| Находка: критичность, доказательство, повтор, вопрос | `Находка`: `критичность`, `доказательство`, `повтор`, `вопрос` | `Finding`: `severity`, `evidence`, `repeat`, `question` |
| Критичность: критическая, значимая, желательная | `Критичность`: `Критическая`, `Значимая`, `Желательная` | `Severity`: `Critical`, `Significant`, `Desirable` |
| Свод: итог (K, P) | `Свод`: `критических`, `проб` | `Summary`: `critical`, `probes` |
| ВходСовещания: предложение, порядок_линз, вопрос_автора | `ВходСовещания`: `предложение`, `порядок_линз`, `вопрос_автора` | `MeetingInput`: `proposal`, `lens_order`, `author_question` |
| ИтогСовещания: решение, источник, число_заходов, открытые | `ИтогСовещания`: `решение`, `источник`, `число_заходов`, `открытые` | `MeetingResult`: `decision`, `source`, `passes`, `open` |
| Записи автомата (не из первоисточника): состояние, событие, вид состояния, сообщение, входящее событие, переход | `Состояние`, `Событие`, `Вид`, `Сообщение`, `Входящее`, `РезультатРоли`, `ВходРоли`, `КонтекстРоли`, `ОшибкаХранилища`, `Переход`: `Куда`, `Заново`, `Остаться`, `НеЖдёт` | `State`, `Event`, `Kind`, `Incoming`, `Transition`: `Go`, `Rerun`, `Stay`, `NotAwaited`; `RoleResult`, `RoleInput`, `RoleContext` — запись автомата; `Message`, `StoreError` — типы движка; в блоке «Типы на Нове» их нет |
| ЗапросАгента, ОтветАгента, ВидВызывающего, ПрофильАгента, ПределыАгента | те же имена, объявлены в [слоя методики](state-machine-methodology-automaton.md) | `AgentRequest`, `AgentReply`, `CallerKind`, `AgentProfile`, `AgentLimits` (поля — там же) |
| Функции записи автомата: функция переходов, недостижимая ветка | `перейти`, `недостижимо` | `step`, `unreachable` |
| Параметры типов: вход запроса, результат роли | `Вход`, `Результат` | `T`, `R` |

Имена, которых нет в первоисточнике и которые завела запись автомата (не данные машины): `ИтогЛинзы`, `РезультатРоли`, `ВходРоли`, `КонтекстРоли`, `Окружение`, `Необратимое`, варианты `Событие` с префиксом ворот (`В13_повторить`, …; один вариант на слово ворот строки первоисточника), `Машина.из_входа`, методы машины для протокола `Автомат` (`начальное`, `общее`, `обращение`, `следующая_попытка` и др.), функции раздела «Механика машины». Типы и функции движка (`Исполнитель`, `Снимок`, `Хранилище`, `Автомат`, `Среда`, `Входящее`, `Переход`, `Куда`, `Заново`, `Остаться`, `НеЖдёт`, `перейти` и др.) — в [state-machine-engine-automaton.md](state-machine-engine-automaton.md).

## Типы

```nova
module meeting

// псевдокод: общий вход паузы, типы вызова агента, отпечаток и арифметика цикла из слоя методики; импорт модулей — вне записи (соглашения, п. 4)
use methodology.{Cycle, NoProbesDecision, PauseInput, CallerKind, AgentProfile, AgentLimits, AgentRequest, AgentReply, fingerprint, ceiling_reached, reset_origin, no_probes_step}

/// Линза
type Lens { id str, lost int, probes int, attempt int }

/// ОтветСвидетеля
type WitnessAnswer enum
  | Answered(Claim)
  | NotMeasured(str)

/// ОтветСвидетеля (с утверждением)
type Claim { kind str, statement str, source str, excerpt Option[str], check Check }

/// Сверка
type Check enum
  | Confirmed
  | ChannelDistortion
  | NotConfirmed

/// ИтогПравки
type EditResult enum
  | Done(str)
  | Asked(Asking)

/// ИтогПравки (вопрос)
type Asking { proposal str, question str }

/// Находка
type Finding { severity Severity, evidence str, repeat bool, question bool }

/// Критичность
type Severity enum
  | Critical
  | Significant
  | Desirable

/// Свод
type Summary { critical int, probes int }

/// ВходСовещания
type MeetingInput { proposal str, lens_order []str, author_question Option[str] }

/// ИтогСовещания; число_заходов = номер_захода при принятии; потолок и число_заходов считаются по номерам заходов, включая не засчитанный как чистый
type MeetingResult { decision str, source str, passes int, open []Finding }

/// Запись автомата: итог линзы (находки и пробы), результат роли ЛИНЗЫ
type LensResult { findings []Finding, probes int }

/// Запись автомата: результат роли — по варианту на обращение первоисточника, где сторона возвращает результат (раздел «Состояния»: Выход); это разобранный результат:
/// сторона вызова — вложенная машина «Шаг агента» — возвращает `ОтветАгента`, а типы совещания исполнитель разбирает из его артефакта при приёме (`разобрать_ответ_агента`, решение 3 первоисточника);
/// у ворот человека результата роли нет: слово человека приходит событием (`Слово`), а не исходом запроса.
type RoleResult enum
  | WitnessOutcome([]WitnessAnswer)    // СВИДЕТЕЛЬ: ответы_свидетеля[номер_захода]
  | LensOutcome(LensResult)               // ЛИНЗЫ: находки_линзы[линза, номер_захода]; пробы
  | EditOutcome(EditResult)             // ПРАВКА и ВОПРОС: итог_правки

/// Запись автомата: вход запроса — по варианту на обращение первоисточника; у обращений к шагу агента (ЛИНЗЫ, СВИДЕТЕЛЬ, ПРАВКА, ВОПРОС) вход — запрос агента,
/// а строки «Вход» со значением «сторона» входят в его `контекст` (`КонтекстРоли`); у ворот — строки таблицы «Вход» состояния, читаемые стороной (у ворот без столбца «Кто читает» — вся таблица); необязательное поле — Option
type RoleInput enum
  | RoleAgentRequest(AgentRequest)                                                           // ЛИНЗЫ, СВИДЕТЕЛЬ, ПРАВКА, ВОПРОС (вложенная машина «Шаг агента»); `контекст` собирает `контекст_роли` по `КонтекстРоли`
  | FailureInput { failed_appeal str }                                                       // СБОЙ
  | ChangedInput { copy str, proposal Option[str] }                                     // ИЗМЕНЁН: предложение может быть нечитаемо
  | RetryInput                                                                              // ПОВТОР: входа нет
  | Gate3Input { summary Option[Summary], lens_findings []Finding }                                    // В3: свод (объект) есть всегда, а его итог — `Свод` — может отсутствовать (None — итога нет, РАЗБОР #3); находки по каждой линзе
  | Gate9Input { gate3_findings []Finding, number int, origin int }                     // В9
  | Gate7Input { author_question str }                                                             // В7
  | AcceptanceInput { proposal str, number int, open []Finding }                   // ПРИНЯТИЕ
  | RolePauseInput(PauseInput)                                          // ПАУЗА

/// Запись автомата: контекст запроса агента — данные, из которых исполнитель собирает непрозрачный текст `контекст` (`контекст_роли`); по варианту на обращение к шагу агента,
/// поля — строки таблицы «Вход» состояния со значением «сторона»; необязательное поле — Option. Шаг агента и слой методики контекст не разбирают.
type RoleContext enum
  | WitnessContext { author_question Option[str], lens_findings Option[[]Finding], proposal str }   // СВИДЕТЕЛЬ: находки — из них вопросы проверяющих (вопрос = да), по каждой линзе
  | LensContext { proposal str, witness_answers Option[[]WitnessAnswer] }                // ЛИНЗЫ: ответы свидетеля — только запрошенной линзе
  | FixContext { proposal str, gate3_findings []Finding, author_guidance Option[str] }        // ПРАВКА: из находки_В3 критические всегда и значимые только без повтора
  | QuestionContext { author_question str, proposal str, gate3_findings []Finding, human_answer str }   // ВОПРОС: ответ_человека — только автору

/// Необратимое действие во внешнем мире: последний этап фиксации, повторяемый без вреда (правило 13: переименование в архив, смена права записи).
type Irreversible enum
  | CloseForWriting(str)
  | OpenForWriting(str)
  | MoveToArchive { pass_number int, suffix int }

/// Окружение перехода совещания: `Среда` движка с типами совещания.
type MachineEnvironment alias Environment[State, Event, Irreversible]
```

Там, где итога свода может не быть, — `Option[Свод]`.

## Данные

```nova
/// Константы и параметры совещания (task-runner.md, начало и «Срок бездействия роли»); предел одновременных запросов отдаёт движку метод `предел_запросов`; СРОК_БЕЗДЕЙСТВИЯ идёт в `пределы_роли` как срок тишины вложенного вызова (`0` — срока нет), срок бездействия самого запроса к вложенной машине — `0` (решение 5 первоисточника)
// псевдокод: значения констант — параметры проекта (task-runner.md), в этом файле не задаются; 0 — заглушка
const CEILING int = 0
const CLEAN_NEEDED int = 0
const PROBES_MIN int = 0
const IDLE_TERM int = 0

/// Предел одновременных запросов: не меньше 1, параметр проекта (правило 21); раннер исполняет только 1; движку отдаёт метод `предел_запросов`
const REQUEST_LIMIT int = 1

/// Машина совещания: данные совещания в одной записи (раздел «Данные» первоисточника); поля названы как переменные первоисточника.
/// Машина — данные и логика совещания: методы этого типа с ресивером `@` читают и пишут только эти поля; данные движка и служебные операции — через `среда`.
/// Машина реализует `Автомат[Состояние, Событие, ВходСовещания, ИтогСовещания, ВходРоли, РезультатРоли, Необратимое]` структурно.
type MachineData {
  // Переменные машины (состояние машины); сохраняются целиком вместе со снимком (правило 22); данные движка (конверт, очереди запросов, журнал) — в `СостояниеДвижка`
  number int,                            
  origin int,                           // заход, от которого считается потолок
  streak int,                            
  no_probes int,                         
  voided HashMap[int, int],             // [номер_захода]; начально 0; k в `*.void-<k>.md`
  lenses HashMap[str, Lens],                    // по записи на идентификатор из порядок_линз: потери_подряд 0, пробы 0, попытка 0; потери_подряд и попытка сохраняются между заходами
  witness_attempt int,                       // счётчики попыток одноадресных обращений (правило 15)
  author_attempt int,                          
  gatekeeper_attempt int,                         
  enhanced_attempt int,                        
  responded int,                              // число линз, ответивших в этом заходе
  failed_appeal str,                       // СВИДЕТЕЛЬ, ЛИНЗЫ, ПРАВКА или ВОПРОС: чей запрос закончился сбоем и ждёт ворот В13
  human_answer str,                          // слово человека у В7 с источником, вход ВОПРОСА
  author_guidance str,                         // решение_человека у В9 для правки автора
  stop_reason str,                               // почему совещание останавливается: исход ворот или «ни одна линза не ответила»
  confirmation str,                           // слово человека на воротах «принять итог»
  gate3_findings []Finding,                        // находки последнего засчитанного захода после поправки человека у В3; вход правки автора
  open []Finding,                          // находки засчитанных заходов, не переданные в правку автора; идут в итог как «открыто»
  // Внешние объекты (хранилище и задание): пишет исполнитель при приёме ответа или в операции вместе с шагом; роль и переход их не пишут
  proposal str,                             // = входной документ совещания
  copy Option[str],                           // текст предложения на начало захода; пишет ЗАМОК
  copy_fingerprint Option[str],               // отпечаток предложения на начало захода; пишет ЗАМОК; по нему СВЕРКА замечает правку за время проверки
  witness_answers HashMap[int, []WitnessAnswer], // [номер_захода]; нет, пока вопросов в заходе не было
  lens_findings HashMap[(str, int), []Finding], // псевдокод: ключ-кортеж; [линза, номер_захода]; начально нет; после ФИЛЬТРА на том же месте без несостоятельных
  summary HashMap[int, Summary],                      // [номер_захода]; начально нет; итоговая строка и находки с меткой линзы
  archive str,                                   // ответы и находки недействительных заходов, вне контекста ролей
  author_question Option[str],                   // вопрос автора человеку, с которым он остановил правку; сбрасывается в None после ответа свидетеля
  lens_order []str,                          // задание совещания, не хранилище: идентификаторы по порядку запуска; непустой, различны и отличны от «свидетель», «автор», «вратарь», «человек»; пишется при старте один раз
}

/// Начальные значения данных машины — раздел «Данные» первоисточника.
fn MachineData.new() -> MachineData => {
  number: 1,
  origin: 1,
  streak: 0,
  no_probes: 0,
  voided: HashMap[int, int].new(),
  lenses: HashMap[str, Lens].new(),
  witness_attempt: 0,
  author_attempt: 0,
  gatekeeper_attempt: 0,
  enhanced_attempt: 0,
  responded: 0,
  failed_appeal: "",
  human_answer: "",
  author_guidance: "",
  stop_reason: "",
  confirmation: "",
  gate3_findings: []Finding.new(),
  open: []Finding.new(),
  proposal: "",
  copy: None,
  copy_fingerprint: None,
  witness_answers: HashMap[int, []WitnessAnswer].new(),
  lens_findings: HashMap[(str, int), []Finding].new(),   // псевдокод: ключ-кортеж (см. п. 7)
  summary: HashMap[int, Summary].new(),
  archive: "",
  author_question: None,
  lens_order: []str.new(),
}

/// Машина по входу совещания: предложение, вопрос автора, порядок линз и записи линз.
fn MachineData.from_input(input MeetingInput) -> MachineData {
  mut machine = MachineData.new()
  machine.proposal = input.proposal
  machine.author_question = input.author_question
  machine.lens_order = input.lens_order
  for lens_id in machine.lens_order {
    machine.lenses.insert(lens_id, Lens { id: lens_id, lost: 0, probes: 0, attempt: 0 })
  }
  machine
}
```

## Инварианты

```nova
// 1. Шаг повышенного внимания: решает человек (по умолчанию) или агент по настройке проекта «исполнитель шагов повышенного внимания» (`исполнитель_повышенного_внимания`); ворота В14, В15, В5, В10а–г, В12, продолжение после «стоп человека» и решения закрытого списка раздела 4 — дорогие: их решает человек (по умолчанию) или усиленный вратарь — только по разрешению владельца в настройке проекта `усиленный_вратарь` (по умолчанию «нет») и с усиленными требованиями (`methodology.md`, раздел 18, «Вратарь»). Повышенное внимание — свойство шага: решение требует осознанного выбора и записи основания; основание пишется всегда, а в журнале — кто решил на самом деле (`решил`: «человек» или «агент») — на воротах В3, В7, В9, В13, ПАУЗА и «принять итог», а сигналом «стоп человека» — в любой момент;
//    исполнитель считает, переключает состояния и пишет журнал. Исключение — В3 в режиме «показать и продолжить», если человек так настроил.
//    В коде: события ворот приходят от стороны «вратарь» (ворота, на которые вправе ответить вратарь) или «усиленный» (дорогие ворота и ПАУЗА: отвечает усиленный вратарь по разрешению, иначе человек) — имя роли ворот, кто исполняет её на деле, пишет `решил` (у вызванной машины в ПАУЗЕ — «от родителя»); перейти их не порождает.

// 2. номер_захода не уменьшается: движок после каждого перехода шага сверяет `метка_инварианта` (у совещания — номер_захода) с её значением до шага
```

## Состояния

```nova
type State enum
  // развилки
  | Pass | LensRefusal | AllClosed | RequestRetry | Comparison | ReviewParsing | NoProbes | Totals | Ceiling
  // операции
  | Lock | Unlock | CopyRestore | Void | Filter | SummaryBuilding
  // обращения
  | Witness | Lenses | FailedRequest | Changed | Retry | Gate3 | Gate9 | AuthorFix | Gate7 | AuthorQuestion | Acceptance | Pause
  // концы
  | Halted | Errored | End

/// Начальное состояние — ЗАХОД. Вид состояния (обращение, операция, развилка, конец) по первоисточнику, раздел «Состояния».
fn MachineData @kind(state State) -> Kind => match state {
  Witness | Lenses | FailedRequest | Changed | Retry | Gate3 | Gate9 | AuthorFix | Gate7 | AuthorQuestion | Acceptance | Pause => Appeal
  Lock | Unlock | CopyRestore | Void | Filter | SummaryBuilding => Operation
  Pass | LensRefusal | AllClosed | RequestRetry | Comparison | ReviewParsing | NoProbes | Totals | Ceiling => Fork
  Halted | Errored | End => Final
}

/// Правка автора: обращения, где пишется предложение (ПРАВКА, ВОПРОС)
fn author_edits(state State) -> bool => match state {
  AuthorFix | AuthorQuestion => true
  _ => false
}
```

## События

```nova
type Event enum
  // общие события: разбираются до строк состояний (раздел «Общие события»)
  | StopFromHuman { human_word str, author str, source str }
  | StopFromParent { id str }
  | CancelRequest { id str }
  // исходы запроса роли (правила 16, 26); у каждого есть событие.сторона
  | Replied                                   // СВИДЕТЕЛЬ, ЛИНЗЫ: «ответ»
  | RepliedDone                         // ПРАВКА, ВОПРОС: «ответ: закончена» (вариант Закончена итога правки)
  | RepliedAsked                            // ПРАВКА, ВОПРОС: «ответ: вопрос» (вариант Вопрос итога правки)
  | Failure { reason FailCode }               // «сбой»; у ЛИНЗЫ событие.сторона — идентификатор линзы
  // исход операции
  | Immediate                                   // «сразу»
  | ImmediateFilter { lenses_without_critical []str }   // «сразу» с данными ФИЛЬТРА: идентификаторы
  // слова ворот человека
  | Gate13Repeat                           // СБОЙ, ПОВТОР: «В13: «повторить»»
  | Gate13HaltMeeting                // СБОЙ, ИЗМЕНЁН: «В13: «остановить совещание»»
  | Gate13Halt                          // ПОВТОР: «В13: «остановить»»
  | Gate13KeepEdit                     // ИЗМЕНЁН: «В13: «оставить правку»»
  | Gate13RestoreCopy                       // ИЗМЕНЁН: «В13: «вернуть копию»»
  | Gate3NotCounted                          // «В3: «не засчитан»»
  | Gate3Counted { gate3_findings []Finding }    // «В3: «засчитан»»
  | Gate9AnotherPass { human_decision str }   // «В9: «ещё заход»»
  | Gate9Stop                         // «В9: «остановиться»»
  | Gate9HaltMeeting                 // «В9: «остановить совещание»»
  | Gate7Answered { human_answer str }       // «В7: «ответил»»
  | AcceptanceConfirmed { confirmation str }   // «ПРИНЯТИЕ: «подтвердил»»
  | PauseWordContinue { human_word str, author str, source str }   // «ПАУЗА: «продолжить»»
  | PauseWordHaltMeeting              // «ПАУЗА: «остановить совещание»»
  | PauseWordContinueFromParent { id str }          // «ПАУЗА: «продолжить от родителя»»
  | PauseWordHaltFromParent { id str }         // «ПАУЗА: «остановить от родителя»»
```

## Механика машины

```nova
// Раздел записывает механику машины совещания: свободные функции и методы `Машина`; методы `Исполнитель` и общие функции — в движке.
// псевдокод: функции без тела — сигнатуры; тело пишет реализация, в Нове внешняя реализация здесь не показана

// Свободные функции
// элементы первых, затем те элементы вторых, которых в первых нет: находка с тем же доказательством — один раз
fn merge_unique(first_list []Finding, second_list []Finding) -> []Finding
fn has_critical(findings []Finding) -> bool
fn desirable(findings []Finding) -> []Finding
fn desirable_and_significant(findings []Finding) -> []Finding
// желательные и значимые с повтор = true
fn desirable_and_significant_repeated(findings []Finding) -> []Finding
// критические всегда и значимые только без повтора
fn critical_and_significant_not_repeated(findings []Finding) -> []Finding
// находки из первых, которых нет в `среди` (по доказательству)
fn not_included_in(findings []Finding, among []Finding) -> []Finding
// «Куда: предыдущее»: значение переменной — имя ждущего состояния, не конца и не ПАУЗЫ (правило 24)
fn MachineData @state_by_name(name str) -> State
// «свидетель», «автор» (вызовы шага агента), «вратарь» (ворота СБОЙ, ИЗМЕНЁН, ПОВТОР, В3, В9, В7, ПРИНЯТИЕ: человек по умолчанию, агент по настройке) или «усиленный» (ПАУЗА); идентификатор линзы — для ЛИНЗ
fn appeal_party(appeal State) -> str
// срок тишины вложенного вызова: СРОК_БЕЗДЕЙСТВИЯ, `0` — срока нет (поле `нет`); бюджеты и предел ходов — `нет` (решение 5 первоисточника)
fn role_limits() -> AgentLimits => AgentLimits { silence_term: if IDLE_TERM == 0 { None } else { Some(IDLE_TERM) }, token_budget: None, cost_budget: None, turn_limit: None }
// профиль стороны вызова: настройка проекта «Профили ролей» (служебное хранилище); у каждой линзы свой
fn party_profile(party str) Objects -> AgentProfile
// контекст запроса агента: непрозрачный текст из данных вызова (промпт роли с подстановками и диалог: новый, у автора — ход живого диалога); слой методики и шаг агента его не разбирают
fn role_context(context RoleContext) Objects -> str
// конверт этой машины для запроса агента: трасса и номер шага (`Среда` их не отдаёт: «Что движок не покрыл», пункт 1)
fn call_trace(environment MachineEnvironment) -> str
fn call_step(environment MachineEnvironment) -> int
// разбор артефакта ответа агента в типы совещания (содержание: находки и пробы линзы, ответы свидетеля со сверкой выдержек, итог правки); общую форму проверил шаг агента, разбор не отказывает;
// роль определяется по `ответ.использование.сессия` (идентификатор линзы, «свидетель» или «автор»; идентификаторы различны); сверку выдержек и один возврат делает обработчик `Связь` (решение 6 первоисточника)
fn parse_agent_reply(response AgentReply) Objects -> RoleResult

// Методы Машины: данные автомата
// счётчики цикла как запись `Цикл`: над ней работает арифметика цикла слоя методики
fn MachineData @cycle() -> Cycle => Cycle { number: @number, origin: @origin, streak: @streak, no_probes: @no_probes }
fn MachineData mut @set_cycle(value Cycle) {
  @number = value.number
  @origin = value.origin
  @streak = value.streak
  @no_probes = value.no_probes
}
// имя варианта Состояние: значение для переменной предыдущее
fn MachineData @state_name(state State) -> str
// «в находках любой линзы захода <номер> есть вопросы проверяющих»: находки с вопрос = true; по линзам из порядок_линз
fn MachineData @has_reviewer_questions(pass_number int) -> bool
// предложение читается из хранилища; false — нечитаемо (СВЕРКА)
fn MachineData @proposal_read() Objects -> bool => match Objects.read(Object { name: "proposal" }) {
  Ok(_) => true
  Err(_) => false
}
// свод[номер]; None, пока итоговой строки нет
fn MachineData @summary(pass_number int) -> Option[Summary] => @summary.get(pass_number)
// аннулирований[номер]; начально 0
fn MachineData @voided(pass_number int) -> int => @voided.get(pass_number) ?? 0
// находки_линзы[линза, номер] по каждой линзе из порядок_линз
fn MachineData @all_lens_findings(pass_number int) -> []Finding
// из них вопросы проверяющих (вопрос = да), по каждой линзе из порядок_линз; None, если таких нет
fn MachineData @reviewer_questions(pass_number int) -> Option[[]Finding]
fn MachineData @lenses(lens_id str) -> Lens => match @lenses.get(lens_id) {
  Some(lens) => lens
  None => unreachable("lens not created: start creates the lens records")
}
fn MachineData mut @set_lost(lens_id str, value int) {
  ro lens = @lenses(lens_id)
  @lenses.insert(lens_id, Lens { id: lens.id, lost: value, probes: lens.probes, attempt: lens.attempt })
}
fn MachineData mut @set_probes(lens_id str, value int) {
  ro lens = @lenses(lens_id)
  @lenses.insert(lens_id, Lens { id: lens.id, lost: lens.lost, probes: value, attempt: lens.attempt })
}
fn MachineData mut @set_attempt(lens_id str, value int) {
  ro lens = @lenses(lens_id)
  @lenses.insert(lens_id, Lens { id: lens.id, lost: lens.lost, probes: lens.probes, attempt: value })
}
// вид вызывающего: линза — «линза» (человека у её ворот нет), свидетель и автор — «ход чата» (решение 2 первоисточника)
fn MachineData @call_kind(party str) -> CallerKind => match @lenses.get(party) {
  Some(_) => CallerKind.Lens
  None => CallerKind.ChatTurn
}
/// Запрос агента вложенной машине «Шаг агента» по стороне вызова и контексту: вид — по стороне, профиль — настройка проекта, сессия — идентификатор стороны, вид диалога «основной», пределы — `пределы_роли`, трасса и номер шага — конверт этой машины
fn MachineData @agent_request(party str, context RoleContext, environment MachineEnvironment) Objects -> RoleInput => RoleAgentRequest(AgentRequest {
  kind: @call_kind(party), profile: party_profile(party), session: party, dialog_kind: "main",
  context: role_context(context), limits: role_limits(), trace: call_trace(environment), step: call_step(environment) })
// вход запроса по таблице «Вход» обращения; сторона — идентификатор линзы у ЛИНЗ; у обращений к шагу агента строки «сторона» идут в контекст запроса агента
fn MachineData @request_input(appeal State, party str, environment MachineEnvironment) Objects -> RoleInput => match appeal {
  Witness => @agent_request(party, WitnessContext { author_question: @author_question, lens_findings: @reviewer_questions(@number - 1), proposal: @proposal }, environment)
  Lenses => @agent_request(party, LensContext { proposal: @proposal, witness_answers: @witness_answers.get(@number) }, environment)
  FailedRequest => FailureInput { failed_appeal: @failed_appeal }
  Changed => ChangedInput {
    copy: required(@copy, "Changed: the copy is written by Lock"),
    proposal: if @proposal_read() { Some(@proposal) } else { None } }
  Retry => RetryInput
  Gate3 => Gate3Input {
    summary: @summary(@number),                                    // None — итога свода нет (РАЗБОР #3 ведёт в В3)
    lens_findings: @all_lens_findings(@number) }
  Gate9 => Gate9Input { gate3_findings: @gate3_findings, number: @number, origin: @origin }
  AuthorFix => @agent_request(party, FixContext {
    proposal: @proposal, gate3_findings: @gate3_findings,
    author_guidance: if @author_guidance == "" { None } else { Some(@author_guidance) } }, environment)
  Gate7 => Gate7Input { author_question: required(@author_question, "Gate7: the author question is recorded by the reply of the fix or question state") }
  AuthorQuestion => @agent_request(party, QuestionContext {
    author_question: required(@author_question, "AuthorQuestion: the author question is recorded by the reply of the fix or question state"),
    proposal: @proposal, gate3_findings: @gate3_findings, human_answer: @human_answer }, environment)
  Acceptance => AcceptanceInput { proposal: @proposal, number: @number, open: @open }
  Pause => RolePauseInput(PauseInput { previous: environment.previous(), call_request_id: environment.call_request_id() })
  _ => unreachable("only appeals build a request input")
}

/// Счётчик попыток одноадресного обращения (правило 15).
fn MachineData @attempt_counter(party str) -> int => match party {
  "witness" => @witness_attempt
  "author" => @author_attempt
  "gatekeeper" => @gatekeeper_attempt
  "enhanced" => @enhanced_attempt
  _ => unreachable("party outside "witness", "author", "gatekeeper", "enhanced"")
}

fn MachineData mut @increment_attempt_counter(party str) => match party {
  "witness" => { @witness_attempt += 1 }
  "author" => { @author_attempt += 1 }
  "gatekeeper" => { @gatekeeper_attempt += 1 }
  "enhanced" => { @enhanced_attempt += 1 }
  _ => unreachable("party outside "witness", "author", "gatekeeper", "enhanced"")
}

// Операции и журнал машины: действия ставятся в необратимые шага через `среда`, строки идут в журнал движка
// ставит действие в необратимые шага; выполняется после сохранения (правило 13)
fn MachineData mut @close_for_writing(object str, environment MachineEnvironment) {
  environment.add_irreversible(CloseForWriting(object))
}
fn MachineData mut @open_for_writing(object str, environment MachineEnvironment) {
  environment.add_irreversible(OpenForWriting(object))
}
// находки_линзы[линза, номер] по каждой линзе из порядок_линз и ответы_свидетеля[номер] — в архив недействительных заходов, суффикс `*.void-<суффикс>.md`
fn MachineData mut @move_to_archive(pass_number int, suffix int, environment MachineEnvironment) {
  environment.add_irreversible(MoveToArchive { pass_number, suffix })
}
// строки счёта по моделям буферизуются и пишутся при фиксации
fn MachineData mut @count_in_model_tally(finding Finding, environment MachineEnvironment)
// «незакрытые находки» в журнал состояния ОСТАНОВЛЕНО
fn MachineData mut @journal_findings(findings []Finding, environment MachineEnvironment) Journal Time -> ()
// запись для диагностики: все переменные и хранилища (Вход ОШИБКИ)
fn MachineData mut @journal_machine_data(environment MachineEnvironment) Journal Time -> ()
// запись КОНЦА; открытые — как «открыто»
fn MachineData mut @journal_decision(decision str, source str, passes int, open []Finding, environment MachineEnvironment) Journal Time -> ()
// четыре признака несостоятельных мнения (task-runner.md); каждое идёт в счёт по моделям; запись на то же место
fn MachineData mut @remove_unsound(pass_number int) Objects -> ()
// идентификаторы
fn MachineData @lenses_without_critical() -> []str
// K, Z, D — суммы по линзам, P — наименьшее из проб
fn MachineData @build_summary(pass_number int) Objects -> Option[Summary]
// отпечаток текущего содержимого предложения; вызывается, когда предложение прочитано (ЗАМОК, СВЕРКА)
fn MachineData @proposal_fingerprint() Objects -> str => match Objects.read(Object { name: "proposal" }) {
  Ok(bytes) => fingerprint(bytes)
  Err(_) => unreachable("proposal not read: Lock reads it on entry")
}

// Методы Машины для движка (протокол `Автомат`): состояния и события машины
fn MachineData @initial() -> State => Pass
fn MachineData @pause_state() -> State => Pause
// значение «остановка» при «остановить» у ПАУЗЫ: «ПАУЗА: <слово остановки>»; слово остановки — параметр подключения фрагмента «Пауза» (раздел «Общие события» первоисточника), значение есть в таблице «конец → ответ»
fn MachineData @pause_stop_reason() -> str => "pause_halt_meeting"
fn MachineData @halted_state() -> State => Halted
fn MachineData @error_state() -> State => Errored
fn MachineData @immediate_event() -> Event => Immediate
fn MachineData @failure_event(reason FailCode) -> Event => Failure { reason }
// событие с данными по результату принятого ответа роли: «ответ» у СВИДЕТЕЛЯ и ЛИНЗ, «ответ: закончена» или «ответ: вопрос» у ПРАВКИ и ВОПРОСА (вариант `ИтогПравки`)
fn MachineData @reply_event(current State, role_result RoleResult) -> Event => match role_result {
  WitnessOutcome(_) => Replied
  LensOutcome(_) => Replied
  EditOutcome(fix) => match fix {
    Done(_) => RepliedDone
    Asked(_) => RepliedAsked
  }
}
// метка инварианта 2: номер_захода не уменьшается (проверяет движок после каждого перехода шага, покомпонентно; у совещания компонент один)
fn MachineData @invariant_mark() -> []int => [@number]
// «остановка» — причина остановки совещания; пишут общие события движка и строки состояний
fn MachineData mut @record_stop(reason str) {
  @stop_reason = reason
}
// общие события: события машины, которые движок разбирает до строк состояний
fn MachineData @common(current State, event_body Event) -> Option[CommonEvent] => match event_body {
  StopFromHuman { human_word, author, source } => Some(HumanStop { human_word, author, source })
  StopFromParent { id } => Some(ParentStop { id })
  CancelRequest { id } => Some(RequestCancelled { id })
  PauseWordContinue { human_word, author, source } => Some(PauseContinue { human_word, author, source })
  PauseWordHaltMeeting => Some(PauseHalt)
  PauseWordContinueFromParent { id } => Some(PauseContinueFromParent { id })
  PauseWordHaltFromParent { id } => Some(PauseHaltFromParent { id })
  _ => None
}
// как состояние-обращение обращается к сторонам: ЛИНЗЫ — набор вложенных вызовов шага агента по линзам из к_отправке, СВИДЕТЕЛЬ, ПРАВКА и ВОПРОС — один вложенный вызов (свидетель, автор), остальные — ворота человека;
// срок бездействия запроса `0`: у вызова вложенной машины срока нет (правило 35, пункт 5), у человека — правило 19; срок тишины агента — `пределы_роли`
fn MachineData @appeal(current State) -> Option[AppealDescription] => match current {
  Lenses => Some(Batch { idle_term: 0, order: @lens_order, nested: true, form_returns: 0 })      // общую форму находок линзы возвращает шаг агента (один возврат в том же диалоге); возвратов исполнителя нет
  Witness | AuthorFix | AuthorQuestion => Some(Single {
    party: appeal_party(current), idle_term: 0,
    nested: true, form_returns: if current == Witness { 1 } else { 0 } })      // у СВИДЕТЕЛЯ несовпадение выдержки — один возврат «исправь выдержку» новым запросом (решение 6); у автора формы нет
  Gate3 | Gate9 | Gate7 | Acceptance | FailedRequest | Changed | Retry | Pause => Some(Single {
    party: appeal_party(current), idle_term: 0,
    nested: false, form_returns: 0 })
  _ => None
}
// номер новой попытки: у линзы — её попытка + 1 (хранится в записи линзы), у одноадресной стороны — счётчик попыток (правило 15)
fn MachineData mut @next_attempt(party str) -> int => match @lenses.get(party) {
  Some(lens) => {
    @set_attempt(party, lens.attempt + 1)
    lens.attempt + 1
  }
  None => {
    @increment_attempt_counter(party)
    @attempt_counter(party)
  }
}
// правит автор и предложение менялось с начала попытки — результат не принимается (правило 14)
fn MachineData @object_changed_since_attempt(current State) Objects -> bool => author_edits(current) && @proposal_changed_since_attempt()
fn MachineData @proposal_changed_since_attempt() Objects -> bool
// последний, повторяемый без вреда этап: переименование в архив, смена права записи (правило 13)
fn MachineData mut @execute(action Irreversible) Objects -> () => match action {
  CloseForWriting(object) => object_ok(Objects.close_for_writing(Object { name: object }), "закрыть для записи не удалось")
  OpenForWriting(object) => object_ok(Objects.open_for_writing(Object { name: object }), "открыть для записи не удалось")
  MoveToArchive { pass_number, suffix } => object_ok(Objects.move_to_archive(Object { name: "pass-${pass_number}" }, suffix), "перенос в архив не удался")
}
// принимает файл попытки в хранилище (правило 14); повторяется без вреда
fn MachineData mut @accept_attempt_file(id str) Objects -> () => object_ok(Objects.accept_attempt_file(Object { name: id }, id), "принять файл попытки не удалось")
// предел одновременных запросов набора: не меньше 1, параметр проекта (правило 21); раннер исполняет только 1
fn MachineData @request_limit() -> int => REQUEST_LIMIT
// вход, результат и событие стороны — в строку и обратно: через `Связь` ходят конкретные типы, а не типы машины; результат вызова шага агента — `ОтветАгента`, исполнитель разбирает его в `РезультатРоли` (`разобрать_ответ_агента`)
fn MachineData @encode_input(input RoleInput) -> PartyInput
fn MachineData @decode_result(result PartyResult) -> RoleResult
fn MachineData @decode_event(event PartyEvent) -> Event
fn MachineData @encode_output(output MeetingResult) -> PartyOutput
// данные машины в строку снимка и обратно; формат — за реализацией хранилища
fn MachineData @capture() -> str
fn MachineData mut @restore(data str)
// подготовки при возобновлении у совещания нет: сохранённое состояние входится сразу
fn MachineData mut @on_resume(saved State, environment MachineEnvironment) Journal Objects Time -> Option[Transition[State]] => None
```

## Переходы

```nova
/// Переход по событию. тело_события — событие, которое ждёт состояние `текущее` (у операции — Сразу, у развилки — Сразу без данных);
/// событие — исходное событие шага: его данные (сторона, идентификатор) доступны всей цепочке до ближайшего обращения (правило 13).
/// Состояние пишется при фиксации; в «Что меняется» оно не повторяется.
fn MachineData mut @step(current State, event_body Event, event Incoming[Event], environment MachineEnvironment) Journal Objects Time -> Transition[State] {
  match current {

  // ===================== ЗАХОД — развилка =====================
  Pass => {
    // ЗАХОД #1: вопрос_автора есть
    if @author_question != None { return Go(Witness) }
    // ЗАХОД #2: вопрос_автора отсутствует, и в находках любой линзы захода номер_захода - 1 есть вопросы проверяющих (находки с `вопрос` = да)
    if @author_question == None && @has_reviewer_questions(@number - 1) { return Go(Witness) }
    // ЗАХОД #3: вопрос_автора отсутствует, и в находках любой линзы захода номер_захода - 1 вопросов проверяющих (находок с `вопрос` = да) нет
    if @author_question == None && !@has_reviewer_questions(@number - 1) { return Go(Lock) }
    // ЗАХОД #4: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "Pass")]))
  }

  // ===================== СВИДЕТЕЛЬ — обращение =====================
  Witness => match event_body {
    // СВИДЕТЕЛЬ #1: ответ
    Replied => {
      @author_question = None                      // сброс после ответа свидетеля
      Go(Lock)
    }
    // СВИДЕТЕЛЬ #2: сбой (причина: КодСбоя)
    Failure { reason } => {
      environment.write_journal(journal_event("witness_no_answer", [param("reason", "${reason}")]))
      @failed_appeal = "Witness"
      Go(FailedRequest)
    }
    _ => NotAwaited
  }

  // ===================== ЗАМОК — операция =====================
  Lock => match event_body {
    // ЗАМОК #1: сразу
    Immediate => {
      environment.set_to_send(@lens_order)
      @responded = 0
      Go(Lenses)
    }
    _ => NotAwaited
  }

  // ===================== ЛИНЗЫ — обращение =====================
  // При приёме (правило 14; запись линзы — событие.сторона): см. при_приёме_ЛИНЗЫ в разделе «Цикл исполнителя».
  Lenses => match event_body {
    // ЛИНЗЫ #1: ответ
    Replied => Go(AllClosed)
    // ЛИНЗЫ #2: сбой (сторона: идентификатор линзы; причина: КодСбоя)
    Failure { reason } => {
      environment.write_journal(journal_event("lens_no_answer", [param("party", "${event.party}"), param("reason", "${reason}")]))
      Go(LensRefusal)
    }
    _ => NotAwaited
  }

  // ===================== ОТКАЗ — развилка =====================
  LensRefusal => {
    // ОТКАЗ #1: потери_подряд линзы событие.сторона = 1
    if @lenses(event.party).lost == 1 {
      environment.write_journal(journal_event("lens_dropped", [param("party", "${event.party}"), param("pass", "${@number}")]))
      return Go(AllClosed)
    }
    // ОТКАЗ #2: потери_подряд линзы событие.сторона = 2
    if @lenses(event.party).lost == 2 {
      @failed_appeal = "Lenses"
      environment.return_first_to_send(event.party)
      return Go(FailedRequest)
    }
    // ОТКАЗ #3: потери_подряд линзы событие.сторона = 3
    if @lenses(event.party).lost == 3 {
      @set_lost(event.party, 1)
      environment.write_journal(journal_event("lens_dropped", [param("party", "${event.party}"), param("pass", "${@number}")]))
      return Go(AllClosed)
    }
    // ОТКАЗ #4: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "LensRefusal")]))
  }

  // ===================== ВСЕ_ЗАКРЫТЫ — развилка =====================
  AllClosed => {
    // ВСЕ_ЗАКРЫТЫ #1: к_отправке — не пустой список
    if environment.to_send().len() > 0 { return Go(Lenses) }
    // ВСЕ_ЗАКРЫТЫ #2: к_отправке — пустой список, и открытые_запросы — не пустой список
    if environment.to_send().len() == 0 && environment.open_requests().len() > 0 { return Go(Lenses) }
    // ВСЕ_ЗАКРЫТЫ #3: к_отправке — пустой список, открытые_запросы — пустой список, и ответившие больше 0
    if environment.to_send().len() == 0 && environment.open_requests().len() == 0 && @responded > 0 { return Go(Unlock) }
    // ВСЕ_ЗАКРЫТЫ #4: к_отправке — пустой список, открытые_запросы — пустой список, и ответившие = 0
    if environment.to_send().len() == 0 && environment.open_requests().len() == 0 && @responded == 0 {
      @stop_reason = "no_lens_answered"
      return Go(Halted)
    }
    // ВСЕ_ЗАКРЫТЫ #5: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "AllClosed")]))
  }

  // ===================== СБОЙ — обращение =====================
  FailedRequest => match event_body {
    // СБОЙ #1: В13: «повторить»
    Gate13Repeat => Go(RequestRetry)
    // СБОЙ #2: В13: «остановить совещание»
    Gate13HaltMeeting => {
      @stop_reason = "${@failed_appeal}_halt_meeting"
      Go(Halted)
    }
    _ => NotAwaited
  }

  // ===================== ПОВТОР_ОБРАЩЕНИЯ — развилка =====================
  RequestRetry => {
    // ПОВТОР_ОБРАЩЕНИЯ #1: сбойное_обращение = «СВИДЕТЕЛЬ»
    if @failed_appeal == "Witness" { return Rerun(Witness) }
    // ПОВТОР_ОБРАЩЕНИЯ #2: сбойное_обращение = «ЛИНЗЫ»
    if @failed_appeal == "Lenses" { return Rerun(Lenses) }
    // ПОВТОР_ОБРАЩЕНИЯ #3: сбойное_обращение = «ПРАВКА»
    if @failed_appeal == "AuthorFix" { return Rerun(AuthorFix) }
    // ПОВТОР_ОБРАЩЕНИЯ #4: сбойное_обращение = «ВОПРОС»
    if @failed_appeal == "AuthorQuestion" { return Rerun(AuthorQuestion) }
    // ПОВТОР_ОБРАЩЕНИЯ #5: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "RequestRetry")]))
  }

  // ===================== РАЗБЛОК — операция =====================
  Unlock => match event_body {
    // РАЗБЛОК #1: сразу
    Immediate => Go(Comparison)
    _ => NotAwaited
  }

  // ===================== СВЕРКА — развилка =====================
  Comparison => {
    // СВЕРКА #1: предложение прочитано и его отпечаток равен отпечатку копии
    if @proposal_read() && Some(@proposal_fingerprint()) == @copy_fingerprint { return Go(Filter) }
    // СВЕРКА #2: предложение прочитано и его отпечаток отличается от отпечатка копии
    if @proposal_read() && Some(@proposal_fingerprint()) != @copy_fingerprint { return Go(Changed) }
    // СВЕРКА #3: предложение не прочитано
    if !@proposal_read() { return Go(Changed) }
    // СВЕРКА #4: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "Comparison")]))
  }

  // ===================== ИЗМЕНЁН — обращение =====================
  Changed => match event_body {
    // ИЗМЕНЁН #1: В13: «оставить правку»
    Gate13KeepEdit => {
      @voided.insert(@number, @voided(@number) + 1)
      Go(Void)
    }
    // ИЗМЕНЁН #2: В13: «вернуть копию»
    Gate13RestoreCopy => {
      @voided.insert(@number, @voided(@number) + 1)
      Go(CopyRestore)
    }
    // ИЗМЕНЁН #3: В13: «остановить совещание»
    Gate13HaltMeeting => {
      @stop_reason = "changed_halt_meeting"
      Go(Halted)
    }
    _ => NotAwaited
  }

  // ===================== ВОЗВРАТ — операция =====================
  CopyRestore => match event_body {
    // ВОЗВРАТ #1: сразу
    Immediate => Go(Void)
    _ => NotAwaited
  }

  // ===================== АННУЛ — операция =====================
  Void => match event_body {
    // АННУЛ #1: сразу
    Immediate => Go(Pass)
    _ => NotAwaited
  }

  // ===================== ФИЛЬТР — операция =====================
  Filter => match event_body {
    // ФИЛЬТР #1: сразу (линзы_без_критических: []Текст — идентификаторы)
    ImmediateFilter { lenses_without_critical } => {
      for lens_id in lenses_without_critical { @set_probes(lens_id, 0) }
      Go(SummaryBuilding)
    }
    _ => NotAwaited
  }

  // ===================== СВОД — операция =====================
  SummaryBuilding => match event_body {
    // СВОД #1: сразу
    Immediate => Go(ReviewParsing)
    _ => NotAwaited
  }

  // ===================== РАЗБОР — развилка =====================
  ReviewParsing => match @summary(@number) {
    // РАЗБОР #1: итог свода есть, и критических больше 0
    Some(outcome) if outcome.critical > 0 => {
      @no_probes = 0
      Go(Gate3)
    }
    // РАЗБОР #2: итог свода есть, критических нет, и проб не меньше ПРОБ_В_ЧИСТОМ
    Some(outcome) if outcome.critical == 0 && outcome.probes >= PROBES_MIN => {
      @no_probes = 0
      Go(Gate3)
    }
    // РАЗБОР #3: итога свода нет
    None => {
      environment.write_journal(journal_event("no_summary_line", []JournalParam.new()))
      @no_probes = 0
      Go(Gate3)
    }
    // РАЗБОР #4: итог свода есть, критических нет, и проб меньше ПРОБ_В_ЧИСТОМ
    Some(outcome) if outcome.critical == 0 && outcome.probes < PROBES_MIN => {
      environment.write_journal(journal_event("pass_clean_without_probes", [param("pass", "${@number}")]))
      @number += 1
      @no_probes += 1
      Go(NoProbes)
    }
    // РАЗБОР #5: иначе
    _ => environment.machine_error(journal_event("fork_no_match", [param("fork", "ReviewParsing")]))
  }

  // ===================== БЕЗ_ПРОБ — развилка =====================
  NoProbes => {
    match no_probes_step(@cycle()) {
      // БЕЗ_ПРОБ #1: без_проб_подряд = 1
      Some(RepeatReview) => Go(Pass)
      // БЕЗ_ПРОБ #2: без_проб_подряд больше 1
      Some(AskHuman) => Go(Retry)
      // БЕЗ_ПРОБ #3: иначе
      None => environment.machine_error(journal_event("fork_no_match", [param("fork", "NoProbes")]))
    }
  }

  // ===================== ПОВТОР — обращение =====================
  Retry => match event_body {
    // ПОВТОР #1: В13: «повторить»
    Gate13Repeat => Go(Pass)
    // ПОВТОР #2: В13: «остановить»
    Gate13Halt => {
      @stop_reason = "retry_halt"
      Go(Halted)
    }
    _ => NotAwaited
  }

  // ===================== В3 — обращение =====================
  Gate3 => match event_body {
    // В3 #1: В3: «не засчитан»
    Gate3NotCounted => {
      environment.write_journal(journal_event("pass_probes_not_probes", [param("pass", "${@number}")]))
      @number += 1
      Go(Pass)
    }
    // В3 #2: В3: «засчитан» (находки_В3: []Находка)
    Gate3Counted { gate3_findings: new_findings } => {
      @number += 1
      @gate3_findings = new_findings
      Go(Totals)
    }
    _ => NotAwaited
  }

  // ===================== ИТОГ — развилка =====================
  Totals => {
    // ИТОГ #1: в находки_В3 есть критические
    if has_critical(@gate3_findings) {
      @streak = 0
      @open = merge_unique(@open, desirable_and_significant_repeated(@gate3_findings))
      return Go(Ceiling)
    }
    // ИТОГ #2: в находки_В3 критических нет, и серия_чистых + 1 меньше ЧИСТЫХ_ПОДРЯД
    if !has_critical(@gate3_findings) && @streak + 1 < CLEAN_NEEDED {
      @open = merge_unique(@open, desirable(@gate3_findings))
      @streak += 1
      return Go(Pass)
    }
    // ИТОГ #3: в находки_В3 критических нет, и серия_чистых + 1 не меньше ЧИСТЫХ_ПОДРЯД
    if !has_critical(@gate3_findings) && @streak + 1 >= CLEAN_NEEDED {
      @open = merge_unique(@open, desirable_and_significant(@gate3_findings))
      @streak = 0
      return Go(Acceptance)
    }
    // ИТОГ #4: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "Totals")]))
  }

  // ===================== ПОТОЛОК — развилка =====================
  Ceiling => {
    // ПОТОЛОК #1: (номер_захода - 1) - заход_отсчёта + 1 меньше ПОТОЛОК_ЗАХОДОВ
    if !ceiling_reached(@cycle(), CEILING) { return Go(AuthorFix) }
    // ПОТОЛОК #2: (номер_захода - 1) - заход_отсчёта + 1 не меньше ПОТОЛОК_ЗАХОДОВ
    if ceiling_reached(@cycle(), CEILING) { return Go(Gate9) }
    // ПОТОЛОК #3: иначе
    environment.machine_error(journal_event("fork_no_match", [param("fork", "Ceiling")]))
  }

  // ===================== В9 — обращение =====================
  Gate9 => match event_body {
    // В9 #1: В9: «ещё заход» (решение_человека: Текст)
    Gate9AnotherPass { human_decision } => {
      @set_cycle(reset_origin(@cycle()))
      @author_guidance = human_decision        // сузить или разбить
      Go(AuthorFix)
    }
    // В9 #2: В9: «остановиться»
    Gate9Stop => {
      @set_cycle(reset_origin(@cycle()))
      @open = merge_unique(@open, critical_and_significant_not_repeated(@gate3_findings))
      Go(Acceptance)
    }
    // В9 #3: В9: «остановить совещание»
    Gate9HaltMeeting => {
      @set_cycle(reset_origin(@cycle()))
      @stop_reason = "gate9_halt_meeting"
      Go(Halted)
    }
    _ => NotAwaited
  }

  // ===================== ПРАВКА — обращение =====================
  AuthorFix => match event_body {
    // ПРАВКА #1: ответ: закончена
    RepliedDone => {
      @author_guidance = ""
      Go(Pass)
    }
    // ПРАВКА #2: ответ: вопрос (любое стоп-слово автора читается как вопрос)
    RepliedAsked => {
      @author_guidance = ""
      Go(Gate7)
    }
    // ПРАВКА #3: сбой (причина: КодСбоя)
    Failure { reason } => {
      environment.write_journal(journal_event("author_fix_no_answer", [param("reason", "${reason}")]))
      @failed_appeal = "AuthorFix"
      Go(FailedRequest)
    }
    _ => NotAwaited
  }

  // ===================== В7 — обращение =====================
  Gate7 => match event_body {
    // В7 #1: В7: «ответил» (ответ_человека: Текст)
    Gate7Answered { human_answer: response_word } => {
      @human_answer = response_word
      Go(AuthorQuestion)
    }
    _ => NotAwaited
  }

  // ===================== ВОПРОС — обращение =====================
  AuthorQuestion => match event_body {
    // ВОПРОС #1: ответ: закончена
    RepliedDone => Go(Pass)
    // ВОПРОС #2: ответ: вопрос
    RepliedAsked => Go(Gate7)
    // ВОПРОС #3: сбой (причина: КодСбоя)
    Failure { reason } => {
      environment.write_journal(journal_event("author_question_no_answer", [param("reason", "${reason}")]))
      @failed_appeal = "AuthorQuestion"
      Go(FailedRequest)
    }
    _ => NotAwaited
  }

  // ===================== ПРИНЯТИЕ — обращение =====================
  Acceptance => match event_body {
    // ПРИНЯТИЕ #1: ПРИНЯТИЕ: «подтвердил» (подтверждение: Текст)
    AcceptanceConfirmed { confirmation: confirmation_word } => {
      @confirmation = confirmation_word
      Go(End)
    }
    _ => NotAwaited
  }

  // ===================== ПАУЗА — обращение =====================
  Pause => NotAwaited

  // ===================== концы: переходов нет =====================
  Halted => unreachable("end state: no transitions; the work on entry is in "Ends and reply"")

  // ОШИБКА — конец. Заканчивает совещание, если сама машина попала в непредусмотренное положение; это дефект машины или реализации, его разбирает человек.
  // Вход: предложение; все данные машины (Все переменные и хранилища — в журнал)
  Errored => unreachable("end state: no transitions; the work on entry is in "Ends and reply"")

  // КОНЕЦ — конец. Записывает принятое решение с источником, числом заходов и открытыми находками: совещание закончено успешно.
  // Вход: предложение; подтверждение; номер_захода; открытые
  End => unreachable("end state: no transitions; the work on entry is in "Ends and reply"")
  }
}
```

## Работа операций

```nova
/// Работа операций при входе (в одном шаге с переходом; отказа и «нет ответа» у операции нет). Результат — событие: `Сразу`, у ФИЛЬТРА — `Сразу_ФИЛЬТР` с данными.
fn MachineData mut @run_operation(operation State, environment MachineEnvironment) Journal Objects Time -> Event => match operation {
  Lock => {
    @copy = Some(@proposal)
    @copy_fingerprint = Some(@proposal_fingerprint())
    @close_for_writing("proposal", environment)
    Immediate
  }
  Unlock => {
    @open_for_writing("proposal", environment)
    Immediate
  }
  CopyRestore => {
    match @copy {
      Some(text) => { @proposal = text }
      None => environment.write_journal(journal_event("copy_restore_no_copy", []JournalParam.new()))    // псевдокод: недостижимо, копию пишет ЗАМОК
    }
    Immediate
  }
  Void => {
    @move_to_archive(@number, @voided(@number), environment)
    Immediate
  }
  Filter => {
    // четыре признака несостоятельных мнения (task-runner.md); каждое идёт в счёт по моделям; запись на то же место
    @remove_unsound(@number)
    ImmediateFilter { lenses_without_critical: @lenses_without_critical() }   // идентификаторы
  }
  SummaryBuilding => {
    // K, Z, D — суммы по линзам, P — наименьшее из проб
    match @build_summary(@number) {
      Some(outcome) => { @summary.insert(@number, outcome) }
      None => {}                                        // итога нет: записи в `свод` нет
    }
    Immediate
  }
  _ => unreachable("the other states have no operation work")
}
```

## Приём ответа и запись результата

```nova
/// При приёме (правило 14; запись линзы — событие.сторона); результат роли уже разобран из артефакта ответа агента (`разобрать_ответ_агента`).
fn MachineData mut @on_accept(current State, response Response[RoleResult]) => match current {
  Lenses => match response {
    // ответ: потери_подряд ← 0, пробы ← пробы из ответа (результат ответа, в событии не повторяется), ответившие + 1
    Answer(outcome) => match outcome.result {
      LensOutcome(outcomes) => {
        @set_lost(outcome.party, 0)
        @set_probes(outcome.party, outcomes.probes)
        @responded += 1
      }
      _ => unreachable("the result of the role Lenses is LensOutcome")
    }
    // сбой: потери_подряд + 1, пробы ← 0
    Refusal(refusal) => {
      @set_lost(refusal.party, @lenses(refusal.party).lost + 1)
      @set_probes(refusal.party, 0)
    }
  }
  _ => ()
}

/// Запись принятого результата в хранилище (правила 8, 14): роль возвращает результат, в хранилище машины не пишет.
/// Вариант результата сверяется с состоянием: чужой вариант — ошибка программы; у ворот результата роли нет.
fn MachineData mut @record_result(current State, response Response[RoleResult]) => match response {
  Refusal(_) => ()
  Answer(outcome) => match current {
    Witness => match outcome.result {
      WitnessOutcome(answers) => { @witness_answers.insert(@number, answers) }
      _ => unreachable("the result of the role Witness is []WitnessReply")
    }
    Lenses => match outcome.result {
      LensOutcome(outcomes) => { @lens_findings.insert((outcome.party, @number), outcomes.findings) }
      _ => unreachable("the result of the role Lenses is LensOutcome")
    }
    AuthorFix | AuthorQuestion => match outcome.result {
      EditOutcome(fix) => match fix {            // ИтогПравки: Закончена ведёт в ЗАХОД, Вопрос — в В7
        Done(text) => { @proposal = text }
        Asked(question) => {
          @proposal = question.proposal
          @author_question = Some(question.question)
        }
      }
      _ => unreachable("the result of the roles AuthorFix and AuthorQuestion is FixOutcome")
    }
    _ => ()                                        // у остальных обращений результат — исход ворот, он идёт событием
  }
}
```

## Концы и ответ

```nova
/// Работа концов при входе (в последнем, повторяемом без вреда этапе фиксации) и ответ вызвавшей стороне.
/// Вход в любой конец отменяет все открытые запросы (правило 22); машина отвечает ровно один раз (правило 35).
fn MachineData mut @on_end_entry(end_state State, environment MachineEnvironment) Journal Time -> () => match end_state {
  // ОСТАНОВЛЕНО: предложение открывается для записи; в журнал — «совещание остановлено: <остановка>», затем незакрытые находки:
  //   открытые и находки_В3, не вошедшие в открытые (находки считаются одной по доказательству); итог не принят, программа продолжает остальную работу.
  Halted => {
    @open_for_writing("proposal", environment)
    environment.write_journal(journal_event("meeting_stopped", [param("reason", "${@stop_reason}")]))
    @journal_findings(@open, environment)
    @journal_findings(not_included_in(@gate3_findings, @open), environment)
  }
  // ОШИБКА: предложение открывается для записи; в журнал — запись из перехода и данные машины; совещание остановлено, итог не принят;
  //   это дефект машины или реализации, решает человек вне машины.
  Errored => {
    @open_for_writing("proposal", environment)
    environment.write_journal(environment.transition_note())
    @journal_machine_data(environment)
  }
  // КОНЕЦ: предложение открывается для записи; в журнал — решение (предложение), источник — подтверждение, число заходов номер_захода,
  //   открытые как «открыто»; приписка: «значимые находки прежних заходов, не вошедшие в «открыто», — в файлах заходов»;
  //   тип проверяющего в каждом заходе — по `methodology.md`, раздел 18.
  End => {
    @open_for_writing("proposal", environment)
    @journal_decision(@proposal, @confirmation, @number, @open, environment)
    environment.write_journal(journal_event("older_findings_in_pass_files", []JournalParam.new()))
  }
  _ => ()
}

/// Таблица «конец → ответ» первоисточника (раздел «Контракт машины»): каждый конец и каждое значение остановка — одна строка.
fn MachineData @end_response(call_request Request[MeetingInput], end_state State, environment MachineEnvironment) -> Response[MeetingResult] {
  match end_state {
    // КОНЕЦ, условие входа: всегда → СРезультатом: итог с числом заходов и открытыми находками
    End => Answer(Reply {
      request: call_request.id, party: call_request.party, trace: call_request.trace, step: call_request.step,
      result: MeetingResult { decision: @proposal, source: @confirmation, passes: @number, open: @open } })
    // ОШИБКА, условие входа: всегда (дефект машины) → Отказ, НетРезультата; текст — запись из перехода
    Errored => refuse_with(call_request, NoResult, environment.transition_note())
    Halted => match @stop_reason {
      // ОСТАНОВЛЕНО: остановка = «ни одна линза не ответила» → Отказ, НетРезультата
      "no_lens_answered" => refuse_with(call_request, NoResult, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «В9: остановить совещание» (потолок заходов с открытыми находками) → Отказ, ПотолокЗаходов
      "gate9_halt_meeting" => refuse_with(call_request, CeilingReached, @stop_reason)
      // ОСТАНОВЛЕНО: «ПАУЗА: остановить совещание», «<сбойное_обращение>: остановить совещание», «ИЗМЕНЁН: остановить совещание»
      //   или «ПОВТОР: остановить» (слово человека; у вложенной машины — сигнал «остановить от родителя» в ПАУЗЕ) → Отказ, ОстановленоЧеловеком
      "pause_halt_meeting" | "changed_halt_meeting" | "retry_halt" => refuse_with(call_request, StoppedByHuman, @stop_reason)
      stop_text if stop_text == "${@failed_appeal}_halt_meeting" => refuse_with(call_request, StoppedByHuman, @stop_reason)
      // ОСТАНОВЛЕНО: остановка = «отмена_запроса» → Отказ, ОтмененоРодителем
      "cancel_request" => refuse_with(call_request, common_stop_fail_code(@stop_reason), @stop_reason)
      _ => unreachable("stop reason outside the table "end to reply": a new value adds a table row")
    }
    _ => unreachable("only end states give a reply")
  }
}

/// Точка подстановки эффектов: обработчики выбирает вызывающий код, один раз (`with`), и вне этого файла — любые (`Time` — стандартный, обработчик по умолчанию).
/// Все функции цепочки от `начать`, `возобновить`, `вызвать` объявляют эффекты в своей сигнатуре; здесь они подставлены. Машину по входу запроса создаёт вызывающий код.
fn start_meeting(request Request[MeetingInput]) Time -> Response[MeetingResult] =>
  with Store = store_handler, Journal = journal_handler, Link = link_handler, Objects = objects_handler {   // псевдокод: обработчики (база, файл поверх Fs/Db, очередь сообщений) — любые, вне файла
    mut engine_instance = Engine.new(MachineData.from_input(request.input))
    engine_instance.call(request)
  }
```

## Что движок не покрыл

Список мест, где совещанию нужно то, чего движок [state-machine-engine-automaton.md](state-machine-engine-automaton.md) не давал: записано обходом внутри этой машины или функцией без тела. Номера пунктов в каждом файле свои: здесь открыты 1–3.

| № | Что нужно совещанию | Что в движке | Обход в этом файле | Предлагаемое решение |
|---|---|---|---|---|
| 1 | Конверт этой машины в запросе вложенной (`ЗапросАгента.трасса`, `номер_шага`) | `Среда` не отдаёт машине трассу и номер шага; их знает только исполнитель | Функции без тела `трасса_вызова`, `номер_шага_вызова` (как у запуска сессии, пункт 12) | Движок: методы `трасса()` и `номер_шага()` в `Среда` либо исключить поля из `ЗапросАгента` |
| 2 | Возврат сверки выдержки свидетеля вложенной стороне | `вернуть_стороне` шлёт тот же запрос с замечанием (правило 14), а вложенная машина по тому же идентификатору отдаёт готовый ответ (правило 35, пункт 4) | `возвратов_формы: 1` у СВИДЕТЕЛЯ; возврат — новый запрос той же стороны (решение 6 первоисточника), действие обработчика `Связь` | Спецификация: возврат ответа вложенной стороне — новый запрос той же стороны; движок: `вернуть_стороне` для вложенных |
| 3 | Разбор артефакта ответа агента в типы совещания (находки, пробы, ответы свидетеля, итог правки) при приёме | `раскодировать_результат(результат РезультатСтороны)` — без эффекта `Объекты`, а артефакт читается из хранилища | Функция без тела `разобрать_ответ_агента` с эффектом `Объекты`; её зовёт обработчик `Связь` при раскодировании | Движок: эффекты у `раскодировать_результат`; слой методики: разбор артефакта как данные роли |
