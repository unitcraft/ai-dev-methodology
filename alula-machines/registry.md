# Реестр методики: примитивы шага агента, совещания, запуска сессии и раннера задачи

Данные методики (71 инструмент и типы их подписей), которые она регистрирует у языка; в языке записи машин инструмент называется «внешняя функция» (раздел 7 спецификации языка). Примитивы `time_now` и `new_id` — язык (раздел 7а, AL-113), здесь их нет. Наборы типов: основной (`standard`), `session` (типы запуска сессии: свои `Finding`, `Severity`, `Summary`) и `runner` (типы раннера). Наборы `session` и `runner` включают основной набор целиком; в их таблицах записаны только свои типы и типы, заменяющие одноимённые типы основного набора (у `session` — `Finding`, `Severity`, `Summary`), повторы не пишутся. Контракт доверенного ввода и доказательств — [task-runner.md](../task-runner.md), «Смена маршрута»; проверка происхождения не заменяется значениями тестового хозяина.

Форма — раздел 7 спецификации Алулы: имена — JSON-имена реестра хозяина; типы — как пишет дерево `machine/2` (`int>=0`, `?text`, `[]Finding`, `"a" \| "b"`); `\|` внутри ячейки — знак `|`; списки «читает» и «пишет» разделены `;`; `—` — пусто. Файл читает `parse_registry_table` пакета `alula` (`alula.machine_table`), программа `alula` берёт его рядом с машинами (`registry.md`) или флагом `--registry`: строка примитива — ровно шесть ячеек, седьмой столбец в таблице «Primitives» не бывает. Причина исключения предметного инструмента (правило 14б `state-machines/state-machine-spec.md`: что теряется при разложении на универсальные примитивы) пишется в отдельной таблице раздела «## Reasons» — загрузчик её не читает (первая ячейка заголовка не `name`), страж универсальности (задача 103) сверяет её с таблицей «Primitives».

## Primitives

