# WC-4: Минимальный host и тестовый исполнитель

Эпик: `doc/tasks/work-coordinator-epic`

## Результат и границы

Минимальный host с устойчивыми state/inbox/outbox/pins, typed controls, доверенным owner source, восстановлением после рестарта и тестовым исполнителем. Backend выбирается только после решений Q-1/Q-2. Реальные интеграции и production-эффекты не входят.

## REQ/AC эпика

REQ-2, REQ-3, REQ-6–8; AC-2, AC-3, AC-6–8.

## Зависимости

Зависит от: `doc/tasks/work-coordinator-epic/wc-2-common-contract`, `doc/tasks/work-coordinator-epic/wc-3-acceptance-scenarios`.

Блокирует: `doc/tasks/work-coordinator-epic/wc-5-end-to-end`.

Пересекается (файлы): общий host/runtime — один владелец результата.

Начинается после: WC-2 и WC-3 приняты; Q-1/Q-2 решены; сопряжение с эпиком 0.29 подтверждено.

## Приёмка

Автотесты проверяют восстановление, повторы, корреляцию доставки, срок/эскалацию, stale transition, unknown effect, typed control и отказ forged owner decision. Гарантии backend не заявлены до выбора и проверки. Не запускать до предшественников и решений.
