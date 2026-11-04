# Результат задачи 096

## Артефакт и граница

Добавлен один локальный агентный адаптер поверх входов, указанных интегратором:

- WC-4 host: `f7b17ddb26c92ea35e522386e7016d9f3c2cca25`;
- WC-5/S20: `3f53863d376746bf08d27b6f7eac947f73bf7a20`.

`agent_adapter.py` доставляет коррелированные решения только от доверенного источника, журналирует effect intent до вызова, возвращает сохранённый результат при повторе успешного эффекта и сохраняет `unknown` без blind retry. `test_agent_adapter.py` проверяет доставку и общую S20-приёмку, недоверенный/несопоставленный ответ, идемпотентный повтор, конфликт effect id и unknown после рестарта. Новых backend, сервисов и внешних интеграций нет; WC-4/WC-5 и контракт не менялись. Это локальный тестовый адаптер, не production интеграция и не гарантия exactly-once.

## Проверки и DoD

1. Команда `python -m unittest -v test_agent_adapter` из каталога задачи 096: `Ran 5 tests ... OK`.
   Имена: `test_decision_delivery_is_correlated_idempotent_and_accepts_s20`, `test_decision_delivery_rejects_untrusted_and_unmatched_decisions`, `test_effect_identity_conflict_is_rejected`, `test_effect_repeat_returns_receipt_without_duplicate_effect`, `test_unknown_effect_is_journaled_and_blind_retry_is_blocked`.
2. Reverse-пробы: отказ доставки/доверия и отсутствующий intent красные по причине несопоставленного или недоверенного ответа; unknown после рестарта красный по причине `blind retry blocked`, повторный вызов внешнего эффекта не происходит; повтор успешного effect зелёный и счётчик вызовов остаётся равен одному. Полный адаптерный набор после реализации зелёный.
3. Общая приёмка: тест `test_decision_delivery_is_correlated_idempotent_and_accepts_s20` вызывает S20 `common_acceptance()` только после коррелированной доставки доверенного `accept`; проверяется результат `E0=accepted`. WC-5 контрольный сценарий также проходит.
4. Test-counts: задача 096 — 5 тестов, 0 пропусков; WC-4 baseline — 8 тестов, 0 пропусков; WC-5 baseline — 6 тестов, 0 пропусков. Итого 19 тестов, 0 пропусков; расхождение относительно двух неизменённых baseline — ровно 5 новых тестов 096.
5. Команды-контроли: `python -m unittest -v test_host` в каталоге 094 — `Ran 8 tests ... OK`; `python -m unittest -v test_e2e_s20` в каталоге 095 — `Ran 6 tests ... OK`.
6. secrets-scan: поиск в изменённых файлах и staged diff URL, почтовых адресов, абсолютных машинных путей, секретов/реквизитов и персональных данных — `NO_MATCHES`; ручная проверка добавленных файлов также нарушений не выявила.
7. `git diff --check` — пустой вывод, код 0.

## Сдача

Проверяемый артефакт для автора — SHA коммита задачи 096, указанный в сдаче. Индекс перед коммитом содержит только `agent_adapter.py`, `test_agent_adapter.py` и этот файл. Owner gate, merge и push не выполнялись.
