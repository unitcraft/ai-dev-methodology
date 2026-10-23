# Алула переехала в nova-alula

С 2026-10-23 первоисточник языка Алула — репозиторий [nv-lang/nova-alula](https://github.com/nv-lang/nova-alula) (версия пакета 0.3.2, тег `v0.3.2`). Содержимое файлов в методике до переезда — коммит методики 0d95919. В методике остаётся общая модель машин: [state-machine-spec.md](state-machine-spec.md), [state-machine-call-protocol.md](state-machine-call-protocol.md), [state-machine-journal.md](state-machine-journal.md), [state-machine-glossary.md](state-machine-glossary.md) (в нём — нормативный словарь JSON-имён, закреплённый хешем формата), [archive/](archive/), [check-tables.py](check-tables.py), [check-protocol.py](check-protocol.py).

**Почему переехали.** Первоисточник языка лежит рядом с его реализацией: правка спецификации, образцов и проверок идёт одним изменением с кодом, и копий, которые расходятся, нет. Решение — слово владельца методики, 2026-10-23 (чат методики): «по рекомендации» на предложение вынести всё про Алулу в `nova-alula`; запись 32 истории языка ([docs/history.md](https://github.com/nv-lang/nova-alula/blob/main/docs/history.md), раздел 5).

## Старый путь → новый

Для документов `.md` на старом пути лежит короткий указатель; файлы ниже без пометки «указатель» из методики удалены.

| Старый путь в методике | Новый путь в nova-alula | На старом пути |
|---|---|---|
| `state-machines/state-machine-alula-spec.md` | [spec/alula-spec.md](https://github.com/nv-lang/nova-alula/blob/main/spec/alula-spec.md) | указатель |
| `state-machines/state-machine-alula-spec.en.md` | [spec/alula-spec.en.md](https://github.com/nv-lang/nova-alula/blob/main/spec/alula-spec.en.md) | указатель |
| `state-machines/alula-keywords.tsv` | [spec/alula-keywords.tsv](https://github.com/nv-lang/nova-alula/blob/main/spec/alula-keywords.tsv) | — |
| `state-machines/state-machine-agent-step.alula.md` | [spec/samples/agent-step.alula.md](https://github.com/nv-lang/nova-alula/blob/main/spec/samples/agent-step.alula.md) | указатель |
| `state-machines/state-machine-agent-step.en.alula.md` | [spec/samples/agent-step.en.alula.md](https://github.com/nv-lang/nova-alula/blob/main/spec/samples/agent-step.en.alula.md) | указатель |
| `state-machines/task-runner-meeting.alula.md` | [spec/samples/meeting-definitions.alula.md](https://github.com/nv-lang/nova-alula/blob/main/spec/samples/meeting-definitions.alula.md) | указатель |
| `state-machines/task-runner-meeting.alula-notes.md` | [spec/samples/meeting-notes.md](https://github.com/nv-lang/nova-alula/blob/main/spec/samples/meeting-notes.md) | указатель |
| `state-machines/check-alula-keywords.py` | [tools/check-alula-keywords.py](https://github.com/nv-lang/nova-alula/blob/main/tools/check-alula-keywords.py) | — |
| `state-machines/check-alula-samples.py` | [tools/check-alula-samples.py](https://github.com/nv-lang/nova-alula/blob/main/tools/check-alula-samples.py) | — |
| `state-machines/check-alula-translation.py` | [tools/check-alula-translation.py](https://github.com/nv-lang/nova-alula/blob/main/tools/check-alula-translation.py) | — |
| `state-machines/alula-overview.md` | [docs/overview.md](https://github.com/nv-lang/nova-alula/blob/main/docs/overview.md) | указатель |
| `state-machines/alula-data-types.md` | [docs/data-types.md](https://github.com/nv-lang/nova-alula/blob/main/docs/data-types.md) | указатель |
| `state-machines/alula-debugging.md` | [docs/debugging.md](https://github.com/nv-lang/nova-alula/blob/main/docs/debugging.md) | указатель |
| `state-machines/alula-diagrams/*.svg` (5 файлов: `alula-agent-step-graph.svg`, `alula-data-flow.svg`, `alula-entities.svg`, `alula-pipeline.svg`, `alula-sequence.svg`) | [docs/diagrams/](https://github.com/nv-lang/nova-alula/tree/main/docs/diagrams) (те же имена) | — |
| `state-machines/alula-logo/README.md` | [assets/logo/](https://github.com/nv-lang/nova-alula/tree/main/assets/logo) (README и файлы логотипа) | — |
| `doc/alula-history.md` | [docs/history.md](https://github.com/nv-lang/nova-alula/blob/main/docs/history.md) | указатель |

Копии в nova-alula отличаются от файлов коммита 0d95919 только ссылками и путями: ссылки на оставшиеся файлы методики там абсолютные (`https://github.com/unitcraft/ai-dev-methodology/blob/main/state-machines/…`), а проверки `check-alula-keywords.py` и `check-alula-samples.py` считают пути от корня пакета и берут словарь методики по указанному пути.

## Как проверить образцы и словарь

Словарь `state-machine-glossary.md` остался в методике, а хеш его нормативной части закреплён форматом Алулы. Поэтому правку словаря проверяют проверками из nova-alula, указав им путь к словарю методики: аргумент `--glossary <путь>` (или `--glossary=<путь>`), иначе переменная среды `ALULA_GLOSSARY`; аргумент сильнее. Без пути проверки имён по словарю пропускаются с явным сообщением.

Из корня клона nova-alula (пути — пример: методика склонирована в `C:/work/ai-dev-methodology`):

```
python tools/check-alula-keywords.py --glossary C:/work/ai-dev-methodology/state-machines/state-machine-glossary.md
python tools/check-alula-samples.py --glossary C:/work/ai-dev-methodology/state-machines/state-machine-glossary.md
python tools/check-alula-translation.py
```

`--selftest` у каждой — с самопроверкой мутациями. Код возврата 1 при расхождениях. Ожидаемый итог для словаря версии 11 и пакета 0.3.2: таблица слов 218 строк, хеш словаря `60383c370415`, расхождений 0.
