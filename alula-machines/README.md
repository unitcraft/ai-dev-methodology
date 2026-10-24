# Машины методики на Алуле

Исполняемая запись алгоритмов методики — таблицы машин на Алуле, их сценарии, реестр примитивов и списки отступлений таблиц от прозы.

**Откуда.** Файлы перенесены байт-в-байт из репозитория потребителя, коммит `53c958ba8b5101363c676a8c1dcf37dd50006624` (каталог `machines/methodology/`), после задачи 162 потребителя. Пакет — [nova-alula](https://github.com/nv-lang/nova-alula) v0.4.0 (коммит `62cb32a`). Деревья `*.alula.json` в методику не переносятся: их строит `alula compile` из таблиц.

## Что лежит

| Что | Где |
|---|---|
| «Запуск сессии» (`session_start`) | [session-start/session_start.alula.md](session-start/session_start.alula.md), сценарии — `session-start/scenarios/` (63) |
| «Проверка цикла» (`cycle_check`) | [cycle-check/cycle_check.alula.md](cycle-check/cycle_check.alula.md), сценарии — `cycle-check/scenarios/` (102) |
| «Раннер задачи» (`task_runner`) | [task-runner/task_runner.alula.md](task-runner/task_runner.alula.md), сценарии — `task-runner/scenarios/` (255) |
| «Шаг агента» (`agent_step`) | таблицы пока нет — будет добавлена отдельным шагом вместе с образцами; сценарии уже лежат в `agent-step/scenarios/` (88: 83 самого `agent_step` и 5 вложенных `runner-flow-nested-*` раннера, которые запускают вложенный `agent_step`). Без таблицы `agent_step` эти сценарии не пройдут |
| реестр примитивов и журнал | [registry/registry.md](registry/registry.md), [registry/journal.md](registry/journal.md) |
| несортированное | `_unsorted/scenarios/` — 6 сценариев машины `dialog_steps` (продукт потребителя, не методика); решить, оставить ли их здесь, при добавлении `agent_step` |
| отступления | `<папка машины>/deviations.md`: [session-start](session-start/deviations.md), [cycle-check](cycle-check/deviations.md), [task-runner](task-runner/deviations.md) |

Всего сценариев 514 = 63 + 102 + 255 + 88 + 6. Каждый сценарий лежит по значению ключа `machine`, кроме пяти вложенных пар раннера (см. выше).

Имена машин и сторон — [state-machine-glossary.md](../state-machines/state-machine-glossary.md), раздел 2.1; [task-runner.md](../task-runner.md), «Алгоритм».

## Как проверять

Сценарии прогоняет программа `alula` из пакета nova-alula **закреплённой версии v0.4.0** (метка `v0.4.0` репозитория пакета; программу собирают из этой метки):

```
alula test alula-machines
```

Реестр `registry/registry.md` программа берёт флагом `--registry alula-machines/registry/registry.md`, если не находит его рядом с машинами. Новую версию пакета берут только вместе со сверкой таблиц с прозой.

## Кто владеет

- **Алгоритм** — методика: проза ([task-runner.md](../task-runner.md), [task-sessions.md](../task-sessions.md)) и правила машин ([state-machine-spec.md](../state-machines/state-machine-spec.md)). Прозой решается, что машина делает.
- **Таблицы** — реализация: она пишет и правит таблицы, сценарии и реестр, методика их принимает. Расхождение таблицы с прозой — либо правка одной из сторон, либо строка в `deviations.md` с доводом.