| name | parameters | result | class | reads | writes |
|---|---|---|---|---|---|
| verify_owner_route_decision | task_dir: text; reference: text | ?RouteDecision | volatile | objects: trusted saved owner decisions | — |
| route_gate_subject | task_dir: text; state: text | text | volatile | objects: current gate subject and artifact versions | — |
| record_route_gate | task_dir: text; gate: text; epoch: int>=0; subject: text; state: text | — | acting | — | objects: trusted gate openings |
| verify_route_gate_decision | task_dir: text; gate: text; epoch: int>=0; reference: text; subject: text | ?GateDecision | volatile | objects: trusted gate openings and saved decisions | — |
| specification_kind | — | "full" \| "brief" | volatile | objects: saved origin of the current specification | — |
| review_history | stage: Stage | []ReviewHistoryEntry | volatile | objects: ordered immutable review records with artifact versions | — |
| review_context | stage: Stage | text | volatile | objects: current goal, boundaries and versioned inputs of the stage | — |
| delivery_revision | — | text | volatile | objects: current delivery artifact version | — |
| create_draft_brief_copy | — | — | acting | objects: brief | objects: draft copy without approval |
| small_route_conditions | task_dir: text | ?SmallRouteConditions | volatile | objects: scope estimate, reversibility and preview availability | — |
| small_route_evidence | task_dir: text | ?SmallRouteEvidence | volatile | objects: versioned brief, test, guard and preview evidence | — |
| worktree_revision | repo_dir: text | text | volatile | objects: content revision of the full working tree | — |
| party_profile | party: text | AgentProfile | volatile | project setting: role profiles | — |
| role_context | context: RoleContext | text | volatile | project objects | — |
| call_trace | — | text | volatile | envelope of the call | — |
| call_step | — | int>=0 | volatile | envelope of the call | — |
| parse_witness_reply | reply: AgentReply | []WitnessAnswer | volatile | object: artifact file of the reply; object: proposal | — |
| parse_author_reply | reply: AgentReply | EditResult | volatile | object: artifact file of the reply | — |
| parse_lens_reply | reply: AgentReply | LensResult | volatile | object: artifact file of the reply | — |
| proposal_read | — | bool | volatile | object: proposal | — |
| proposal_with_fingerprint | — | text | volatile | object: proposal | — |
| proposal_changed_since_attempt | — | bool | volatile | object: proposal | — |
| count_in_model_tally | finding: Finding | — | acting | — | buffer: model tally |
| journal_findings | findings: []Finding | — | acting | — | — |
| journal_machine_data | — | — | acting | all_data | — |
| journal_decision | decision: text; source: text; passes: int>=0; open: []Finding | — | acting | — | — |
| remove_unsound | number: int>=1 | — | acting | lens_findings | lens_findings |
| build_summary | number: int>=1 | ?Summary | volatile | lens_findings; lenses | object: summary file |
| close_for_writing | object: text | — | acting | — | — |
| open_for_writing | object: text | — | acting | — | — |
| move_to_archive | number: int>=0; suffix: int>=0 | — | acting | — | — |
| reply_validation | — | ReplyCheck | volatile | reply_text; reply_artifact; agent_request; objects: session files | service record: form remarks (read by the turn fix) |
| close_agent_turn | — | — | acting | — | — |
| check_cache | dialog_kind: "main" \| "delivery" | — | acting | — | service record: request start mark |
| launch_scope | — | LaunchScope | volatile | objects: measure of the dialog of the launch | — |
| launch_profile | session: text | AgentProfile | volatile | service store: profile confirmed at the gate of the profile | — |
| session_context | session: text; source: text; launch_pass: ?int; delivery_mode: text; task_dir: text; repo_dir: text; route: text; source_list: ?text; delivery_short: bool | text | volatile | objects: plan of the task, prompts of the sessions, dialog of the author | — |
| parse_session_artifact | session: text; reply: AgentReply | SessionParsing | volatile | objects: artifact file of the session | — |
| prepare_launch | session: text; launch_pass: ?int; task_dir: text; repo_dir: text | — | acting | — | objects: group of the processes of the agent, record of the launch, marks progress.log and profile.log |
| finish_launch | session: text; launch_pass: ?int; task_dir: text; answered: bool | — | acting | objects: profile.log, progress.log, dialog of the agent | objects: hint from profile.log, check of progress.log, transcript of the dialog |
| stop_agent_group | — | — | acting | — | — |
| run_preparation | task_dir: text; repo_dir: text | PreparationResult | acting | objects: state of the runner, files of the cycles on the disk, lock, mark of the tree | objects: lock of the runner, state, file of a torn pass |
| specification | — | TaskDocumentState | volatile | objects: spec.md | — |
| task_plan | — | TaskDocumentState | volatile | objects: plan.md | — |
| implementation_report | — | TaskDocumentState | volatile | objects: result.md | — |
| route_features | — | ?RouteFeatures | volatile | objects: section Route features of the brief | — |
| project_settings | — | ProjectSettings | volatile | project setting: thresholds and numbers of the cycle by the routes | — |
| source_list | — | ?text | volatile | objects: line Source list of the brief | — |
| brief_complete | — | bool | volatile | objects: brief task/message.md | — |
| copy_approval | word: text; date: text | Approval | volatile | objects: brief task/message.md | — |
| approval_by_document | document: TaskDocument | Approval | volatile | objects: spec.md, plan.md | — |
| source_with_specification_marks | source: text | text | volatile | objects: specification, file of the review | — |
| last_implementation_review | — | ?text | volatile | objects: last file of the implementation review | — |
| has_unresolved_line | — | bool | volatile | objects: implementation report | — |
| customer_letter | — | ?text | volatile | objects: letter to the customer | — |
| round_letters | round: int>=0 | ?text | volatile | objects: letters of the rounds | — |
| secrets_report | — | ?text | volatile | objects: last file of the implementation review | — |
| acceptance_criteria | — | []text | volatile | objects: acceptance criteria of the brief task/message.md | — |
| tree_diff | — | text | volatile | objects: working tree | — |
| commit_message | — | text | volatile | objects: history of the working tree | — |
| commit_text | — | text | volatile | objects: commit.txt | — |
| feedback_route | — | ?text | volatile | objects: file of the feedback analysis | — |
| write_answers | answers: text | — | acting | — | objects: section Answers of the specification |
| write_decisions | decisions: text | — | acting | — | objects: section Requires approval of the plan |
| write_owner_marks | decisions: text | — | acting | — | objects: implementation report |
| save_round_notes | round: int>=0; text: text | — | acting | — | objects: folder of the feedback round |
| write_draft_status | document: TaskDocument | — | acting | — | — |
| create_approved_copy | word: text; date: text | — | acting | — | — |
| rename_letter | round: int>=0 | — | acting | — | — |
| release_lock | — | — | acting | — | — |
| show_human | text: text | — | acting | — | — |

