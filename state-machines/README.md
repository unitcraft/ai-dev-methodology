# Стейт-машины методики

Файлы описания и кода стейт-машин методики. Правила записи — [state-machine-spec.md](state-machine-spec.md); именование файлов — `AGENTS.md`, правило о вынесенных алгоритмах.

| Файл | Что это |
|---|---|
| [state-machine-spec.md](state-machine-spec.md) | спецификация стейт-машин: правила записи, сверки, контракт вызова, подключаемый фрагмент |
| [state-machine-engine-automaton.md](state-machine-engine-automaton.md) | движок любой машины: исполнитель, эффекты, протокол `Автомат`, контракт вызова (код на Нова) |
| [state-machine-methodology-automaton.md](state-machine-methodology-automaton.md) | слой методики между движком и машинами: общие типы, ворота, цикл, запись расхода, запрос агента |
| [state-machine-pause-states.md](state-machine-pause-states.md) | подключаемый фрагмент «Пауза» и общих остановок |
| [state-machine-agent-step-states.md](state-machine-agent-step-states.md), [state-machine-agent-step-automaton.md](state-machine-agent-step-automaton.md) | машина «Шаг агента»: один вызов агента с типизированным запросом и ответом |
| [task-runner-session-states.md](task-runner-session-states.md), [task-runner-session-automaton.md](task-runner-session-automaton.md) | машина «Запуск сессии» |
| [task-runner-review-states.md](task-runner-review-states.md), [task-runner-review-automaton.md](task-runner-review-automaton.md) | машина «Проверка цикла» |
| [task-runner-states.md](task-runner-states.md), [task-runner-automaton.md](task-runner-automaton.md) | машина «Раннер», фазы цикла и маршрут задачи |
| [task-runner-meeting-states.md](task-runner-meeting-states.md), [task-runner-meeting-automaton.md](task-runner-meeting-automaton.md) | машина «Совещание агентов» |
| [task-runner-pseudocode.md](task-runner-pseudocode.md), [task-runner-meeting-pseudocode.md](task-runner-meeting-pseudocode.md) | старые схемы раннера и совещания; устарели, первоисточник — файлы состояний |

Слои: движок — любая машина; слой методики — общее для машин методики; машины — совещание, раннер, проверка цикла, запуск сессии, шаг агента. Корневые документы методики остаются в корне репозитория: [methodology.md](../methodology.md), [task-sessions.md](../task-sessions.md), [task-runner.md](../task-runner.md).
