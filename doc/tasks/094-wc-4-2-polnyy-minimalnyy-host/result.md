# Результат задачи 094

## Артефакт и граница

Расширены `host.py` и `test_host.py` в этой карточке. Это локальная проверочная модель WC-4, не production host и не runtime conformance. JSON-файл служит только демонстрацией сохранения/восстановления. WC-2, WC-3, движок и их сценарии не менялись.

Проверяемые возможности: единый граф containment/dependency с отклонением цикла до изменения графа; адресные pins с сохранением версии; политики изменения input и отдельные blocker/latch с типизированным разрешением; durable owner-intent и восстановление после нового Host; агрегирование результатов epic; typed admission с проверкой формы/типа/revision и idempotent receipt/dedup после restart.

## DoD и проверки

1. `python -m unittest -v test_host` из каталога задачи: `Ran 8 tests ... OK`. Имена: `test_graph_pins_and_cycle_rejected_without_mutation`, `test_input_policies_and_independent_blockers`, `test_missing_policy_pauses_and_reject_policy_is_atomic`, `test_durable_owner_intent_survives_restart_and_conflict_rejected`, `test_aggregate_reflects_all_children_and_persists`, `test_typed_admission_dedup_restart_and_rejections`, `test_stale_revision_and_start_guard`, `test_reverse_probe_without_durable_write_is_red`.
2. Reverse-probes: цикл отвергается без мутации; policy reject оставляет прежний input; разрешение blocker другого типа отвергается; start из queued отвергается; malformed/unknown typed events отвергаются без receipt; повтор того же event после restart возвращает прежний outcome без повторного применения; удаление долговечной записи intent делает `test_reverse_probe_without_durable_write_is_red` красным с `durable write missing`, восстановление записи даёт зелёный тест.
3. Числа: baseline WC-4.1 — 3 теста, 0 пропусков (`doc/tasks/093-wc-4-1-minimalnyy-in-memory-host/result.md`, команда `python -m unittest -v test_host`). Здесь 8 тестов, 0 пропусков: добавлено 5 проверок, изменений/удалений baseline тестов нет.
4. `git diff --check` — ожидается пустой вывод, код 0 (проверить перед коммитом).
5. Сканирование секретов/реквизитов/URL/почтовых адресов/абсолютных машинных путей/персональных данных по diff и файлам сдачи — совпадений нет; ручная проверка добавленных файлов также не выявила таких данных.

## Ограничения и открытая граница

Реализация специально компактна: нет полной машины WC-2, trusted owner decision, внешней доставки/effects, общей nested-epic рекурсии и сопряжения с движком. В доступных артефактах нет подтверждённого runtime API WC-2/WC-3/092; поэтому тесты проверяют только поведение этого локального host и не подменяют runtime conformance. Это оставшийся интерфейсный gap, не заявка на изменение WC-2/WC-3/движка. WC-5/WC-6, backend, сервисы и внешние эффекты не реализованы.

## Сдача

До коммита индекс должен содержать только файлы задачи 094: `host.py`, `test_host.py`, `result.md`. В отчёте сдачи указать точный SHA. Merge/push и owner gate не выполняются.