## Reasons

Правило 14б `state-machines/state-machine-spec.md`: предметный инструмент допустим, только если не раскладывается на универсальные примитивы среды исполнения (чтение файла, запись файла, запуск команды) без потери смысла; причина — что теряется при разложении — называется при его объявлении. Причина каждого предметного инструмента — ниже, отдельной таблицей: седьмой столбец в таблице «Primitives» ломает загрузку реестра (`parse_registry_table` читает строку примитива ровно из шести ячеек). Каждая причина записана тремя частями: почему инструмент не убрать безболезненно, что он даёт, чего лишимся, если уберём. Строка причины не называет других инструментов реестра: такая декларация признала бы разложение (уточнение критерия стража, письмо интегратора 2026-11-06). Общее для всех 71: имена и сигнатуры инструментов — контракт хозяина; по ним 595 тестов машин скриптуют ответы хозяина, поэтому убрать любой инструмент без замены контракта нельзя — это отдельная переделка машин и фикстур. Проверяет страж задачи 103.

| tool | reason |
|---|---|
| verify_owner_route_decision | не убрать безболезненно: смена маршрута по сигналу со ссылкой перестанет проверяться по происхождению, а ответы хозяина на него скриптуют тесты смены маршрута; даёт: проверенную запись сохранённого решения владельца (задача, маршрут, основание, слово, дата, источник) либо отсутствие; если убрать: машина примет самозаявленное «owner=true» из полей события — граница доверенного ввода «Смены маршрута» (task-runner.md) исчезнет |
| route_gate_subject | не убрать безболезненно: после смены маршрута ворота потеряют предмет решения: версии артефактов, состояние и нерешённые вопросы машине недоступны; даёт: версию предмета открытия ворот одним снимком; пустая строка не подтверждает предмет; если убрать: решение ворот сверять не с чем — защита от ответов, несовместимых с текущим предметом, падает |
| record_route_gate | не убрать безболезненно: открытия ворот перестанут сохраняться идемпотентно по задаче и идентификатору; даёт: запись номера открытия, эпохи и предмета с задачей и состоянием; повтор после сбоя возвращает ту же запись, а не второе открытие; если убрать: хозяин не свяжет будущее решение с открытием: сбой между открытием и решением даст второе разрешение на то же ворота |
| verify_route_gate_decision | не убрать безболезненно: ответы ворот перестанут связываться с сохранённым открытием, эпохой и полномочиями автора; даёт: проверенную запись решения (задача, открытие, эпоха, предмет, исход, автор, источник, полномочия); если убрать: решение возьмётся из самозаявленного содержимого события — разрешение ворот подделывается текстом письма |
| specification_kind | не убрать безболезненно: различие полной спецификации и копии постановки по происхождению, а не имени файла, исчезнет; даёт: «full» или «brief» по сохранённому происхождению действующего документа; если убрать: копия постановки пройдёт за полную спецификацию — зачёт документов пойдёт по чужому документу |
| review_history | не убрать безболезненно: зачёт стадий по чистой серии заходов перестанет опираться на неизменяемые записи; даёт: упорядоченные записи реальных заходов: версия артефакта, контекст, номер, чистота, пробы, независимость, доказательство; если убрать: серия считается из состояния машины: пропуск или повтор номера создадут чистую серию, история обманется |
| review_context | не убрать безболезненно: зачёт потеряет снимок цели и границ стадии на момент проверки; даёт: версию цели, границ и версионных входов стадии одним атомарным снимком; если убрать: проверка зачтёт по текущим файлам, а не по версии проверяемого — результат подтвердит другое |
| delivery_revision | не убрать безболезненно: снимок зачёта сдачи потеряет версию артефакта сдачи; даёт: версию содержимого артефакта сдачи (не время изменения файла); если убрать: зачёт не заметит подмены содержимого артефакта между проверками |
| create_draft_brief_copy | не убрать безболезненно: черновик постановки для малого маршрута не создастся без утверждения; даёт: копию постановки, не утверждая её и не заменяя уже имеющийся документ; если убрать: придётся либо утвердить копию, либо править постановку в обход утверждения |
| small_route_conditions | не убрать безболезненно: малый маршрут потеряет проверку допуска по соразмерности исполнения; даёт: исходную оценку и суммарный объём слова или эпика, накопленное время, обратимость, наличие внешних эффектов и доступность экземпляра для просмотра; начало отсчёта — от исходного слова владельца; если убрать: необратимая, большая или непроверяемая правка пойдёт мгновенным путём — цена ошибки малого маршрута перестанет быть малой |
| small_route_evidence | не убрать безболезненно: ворота малого зачёта останутся без доказательств для текущей версии; даёт: постановку с примером приёмки, результаты тестов и стражей, доступный экземпляр и при необходимости независимый просмотр различий; тесты правки — только с сохранённым красным прогоном до кода; если убрать: малый результат примется вслепую: без красного прогона, экземпляра и просмотра; приёмка всё равно не давала бы разрешений коммита и публикации, а теперь не даст и уверенности |
| worktree_revision | не убрать безболезненно: снимки зачёта и пересверки потеряют версию рабочего дерева; даёт: ревизию содержимого дерева (не время файлов) для снимков зачёта; если убрать: пересверка не заметит посторонней правки дерева между заходами — чужая правка пройдёт за свою |
| party_profile | не убрать безболезненно: ворота профиля в запуске сессии останутся без профиля стороны; даёт: профиль (семейство, модель, усилие) стороны из настроек проекта; если убрать: запуск не узнает, какой моделью и с каким усилием исполнять сторону |
| role_context | не убрать безболезненно: стороны-роли получат пустой контекст; даёт: текст контекста роли (свидетель, линза, правка, вопрос) снимком из объектов проекта; если убрать: роли будут работать без находок, предложения и ответа человека — формально, без смысла |
| call_trace | не убрать безболезненно: идентификация запроса по трассе конверта вызова исчезнет; даёт: трассу текущего вызова из конверта; если убрать: журнал и ответы не свяжутся с вызовом: повтор не отличить от нового запроса |
| call_step | не убрать безболезненно: нумерация шагов внутри вызова пропадёт; даёт: номер шага вызова из конверта; если убрать: порядок событий внутри вызова не восстановить — разбор сбоя станет слепым |
| parse_witness_reply | не убрать безболезненно: свидетель не сможет вернуть ответы на утверждения в типизированном виде; даёт: разбор артефакта ответа в список ответов по утверждениям (подтверждено или не измерено) со сверкой предложения; если убрать: машина станет извлекать ответы из свободного текста — сверка предложения и границы «не измерено» исчезнут |
| parse_author_reply | не убрать безболезненно: автор не сможет вернуть итог правки; даёт: разбор артефакта в «готово» с предложением или «вопрос» с предложением и вопросом; если убрать: итог правки определится по тексту письма — вопросы автора потеряются, ворота В4 не различат исходы |
| parse_lens_reply | не убрать безболезненно: линза не сможет вернуть находки со счётом проб; даёт: разбор артефакта ответа линзы в находки и число проб; если убрать: находки придётся извлекать из текста — пробы и структура находок потеряются, сводка исказится |
| proposal_read | не убрать безболезненно: стороны не узнают, есть ли предложение для работы; даёт: признак наличия и читаемости предложения; если убрать: машина обратится к объекту, пути к которому у неё нет — шаг упадёт или пройдёт мимо |
| proposal_with_fingerprint | не убрать безболезненно: смена и снятие предложения потеряют отпечаток для данных машины; даёт: текст предложения с отпечатком, вычисленным по правилам хозяина; если убрать: нечем сверять изменение предложения с момента попытки — повтор попытки уйдёт вслепую |
| proposal_changed_since_attempt | не убрать безболезненно: повтор попытки не отличит изменившееся предложение; даёт: сравнение предложения с сохранённой попыткой; если убрать: правка по устаревшему предложению пройдёт незамеченной — итог сверят не с тем |
| count_in_model_tally | не убрать безболезненно: свод находок по моделям перестанет вестись; даёт: учёт находки в служебном буфере свода моделей; если убрать: статистика моделей исчезнет — оценку качества моделей по находкам не собрать |
| journal_findings | не убрать безболезненно: журнал потеряет записи находок проверок; даёт: запись находок в журнал по таблице шаблонов хозяина; если убрать: след проверки в журнале исчезнет — приёмка потеряет доказательство, разбор цикла — находки |
| journal_machine_data | не убрать безболезненно: журнал не получит снимок данных машины на конец работы; даёт: служебную запись всех данных машины; если убрать: разбор сбоя и перенос сохранённой задачи станут невозможны — состояние не восстановить |
| journal_decision | не убрать безболезненно: журнал не зафиксирует решение проверки с числом заходов и открытыми находками; даёт: запись решения по таблице шаблонов хозяина; если убрать: решение останется только в данных машины — история цикла его не увидит, повторный цикл не узнает |
| remove_unsound | не убрать безболезненно: необоснованные находки не снимутся со свода линз; даёт: снятие находки по номеру из служебного буфера линз; если убрать: отвергнутые находки продолжат блокировать зачёт — цикл зациклится на отклонённом |
| build_summary | не убрать безболезненно: сводка цикла не соберётся и не запишется; даёт: сводку (число критичных, пробы) с записью файла сводки; если убрать: итог цикла останется в буфере — файла сводки не будет, человек его не увидит |
| close_for_writing | не убрать безболезненно: объект не закроется для записи перед снятием копии; даёт: закрытие внешнего объекта для записи; если убрать: снятие копии поймает объект в середине записи — копия будет повреждена |
| open_for_writing | не убрать безболезненно: объект не откроется для записи после снятия; даёт: возврат внешнего объекта в редактируемое состояние; если убрать: документ останется закрытым — правки по итогам ворот в него не попадут |
| move_to_archive | не убрать безболезненно: архивная версия записи не сохранится при замене; даёт: перенос записи в архив с номером и суффиксом; если убрать: прежняя версия потеряется — историю записи не восстановить, откат невозможен |
| reply_validation | не убрать безболезненно: ответ агента перестанет проверяться по правилам формы; даёт: вердикт формы (годен, нарушен, пуст) со служебной записью замечаний для правки хода; если убрать: нарушения формы ответа пройдут в работу — правка хода не сработает, цикл пойдёт по ложному итогу |
| close_agent_turn | не убрать безболезненно: ход агента не закроется протокольно; даёт: закрытие хода агента средой исполнения; если убрать: ресурсы хода повиснут — повтор хода станет невозможен, запуск встанет |
| check_cache | не убрать безболезненно: кеш диалога не проверится перед запросом; даёт: проверку кеша (основной диалог или сдача) и служебную отметку начала запроса; если убрать: повторный запрос уйдёт заново — цена и время вырастут, отметка начала запроса потеряется |
| launch_scope | не убрать безболезненно: ворота объёма запуска не решат, влезает ли диалог; даёт: меру диалога запуска (влезает или не влезает), измеренную хозяином; если убрать: запуск с гарантированным превышением контекста уйдёт в работу и упадёт дороже, чем ворота |
| launch_profile | не убрать безболезненно: ворота профиля не получат подтверждённый профиль; даёт: профиль запуска из служебного хранилища ворот профиля; если убрать: запуск не узнает подтверждённую модель и цену — исполнение уйдёт не туда |
| session_context | не убрать безболезненно: промпт сессии не соберётся из источников задачи; даёт: текст промпта одним снимком: план задачи, промпты сессий, диалог автора, параметры маршрута; если убрать: машина соберёт промпт сама без плана и диалога автора — сессия потеряет контекст задачи |
| parse_session_artifact | не убрать безболезненно: итог сессии не разберётся из артефакта; даёт: итог сессии (готово, правка, план, требования, вопрос) со сводкой и находками; если убрать: итог придётся определять по тексту — ветвления после сессии в раннере и запуске сломаются |
| prepare_launch | не убрать безболезненно: запуск не подготовится: ни процессов, ни записи, ни отметок; даёт: группу процессов агента, запись запуска, отметки журналов прогресса и профиля; если убрать: сессия не стартует — механизм запуска пуст |
| finish_launch | не убрать безболезненно: итог запуска не зафиксируется и не расшифруется; даёт: подсказку из профиля, проверку прогресса и расшифровку диалога из служебных записей; если убрать: ворота сбоя сессии не узнают, что случилось — сессию не восстановить, повтор уйдёт вслепую |
| stop_agent_group | не убрать безболезненно: группа процессов не остановится перед подготовкой к запуску; даёт: остановку группы процессов агента средой; если убрать: при возобновлении задачи старая группа останется жить и помешает новой — запуск зациклится |
| run_preparation | не убрать безболезненно: раннер не подготовится к циклу: состояние, занятость дерева и замка не прочитаются снимком; даёт: снимком состояние раннера, файлы заходов, замок и метку дерева, номер цикла и итог подготовки; если убрать: два раннера возьмут одно дерево — ворота «дерево занято» и «не остановлена группа» не сработают |
| specification | не убрать безболезненно: зачёт документов в воротах разбора потеряет состояние спецификации; даёт: наличие, статус (черновик, утверждён, в работе, готов), стоп-слово и хеш спецификации; если убрать: машина не отличит черновик от утверждённого — ворота утверждения и снятия потеряют предмет |
| task_plan | не убрать безболезненно: зачёт в воротах плана потеряет состояние плана; даёт: наличие, статус, стоп-слово и хеш плана; если убрать: ворота плана и решений сверят не тот документ — очереди правок собьются |
| implementation_report | не убрать безболезненно: зачёт реализации и сдачи потеряет состояние отчёта; даёт: наличие, статус, стоп-слово и хеш отчёта реализации; если убрать: ворота реализации не заметят неготовый отчёт — зачёт пойдёт по пустому |
| route_features | не убрать безболезненно: классификация маршрута потеряет признаки из постановки; даёт: цель, число источников и частей, риск, необратимость, известность причины, касание нормы из раздела постановки; если убрать: маршрут предложится вслепую — пороги малый, быстрый и полный не применить |
| project_settings | не убрать безболезненно: проверка параметров проекта исчезнет; даёт: пороги маршрута и числа цикла по маршрутам из настроек проекта; если убрать: раннер не остановится на настройке ниже минимума — ослабление инварианта пройдёт молча |
| source_list | не убрать безболезненно: перечень источников не прочитается из постановки; даёт: строку перечня источников постановки; если убрать: сужение проверки по критериям приёмки невозможно — проверка пойдёт не по тем исходам |
| brief_complete | не убрать безболезненно: проверка готовности постановки исчезнет; даёт: признак завершённости постановки по правилам хозяина; если убрать: незавершённая постановка пойдёт в работу — цикл начнётся без критериев |
| copy_approval | не убрать безболезненно: копия постановки не получит утверждение по слову и дате; даёт: запись утверждения (дата, кто, хеш), проверенную по постановке; если убрать: утверждение копии не зафиксируется — малый маршрут потеряет основание слова |
| approval_by_document | не убрать безболезненно: ворота утверждения не сверят утверждение с документом; даёт: утверждение со сверкой хеша и статуса документа; если убрать: утверждение устаревшей версии пройдёт — «утверждение действует» перестанет работать |
| source_with_specification_marks | не убрать безболезненно: снятие документа потеряет отметки сомнительных мест; даёт: исходник с наложенными отметками спецификации и файла проверки; если убрать: сессия снятия получит чистый исходник — отметки не дойдут до проверяющего |
| last_implementation_review | не убрать безболезненно: сдача не найдёт последнюю проверку реализации; даёт: текст последнего файла проверки реализации; если убрать: ворота сдачи не сверят отчёт с последней проверкой — сдача пойдёт вслепую |
| has_unresolved_line | не убрать безболезненно: проверка неразрешённых строк отчёта исчезнет; даёт: признак неразрешённой строки в отчёте реализации; если убрать: отчёт с нерешённым вопросом пройдёт зачёт реализации |
| customer_letter | не убрать безболезненно: сдача не получит письмо заказчику; даёт: текст письма заказчику или отсутствие; если убрать: машина напишет письмо без исходного — формулировки разойдутся с обещанным |
| round_letters | не убрать безболезненно: разбор обратной связи не получит письма раунда; даёт: письма раунда обратной связи по номеру; если убрать: раунд не разберётся — маршрут «обратная связь» потеряет вход |
| secrets_report | не убрать безболезненно: сдача потеряет отчёт о секретах; даёт: отчёт о секретах из последней проверки реализации; если убрать: утечка реквизитов не попадёт в проверку сдачи |
| acceptance_criteria | не убрать безболезненно: проверка сдачи по критериям исчезнет; даёт: список критериев приёмки из постановки; если убрать: сдача примется целиком или никак — точные критерии не проверить, частичную приёмку не провести |
| tree_diff | не убрать безболезненно: различия дерева не получить с доверенными фильтрами; даёт: текст различий рабочего дерева с фильтрами и исключениями хозяина; если убрать: посторонние и служебные файлы попадут в сдачу — разрешение коммита потеряет предмет |
| commit_message | не убрать безболезненно: сообщение коммита не прочитается из истории дерева; даёт: текст сообщения последнего коммита рабочего дерева; если убрать: ворота коммита сверят не то — разрешение коммита потеряет предмет |
| commit_text | не убрать безболезненно: текст коммита из предметного файла не прочитается; даёт: содержимое файла с текстом коммита, который написал человек; если убрать: машина не узнает текст, зафиксированный человеком — ворота коммита не сработают |
| feedback_route | не убрать безболезненно: маршрут из разбора обратной связи не прочитается; даёт: маршрут, записанный в файле разбора обратной связи; если убрать: после обратной связи раннер не узнает, куда идти — ветвление продолжения потеряет основание |
| write_answers | не убрать безболезненно: ответы на вопросы не запишутся в документ; даёт: запись ответов в предметный раздел спецификации; если убрать: ответы останутся в данных машины — документ их не получит, следующая сессия не увидит |
| write_decisions | не убрать безболезненно: решения не запишутся в постановку; даёт: запись решений в предметный раздел «требует утверждения»; если убрать: владелец не увидит решений в документе — ворота решений потеряют предмет |
| write_owner_marks | не убрать безболезненно: решения владельца не попадут в отчёт; даёт: запись решений владельца в отчёт реализации; если убрать: итог сдачи не зафиксируется в документе — отчёт разойдётся с принятым |
| save_round_notes | не убрать безболезненно: заметки раунда не сохранятся; даёт: запись текста заметок в папку раунда обратной связи; если убрать: разбор раунда не оставит следа — повторный раунд начнёт с нуля |
| write_draft_status | не убрать безболезненно: статус документа не запишется; даёт: запись статуса черновика документа; если убрать: снятие документа не пометит его — повторное снятие не отличит свежую копию |
| create_approved_copy | не убрать безболезненно: утверждённая копия не создастся доверенно; даёт: создание утверждённой копии по слову и дате с проверкой происхождения; если убрать: копия не появится или появится без утверждения — происхождение утверждённого документа потеряется |
| rename_letter | не убрать безболезненно: письмо раунда не переименуется; даёт: переименование письма по номеру раунда; если убрать: переписка раунда собьётся — письма раундов не опознать |
| release_lock | не убрать безболезненно: замок раннера не снимется в конце работы; даёт: снятие замка с гарантией исключительности; если убрать: дерево останется занятым — следующая задача встанет; отметка в журнале при этом уже написана |
| show_human | не убрать безболезненно: человек не увидит тексты ворот и итогов; даёт: показ текста человеку вне каналов машины; если убрать: ворота замолчат — владелец не узнает, что ждёт его решения; при сбое показа отметка в журнале уже сохранена |


