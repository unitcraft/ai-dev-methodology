# Результат задачи 095

## Артефакт и граница

Добавлен один локальный исполняемый сквозной сценарий WC-5/S20:

- `scenario_s20.py` — детерминированный oracle-driver поверх принятого WC-4 host fixture;
- `test_e2e_s20.py` — исполняемый сквозной тест и reverse-пробы.

Использованы опубликованные входы: WC-3 `669939fee2e9c1c3f6d5d41b411302b37ef97417` и WC-4 `f7b17ddb26c92ea35e522386e7016d9f3c2cca25`. WC-4, WC-3, WC-2, движок и методика не менялись. Это не production host, не runtime conformance, не backend и не внешняя интеграция; trusted owner decision и delivery моделируются только локальной доверенной фикстурой с тем же correlation id.

## Покрытый сценарий

S20: root `E0`, nested `E1`, независимая параллельная `T2`; `T1` меняет `src-A` во время работы; адресная пересверка сначала только `T1`, затем отдельная пересверка downstream `T3` после принятия `T1/build/V2`; `T3` стартует из `ready`; `T2` завершается без перезапуска и без смены pin `input/V1`; после durable common intent `Q17` выполняется restart, восстанавливается тот же intent id, доставляется локальный receipt, применяется коррелированный trusted `accept`, затем фиксируется общая приёмка объединённого результата.

## DoD и проверки

- dod-evidence: каждая строка ниже доказана командой или именем теста.
- trace-decisions: нет `NOT VERIFIED` и `FAIL` без решения владельца; все reverse-исходы ожидаемо красные по названной причине.
- reverse-probe: красные пробы при потере пересверки `T1`, пересверки `T3`, delivery receipt и общей owner-приёмки; зелёный полный сценарий после возврата шагов.
- test-counts: 095 — 6 тестов, 0 пропусков; baseline WC-4 — 8 тестов, 0 пропусков; расхождение только +6 новых тестов 095.
- secrets-scan: по файлам сдачи и diff поиск URL, почтовых адресов, абсолютных машинных путей, секретов/реквизитов и персональных данных дал `NO_MATCHES`; ручная проверка также нарушений не выявила.
- single-commit: индекс перед коммитом содержал ровно 5 файлов задачи 095; один коммит, английское сообщение без подписей/трейлеров/имён моделей.

1. `python -m unittest -v test_e2e_s20` из каталога задачи 095: `Ran 6 tests ... OK`.
   Имена: `test_s20_green_nested_parallel_change_restart_owner_and_common_acceptance`, `test_reverse_probe_red_when_t1_input_revalidation_missing`, `test_reverse_probe_red_when_t3_dependency_revalidation_missing`, `test_reverse_probe_red_when_delivery_receipt_not_restored`, `test_reverse_probe_red_when_common_owner_acceptance_missing`, `test_restart_preserves_same_owner_intent_id_and_t2_pin`.
2. Reverse-пробы красные по названной причине при отключении: пересверки входа `T1`, пересверки зависимости `T3`, восстановления/наличия коррелированного delivery receipt, общей owner-приёмки. После включения шагов тот же сценарий зелёный.
3. Базовый WC-4 host не изменён; контрольный прогон `python -m unittest -v test_host` из `doc/tasks/094-wc-4-2-polnyy-minimalnyy-host`: `Ran 8 tests ... OK`.
4. Числа: здесь 6 тестов, 0 пропусков; baseline WC-4 — 8 тестов, 0 пропусков. Расхождение только добавленными 6 тестами 095; изменений/удалений baseline нет.
5. `git diff --check` — пустой вывод, код 0.
6. Сканирование секретов/реквизитов/URL/почтовых адресов/абсолютных машинных путей/персональных данных по diff и файлам сдачи: совпадений нет; ручная проверка добавленных файлов также таких данных не выявила.

## Сдача

Один коммит в ветке `task/095-wc-5-ispolnyaemyy-skvoznoy-scenariy`; индекс перед коммитом содержит только файлы задачи 095. Owner acceptance, merge и push не выполнялись.
