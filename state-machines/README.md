# Стейт-машины методики

Файлы описания и кода стейт-машин методики. Правила записи — [state-machine-spec.md](state-machine-spec.md); именование файлов — `AGENTS.md`, правило о вынесенных алгоритмах.

| Файл | Что это |
|---|---|
| [state-machine-spec.md](state-machine-spec.md) | спецификация стейт-машин: правила записи, сверки, контракт вызова, подключаемый фрагмент |
| [state-machine-portolan-format.md](state-machine-portolan-format.md) | «Портолан» (`Portolan`): формат записи машины таблицами с формальными столбцами (типы, выражения, действия, стороны, фрагменты, каталог встроенных функций), версия 2.7; опытный: выразимость проверена пилотами, равенство с автоматом по журналу подтверждено на одной небольшой машине |
| [state-machine-engine-automaton.md](state-machine-engine-automaton.md) | движок любой машины: исполнитель, эффекты, протокол `Автомат`, контракт вызова (код на Нова) |
| [state-machine-methodology-automaton.md](state-machine-methodology-automaton.md) | слой методики между движком и машинами: общие типы, ворота, цикл, запись расхода, запрос агента |
| [state-machine-call-protocol.md](state-machine-call-protocol.md) | проводной формат контракта вызова (конверт JSON-RPC 2.0 поверх JSON Lines, сообщения, доставка, коды отказов) и набор проверок соответствия |
| [state-machine-journal.md](state-machine-journal.md) | журнал: формат события (`JournalEvent`: код и параметры), кодирование, таблица русских шаблонов строк журнала, правило для обработчика; сверяется с кодом автоматов скриптом `check-tables.py` |
| [state-machine-glossary.md](state-machine-glossary.md) | словарь английских имён: русское имя → английское для идентификаторов кода автоматов и провода, строковые значения-перечисления, расхождения с таблицами соответствия (фаза 1 перевода кода) |
| [state-machine-pause-states.md](state-machine-pause-states.md) | подключаемый фрагмент «Пауза» и общих остановок |
| [state-machine-agent-step-states.md](state-machine-agent-step-states.md)<br>[state-machine-agent-step-automaton.md](state-machine-agent-step-automaton.md) | машина «Шаг агента»: один вызов агента с типизированным запросом и ответом |
| [state-machine-agent-step.portolan.md](state-machine-agent-step.portolan.md) | машина «Шаг агента» целиком в формате «Портолан», версия 2.7: опытная иллюстрация; эквивалентность по журналу с автоматом не проверялась, источник правды — `states` и `automaton` |
| [task-runner-session-states.md](task-runner-session-states.md)<br>[task-runner-session-automaton.md](task-runner-session-automaton.md) | машина «Запуск сессии» |
| [task-runner-review-states.md](task-runner-review-states.md)<br>[task-runner-review-automaton.md](task-runner-review-automaton.md) | машина «Проверка цикла» |
| [task-runner-states.md](task-runner-states.md)<br>[task-runner-automaton.md](task-runner-automaton.md) | машина «Раннер», фазы цикла и маршрут задачи |
| [task-runner-meeting-states.md](task-runner-meeting-states.md)<br>[task-runner-meeting-automaton.md](task-runner-meeting-automaton.md) | машина «Совещание агентов» |
| [check-tables.py](check-tables.py) | сверка таблиц состояний с кодом автоматов и событий журнала с таблицей шаблонов (имена, виды, стороны, «Куда», достижимость); запуск `python state-machines/check-tables.py` из корня, код 1 при расхождениях |
| [check-protocol.py](check-protocol.py) | прогонщик набора проверок протокола вызова (раздел H) для получателя: играет вызывающего, запускает программу дочерним процессом, сверяет ответы; есть встроенный эталонный получатель и самопроверка мутациями; запуск `python state-machines/check-protocol.py -- <команда>` или `--selftest` из корня, код 1 при провале |
| [task-runner-pseudocode.md](task-runner-pseudocode.md), [task-runner-meeting-pseudocode.md](task-runner-meeting-pseudocode.md) | старые схемы раннера и совещания; устарели, первоисточник — файлы состояний |

Слои: движок — любая машина; слой методики — общее для машин методики; машины — совещание, раннер, проверка цикла, запуск сессии, шаг агента. Корневые документы методики остаются в корне репозитория: [methodology.md](../methodology.md), [task-sessions.md](../task-sessions.md), [task-runner.md](../task-runner.md).