## Types

| type | kind | members |
|---|---|---|
| RouteDecision | record | task: text; reference: text; route: "full" \| "fast" \| "small"; basis: text; word: text; date: text; source: text |
| GateDecision | record | task: text; reference: text; gate: text; epoch: int>=0; subject: text; word: text; text: text; factory_word: text; factory_word_date: text; date: text; author: text; source: text; actor: "owner" \| "delegate"; viewed_at: ?int>=0 |
| ReviewHistoryEntry | record | number: int>=1; hash: text; context: text; clean: bool; probes: int>=0; independent: bool; evidence: text |
| SmallRouteConditions | record | estimate_ms: ?int>=0; total_ms: ?int>=0; work_ms: ?int>=0; overhead_ms: ?int>=0; reversible: bool; external_effects: bool; preview: "test" \| "local" \| "none"; scope_word: text; started: int>=0 |
| SmallRouteEvidence | record | task: text; hash: text; brief: text; tests: text; guards: text; preview: text; visible: bool; independent_diff: text; tests_passed: bool; guards_passed: bool; preview_available: bool; diff_independent: bool; diff_ms: int>=0 |
| Finding | record | severity: Severity; evidence: text; repeat: bool; question: bool |
| Summary | record | critical: int>=0; probes: int>=0 |
| AgentProfile | record | family: text; model: text; effort: ?text |
| AgentModel | record | id: text; provider: text; variant: ?text |
| TokenUsage | record | input: ?int; output: ?int; reasoning: ?int; cache_read: ?int; cache_write: ?int |
| Usage | record | session: text; result: text; family: text; model: AgentModel; tokens: TokenUsage; cost: ?float; created: int; updated: int; context_used: ?int; trace: text; step: int |
| AgentReply | record | text: ?text; artifact: ?text; usage: Usage; request_started: ?int |
| Claim | record | kind: text; statement: text; source: text; excerpt: ?text; check: Check |
| LensResult | record | findings: []Finding; probes: int>=0 |
| JournalEvent | record | code: text; params: [](text, text) |
| Severity | variant | Critical; Significant; Desirable |
| Check | variant | Confirmed; ChannelDistortion; NotConfirmed |
| ReplyCheck | variant | Valid; Violated; Empty |
| WitnessAnswer | variant | Answered(claim: Claim); NotMeasured(claim: text) |
| EditResult | variant | Done(proposal: text); Question(proposal: text, question: text) |
| RoleResult | variant | WitnessOutcome(answers: []WitnessAnswer); LensOutcome(result: LensResult); EditOutcome(result: EditResult) |
| RoleContext | variant | WitnessContext(author_question: ?text, findings: ?[]Finding, proposal: text); LensContext(proposal: text, witness_answers: ?[]WitnessAnswer); FixContext(proposal: text, gate3_findings: []Finding, author_guidance: ?text); QuestionContext(author_question: text, proposal: text, gate3_findings: []Finding, human_answer: text) |

## Types: session

| type | kind | members |
|---|---|---|
| Finding | record | severity: Severity; level: Level; evidence: text |
| Summary | record | essential: int>=0; probes: int>=0 |
| SessionParsing | record | result: SessionResult; summary: ?Summary; findings: ?[]Finding |
| Severity | variant | Essential; Superficial |
| Level | variant | Implementation; Plan; Requirements; OutOfScope; Delivery |
| SessionResult | variant | Done; Revision; Plan; Requirements; Question |
| LaunchScope | variant | Fits; DoesNotFit |

## Types: runner

| type | kind | members |
|---|---|---|
| Cycle | record | number: int>=1; origin: int>=1; streak: int>=0; no_probes: int>=0 |
| Approval | record | date: text; who: text; hash: text |
| TaskDocumentState | record | exists: bool; status: DocumentStatus; stop_word: StopWord; hash: text |
| RouteFeatures | record | goal: text; sources: ?int; parts: ?int; risk: Risk; irreversible: Rating; cause_known: Rating; touches_norm: Rating; helper_proposal: text |
| RouteThresholds | record | max_sources: int>=0; max_parts: int>=0; allowed_risk: Risk |
| RouteSettings | record | ceiling: int>=0; clean_needed: int>=0; probes_min: int>=0; delivery_short: bool; relaxations: []text |
| ProjectSettings | record | thresholds: RouteThresholds; fast_proposal_allowed: bool; full: RouteSettings; fast: RouteSettings |
| PreparationResult | record | outcome: PreparationStatus; cycle: full {Stage: Cycle} |
| Stage | variant | Analysis; Plan; Implementation; Delivery; Meeting |
| TaskDocument | variant | Specification; Plan; ImplementationReport |
| DocumentStatus | variant | Draft; Approved; InProgress; Done; Unparsed |
| StopWord | variant | NoWord; Revision; Plan; Requirements; Question |
| Risk | variant | Low; Medium; High; Unrated |
| Rating | variant | Confirmed; No; Unrated |
| PreparationStatus | variant | Ready; BusyByLiveProcess; TreeBusyByOtherTask; GroupNotStopped |
