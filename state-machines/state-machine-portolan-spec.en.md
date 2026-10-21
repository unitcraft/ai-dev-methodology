# Portolan: specification of the language for writing state machines as tables, version 2.13

Translation of [state-machine-portolan-spec.md](state-machine-portolan-spec.md); the Russian text is normative: on any difference the Russian text is correct.

The name of the notation is **“Portolan”** (`Portolan`; the owner's word, 2026-10-19: «Portolan - ОК»): a portolan is a medieval pilot chart on which ports and the routes laid between them are drawn; in the notation the states are the ports, the transitions are the routes between them, and the chart itself is compiled by people in ordinary words. A machine file is a “machine table” in Portolan. The name's availability was checked by a search on 2026-10-19: no programming language, format or state-machine tool with this name was found; there are small unrelated uses (a geospatial command-line tool and plugins for a geographic information system, a tool for a web-framework API, an inactive dynamic mapping platform, a German accounting-software firm), and there is no conflict with system software. The history, reasons and goals of the language are in [doc/portolan-history.md](../doc/portolan-history.md). **What the word means.** A portolan (Italian *portolano*, from *porto*, “port”) is a medieval pilot chart, originally a book of sailing directions (13th–17th centuries, the Mediterranean and Black Seas): a coastline, the names of ports along the coast, and a net of straight rhumb lines from a wind rose along which a navigator laid a course from port to port. The chart describes not the terrain but the routes between ports, and it was compiled by the sailors themselves in plain language; hence the ports are the states of the machine, the courses between them are the transitions, and the chart is written by people in ordinary words.

Format version: 2.13, 2026-10-20. Status: **experimental format; version 2.2 was implemented by an interpreter in another language; equality with the automaton by journal is confirmed on 39 scenarios of one small machine (the chat machine); the expressibility of “Agent step” and “Meeting” was checked by pilots; not implemented: nested machines, `Edits`, the party profile, `Request limit`, `Form returns`, `pass`.** The rules for writing machines are in [state-machine-spec.md](state-machine-spec.md); this file sets the formal notation of the same tables: types, expressions, actions, parties, fragments. The journal is [state-machine-journal.md](state-machine-journal.md); the glossary of English names is [state-machine-glossary.md](state-machine-glossary.md) (a source of suggested JSON names, section 1a). On a difference with the rules of the specification the specification is correct, and this file is corrected after it.

Goal: a machine is described by one file without code in Nova; from the description an executor gives the same behavior as the automaton in Nova: the same transitions, the same structured journal, the same data and queue. Checked by the expressibility of the automata rows (which rows are written without workarounds) and by running one small machine through an interpreter (comparison with the automaton by journal, the header).

The examples are taken from the pilots (excerpts of “Agent step” and “Meeting”); under each one it is said what was changed against the pilot's record. A construct used in an example is defined in sections 2–5, 7–9 or in the catalog (section 12). The labels in parentheses in the text are the numbers of corrections: of earlier versions (А, АМ, E, T, С, ША, ШМ, ШВ, СГ, ИС), of version 2.3 (Н-…), of version 2.4 (И-…), of version 2.5 (Т-…), of version 2.6 (С-1), of version 2.7 (П-1…П-9), of version 2.8 (Я-1…Я-4), of version 2.9 (Я-5…Я-18) of version 2.10 (Я-19…Я-21), of version 2.11 (Я-22), of version 2.12 (Я-23…Я-37) and of version 2.13 (Я-38…Я-49, section 0). The examples are excerpts: JSON names in parentheses (section 1a) are written in them only in state headings; in a machine file they are needed for all non-Latin names that leave the machine (the samples). The examples of this English version are written in the English form of the language (section 1a): the keywords come from the `en` column of the word table [portolan-keywords.tsv](portolan-keywords.tsv), and the names invented by an author are English (Latin), so each of them is its own JSON name.

## 0. What changed

**Against version 2.12.** The labels of version 2.13 are **Я-38…Я-49**: a simplification release. The source is the methodology's list of simplifications after the remarks of the consumer project (the neighbour's runtime, its task on nested machines and the cycle check); the owner's word, 2026-10-20: “agreed” («согласовано»).

| № | Correction | Where |
|---|---|---|
| Я-38 | a party signal instead of a word: the event `word(…)` and the event-kind word `word` are removed; a gate word of a human, an enhanced gatekeeper and a gatekeeper is a **party signal** `signal(…)`, declared in the column “signals” of the “Parties” table (formerly “gate_words”): the declaration itself names which party may give the signal; a party signal is accepted by a row of an appeal to that party; what happens to a declared signal for which the current state has no row is an open item (section 14); machine signals (the common events of a fragment) work as before; the fragment parameter `halt_word` of the kind `word` is `halt_signal` of the kind `signal`. The reason: a gate event was written by two kinds (`word`, `signal`) that differed only in who may give it; this is now said by the declaration at the party; a party signal is bound to the party's open request by rules 15–19 of the specification, as the word was | 1, 2, 3.1, 4.3, 9, 10, 11, 13, samples |
| Я-39 | the state key line `Input:` is split: for an appeal — `Request:` (the table of the request fields to the party; Russian — `Запрос:`, in JSON `inputs`), for an operation, a fork and an end — `Reads:` (the names the state reads; Russian — `Читает:`, in JSON `reads`); the machine section `## Input` does not change | 1b, 3, 4, 7, 9, 10, 13 |
| Я-40 | empty values are not written: a key with an empty value (`—`, `none`) is skipped, and an omitted key means the default — no request fields — no line `Request:`, the state reads nothing — no line `Reads:` (`Input: none` is no longer written; replaces Я-23 in its writing part), `Idle term: —` and `On entry: —` are not written; a key with a real default value (`Idle term: 0`, `Form returns: 0`) may stay written | 1b, 4.1, 4.2, 10 |
| Я-41 | the “value words” of an enumeration are called **values** (Russian «значения», the JSON key `values` instead of `words`): `enum Name = El "value" \| El`; the word «слово» (“word”) stays in the language only in “keywords” | 2, 3.3, 5, 6 |
| Я-42 | operator signs are ASCII only: `>=`, `<=`, `!=`, `->`, `...`, `in` in both languages (the type bound `int>=n`, `yes, <= expr`, `match` branches and lambdas with `->`, `failure(reason in {…})`, `Except: stop_reason in {…}`); the spellings `≥`, `≤`, `≠`, `→`, `…`, `∈` are removed from the grammar and from the word table (replaces Я-9 in its part on signs) | 1a, 1b, 2, 3, 4, 12, 14, word table |
| Я-43 | one record per type: type synonyms are removed — `HashMap[K, V]` is not accepted in parsing, the English record of a map is only `map[K, V]` | 1a, 2 |
| Я-44 | the reference section `## Fragment expansion “Name”` is removed (replaces П-2 in its expansion part and Я-17): neither parsing nor the checks read it, and the cycle “md → JSON → md” is checked by tree equality; what a fragment brings is described by the fragment file (for “Pause” — section 9) | 1, 1b, 4.1, 9, 10, word table, samples |
| Я-45 | the canonical form (1b) is recommended: the normative requirement for a “tree → file” generator is any text that translates back to an equal tree; the rules of 1b are the recommended form of such a text | 1b, 14 |
| Я-46 | a JSON name — one rule and one place: the JSON name of a declared name is written in parentheses at the declaration (`### ПОВТОР — развилка (Retry)`, `число_повторов (retry_count)`, `тип Токены (TokenUsage) { вход (input) ?число }`, `разрешить (allow)`), without parentheses the JSON name is the name itself; a non-Latin name that leaves the machine (a state, a datum, an input field, a type, a field, a variant, an enumeration element, a party signal and its field, a primitive, the name of the gatekeeper setting in `human or agent by setting <name>`) without parentheses is a check error; the glossary is only a source of suggested names, parsing does not read it (replaces Я-5 and the glossary lookup of Я-15, of primitives and of fragment bindings) | 1a, 2, 4.1, 4.3, 5, 6, 7, 9, 10, 13, 14, samples |
| Я-47 | `int` and `int>=n` are compatible both ways also when the input type of a nested machine is compared: a field of type `int` in the caller's `input Type` and a field `int>=0` in the called machine's `## Input` (and the reverse) are one field; the bound is checked by the called machine when it accepts the input (`input_rejected`, `reason=type`) | 1, 2 |
| Я-48 | an optional input field: a field of `## Input` of type `?T` that is absent from the input equals `none`; the refusal `missing` is only for a required field | 1 |
| Я-49 | `reason` (the binding of the failure code in `failure(reason)`) is a readable name, the kind `readable` of the word table (Russian `причина`); the JSON name of a readable name is the `en` word of the word table (for `причина` — `reason`, as in the English “Agent step” sample; the owner's word, 2026-10-20: «reason лучше, чем prichina» — “reason is better than prichina”) | 3.1, 4.3, word table |

`format: 2.13` stands in the headers of the machine, the fragment and the definitions file; the hash of the definitions file sample is recomputed (section 8). There is no section “Reserve”: each of the candidates for the reserve (`Edits`, `Form returns`, `parse`, `pass`, the party profile) is used by the samples — “Meeting”: `Edits` in AuthorFix and AuthorQuestion, `Form returns: 1` in Witness, `parse` and the column `profile` for the parties witness, author, lens; “Agent step”: `Form returns: 0` in AgentTurn; both — `pass` in the rows of the “Pause” fragment (section 9); therefore all of them stay in the core of 2.x.

**Against version 2.11.** The labels of version 2.12 are **Я-23…Я-37**. Sources: the notes to the record of “Meeting” in Portolan (a pilot of the methodology) and the remarks of the consumer project on nested machines and the cycle check.

| № | Correction | Where |
|---|---|---|
| Я-23 | an appeal without request fields (the gate “repeat / halt” without data): `- Input: none` instead of a table; the request carries only the fields given by the executor (and `profile` from “Parties”), the rows read bindings, constants and parameters | 4.1, 4.2, 10 |
| Я-24 | the body of `for each` is one action (up to `;`) or a list of actions in parentheses `for each x in xs: (a; b)`, as with `if` | 5 |
| Я-25 | the values of a literal set are any text, including Cyrillic and a space (`"наблюдалось" \| "не наблюдалось" \| "вывод"`); rule 34(б) allows Latin in them but does not require it | 2, 13 |
| Я-26 | shadowing: a field of a word, a variant or a signal may be named as a datum, a binding may not (renaming `field: name`); the check goes after the substitution of a fragment: the bindings of the fragment rows (`human_word`, `author`, `source`, `id`) do not coincide with the machine data | 3.1, 4.3, 9, 10 |
| Я-27 | the column `reads` of the “Input”, when the source does not say who reads a field: `party` (the field goes into the request); `executor` — only if the source names the field as not going into the request | 4.2 |
| Я-28 | a request field named as a datum allows any “Input” expression (including `call` and `if`); the rows read the datum, the field is only `reads: party` | 4.2 |
| Я-29 | fork conditions: a `pure` primitive and a definition are called as functions `name(arg)`, a reading primitive — only through a `let` binding of “On entry” | 4.6 |
| Я-30 | the input of a nested machine: the type in `input Type` of a party `machine` is a record whose fields are exactly the fields of the `## Input` of the called machine (names and types); the “Agent step” sample: `## Input` is the eight fields of `AgentRequest`, the datum `agent_request` is built by a record constructor | 1, 2, 4.2, sample |
| Я-31 | product journal codes: declared by a product template table of the same form next to the methodology table; the check takes the union of the two tables; a product code does not repeat a methodology code and does not replace a code that the format itself writes (`signal_passed` of `pass`, `input_rejected`, `machine_error`, `machine_data`) | 5, 10 |
| Я-32 | canonical form, a fragment include: the generator writes the include line with all parameters (the parameters of the kind `behavior` — `request_cancel`, `reentry` — are not expressed by substitution into the text), and does not write the states, data and common events of the fragment as its own | 1b |
| Я-33 | a `parse` failure: a response that the parse did not accept is a response not by form: a return to the party by “Form returns”, after exhaustion — `failure` with the code `FormNotFixed`; the result `by role`: the type is chosen by the literal at the check, the `reads` of a role enter the `Input` only for a party with that role | 1, 4.2, 7 |
| Я-34 | open: the input and result types of a nested machine are declared in both machines (the caller and the called), their comparison between files is the product's; a common file of call types is not created | 14 |
| Я-35 | open: the “Pause” fragment has no file in Portolan; the definition in section 9 is a sample, the include is not resolved by the methodology scripts | 9, 14 |
| Я-36 | section 14, the discrepancy ИС2 of “Meeting”: the stale text is corrected — Void clears the findings, the witness answers and the summary of the voided pass (`without_key`), as the primary source and the code do | 14 |
| Я-37 | glossary version 10: the datum `источник_запуска` → `launch_source` (was `source`: it coincided with the field `source` of the words of the “Pause” fragment, shadowing is forbidden, Я-26); two different records `Находка` (of the methodology layer and of the meeting) — a question to the owner with the proposal `НаходкаСовещания` → `MeetingFinding` | glossary |

In version 2.12 `format: 2.12` stood in the headers of the machine, the fragment and the definitions file; the hash of the definitions file sample was recomputed (section 8).

**Against version 2.10.** The label of version 2.11 is **Я-22**; the labels of version 2.10 are Я-19…Я-21.

| № | Correction | Where |
|---|---|---|
| Я-19 | the file name of the tree: a compiled machine (the JSON tree `machine/2`, section 6) is called `<name>.portolan.json`; the pair `agent_step.portolan.md` ↔ `agent_step.portolan.json`; JSON is the executable form of the language itself, not a separate format: a hand-written tree is also Portolan, written in the JSON form; `format: "machine/2"` inside the tree does not change | 1, 6 |
| Я-20 | the file name of a scenario: a scenario (`scenario/0`) is called `<name>.scenario.test.json`; the scenario format does not change | 11 |
| Я-21 | section 1b “Canonical form (for generators)”: the rules by which a “tree → file” generator writes a Portolan file, so that the result is predictable and the cycle “md → JSON → md → JSON” gives an equal tree | 1b |
| Я-22 | there is no transition period for the former file names: `*.table.md`, `*.table.txt` and `*.machine.json` are neither used nor accepted; the extensions are `*.portolan.md` (machine, definitions, fragment), `*.portolan.json` (compiled machine), `*.scenario.test.json` (scenario); the owner's word, 2026-10-19: “there is no transition period” | 1, 6 |

In version 2.11 `format: 2.11` stood in the headers of the machine, the fragment and the definitions file; the hash of the definitions file sample was recomputed (section 8).

**Against version 2.8.** The labels of version 2.9 are **Я-5…Я-18**.

| № | Correction | Where |
|---|---|---|
| Я-5 | state heading: the name in parentheses is the state name in JSON; required if it differs from the name in the heading (Russian `ПОВТОР` → `(Retry)`), and not written if it coincides (`### Retry — fork`); an author who wants another name in JSON writes it in parentheses (`### Pass — appeal (Gate3)`); parsing accepts both spellings | 4.1, 10 |
| Я-6 | a parameter in a primitive registry row is written in the Nova notation through a space: `role text` instead of `role: text` | 7 |
| Я-7 | the Gate3 example: an excerpt of the “Parties” table with the gate words `not counted`, `counted(findings []Finding)` is added to the example; the words of the example rows are declared in the “gate_words” of the appeal's party | 1, 4.3 |
| Я-8 | a field binding with a colon: a field declaration is `findings []Finding`, a binding in a transition row is `field: name` (read “field → name”), a single name if it coincides with the field | 1, 3.1, 4.3 |
| Я-9 | operators: both spellings are accepted in parsing (`≥`/`>=`, `≤`/`<=`, `≠`/`!=`, `→`/`->`, `…`/`...`, `∈`/`in`); the kind `operator` of the word table; `для каждого`/`for each` and `нет`/`none` (the value of `Input: none`) in the word table | 1a, 4.1, 10 |
| Я-10 | string values in JSON: the `machine/2` tree is the same for any file language except string values, which an author writes in his own language | 1a |
| Я-11 | project keys `project.<key>` are named by the product and are not part of the language; a default value that depends on an external key applies only when the key is present | 1 |
| Я-12 | a comment paragraph needs an empty line before and after; a text line pressed against a table, a heading or a list is not a paragraph | 4.1, 10 |
| Я-13 | declarations (`type`, `enum`, `variant`, `define`) are written only inside a code block; outside it a declaration is a comment and a warning | 2, 10 |
| Я-14 | the list of keys of the prose warning: “To” is a column, not a key line, and is removed from the list | 4.1 |
| Я-15 | enumeration value words: partial words are allowed, a word is `[a-z][a-z0-9_]*`; an enumeration without words is the Latin tree name in the tree and in `machine_data`/`all_data` | 2, 5, 6 |
| Я-16 | the history of the language versions: 2.7 (2026-10-19) — the language received the name “Portolan”; 2.8 — bilingualism (Я-1…Я-4) | 0 |
| Я-17 | `## Fragment expansion “Name”`: a reference section anywhere in the file after `## Includes`, parsing skips it entirely; the name coincides with the name of an included fragment (otherwise a warning), there may be several such sections | 1, 9, 10 |
| Я-18 | extension `*.portolan.md`: parsing does not check the extension, only the formatting check script does | 1 |

In version 2.9 `format: 2.9` stood in the headers of the machine, the fragment and the definitions file; the hash of the definitions file sample was recomputed (section 8).

**Against version 2.7.** The labels of version 2.8 are **Я-1…Я-4**.

| № | Correction | Where |
|---|---|---|
| Я-1 | file language: the Portolan language is bilingual (Russian and English); the keywords of a file are written entirely in one language, declared by a header line `- language: ru` or `- language: en` (`ru` by default); a file with an English header without the declaration is a check error; the `machine/2` JSON does not depend on the file language | 1a, 6 |
| Я-2 | word table: the normative source of the keywords of both languages is [portolan-keywords.tsv](portolan-keywords.tsv), rows `kind`, `ru`, `en` over a closed list of word kinds; parsing reads the words by `kind` and by the header language | 1a |
| Я-3 | script [check-portolan-keywords.py](check-portolan-keywords.py): checks the word table and compares the sample machine with it, self-check by mutation | 1a, 10 |
| Я-4 | the party kind “human or agent by setting” is called `gatekeeper` in JSON: in the specification the record `human or agent by setting <name>` (Russian — `human или agent по настройке <имя>`) corresponds to the JSON kind `gatekeeper` | 1 |

In version 2.8 `format: 2.8` stood in the headers of the machine, the fragment and the definitions file; the hash of the definitions file sample was recomputed (section 8).

**Against version 2.6.** The labels of version 2.7 are **П-1…П-9**.

| № | Correction | Where |
|---|---|---|
| П-1 | prose in a machine file: a paragraph outside tables, code blocks and key lines is a comment to the reader, parsing skips it; the formatting check warns about a paragraph line that begins with a word of a known key without the marker `- ` | 4.1, 10 |
| П-2 | `## Includes` — only an include line; the fragment expansion is a reference section `## Fragment expansion “Name”` that parsing skips; a fragment state heading in `## States` is forbidden (“declared twice”) | 1, 9, 10 |
| П-3 | “Agent step” sample: the name `needs_elevated_attention` by the glossary | sample, 3.1 |
| П-4 | fork example: the Latin name `ReplyValidation` (a glossary name) | 4.6 |
| П-5 | a literal set `"a" \| "b"` — wherever a type is expected: the argument of `map[K, V]`, the result and the parameter of a definition | 2 |
| П-6 | tables: the separator row and the escaping of `\|` in a cell | 1 |
| П-7 | JSON: enumerations with value words have the key `words`; the encoding of `all_data` takes the value word | 6 |
| П-8 | scenarios: a word or a signal with one field carries the text value, with several fields — an object | 11 |
| П-9 | project parameters: the executor accepts a “key → value” table (`project.<key>` and the scenario `params`) — the passing mechanism | 1, 11 |

In version 2.7 `format: 2.7` stood in the headers of the machine, the fragment and the definitions file; the hash of the definitions file sample was recomputed (section 8).

**Earlier versions.** The corrections of versions 2, 2.1, 2.2, 2.3, 2.4, 2.5 and 2.6 (label С-1 of version 2.6, Т-1, Т-2 of version 2.5, И-1…И-4 of version 2.4, Н-1…Н-12 of version 2.3 and the earlier ones: А1–А8, АМ1–АМ10, E1–E11, T1–T11, С11, С30, ША1–ША11, ШМ1–ШМ3, ШВ1–ШВ12, СГ1–СГ15, ИС6 in the text) are in the history of the file (`git log`, the commits “Table format 2.6…”, “Table format 2.5…”, “Table format 2.4…”, “Table format 2.3…”, “Table format 2.2…” and the earlier ones); the tables are not repeated.

Removed from v1 and not replaced by a namesake: `add(field, expr)` — in its place `field += [expr]` (a list) and `+`; `by_key(field, key) = expr` — in its place `field[key] = expr`; `send(...)`, `cancel(...)` — sending and cancelling requests — are contract mechanics (rules 14, 15, 18, 21), the pilots did not use them; `call(machine, input)` — a nested machine is called by a request to a party of kind `machine`; the party kind `lens` — a set of parties is a property of an appeal, not a party kind.

## 1. Machine file

The keywords of this section (section headings, column names, key lines, party kinds) are quoted here in their English form; in the Russian form of a file they are the Russian words, and in the English form they are written by the [word table](portolan-keywords.tsv); the rules are in section 1a.

**Extension.** A machine file in Portolan is called `*.portolan.md` (the machine name is Latin, as in `- machine:`; for example `agent_step.portolan.md`); the former names `*.table.md` and `*.table.txt` are not used, there is no transition period (the owner's word, 2026-10-19: “there is no transition period”; version 2.11, Я-22). Parsing does not check the extension: the extension is checked only by the formatting check script (Я-18). A definitions file and a fragment file are also `*.portolan.md` with a header of their own kind. **A compiled tree** (JSON `machine/2`, section 6) is called `<name>.portolan.json` (Я-19): `agent_step.portolan.md` ↔ `agent_step.portolan.json`; it is not a separate format but the executable form of the language itself — a hand-written tree is also Portolan, written in the JSON form; `format: "machine/2"` inside the tree does not change. The former `*.machine.json` is not used, there is no transition period (Я-22). The machine version (`- machine_version:`) is set by the author of the file; a string of the form `portolan-<format version>` is recommended (for example `portolan-2.13`) — it answers the question “in which language and which version is the machine written”; the caller compares it only for equality with the registry entry (call protocol, section B, item 6).

Markdown, sections in order:

| Section | Contents |
|---|---|
| header | `# Machine: <Name>`; list items `- machine: <latin_name>`, `- machine_version: <string>`, `- format: 2.13`, optionally `- language: ru` or `- language: en` (1a; the marker `- ` is optional in parsing; in writing it is required: markdown glues consecutive lines together) |
| `## Types` | records, variants, enumerations (section 2) |
| `## Constants` | `name`, `type`, `value` |
| `## Parameters` | `name`, `type`, `default`, `project_override` (`project.<key>`); the default value is required: if the source gives a stub, it is written with the note “source stub”; a project key that the source does not name is `—` (АМ10); passing values from outside — below (П-9) |
| `## Input` | the call input fields: `name`, `type`, note; lines `Invariant: <bool expression over the fields>`; the input value is the name `input` |
| `## Data` | `name`, `type`, `initial`, `non_decreasing`, `writes` (section 2) |
| `## Parties` | see below |
| `## Definitions` | pure functions (section 8) |
| `## Includes` | **only** include lines: fragments (section 9) and definitions files `definitions: <name> version <N> hash <hex12>` (section 8, СГ4); without prose and lists (П-2) |
| `## States` | the first line `Initial state: NAME`, then the states (section 4) (А8) |
| `## Ends` | the table “end → response” (4.7) |
| `## Primitives` | host primitives that the machine calls (section 7) |

**Tables** (П-6). The separator row under a table heading (`|---|---|`, `|:---|---:|`) is a row of the signs `-`, `:`, spaces and `|`; parsing skips it. The sign `|` inside a cell is written `\|` (a literal set `"a" \| "b"`, a lambda with `|`); parsing removes the escaping. In the examples of the format the separator is omitted.

**`## Parameters`: passing values from outside** (П-9). The executor accepts parameter overrides as a “key → value” table: the key is `project.<key>` from the column “project override”; the value is checked against the parameter type (a full map — by the rules of section 2), a key that is not in the column is a load refusal. This is the passing mechanism; where the executor takes the table from (project settings, the scenario `params`, section 11) the format does not define. The keys `project.<key>` are named by the product, they are not part of the language; the column “project override” of the sample stays `—` because the source names no keys. A default value that depends on an external key applies only when the key is present in the override table; otherwise the default value works (Я-11).

**`## Input`.** The input type is a record made of the fields of this section (rule 35, item 1); `initial: input.<field>` takes the value from the input. An optional field (of type `?T`) that is absent from the input equals `none` (Я-48). The invariant is checked by the executor when it accepts a request; a violation is a call refusal (И-1): the executor writes the journal event `input_rejected` and finishes the call with the refusal `NoResult` with the text `input rejected: <reason>`; the machine state does not change. The same refusal — when parsing the input. The event parameters (journal, subsection “Events of the table format”): `reason` — a closed list `json` (the input is not JSON), `missing` (a required input field is absent; an optional one gives no refusal, Я-48), `type` (a field of another type, outside the type bound, outside a literal set, or not an `id` of UUID format, for example `int>=0` at −1), `invariant` (an input invariant is violated); `field` — the input field name (for `missing` and `type`); `index` — the invariant number from zero (for `invariant`). `field` and `index` are optional: with `json` they are absent, and the template skips them. Examples: `input_rejected(reason=json)`, `input_rejected(reason=missing; field=label)`, `input_rejected(reason=type; field=start)`, `input_rejected(reason=invariant; index=0)`. The call request identifier (`call_request_id`) does not lie in the input: the executor gives it (section 9).

**The input of a called machine and `input Type` of the caller** (Я-30). A party `machine <name>(input Type, …)` names a record type whose fields are exactly the fields of the `## Input` of the called machine: the same names and types, the order is not significant; the request fields are the fields of this type, except `profile` (4.2). Therefore an input that the callers pass by fields (`kind`, `session`, `context`, …) is declared by the called machine with the same fields, not with one record field; the record as a whole, if it is needed in the data, is built by `initial` with a record constructor (`AgentRequest { kind: input.kind, … }`, the “Agent step” sample). The field types are compared by the compatibility of section 2: `int` and `int>=n` are compatible both ways (Я-47) — a field `int` in the caller and `int>=0` in the called machine (or the reverse) are one field, the bound is checked by the called machine when it accepts the input (`input_rejected`, `reason=type`). The comparison of the types of the two files is the product's (section 14).

**`## Parties`.** The table `| name | id | kind | profile | signals | counter |`.

| Kind | What it is |
|---|---|
| `agent(result Type)` | an agent; `result` is the party's result type (ША2) |
| `human(result GateOutcome)` | a human at a gate |
| `enhanced(result GateOutcome)` | an enhanced gatekeeper |
| `human or agent by setting <name>(result GateOutcome)` | a gatekeeper: a human or an agent, by the project setting (rule 19); `<name>` is the key of the project setting, it leaves the machine: a non-Latin name carries a JSON name in parentheses (`исполнитель_повышенного_внимания (elevated_attention_executor)`, 1a, Я-46); the Russian record is `human или agent по настройке <имя>(итог ИсходВорот)`; in the JSON tree this kind is called `gatekeeper` (Я-4) |
| `machine <name>(input Type, result Type)[; parse: <primitive>[("<role>")] -> Type]` | a nested machine (rule 35): a name from the caller's registry (rule 35, [call protocol](state-machine-call-protocol.md), section J, item 6), the request input type, the response result type; an optional result parse (see below) |

- `id` is the Latin word of the party (А6): a value “request party” of the glossary ([state-machine-glossary.md](state-machine-glossary.md), section 2.14: `agent`, `gatekeeper`, `enhanced`, `witness`, `author`, `session_launch`, `review`, `meeting`, `agent_step`); it goes into the envelope of the request and the response and into the request identifier (`<id>-<number>`), therefore it gets into the journal. For a party with a set (4.2) it is `—`: the identifier is the element of the set. The party identifiers of a machine are distinct.
- **`result`** (ША2) is the party's result type: for `agent` and `machine` — a type from `## Types`; for `human`, `enhanced` and the gatekeeper — the built-in `GateOutcome`, whose variants are the signals of the column “signals” (a signal without data is a variant without fields, `signal(field type)` is a variant with fields; rule 19), the event `signal(…)` of the party is a variant of `GateOutcome`. `response: Variant` is resolved by the party's `result` (for `machine` with `parse` — by the parse result); the qualified form `response: TurnResult.Finished(…)` is allowed, the type in it being the party's result type; an unqualified variant name is searched only in this type.
- `profile` is an expression or `—`; **the only source of the profile**: the request field `profile` is taken by the executor from here, a `profile` line in the “Request” is a check error (T3). The column reads the machine data, constants, parameters, `input` and (for a set) `party`; `call` reading is allowed (section 7), its hidden reads are machine data; the column does not read the names of a state's `Request`: the table of “Parties” is one per machine, rule 11 does not apply to it (ША4). If the profile lies inside the request (for the party `agent` — `agent_request.profile`), the party has no separate field and `—` is written.
- `counter` (СГ1, rule 15) is **required for every party**: the datum where the party's attempt counter lies — a datum name (`agent_attempt`) or, for a party with a set, the path of a field of the element record (`lenses[*].attempt`). The datum is `int>=0`, initial `0`, `non_decreasing: yes`, `writes: mechanics`; for a field path the initial `0` is set by the datum row with the element record (`attempt: 0` in `lenses`, section 2), and for a path in the “Data” table the `initial` is `—` (Н-5); the attempt number of a request equals the counter value after the increase (mechanics, before sending; at a gate of a human — before the gate is shown, rule 19), the request identifier is `<id>-<number>` (for a set — `<set element>-<number>`). The check of section 10 verifies the datum.
- `signals` (Я-38) — for the kinds `human`, `enhanced`, the gatekeeper: the **party signals** — what the party says to the machine at a gate: a signal or `signal(field type, …)` — a signal with data; the signals are written as in the machine tables (including those of several words: `halt meeting`); the JSON name of a signal and of its fields is in parentheses at the declaration (1a, Я-46), needed only for a non-Latin name (`засчитан (counted)(находки (findings) []Находка)`); a signal field is declared through a space, `counted(findings []Finding)`, and in a transition row it is bound as `signal(counted(findings: new_findings))` (3.1, Я-8). The declaration itself names which party may give the signal: these are **all signals of the party**; the signals of a state are the signals of its rows (4.3). A party signal is an event of the party from its declared set (for `human`, `enhanced` and the gatekeeper — a variant of `GateOutcome`); it belongs to the open request of that party, and when a human answers — to its open gate and carries its identifier, as rules 15–19 of the specification say (the attempt counter, the acceptance of the response, the words of a human); the gate identifier `<identifier>-<number>` names the party, and the signal is checked against the signals of that party: one it did not declare or one that came from another party is discarded (“a word of a foreign party”, rules 17, 19). It differs from a machine signal (common events, section 9) by being declared at the party and by who may give it. For the other kinds — `—`.
- **`parse`** (E1, СГ13) — only for the kind `machine`: a reading primitive (section 7) with a parameter of the type `result`, an optional second parameter — a text literal of the role (`parse_agent_reply("author")`: one host primitive serves several roles) and a result of the given type; for a primitive with the result `by role {…}` (section 7) the given type must coincide with the registry type for that literal (Н-12). The executor calls it when it accepts the response (rule 14), after the “Edits” check (4.2) and before “On accept”, and the **response value** for `response(name)`, `response: Variant(…)` and “On accept” becomes the parse result; without `parse` it is the `result` itself. The event `response: Variant` requires that the response value be a variant. The primitive's hidden reads (`reads`) enter the reads of the state (`Request`, rule 11); the parse is called once per response, the result is stored with the accepted event. A parse by role is the same registry primitive with another role literal (the result `by role` — section 7).
- **A parse failure** (Я-33). A parse either gives a value of the given type or refuses: a response not by form (the artifact is unreadable, there are no excerpts, the comparison did not converge); the remarks of the refusal are a service record that the return of the party reads. A parse refusal is a response not by form (rule 18): no event arises, “On accept” is not executed, the response is not written in `accepted_requests`; while the returns are fewer than “Form returns” (4.2), the executor returns the response to the party (for `machine` — with a new request of the same party with a remark); after exhaustion, and with `Form returns: 0` at once, the request is closed by the event `failure` with the code `FailCode.FormNotFixed` (a code outside the state's list the executor brings to `NoResult`, 4.3). The return and its journal record are executor mechanics (product journal codes — section 5). A value of another type than the one named after `->` (for a result `by role` — not of the role's type) is a host defect, that is a program defect (3.3), not a response not by form.
- Under the table — a list item `- Request limit: <int>=1 expression>` (one per machine, rule 21; if not written — 1).

Example (pilots; `human or agent by setting` and the signals — “Agent step”, `machine`, the parse and the signals with data — “Meeting”). Changed: the party signals — the column “signals” (Я-38); the signals of the enhanced gatekeeper — by the “Pause” fragment (section 9); for “Meeting” the kind `lens` is replaced by `machine`, identifiers and the parse by role are added; for both machines `result` and the column `counter` are added; the agent's profile is inside `agent_request`, therefore `—`.

```
| name | id | kind | profile | signals | counter |
| agent | agent | agent(result TurnResult) | — | — | agent_attempt |
| gatekeeper | gatekeeper | human or agent by setting elevated_attention_executor(result GateOutcome) | — | allow, deny | gatekeeper_attempt |
| enhanced | enhanced | enhanced(result GateOutcome) | — | continue(human_word text, author text, source text), halt | enhanced_attempt |

- Request limit: 1

| witness | witness | machine agent_step(input AgentRequest, result AgentReply); parse: parse_agent_reply("witness") -> []WitnessAnswer | call(party_profile, "witness") | — | witness_attempt |
| author | author | machine agent_step(input AgentRequest, result AgentReply); parse: parse_agent_reply("author") -> EditResult | call(party_profile, "author") | — | author_attempt |
| lens | — | machine agent_step(input AgentRequest, result AgentReply); parse: parse_agent_reply("lens") -> LensResult | call(party_profile, party) | — | lenses[*].attempt |
| gatekeeper | gatekeeper | human or agent by setting elevated_attention_executor(result GateOutcome) | — | repeat, not counted, counted(findings []Finding), another pass(decision text), answered(answer text) | gatekeeper_attempt |
| enhanced | enhanced | enhanced(result GateOutcome) | — | continue(human_word text, author text, source text), halt meeting | enhanced_attempt |

- Request limit: REQUEST_LIMIT
```

## 1a. File language and keywords

The Portolan language is bilingual (Я-1): a file `*.portolan.md` is written either in Russian or in English. The Russian form is the base one; all examples of the Russian specification are written in it. The English form is the same constructs with English keywords; the examples of this English version are written in it. An English sample machine is a separate work and does not affect this section.

**Keywords** are the words that the specification defines: the headings of sections and of the header, key lines, table column headings, state kinds, the words of events and of “To”, the words of expressions, actions, catalog functions, the literals `true`/`false`/`none`, the kinds of word parties, the values of `writes` and `reads`. They are written **entirely in one language — the language of the file**. Mixing is not allowed: a file with Russian headings and the English action `journal(…)` is an error.

**There are two languages, declared by a header line:** `- language: ru` or `- language: en`. The line is optional, `ru` by default. The parsing rules:

- the check does not guess and does not switch silently: the language is taken only from the `language` line or by default;
- a file with an English header (`# Machine:`, `# Definitions:`, `# Fragment:`) without `- language: en` is a check error (“the header language is English, and language is not declared”); the same for a Russian header with `- language: en`;
- a keyword not of the file language is a check error with the line number of the first foreign word.

**Free, in any language and mixed** (these are not keywords): the names that an author invents — data, states, definitions, types, fields, party signals, fragment parameters and their values; prose comments outside tables (4.1); string values inside data and journal event codes (in Latin by convention, rule 34(б)); the names of host primitives from the registry (as written there); party identifiers (`agent`, `human`, etc.). The header keys (`machine`, `machine_version`, `format`, `definitions_version`, `fragment`, `language`) and the primitive classes (`pure`, `reading`, `writing`, `irreversible`) are Latin in both languages.

**JSON.** The `machine/2` tree (section 6) does not depend on the file language: the keywords of both languages correspond to the same keys and values, names enter the tree by their JSON names (below), string values (refusal texts, messages, text literals) — as the author wrote them (Я-10). Therefore files of the two languages with the same JSON names and string values give one tree up to the internal names (below). The sample comparison ([check-portolan-samples.py](check-portolan-samples.py)) does not compare string values.

**JSON name** (Я-46) — one rule and one place. A JSON name is the name in the `machine/2` tree, in the journal, in `all_data` and on the wire. For a name that an author declares it is written **in parentheses right after the name at the place of declaration**: a state heading `### ПОВТОР — развилка (Retry)`; the first column of the tables `## Input`, `## Data`, `## Primitives` (`число_повторов (retry_count)`); the declarations of the code block `## Types` — a type, an enumeration element, a variant, a field (`тип Токены (TokenUsage) { вход (input) ?число }`, `НетРезультата (NoResult) "no_result"`); a party signal and its field in the column “signals” (`продолжить (continue)(автор (author) текст)`); the name of the gatekeeper setting in the party kind (`human или agent по настройке исполнитель_повышенного_внимания (elevated_attention_executor)(итог ИсходВорот)`). Without parentheses the JSON name is the name itself; parentheses at a Latin name give another JSON name (`### Pass — appeal (Gate3)`). A JSON name is Latin: `[A-Za-z_][A-Za-z0-9_]*`. **Parentheses are required** for a non-Latin name that leaves the machine: a state (the journal field `state`, the parameter `fork`, `text(State)`), a datum (`all_data`, `machine_data`), an input field, a type, a field of a record and of a variant, a variant, an enumeration element (the wire, `all_data`), a party signal and its field (the wire, a scenario), a primitive (the JSON name is the host registry name), the name of the gatekeeper setting (a project setting key); without them it is a check error (section 10). No parentheses are written for: a field path `name[*].field` (it is made of declared names); keywords and readable names, including the contract data and the data of the “Pause” fragment (`stop_reason`, `to_send`, `open_requests`, `previous`, `call_request_id`) and the binding `reason`, — their JSON name is the `en` word of the word table (Я-49); **internal names** that do not leave the machine — constants, parameters (their external name is `project.<key>`), definitions and their parameters, party names (their external name is `id`), event bindings and `let`, lambda parameters, the variable of `for each` — enter the tree as written. The names of a fragment (parameters, signals and their fields) are declared by the fragment file by the same rule (section 9). The glossary of English names ([state-machine-glossary.md](state-machine-glossary.md)) is only a source of suggested JSON names: parsing and the checks do not read it. There are no other ways to set a JSON name.

**The word table is the single normative source:** [portolan-keywords.tsv](portolan-keywords.tsv). Rows `kind`, `ru`, `en` (tab), the first row is the heading; the word kind (`kind`) is from a closed list:

| `kind` | Words |
|---|---|
| `header` | header words: `Machine`, `Definitions`, `Fragment` and the header keys |
| `section` | headings of `##` sections (including `Requires`, `Common events` of a fragment file) |
| `column` | table column headings |
| `kind_state` | state kinds: appeal, operation, fork, end |
| `key` | key lines (`Party`, `Request`, `Reads`, `Edits`, `check`, `set`, `Except`, etc.), the words of the include line (`definitions`, `version`, `hash`), the prefix `project` |
| `kind_party` | party kinds and the words of their record (`parse`, `result`, `input`, `human or agent by setting`) |
| `event` | event words (`response`, `failure`, `immediate`, `signal`), `reason`, `else` |
| `destination` | the words of “To”: `previous`, `preparation_return`, `same`, the suffix `rerun` |
| `decl` | declaration words: `type`, `enum`, `variant`, `define` |
| `type` | type words, built-in types, fragment parameter kinds |
| `expr` | expression words, literals, the constructors `Response`, `Refusal` |
| `operator` | ASCII operators and signs: one spelling in both languages, `ru` and `en` coincide (Я-42) |
| `action` | action words and their arguments (including `for each`) |
| `readable` | executor readable names, contract data and the binding `reason` (Я-49) |
| `enum_value` | the values of `writes` and `reads`, `yes` of the column “non_decreasing”, the values of `behavior` parameters, the values of `Signal`, primitive classes |
| `catalog` | catalog functions (section 12) |

A word that fits two kinds is written as two rows (`else` — in `event`, `expr`, `action`; `end` — in `kind_state` and `catalog`). Within a kind the `ru` words do not repeat and the `en` words do not repeat: a word that is the same in the English form for two Russian words belongs to different kinds. Parsing reads a word by the `kind` of the position and the file language. The check of the table and of the sample is [check-portolan-keywords.py](check-portolan-keywords.py) (section 10).

**Operators and signs — ASCII only** (Я-42). The signs are written the same in both languages (the kind `operator` of the word table: `ru` and `en` coincide); there are no other spellings:

| Sign | Where |
|---|---|
| `>=` | comparison; the type bound `int>=n` (Russian `число>=n`) |
| `<=` | comparison; `yes, <= expr` of the column “non_decreasing” |
| `!=` | comparison |
| `->` | a `match` branch, a lambda, the result type `-> Type` |
| `...` | the spread `{ ...expr, field: expr }` |
| `in` | `failure(reason in {…})`, `stop_reason in {…}` (“when” of ends, `Except`) |
| `??`, `_` | a default value; an unneeded lambda parameter |

The ellipsis `…` in the grammar description (3.1) and in the text of the specification is a meta-sign of omission, not a sign of the language.

**English record of types and signs.** `число`→`int`, `число>=n`→`int>=n`, `дробное`→`float`, `текст`→`text`, `да/нет`→`bool`, `словарь[K, V]`→`map[K, V]` (in JSON a map is `{K: V}`; types have no synonyms, `HashMap[K, V]` is not accepted, Я-43), `полный словарь[K, V]`→`full map[K, V]`, `ид`→`id`; `?T`, `[]T`, the tuple `(T1, T2)`, `—` and `№` are the same in both languages (operators — above); the value “nothing” is `none` (the literal `пусто`), the type “nothing” in JSON is `nothing`. For example, `выбор … { альт | альт если выр -> выр; иначе -> выр }` is `match … { alt | alt if expr -> expr; else -> expr }`, `для каждого x в xs: …` is `for each x in xs: …`, `ответ: Вариант(…)` is `response: Variant(…)`, `сбой(причина in {…})` is `failure(reason in {…})`.

## 1b. Canonical form (recommended for generators)

A “tree → file” generator (the reverse conversion of the JSON `machine/2` to Portolan, Я-21) is bound by one thing (Я-45): the text it writes translates back to a tree equal to the original — the cycle “md → JSON → md → JSON” gives an equal tree. The rules of this section are the **recommended** canonical form of such a text: with it the result is predictable, and two generators write one text; a generator that writes otherwise does not break the requirement if the tree is equal. The reverse conversion loses comment paragraphs, formatting (alignment, line breaks inside declarations) and the names that are not in the tree (for a name with a JSON name in parentheses the tree holds only the JSON name, 1a); the meaning is not lost. A file written by a person in another way (the order of key lines, prose, line breaks) stays valid — parsing accepts it.

- **(а) Header.** `# Machine: <Name>` (the Russian form — `# Машина: <Имя>`), where `<Name>` is the Latin name of the machine (`machine` of the tree); an empty line; a list of four items in this order: `- machine: <name>`, `- machine_version: <string>`, `- format: <format version>`, `- language: <ru|en>`; the line `language` is always written, the default is not used. `machine_version` is `version` of the tree; `format` is the format version in which the source was written (`table_format` of the tree; if it is absent — the format version of the generator).
- **(б) Sections.** The eleven sections of section 1 in order — `## Types`, `## Constants`, `## Parameters`, `## Input`, `## Data`, `## Parties`, `## Definitions`, `## Includes`, `## States`, `## Ends`, `## Primitives` — are always written, once each; an empty section is the single line `—` under the heading; one empty line between sections. The key lines of sections are list items: `- Invariant: <expression>` (one per invariant) — after the `## Input` table; `- Request limit: <expression>` (if `request_limit` is set in the tree) — after the `## Parties` table; `- Result: <Type>` — before the `## Ends` table.
- **(в) States.** The first line of `## States` is `Initial state: NAME` (the Russian form — `Начальное состояние: ИМЯ`), not a list item, then an empty line; states are in the order of `states` of the tree. The key lines of a state are list items, one after another, in this order: `Party`, `Idle term`, `Edits`, `Form returns`, `Request`, `On accept`, `Reads`, `On entry`, `Except` (the Russian ones — `Сторона`, `Срок тишины`, `Правит`, `Возвратов формы`, `Запрос`, `При приёме`, `Читает`, `При входе`, `Кроме`); a key the state does not have or whose value is empty (`—`, `none`) is not written (Я-40); a key with a real default value (`Idle term: 0`, `Form returns: 0`) may be written by the generator. An item with a table (`Request:` of an appeal, `On accept:`) stands before its table, and an empty line stands between a table and the next block; the body of “On entry” of several actions is a nested list, one action per item (4.1).
- **(г) Tables.** The header and the rows have one space on each side of `|`, with no alignment of column widths; the separator row is `|---|` by the number of columns; an empty cell is `—`; `|` inside a cell is `\|`. The actions in a cell are in the order of the tree, joined by `; `. The words of the column headings come from the word table of the file language.
- **(д) Declarations.** Types and definitions are written in code blocks under `## Types` and `## Definitions` (Я-13), in the order of the tree, **one declaration per line**: `enum Name = El "value" | El`, `type Name { field type, field type }`, `define name(parameter type) -> Type =` and the body of the definition on the next line with an indent of two spaces (as one line). Only `variant` is written on several lines: `variant Name {`, then one variant per line with an indent of two spaces (`Var { field type, field type }`, a variant without fields — by name), then `}`. An empty line stands between declarations of different kinds, around `variant` and between definitions; enumerations in a row and types in a row are not separated by an empty line.
- **(е) Operators.** ASCII only in both languages (Я-42): `->` in `match` branches, in lambdas and before a result type; `>=`, `<=`, `!=`, `==` in comparisons; `...` in a spread; `in` in `failure(reason in {…})`, “when” and `Except`; `int>=n` (`число>=n`); `yes, <= expr` (`да, <= выр`). The signs are in the word table, the kind `operator` (1a).
- **(ж) Names.** The generator writes every name as it lies in the tree: for a name with a JSON name only the JSON name lies in the tree; internal names lie as written (Я-46); so the generator writes no JSON-name parentheses (1a) — `### Retry — fork`, `| retry_count | int>=0 | …`; the same state name stands in `Initial state` and in the “To” column. The kinds are the words `appeal`, `operation`, `fork`, `end` (the Russian ones — `обращение`, `операция`, `развилка`, `конец`).
- **(з) File language.** The generator chooses the language by a parameter (`ru` or `en`); all keywords come from [portolan-keywords.tsv](portolan-keywords.tsv) by this language (1a), with no mixing; the names invented by an author (data, types, fields, definitions) and the enumeration values are carried over from the tree as they are.
- **(и) String values and journal codes** are carried over as they are, with no translation or normalization; a string literal is in double quotes, `"` and `\` inside are escaped with `\`.
- **(к) Prose.** Comments and prose are not generated. It is allowed to write `title` of the tree, if there is one, as one paragraph under the header (after the header list); nothing more.
- **(л) The file** ends with exactly one line feed (no empty lines at the end), encoding UTF-8 without BOM, line endings LF.
- **(м) Includes.** A fragment (Я-32): the tree carries it already substituted (section 9) and carries the include node with parameters (section 6); the generator writes the include line of the fragment with all parameters, in one line, the parameters in the order of the table `## Parameters` of the fragment (`Pause(halt_signal: halt, halt_code: "pause_halt", nested: [], request_cancel: stop_transport_turn, reentry: nothing, write_right: "…")`), and does not write the states, data and common events of the fragment as its own: a repetition would be “declared twice” (П-2), and without the include line the parameters of the kind `behavior` (`request_cancel`, `reentry`) would be lost — they are not expressed by substitution into the text, their effect lies on `cancel_open` and `To: previous`. A definitions file: the tree carries both the reference (`includes`) and a copy of its types, constants and definitions (section 6); the generator writes either the include line (and then does not write the copies) or the copies (and then there is no include line) — otherwise the names are declared twice (section 8); the choice is a generator parameter, by default the include line.

The samples [state-machine-agent-step.portolan.md](state-machine-agent-step.portolan.md) and [state-machine-agent-step.en.portolan.md](state-machine-agent-step.en.portolan.md) are written by a person and are not brought to the recommended form: they carry prose (к), the fragment include line with line breaks (м), line breaks inside declarations and multi-line bodies of definitions (д); the Russian sample, besides, has Russian names with JSON names in parentheses (ж) and has no `language` line (а). The rest (the header, the order of sections and key lines, tables, operators) corresponds in the samples to the canonical form. The cycle “md → JSON → md → JSON” is checked by the consumer product; the methodology scripts do not check the canonical form (section 14).

## 2. Types and data

| Type | Record | Notes |
|---|---|---|
| integer | `int`; `int>=n` (n is an integer literal: `int>=0`, `int>=1`) | going outside the bound, like overflow, is a machine error; `int>=n` and `int` are compatible both ways (the bound at assignment is checked by the executor), also when the input type of a nested machine is compared (section 1, Я-47) (АМ4) |
| float | `float` | not mixed with int: `float(x)`, `int(x)` are explicit; the format does not express bounds for `float` (the source “non-negative” remains in the description, the executor does not check the bound) (ША9) |
| text | `text` | comparison letter by letter |
| literal set | `"first" \| "retry" \| "continue"` — two or more text literals; optional — `?("first" \| "retry")` | a closed set of text values (Т-1); allowed **wherever a type is expected** (П-5): the cell “type” of the tables “Input”, “Parameters”, “Data”, a type argument (`map[text, "allow" \| "deny" \| "ask"]`, `full map[ActionKind, "allow" \| "deny"]`), the result and the parameter of a definition (`define decision(…) -> "allow" \| "deny" =`); the parentheses are required under `?` and `[]`, in other positions they are optional and allowed when ambiguous; in a table cell `\|` (section 1); assigning a value outside the set is a table check error; a `match` over a set is exhausted by the rules of enumerations (all values are named or there is `else`); `text(x)` gives the literal itself; in the JSON schema — a list of strings |
| identifier | `id` | a built-in type: text of UUID format (Т-2); details below |
| yes/no | `bool` | |
| optional | `?T` | `?` and `[]` apply to the whole type on the right; a literal set under them is written in parentheses: `?("allow" \| "deny")`, `[]("a" \| "b")`; the record `?"a" \| "b"` is not defined |
| list, map | `[]T`, `map[K, V]` | key: text, int, enumeration, tuple or a record of such (structural equality) |
| full map | `full map[K, V]` | `K` is an enumeration: the keys are all its values, indexing gives `V`, not `?V`; an incomplete literal or a project override is a check error |
| tuple | `(T1, T2, …)` — from two fields | an anonymous record with positional fields; the value `(a, b)`, the field `t.0`, `t.1` (from zero, as in Nova) |
| record | `type Name { field T, … }` | |
| variant | `variant Name { Var { field T, … } Var }` | a variant without fields is `Var` without braces |
| enumeration | `enum Name = El "value" \| El "value" …` | an element is a name (`El`) and an optional **value** — a text in quotes (Я-41); `text(Name.El)` gives the value; `text` of an enumeration without values is forbidden; values may be given not for all elements (Я-15); an element without a value enters a data record (section 5) by its JSON name (1a, Я-46, ША1) |
| state | `State` | a built-in enumeration of the machine's state names (a literal is a state name); the text is the JSON name of the state (1a) |
| signal | `Signal` | a built-in enumeration `stop`, `continue`, `halt`, `cancel` |
| journal event | `JournalEvent` | a record `{ code text, params []Param }`, where `Param` is a tuple `(text, text)`: name, value |
| gate outcome | `GateOutcome` | a built-in variant of the result of the parties `human`, `enhanced`, the gatekeeper: the variants are the signals of the party's column “signals” (section 1, Я-38) |

**Literal set or enumeration** (Т-1). A literal set — when the set is small, local to one machine, the values are not needed by the journal as enumeration values and do not cross the machine boundary (`turn`, `stop_reason` of “Agent step” — so in the source). An enumeration with values (`enum Name = …`) — when the set is common to several machines or fragments, crosses the call boundary (input, response, failure code — `FailCode`), the values are needed for the journal and `text(x)`, or the elements have fields (then `variant`). **The values of a set** (Я-25) are any text, including Cyrillic and a space (`"наблюдалось" | "не наблюдалось" | "вывод"` — the words of a role artifact): rule 34(б) allows Latin in the text literals of closed sets but does not require it; the values are written as in the source (the words of the automaton code — in Latin, the words of an artifact — as in the artifact). The restriction `[a-z][a-z0-9_]*` applies only to the values of an enumeration (Я-15, Я-41).

**The type `id`** (Т-2). Text of UUID format: 8-4-4-4-12 hexadecimal signs through hyphens, lowercase (`0192f3a0-7c1e-7b2a-9d4e-5a6b7c8d9e0f`). The check is at data load and at input parsing: a violation of the input is the refusal `input_rejected`, `reason=type`, `field` is the field name (section 1); a violation of data is a load error by the format rules. The format does not fix the UUID version; for the identifiers of sessions, host requests and runs version 7 is preferable (by time, sortable). `id` is assigned to a datum and a parameter of type `text` (the type is forgotten, as with a literal set); the reverse — only a literal of UUID format. `==` is structural, `text(x)` gives the text itself. The value is issued by the host primitive `new_id` (section 7). **Not changed:** the request identifier `<party>-<attempt>` (rule 15, [call protocol](state-machine-call-protocol.md)) and the trace envelope (`trace`, `step`, rule 31) remain as in the specification — `id` serves the data of machines (identifiers of sessions, runs, etc.), not the envelope.

**Enumeration values** (Я-15, Я-41). Values may be given not for all elements; a value is `[a-z][a-z0-9_]*`. An element without a value is shown in `text(x)` and in `all_data` by its JSON name (1a, Я-46): in the file the element name is in the file language, in the tree, in `machine_data` and `all_data` it is the JSON name; the `machine_data` comparison goes by the JSON name (for `FailCode` — by the value, as in the engine).

**The declaration notation is as in Nova** (decision of the owner, 2026-10-19): a declaration is `name type` through a space (a field of a record and of a variant, a parameter of a definition and of a catalog function, a parameter of a party signature and a signal field, a registry parameter); the result is after `->`. A colon stands only in a record literal `Type { field: expr }`, in a named argument `name: expr`, in a map literal pair `{k: v}` and in a pattern field binding `field: name` (4.3). Tables with a separate column “type” (`## Input`, `## Parameters`, `## Data`) do not change. **Declarations only in a code block** (Я-13): `type`, `enum`, `variant`, `define` are written inside a code block (``` fences) under `## Types` and `## Definitions`; a declaration line outside a code block is a comment (a paragraph) and a check warning: markdown would distort `|`, `{}`, `->`.

**Type records and Nova** (checked against the language specification and the automata code): as in Nova — `[]T`, the tuple `(T1, T2)` (in a type position), `map[K, V]` (in Nova `HashMap[K, V]`; the literal `{k: v}` as in Nova), the record `type Name { field T }`; the translation of names — `int`, `text`, `float`, `bool` (in Nova `int`, `str`, `f64`, `bool`). **Extensions of the format** that Nova does not have: `?T` (in Nova `Option[T]`), `int>=n`, the literal set `"a" | "b"`, `id`, `full map[K, V]`; the other differences are in the list of section 14.

Example (the “Agent step” pilot; changed: the values of `FailCode` are from `fail_code_word` of the engine, in the pilot they were in the text).

```
enum FailCode = NoResult "no_result" | ModelRefused "model_refused" | ConnectionLost "connection_lost"
              | FormNotFixed "form_not_fixed" | Timeout "timeout" | StoppedByHuman "stopped_by_human"
              | CeilingReached "ceiling_reached" | Cancelled "cancelled" | MaxTokens "max_tokens"
              | MaxTurnRequests "max_turn_requests"

variant TurnResult {
  Finished { text ?text, artifact ?text, usage TransportUsage }
  Truncated { usage TransportUsage }
  TurnRequestLimit { usage TransportUsage }
  ModelRefusal { usage TransportUsage }
  Stopped { usage TransportUsage }
  TransientError
  PermanentError
  NeedsPermission { permission_request PermissionRequest }
}
```

**Data.** The table `| name | type | initial | non_decreasing | writes |`.

- `name` is a datum or a **field path** inside a map: `name[*].field` (`*` is any key; for a nested one `name[*].field.field`). A row with a path carries only `non_decreasing` and `writes` and acts on every value of the map; `type` is the field type, `initial` is `—` (the value is set by the row of the datum itself) (С11).
- `initial` is an expression or `input.<field>`.
- `non_decreasing` is `—`, `yes` or `yes, <= expr`; the expression may be any expression over constants, parameters and the input (`max(1, limit)`); the bound is checked by the executor after the transition (for a path — at the write; a violation is a machine error). If the bound in the primary source is wrong for some values, it is not written.
- `writes` — who changes the datum: `rows` (everything written in the machine tables: the row actions, the “On accept” block, writing primitives called from the tables; the default), `mechanics` (executor writes outside the machine text: attempt counters, the transfer from `to_send`, `open_requests`, rules 14, 15, 21), `rows_and_mechanics` (both; the exception of rule 29 is named explicitly), `fragment` (data of an included fragment), `rows_and_fragment` (the machine rows and the fragment rows: the datum `stop_reason`) (А3, E5). `writes` is set for the whole datum; a path has its own value: a write from a transition row into a field with `writes: mechanics` is a table check error (С11).
- **Contract data** is entered into the table and enters `all_data` (АМ8): `open_requests` (`[]text`, initial `[]`, `writes: mechanics`) is entered by the “Pause” fragment — it is read by `pass` and `cancel_open` (section 9); for a machine without the fragment that reads it itself, the machine enters it; a declaration in two places is a name conflict (rule 36), a check error (ША1, ШВ3); `to_send` (`[]text`) is `rows_and_mechanics`: the rows write it (Lock, LensRefusal), the mechanics moves the parties to `open_requests` (rule 21, СГ5); the party attempt counter is the datum from the column `counter` of “Parties” (section 1, СГ1).
- **The composition of `all_data`** (СГ2, ША1, Н-1): **every** datum named in the `## Data` tables of the machine and of the included fragments, and the contract data (the previous item); a field path is inside its datum. The sign is one and is checked by the tables: named in a table — included; there are no exceptions among the named. Therefore data that the source relates to external objects and the assignment are also included (for “Meeting” `proposal`, `copy`, `copy_fingerprint`, `witness_answers`, `lens_findings`, `summary`, `archive`, `author_question`, `lens_order`), and the copy of the input (`agent_request` of “Agent step”): the primary source gives for ERROR “all variables and stores”, rule 11 of the specification — “all data of the machine”. Only what is not in the tables is not included: executor data and the envelope (`state`, `trace`, `step`, `event_counter`, `cause`, `accepted_requests`, the journal) and the stores of rule 31 (`human_words`, `failure_texts`; a human's word and a failure text are not written to the journal in full). Encoding — section 5.

Example (pilots; the bounds and `writes` are as in the pilots, except `lenses`: a field path instead of `rows_and_mechanics`).

```
| name | type | initial | non_decreasing | writes |
| agent_request | AgentRequest | AgentRequest { kind: input.kind, profile: input.profile, session: input.session, dialog_kind: input.dialog_kind, context: input.context, limits: input.limits, trace: input.trace, step: input.step } | — | rows |
| turn | "first" \| "retry" \| "continue" \| "fix" \| "permission" | "first" | — | rows |
| retry_count | int>=0 | 0 | yes, <= RETRIES | rows |
| turn_count | int>=0 | 0 | yes | rows |
| turn_before_retry | ?("first" \| "retry" \| "continue" \| "fix" \| "permission") | none | — | rows |
| stop_reason | "" \| "no_result" \| "max_tokens" \| "pause_halt" \| "cancel_request" | "" | — | rows_and_fragment |
| agent_attempt | int>=0 | 0 | yes | mechanics |
| number | int>=1 | 1 | yes | rows |
| lenses | map[text, Lens] | dict(input.lens_order, l -> l, l -> Lens { id: l, lost: 0, probes: 0, attempt: 0 }) | — | rows |
| lenses[*].attempt | int>=0 | — | yes | mechanics |
| witness_answers | map[int>=0, []WitnessAnswer] | {} | — | rows |
```
(The types `turn`, `turn_before_retry`, `stop_reason` are rewritten to a literal set, the values are the same as in the earlier record. The first seven rows are “Agent step”, the rest are “Meeting”; `agent_request` is built by a constructor from the input fields (section 1, Я-30); `open_requests` is entered by the “Pause” fragment, its row is not written in the machine table. In `stop_reason` a part of the set is shown; the full set of the pilot is twelve values. `turn_count` has no `<=` bound: with a turn limit below 1 the code gives 1. `number` is `int>=1`: in the code `Cycle.new()` and `MachineData.new()` give 1, it changes only by `+= 1` (the invariant “does not decrease”); `number - 1` is `int`, 3.2. The row `lenses` changes `lost` and `probes`, `attempt` only by the mechanics: the record `lenses[k] = { ...l, field: expr }` that does not name `attempt` is a copy, not a write into it.)

## 3. Expressions

The words of expressions (`if`, `then`, `else`, `and`, `or`, `not`, `let`, `in`, `match`, `true`, `false`, `none`, `unreachable`) and the readable names are quoted in the English form; the Russian form is in the [word table](portolan-keywords.tsv), the kinds `expr` and `readable` (1a).

### 3.1 Grammar

```
expr := literal | true | false | none | unreachable | name | ( expr ) | expr.field | expr.N | expr[expr]
     | Type { field: expr, ... } | Type.Variant { field: expr, ... } | Type.Variant     record, variant with fields, variant without fields
     | { ...expr, field: expr, ... }                        copy of a record with fields replaced
     | (expr, expr, ...)                                  tuple (from two fields)
     | [expr, ...] | {expr: expr, ...}                       list; map (the key is an expression); [] and {} are empty
     | not expr | -expr | expr (+|-|*|/|%) expr | expr (==|!=|<|<=|>|>=) expr
     | expr (and|or) expr | expr ?? expr
     | if expr then expr else expr | let name = expr in expr
     | match expr { alt [| alt]... [if expr] -> expr; ... ; else -> expr }       exhaustive
     | name(expr, ...[, name: expr, ...])                     catalog function or definition (pure); named arguments come after positional ones
     | macro(expr, name -> expr) | fold(expr, expr, (name, name) -> expr)
     | call(primitive, expr, ...)                      reading: only in “Request”, “profile” and in “let” of “On entry”/“On accept”; in any position of these expressions (section 7)
alt := Type.Value | Variant | Variant(field, field: name, ...) | literal
```

- **Precedence** (highest first): parentheses `( )`, `.`, `[]`, call; unary `-`; `* / %`; `+ -`; comparisons; `not`; `and`; `or`; `??`. `if`, `let`, `match` capture everything to the right.
- **Literals:** integer `12`, float `0.0`, text `"…"`; `true`, `false`; `none` — the absence of a value of `?T`. The word “no” (Russian `нет`) is not a literal (rule 30: the “no” of the specification is `none` of `?T`). `unreachable` is an expression of any type: a program defect, the evaluation is stopped by the executor, like `require(none)` (3.3, И-3); it stands in the `match` branch for a variant that by the contract does not arrive (E1).
- **Names.** A name is a datum, a constant, a parameter, a definition, a binding. A state reads any name from its reads (`Reads`; for an appeal — the `Request` table), whatever its `reads` is (T9). An event field binding, `let` and a lambda parameter are visible only in their scope; an event field binding does not coincide with the name of a machine datum (4.3, Я-26). A function and a name lie in different spaces: a bound field `text` and a call `text(x)` do not interfere. **Reserved words** (СГ12) are never the name of a binding, a datum or a field: `in`, `then`, `else`, `and`, `or`, `not`, `let`, `match`, `if`, `for`, `each`, `true`, `false`, `none`, `unreachable`.
- **Field binding with a colon** (Я-8). A field of a signal or a variant is declared in the Nova notation through a space (`findings []Finding`, section 2); a binding in a pattern of a transition row is `field: name`, the colon is read “field → name” (`signal(counted(findings: new_findings))`, `response: Finished(text, artifact, usage: received)`); if the name coincides with the field, the single name is written.
- **A lambda** is unary (binary only in `fold`); a parameter that is not needed is written `_`; lambdas stand only in a macro argument.
- **Readable names of the executor** (not computations, rule 11): `input`; `event.id` (of any event); `event.<field>` (a field of the event data of a row or a chain, rule 13); `party` (for a set — the identifier of the event's party; in the “profile” and “Request” of a set — the current party); `reason` — the failure code of the event `failure(reason)` (4.3; visible to the row and the chain, Я-49); `state` (section 9; type `State`); `transition_note` (type `JournalEvent`; in “On entry” and in the “response” of ends; defined when the machine has entered ERROR, and ERROR is entered in two ways: by `machine_error` — the record of this action (А4) and by an executor machine error (3.3) — the record `machine_error`; both ways give a record, ША8, СГ6); `all_data` (a record of the machine data; the composition is in section 2; in the action `journal(all_data)` the same name is an abbreviation of the event `machine_data`, section 5, И-2). `previous` and `call_request_id` are not executor names but data of the “Pause” fragment (section 9, T6). The JSON name of a readable name is the `en` word of the word table, the kind `readable` (`party`, `reason`; 1a, Я-49). The names `trace` and `step` (the envelope, rule 31) are available **only** in the “Request” expressions of a party of kind `machine` — this is the envelope of a nested machine call (rule 35, item 1); in conditions and actions the envelope is not read.
- **Not introduced from the methodology's count:** `contains`, slices, postfix `?`, sorting, loops and recursion outside `for each`.

Example of expressions (the “Agent step” pilot, definitions).

```
define needs_elevated_attention(action_kind ActionKind) -> bool =
  match action_kind { ActionKind.Delete | ActionKind.Move | ActionKind.Execute | ActionKind.Network | ActionKind.SwitchMode -> true;
                      else -> false }

define retry_pause(n int>=0) -> int =
  fold(range(1, n), RETRY_PAUSE, (m, _) -> m * 2)
```

### 3.2 Expression types

| Rule | Record |
|---|---|
| Raising `T` to `?T` | in an assignment to a field `?T`, in a record constructor field, in a function argument with a parameter `?T`, in a branch of `if`/`match`, to the right of `??` |
| `if`, `match` | branches `T` and `?T` (or `none`) give `?T`; branches of one type — that type |
| `??` | `?T ?? T` is `T`; `?T ?? ?T` is `?T`: the right operand of either of the two types, the result is `T` only with the right `T` |
| `+` | int, float (cannot be mixed), text (concatenation), a list of one type (concatenation: the left first) |
| `==`, `!=` | structural for records, tuples, lists, maps, enumerations, `?T`; `T` with `?T` — through raising (`none` is not equal to a value) |
| `<`, `<=`, `>`, `>=` | int, float |
| `expr[key]` | map: `?V`, an absent key is `none` (not an error); for a full map — `V`. List: `?T`, an index out of bounds is `none` |
| Literal set | the value of the expression is a **set of values**: a literal is one; `+` — pairwise concatenations; `if`/`match` — the union of the branches; `require(x)` — the set of `x` without `none`; `non_empty(x)` — the set of `x` without `""`; `text(x)` for an enumeration or its subset — their values; assignment and comparison with a datum of the “literal set” type check the inclusion of the set. A concatenated field with an “empty” beginning is declared by the source (E9, СГ3): the source gives “no” — `?("a" \| "b")` without `""`, `none` and `require`; the source gives `""` — `"" \| "a" \| "b"`, initial `""` and `non_empty`. One value is not replaced by another: in a data snapshot `""` and `none` are different |
| literal set → `text` | a set value is assigned to a datum and passed to a parameter of type `text`, the set is forgotten; the reverse — by the inclusion of the set (ША10) |
| `id` → `text` | assigned to a datum and to a parameter of type `text`, the type `id` is forgotten; the reverse — only a literal of UUID format (section 2, Т-2) |
| `int>=n` | assigning a value that violates the bound is a machine error; statically checked only for literals and constants; `int>=n` is compatible with `int` both ways. The result of `+`, `-`, `*` over `int>=n` is `int` (without a bound): `number - 1` is `int`, passing it to a parameter `int>=0` is checked at the call (T8, АМ4) |
| `unreachable` | any type: compatible with `T` and `?T`; in `match` it does not affect the result type |

Example (the “Agent step” and “Meeting” pilots; `failed_appeal` is declared `"" | "Witness" | "Lenses" | "AuthorFix" | "AuthorQuestion"` (a literal set), initial `""`, as in the source: the set after `non_empty` has no empty value).

```
stop_reason = text(reason)                                     // reason in {ConnectionLost, Timeout, NoResult}: the set {"connection_lost","timeout","no_result"}
stop_reason = non_empty(failed_appeal) + "_halt_meeting"      // the set: four values “..._halt_meeting”, all belong to the set stop_reason
```

### 3.3 Evaluation

- Evaluation is strict, left to right: function arguments, record fields, list and map elements — in the order of writing; `match` branches — top to bottom, the `if` guard — after the alternative matches; `let` — first the value, then the body. **Lazy** are only `if`, `and`, `or`, `??`: an unselected branch and a right part that is not needed are not evaluated.
- **A reading call inside `if`/`match`** (E4): the selected branch evaluates the call, the unselected one does not (laziness above); the read of the call enters the reads of the state unconditionally, by the `reads` list of the primitive. Calls in arguments are evaluated in the order of writing.
- **The language is not total.** Two kinds of partial operations (ША8, СГ6, ШВ1, СВ2).
  - **A program defect** (И-3): `require(x)` with an empty `x`, `non_empty("")` and `unreachable` — the process is stopped by the executor (not the table); there is no transition to ERROR, the machine state is not rolled back; the call response is an end with `NoResult`; the journal of the defect is at the executor's discretion (this is how `required` of the automata behaves).
  - **A machine error:** `int` overflow, division by zero, going outside `int>=n`, `int(x)` out of range, a repeated key in `dict(…)`, an absent key in `name[key].field = expr`, an index out of bounds when writing into a list. The executor writes the journal event `machine_error` with the parameter `reason` — a word from the closed list `overflow`, `division_by_zero`, `bound_violation`, `conversion_range`, `duplicate_key`, `missing_key`, `list_index` (journal, subsection “Events of the table format”) — and enters ERROR; this event is the `transition_note` (3.1).
  - Indexing a map and a list when reading is not a partial operation.
- `if` is not nested into a branch of another `if` (three or more outcomes — a `match` with guards or a fork).
- `text(x)`: an integer is a decimal record; a float is the shortest decimal record that is reversible to the same float; an integral value is written with `.0` (`1.0`, `0.0`); without an exponent `e` if `1e-4 <= |x| < 1e16`, otherwise an exponent of the form `1e-7`, `1.5e20` (lowercase `e`, without `+` and without leading zeros of the exponent); examples: `0.0`, `2.0`, `0.42`, `0.0001`, `1e-7`, `1.5e20`; NaN and infinity are a machine error (А1); an enumeration is the value of the element (for an element without a value — the JSON name); `State` is the JSON name; text is itself; `none` of any of these types is `none`. For `bool` and composite types `text` is not defined.

## 4. States

### 4.1 General

The heading `### NAME — kind (Latin_name)`: kind is `appeal`, `operation`, `fork`, `end`; **the name in parentheses is the JSON name of the state** (1a, Я-46): Latin, for the journal and the envelope (the field `state`, the parameter `fork`, `text(State)`). The parentheses are required for a non-Latin name (Russian `ПОВТОР` → `(Retry)`); for a Latin one the JSON name is the name itself (`### Retry — fork`), parentheses give another one (`### Pass — appeal (Gate3)`). The template headings below keep the form with a distinct name in parentheses. The `№` of a row = the label `// NAME #n` in the primary source. The **first** suitable row is selected. The initial state is the first line of the section `## States`: `Initial state: NAME` (А8); the check 34(г) requires that it name a state of the section. **The reads of a state** (rule 11, Я-39): for an appeal — the table `Request:` (4.2), for an operation, a fork and an end — the key line `Reads:` with the names of data that are read by the “On entry”, the conditions and the actions of the state, through commas; a state that reads nothing writes no `Reads:` line, an appeal without request fields — no `Request:` line (Я-40); the reads of a reading primitive (section 7) enter the reads of the state by its `reads` list; the `Reads` of ERROR is `all_data` (all data of the machine without executor data; the names are read as data). In the examples of this English version the state names are the Latin names, so the parentheses are omitted (Я-46).

**State key lines** (С-1) — `Party`, `Idle term`, `Edits`, `Form returns`, `Request`, `Reads`, `On entry`, `On accept`, `Except`, and in the sections `## Parties` and `## Ends` — `Request limit` and `Result` — are **items of a bulleted list**: `- Party: agent`, `- Idle term: IDLE_TERM`, `- Reads: retry_count, turn`. The marker `- ` is optional in parsing (compatibility with version 2.5), required in writing; the reason: markdown glues consecutive lines into one paragraph, and the preview shows “Party: agent Idle term: IDLE_TERM Request:” as one line. **Empty values are not written** (Я-40): a key with an empty value (`—`, `none`: no request fields, nothing to read, no term, no work on entry) is skipped, and an omitted key means the default; `- Idle term: —`, `- On entry: —`, `- Input: none` are not written. A key with a real default value (`- Idle term: 0`, `- Form returns: 0`) may stay written: so it shows that the value is chosen, not forgotten. The other rules of writing:

- a table (request field | expression | reads of `Request`; event | actions of `On accept`; the state rows) stands **at the block level**, not inside a list item: between the last list item and the table, as between two tables, there is an empty line; the item itself (`- Request:`, `- On accept:`) remains the last in the list before its table;
- a value in one line is in the item itself (`- On entry: let moment = call(time_now)`); the body of “On entry” of several actions is a nested list, one action per item (`  - let current_time = call(time_now);`), the sign `;` at the end of the item is kept, parsing glues the items into the same action list through `;`;
- the state heading `### NAME — kind (Latin_name)` and the line `Initial state: NAME` (one per section) are not written as a list.

**Prose** (П-1, Я-12). A paragraph — one or several lines of text between empty lines (an empty line is needed both before and after) outside tables, outside code blocks and outside key lines — is a comment for the reader: translators and checks skip it, the signs “`” and “« »” inside it are allowed. A text line pressed against a table, a heading or a list item without an empty line is not a paragraph (markdown glues it to the neighboring block): the formatting check warns, parsing reads it as an extra line of the neighboring block. Headings `#`, `##`, `###`, tables and the list items of key lines (`- Key: …`) are not prose. So that a typo in a key does not become a silent comment, the formatting check (section 10) warns about a paragraph line that begins with a word from the list of keys (`Party`, `Idle term`, `Request`, `Reads`, `Edits`, `Form returns`, `On entry`, `On accept`, `Result`, `Except`, `Request limit`) without the marker `- ` or with a typo in it.

**“To”:** a state name; `previous`; `preparation_return` (rule 24); `same` (stay in the state; for common events); the suffix `, rerun` (rule 18); `—` for a row with `machine_error`.

**The fork default.** A fork without a suitable row is `machine_error("fork_no_match", fork: "<Latin_name>")` (the value of `fork` is a text literal, АМ6, T10). An `else` row by rule 27 is allowed: it is written last with the same action (and the same literal `fork`) and leads to `—`; it equals the default. The default label is the next number after the last row.

### 4.2 Appeal

```
### NAME — appeal (Latin_name)
- Party: <name from “Parties”>[; set: <list expression of identifiers>]
- Idle term: <expression of type ?int>=0>   optional; an empty one (`—`) is not written, not written — no term
- Edits: <datum>; check: <reading primitive>   optional (rule 14)
- Form returns: <int>=0>                 optional, 0 by default (`0` may be written)
- Request:                               optional: no request fields — no line

| request_field | expression | reads |       reads: party | executor

- On accept:                                  optional

| event | actions |
| <event> | <actions> |

| № | Event | Condition | Actions | To |
```

- **Request.** `reads: party` — a request field to the party; `executor` — a name that the state rows read, and it does not go into the request (`request field` = expression = name). The state rows, “On accept”, “Idle term” read **any** name from `Request`, whatever the value of `reads` is (T9). The request field `profile` is not written in the “Request”: it is given by the column `profile` of “Parties” (T3). The expressions read the machine data, constants, parameters, `input`, `party` (a set) and — for a party `machine` — `trace`, `step`; `call` reading is allowed (evaluated on entry, before sending, in the order of the rows). The request fields of a party `machine` are exactly the fields of its type `input`, except `profile` (it is given by the column of “Parties”, СВ5). A request field may be named as a datum with a different expression (`previous` — `require(previous)` of Pause): the rows, the conditions and “On accept” read the **datum**, not the field, the field is visible only to the party, and such a field is only `reads: party` (ША3); the expression of such a field is any “Request” expression, including `call` and `if` (in Changed of “Meeting” the field `proposal` is `if call(proposal_read) then proposal else none`), the rows do not read it (Я-28). The conditions, “On accept” and “Actions” read only the names from `Request`, `event.…`, bindings, constants and parameters (rule 11).
- **`reads` by default** (Я-27). If the source does not say who reads a field (its state “Input” table has no column “Who reads”), `party` is written: the field goes into the request, as in the source; `executor` — only for the names that the source names as not going into the request.
- **An appeal without request fields** (Я-23, Я-40). If the party needs no request fields (the gate “repeat / halt” without data), the line `Request:` and the table are not written: the request carries only what the executor gives (the envelope, `profile` from the column of “Parties”); the rows, “On accept” and “Idle term” of such a state do not read machine data — only `event.…`, bindings, constants and parameters. For a party `machine` a request without fields is allowed only if the type `input` has no fields (section 1, Я-30).
- **Idle term.** A line not written (an empty value `—` is not written, Я-40), `none` or `0` mean no term ( a human has no term — an open gate, rule 19; a gatekeeper has no term written in the state: the term of an agent gatekeeper is a parameter of the gatekeeper, rule 19; a machine call has no term, rule 35, item 5). The expression reads the same names as the “Request” expressions (data, constants, parameters, `input`, `party` of a set), without `call` (catalog functions are allowed, ША5); these names are named in the `Request` of the state (А7). It is evaluated on entry, after the “Request”, before the request is sent.
- **Edits** (E3, rule 14). `Edits: <datum>; check: <primitive>` — the party's response edits an object that the datum reflects (`proposal`), and the result cannot be accepted if the object changed since the beginning of the attempt. `check` is a reading primitive without parameters with the result `bool`; the executor calls it when it accepts the response, after the check of the openness of the request and the form and before `parse` and “On accept”. `true` — the result is not accepted (it is not written to `accepted_requests`, “On accept” is not executed, there is no event), the request is cancelled and goes out again: a new attempt, the `Request` is evaluated again; the journal entry about this is executor mechanics. The “beginning of the attempt” and the comparison are owned by the executor, the primitive reads its service record and the object (`reads`). A datum from `Edits` must be written in the “On accept” of this state (table check).
- **Set** (rule 21): `Party: lens; set: lens_order` — one request per identifier; `party` in the “Request” is the identifier for which the request is built; `Request limit` is a section of “Parties”. `to_send` is a datum `rows_and_mechanics`, `open_requests` is `mechanics` (section 2, СГ5), the party attempt counter is the column `counter` of “Parties” (section 1, СГ1).
- **Form returns** — how many times the executor returns to the party a response that is not by form or not by the comparison done by `parse` (for example, of excerpts; rule 18, СГ14). For the kinds other than `machine` — in the same request. For a party `machine` — with a new request of the same party with a new identifier and a remark: the same identifier would return the ready response (rules 14, 35, item 4). The comparison (for example, of excerpts) is done by the primitive `parse` on acceptance, the return itself is executor mechanics (E7). When the returns are exhausted, the request is closed by the event `failure` with the code `FormNotFixed` (a parse failure, section 1, Я-33).
- **Condition** in an event row — only for the common events and the signals of a fragment (rules 23, 35); for appeal rows `—`. An event whose condition is false is dropped (rule 17, the journal entry is mechanics). The condition `else` (E11) is allowed for a signal: the last row of the same event, taken if the conditions of the previous rows of this event are not true; the other events have no `else`.

Example (the “Meeting” pilot, Lenses). Changed: the key of findings is a tuple instead of the pilot's record; the names `trace`, `step` instead of the reading primitives `call_trace`, `call_step`; there is no `profile` row (T3); not all rows of the “Request” are shown.

```
### Lenses — appeal
- Party: lens; set: lens_order
- Idle term: 0
- Request:

| request_field | expression | reads |
| kind | CallerKind.Lens | party |
| session | party | party |
| context | call(role_context, RoleContext.LensContext { proposal: proposal, witness_answers: witness_answers[number] }) | party |
| trace | trace | party |
| step | step | party |
| number | number | executor |
| to_send | to_send | executor |
| lenses | lenses | executor |
| responded | responded | executor |
```

### 4.3 Appeal events

A table of rows `| № | Event | Condition | Actions | To |`. The kinds of events:

| Event | Meaning |
|---|---|
| `response`, `response(name)` | the response value (the party's result or the result of its `parse`, section 1); `name` binds it as a whole |
| `response: Variant(field, field: name, …)`, `response: Variant`, `response: Type.Variant(…)` | the response value is a variant of the party's `result` type (for `machine` with `parse` — of the parse result, E1, ША2); the fields are bound as names (`field: name` — with renaming); a variant without fields — without parentheses |
| `failure`, `failure(reason)`, `failure(reason in {…})` | a refusal or “no response” (rule 16); a closed subset of codes is the **list of the state**: the union of the sets of its `failure` rows (a row without a set — all `FailCode`). A code outside the list is brought by the executor to `FailCode.NoResult` (rule 16), the event already carries it; if `NoResult` is also outside the list — `unreachable` (the set is declared full for the state) (СВ3) |
| `signal(<signal>)`, `signal(<signal>(field, field: name, …))` | a **party signal** of the appeal (`human`, `enhanced`, the gatekeeper; Я-38): the signal is from the column “signals” of the party, the fields and their types are from there too; or a **machine signal** outside the contract (stop, cancel, signals from a parent) — only in the common events and in Pause of a fragment (section 9); a machine signal row may have the condition `else` (4.2) |
| `immediate` | for an operation: a transition without an event after the work on entry (rule 26) |

- **Bindings.** Any event field is available also as `event.<field>`; a binding is needed for brevity. A binding name that coincides with a machine datum name without renaming is a check error (there is no shadowing). A part of the fields may be bound.
- **A field named as a datum** (Я-26). A field of a signal or a variant may be named as a machine datum (the signal `confirmed(confirmation text)` with the datum `confirmation`): it is the binding that shadows, not the field declaration; such a field is bound with renaming (`signal(confirmed(confirmation: confirmation_word))`) or read as `event.confirmation`. The machine data here are taken together with the data of the included fragments, and the check goes after the substitution of a fragment: the bindings of the rows of the “Pause” fragment (`human_word`, `author`, `source`, `id`; in a Russian file — the names of the Russian fragment file) coincide with no machine datum, therefore a machine datum is not named so (glossary version 10: `источник_запуска` → `launch_source`, not `source`, Я-37).
- **Set.** The events of a set carry `party`; the chain of forks behind an event row reads it as `event.party` (rule 13).
- **Party signals** (Я-38). The signals of a state are the signals of its rows. A party signal is accepted by a row of an appeal whose `Party` declared it; a signal of a human carries the identifier of the open gate, and with the identifier of a gate that is not open it is discarded (rules 17, 19); with gates of several parties in one state the signal belongs to the party named in the identifier, and a signal it did not declare or a signal from another party is discarded (“a word of a foreign party”, rule 19); a signal of a human on a gate accepted by the answer of the agent gatekeeper replaces that answer until the transition by it (window 2, rule 19); a free message of a human without an identifier (an appeal without gates, a “wall”, rule 19) cannot be written by the format yet (section 14); a signal the party did not declare is a row check error. A declared party signal for which the current state has no row is not accepted by a row of the state; it is discarded, and the gate stays open (rules 14, 17, 19; the item of section 14 is closed). Every signal of a party is used in at least one row of the machine (or of a fragment); the signal of an event of an appeal row enters the list of signals of its party. A signal field is declared in the column “signals” through a space, and in a row it is bound as `field: name` (3.1, Я-8).
- “On accept” — actions BEFORE the transition (rule 14), section 4.4.

Example (pilots). Changed: signals with data — the record `signal(counted(findings: new_findings))` instead of the pilot's undefined binding; fields that coincided with data are renamed; an excerpt of the “Parties” table is added to Gate3: the signals `not counted` and `counted(findings []Finding)` are declared in the column “signals” of the gatekeeper, the party of the appeal (Я-7, Я-38).

```
### AgentTurn — appeal       // rows 1, 3, 6, 8, 9 of the “Agent step” pilot
| № | Event | Condition | Actions | To |
| 1 | response: Finished(text, artifact, usage: received) | — | transport_usage = add_usage(transport_usage, received); reply_text = text; reply_artifact = artifact | ReplyValidation |
| 3 | response: TurnRequestLimit(usage: received) | — | transport_usage = add_usage(transport_usage, received); stop_reason = "max_turn_requests"; journal(turn_requests_exhausted) | Accounting |
| 6 | response: TransientError | — | — | Retry |
| 8 | response: NeedsPermission(permission_request: request) | — | permission_request = request | Policy |
| 9 | failure(reason in {FailCode.ConnectionLost, FailCode.Timeout, FailCode.NoResult}) | — | stop_reason = text(reason); journal(turn_failed, reason: text(reason)) | Accounting |

| name | id | kind | profile | signals | counter |
| gatekeeper | gatekeeper | human or agent by setting elevated_attention_executor(result GateOutcome) | — | not counted, counted(findings []Finding) | gatekeeper_attempt |

### Gate3 — appeal                      // rows 1, 2 of the “Meeting” pilot
- Party: gatekeeper

| 1 | signal(not counted) | — | journal(pass_probes_not_probes, pass: text(number)); number += 1 | Pass |
| 2 | signal(counted(findings: new_findings)) | — | number += 1; gate3_findings = new_findings | Totals |
```

### 4.4 On accept

The appeal block `On accept:` is a table `| event | actions |`. The event is `response`, `response(name)`, `response: Variant(…)` or `failure`; the event bindings and `party` are available; the response value is the result of the party's `parse` (section 1). The executor executes the block when it accepts the response, before the transition, in one commit with the record in `accepted_requests` (rule 14); the bindings of the block (`let`) are saved with the accepted event and are visible to its row and chain. The order of acceptance: the openness of the request and the form, “Edits” (4.2), `parse`, the block.

Allowed in the block: assignments to data, `+=`, `field[key] = expr`, `field[key].field = expr` (5), `for each`, `if`, `let name = expr` and `let name = call(reading, …)` (in any position of an expression, 3.1). Not allowed: `journal`, `machine_error`, `call` writing and irreversible, a transition; writing calls after acceptance (for example, a time mark and a cache check) are written in the row actions (АМ9). The data that the block writes are `writes: rows` (2).

Example (the “Meeting” pilot, Lenses). Changed: the value of `result` is the result of the `parse` of the party `lens` (`LensResult`, section 1), not the pilot's record; the write into a lens is a copy of the record with fields replaced through `require(lenses[party])` (Н-11): in the code `@lenses(lens_id)` for an absent lens is `unreachable` (the lenses are created at the start), that is a program defect, `require(none)` (3.3); the short record `lenses[party].field = expr` would give the machine error `missing_key` (3.3), differing from the code.

```
- On accept:

| event | actions |
| response(outcome) | let l = require(lenses[party]) in (lenses[party] = { ...l, lost: 0, probes: outcome.probes }); responded += 1; lens_findings[(party, number)] = outcome.findings |
| failure | let l = require(lenses[party]) in (lenses[party] = { ...l, lost: l.lost + 1, probes: 0 }) |
```

Example (the “Meeting” pilot, AuthorFix): the property “Edits”, the parse into the variant `EditResult`, the write on acceptance and the rows by variant (СГ15). Changed: the pilot could write neither the check of rule 14 nor the choice of a row by the variant of the role result; the write on acceptance is by variant, not a `match` over both: with `Done` the `author_question` is neither read nor written, as in the code. The type `EditResult` is defined in the example (Н-9): the variant fields are as in the table of the primary source (“done”: `proposal`; “question”: `proposal`, `question`); in the code `Done(str)` and `Asked(Asking)` with the fields `proposal`, `question` — the record `Asking` is expanded into the variant fields.

```
variant EditResult {
  Done { proposal text }
  Question { proposal text, question text }
}

### AuthorFix — appeal
- Party: author
- Idle term: 0
- Edits: proposal; check: proposal_changed_since_attempt
- Form returns: 0
- Request:

| request_field | expression | reads |
| context | call(role_context, RoleContext.FixContext { proposal: proposal, gate3_findings: gate3_findings, author_guidance: if author_guidance == "" then none else author_guidance }) | party |

- On accept:

| event | actions |
| response: Done(proposal: fix) | proposal = fix |
| response: Question(proposal: fix, question: question_text) | proposal = fix; author_question = question_text |

| № | Event | Condition | Actions | To |
| 1 | response: Done | — | author_guidance = "" | Pass |
| 2 | response: Question | — | author_guidance = "" | Gate7 |
```
(Not all rows of the “Request” and the failure rows are shown. The reads of the primitives `check` and `parse` enter the `Request` by their `reads` lists, section 7.)

### 4.5 Operation

```
### NAME — operation (Latin_name)
- Reads: <names>                          optional
- On entry: <let bindings and calls>

| № | Event | Condition | Actions | To |
| 1 | immediate | — | <data changes, journal> | ... |
```

“On entry” is work with the outside world (rule 10): `let name = <expression>` and `let name = call(primitive, …)` (reading and writing), writing and irreversible calls without a result. A binding is visible further in “On entry” and in all rows of the state; it is evaluated once per entry. The write of a writing primitive (its `writes`) is visible to the bindings of “On entry” and the rows that follow it: the order of writing is the order of execution (T7). Data changes and the journal are in the row `immediate` (rule 29). An operation has one event — `immediate`.

Example (the “Agent step” pilot, Start and Accounting; “Meeting”, Lock, CopyRestore, Filter, SummaryBuilding). Changed: the write of data is moved from “On entry” into the row; `immediate(data)` is replaced by a binding; in CopyRestore the conditional action is in the row; in Lock `copy` is the text of the proposal, `copy_fingerprint` is the fingerprint (T1; fixed in the source, ИС1); in Filter the write into a lens is a copy through `require(…)`, as on acceptance in Lenses (4.4, Н-11), and `lenses_without_critical` is a primitive without a body in the source (section 7), the `Reads` includes its reads; in SummaryBuilding the `Reads` includes the reads of `build_summary` from the registry (Н-7: the v2.2 example named only `number`).

```
### Start — operation
- On entry: let moment = call(time_now)

| 1 | immediate | — | started = moment; turn_count = 1 | AgentTurn |

### Accounting — operation
- Reads: agent_request, stop_reason, transport_usage, started
- On entry:
  - let current_time = call(time_now);
  - let collected = collect_usage(agent_request, stop_reason, transport_usage, started, current_time)

| 1 | immediate | — | usage = collected; journal(usage_event(collected)) | StepOutcome |

### Lock — operation
- Reads: proposal, lens_order
- On entry: let fingerprint = call(proposal_fingerprint); call(close_for_writing, "proposal")

| 1 | immediate | — | copy = proposal; copy_fingerprint = fingerprint; to_send = lens_order; responded = 0 | Lenses |

### CopyRestore — operation
- Reads: copy

| 1 | immediate | — | if has(copy) then (proposal = require(copy)) else (journal(copy_restore_no_copy)) | Void |

### Filter — operation
- Reads: number, lens_order, lens_findings, witness_answers, lenses
- On entry:
  - call(remove_unsound, number);
  - let without_critical = call(lenses_without_critical)

| 1 | immediate | — | for each l in without_critical: lenses[l] = { ...require(lenses[l]), probes: 0 } | SummaryBuilding |

### SummaryBuilding — operation
- Reads: number, lens_order, lens_findings, lenses
- On entry: let outcome = call(build_summary, number)

| 1 | immediate | — | if has(outcome) then (summary[number] = require(outcome)) | ReviewParsing |
```

(`usage_event` and `collect_usage` are definitions, the example is in section 8.)

### 4.6 Fork

```
### NAME — fork (Latin_name)
- Reads: <names>                          optional
- On entry: let name = <expression, including one with a reading call in any position>      optional

| № | Condition | Actions | To |
```

A fork does nothing and waits for nothing (rule 9): “On entry” is only `let` bindings (an expression; a reading call is allowed in any position of an expression, including in a branch of `if`, 3.3), each evaluated once per entry; the row actions change data only in its transition. The conditions do not call primitives through `call`: the result of a reading primitive is read by a `let` binding of “On entry”; a `pure` primitive (section 7) and a definition are called in a condition as functions `name(arg)`, and so are the catalog functions (Я-29).

Example (the “Agent step” pilot). Changed: the default without an `else` row; the Latin name of ReplyValidation is `ReplyValidation`, as in the glossary (П-4); the ReplyValidation example does not pass a non-existent argument: the reads of `reply_validation` are named in the registry (section 7) and enter the `Reads`.

```
### Retry — fork
- Reads: retry_count, turn

| 1 | retry_count < RETRIES and turn != "retry" | retry_count += 1; turn_before_retry = turn; turn = "retry"; journal(agent_transient_error, retry: text(retry_count)) | Budget |
| 2 | retry_count < RETRIES and turn == "retry" | retry_count += 1; journal(agent_transient_error, retry: text(retry_count)) | Budget |
| 3 | retry_count >= RETRIES | stop_reason = "no_result"; journal(agent_transient_error_exhausted, retries: text(RETRIES)) | Accounting |

### ReplyValidation — fork
- Reads: return_count, reply_text, reply_artifact, agent_request
- On entry: let validation = call(reply_validation)

| 1 | validation == ReplyCheck.Valid | — | Accounting |
| 2 | validation == ReplyCheck.Empty | stop_reason = "no_result"; journal(agent_no_result) | Accounting |
| 3 | validation == ReplyCheck.Violated and return_count < FORM_RETURNS | return_count += 1; turn = "fix"; journal(reply_form_violated) | Budget |
| 4 | validation == ReplyCheck.Violated and return_count >= FORM_RETURNS | stop_reason = "form_not_fixed"; journal(reply_form_not_fixed) | Accounting |
```

Example of a nested reading call (the “Meeting” pilot, Comparison; E4): the fingerprint is read only if the proposal is read; `proposal_fingerprint` for an unreadable proposal is `unreachable`, therefore the call stands in a branch of `if`, and the `Reads` of Comparison includes the reads of both primitives.

```
### Comparison — fork
- Reads: copy_fingerprint
- On entry:
  - let was_read = call(proposal_read);
  - let fingerprint = if was_read then call(proposal_fingerprint) else none

| 1 | was_read and fingerprint == copy_fingerprint | — | Filter |
| 2 | was_read and fingerprint != copy_fingerprint | — | Changed |
| 3 | not was_read | — | Changed |
| 4 | else | machine_error("fork_no_match", fork: "Comparison") | — |
```

Example of a fork of a set chain (the “Meeting” pilot, LensRefusal): `event.party` is from the event Lenses #2.

```
### LensRefusal — fork
- Reads: lenses, to_send, number

| 1 | require(lenses[event.party]).lost == 1 | journal(lens_dropped, party: event.party, pass: text(number)) | AllClosed |
| 2 | require(lenses[event.party]).lost == 2 | failed_appeal = "Lenses"; to_send = [event.party] + to_send | FailedRequest |
```

### 4.7 End

```
### NAME — end (Latin_name)
- Reads: <names> | all_data             optional
- On entry: <actions>                     optional
- Except: <value in {...}>                optional
```

The “On entry” of an end is work with the outside world and the journal: `let` bindings, `call` (reading, writing, irreversible), `journal`, conditional `if`, `for each` with a body of `journal(…)` and `if` (E2); an end does not change data (rule 29). `Except:` — the values of the set with which this end is not entered: the exhaustion of the “Ends” is checked by the set without them; an entry with such a value is `unreachable`.

**The “Ends” table** (rule 35, item 2, “end → response”): first a list item `- Result: <the machine response type>`, then (through an empty line) the table

```
| end | № | when | response |
```

- `when` is the entry condition: `true`, `stop_reason == "…"`, `stop_reason in {…}`; the rows of one end are mutually exclusive and cover the set over which they branch (except `Except`); an uncovered value is a table check error.
- `response` is `Response(<a value of the result type>)` or `Refusal(<FailCode code>, <text>)`; the envelope of the response (request, party, trace, step) is assembled by the executor; the refusal code is taken from the constructor, there is no separate column.
- In the “response” are available data, `transition_note` (the fields `code`, `params`; the value is always there: ERROR is entered by `machine_error` or by an executor machine error, and both ways write a record, 3.3, А4, ША8) and catalog functions; the text of the whole record is `record_text(transition_note)` (E8).

Example (the “Agent step” pilot). Changed: the conditional action and the event value close what the pilot could not write (in the code `Time.now()` is read inside a branch, here — before it; a time read leaves no trace). The `Reads` of ERROR is `all_data`: `usage`, `agent_request` and the other names in its “On entry” are read from `all_data` as data (ШМ3).

```
### Halted — end
- Reads: usage, agent_request, stop_reason, transport_usage, started
- On entry:
  - let current_time = call(time_now);
  - call(close_agent_turn);
  - if not has(usage) then (journal(usage_event(collect_usage(agent_request, stop_reason, transport_usage, started, current_time))));
  - journal(agent_step_stopped, reason: stop_reason)
- Except: stop_reason in {""}

### Errored — end
- Reads: all_data
- On entry:
  - let current_time = call(time_now);
  - call(close_agent_turn);
  - if not has(usage) then (journal(usage_event(collect_usage(agent_request, stop_reason, transport_usage, started, current_time))));
  - journal(transition_note);
  - journal(all_data)

## Ends

- Result: AgentReply

| end | № | when | response |
| End | 1 | true | Response(AgentReply { text: reply_text, artifact: reply_artifact, usage: require(usage), request_started: if has(transport_usage) then require(transport_usage).request_started else none }) |
| Errored | 1 | true | Refusal(FailCode.NoResult, "agent step defect: " + transition_note.code) |
| Halted | 1 | stop_reason == "no_result" | Refusal(FailCode.NoResult, stop_reason) |
| Halted | 2 | stop_reason == "model_refused" | Refusal(FailCode.ModelRefused, stop_reason) |
| Halted | 7 | stop_reason == "cost_limit" | Refusal(FailCode.MaxTokens, stop_reason) |
| Halted | 10 | stop_reason == "pause_halt" | Refusal(FailCode.StoppedByHuman, stop_reason) |
| Halted | 11 | stop_reason == "cancel_request" | Refusal(FailCode.Cancelled, stop_reason) |
```

Example (the “Meeting” pilot; E2, E8). Changed: `journal_findings`, `journal_decision` and `journal_machine_data` of the code are ordinary journal rows (the codes `unclosed_finding`, `meeting_decision`, `open_finding`, `machine_data`, [state-machine-journal.md](state-machine-journal.md), section 2, subsection “Events of the table format”); severity is a value of the enumeration `Severity` (`"critical"`, `"significant"`, `"desirable"`), yes/no is `yes_no_word` (a definition: `if b then "yes" else "no"`).

```
### Halted — end
- Reads: stop_reason, open, gate3_findings
- On entry:
  - call(open_for_writing, "proposal");
  - journal(meeting_stopped, reason: stop_reason);
  - for each f in open: journal(unclosed_finding, severity: text(f.severity), evidence: f.evidence, repeat: yes_no_word(f.repeat), question: yes_no_word(f.question));
  - for each f in not_included_in(gate3_findings, open): journal(unclosed_finding, severity: text(f.severity), evidence: f.evidence, repeat: yes_no_word(f.repeat), question: yes_no_word(f.question))
- Except: stop_reason in {""}

### End — end
- Reads: proposal, confirmation, number, open
- On entry:
  - call(open_for_writing, "proposal");
  - journal(meeting_decision, decision: proposal, source: confirmation, passes: text(number));
  - for each f in open: journal(open_finding, severity: text(f.severity), evidence: f.evidence, repeat: yes_no_word(f.repeat), question: yes_no_word(f.question));
  - journal(older_findings_in_pass_files)

### Errored — end
- Reads: all_data
- On entry:
  - call(open_for_writing, "proposal");
  - journal(transition_note);
  - journal(all_data)

## Ends

- Result: MeetingResult

| end | № | when | response |
| End | 1 | true | Response(MeetingResult { decision: proposal, source: confirmation, passes: number, open: open }) |
| Errored | 1 | true | Refusal(FailCode.NoResult, record_text(transition_note)) |
```

(Not all rows of Halted are shown in the “Ends” table: “Agent step” has 11 of them ([archive/state-machine-agent-step-states.md](archive/state-machine-agent-step-states.md), “end → response”; the example shows №№ 1, 2, 7, 10, 11), “Meeting” has 10, by the number of values of `stop_reason` without `""`. For “Meeting” four rows `stop_reason == "Witness_halt_meeting"` … `"AuthorQuestion_halt_meeting"` lead to `Refusal(FailCode.StoppedByHuman, stop_reason)`, the values are computed by FailedRequest #2, section 3.2.)

## 5. Actions

The words of actions (`journal`, `machine_error`, `call`, `pass`, `cancel_open`, `for each`) are quoted in the English form; the Russian form is in the [word table](portolan-keywords.tsv), the kind `action` (1a).

A list through `;` in the order of writing (rule 29); **every action sees the results of the previous ones** (after `retry_count += 1` the journal reads the new value). The `call` actions of irreversible primitives are written in order but executed as the last stage of the commit, after saving (rule 13); their arguments are evaluated at the point of writing.

| Action | Meaning | Where |
|---|---|---|
| `field = expr`; `field += expr` | assignment; addition (int, float, text, list) | rows, “On accept” |
| `field[key] = expr` | map: insertion or replacement; list: an existing index, otherwise a machine error | rows, “On accept” |
| `field[key].field = expr` | a short record of `field[key] = { ...field[key], field: expr }` (С11); no key — a machine error, the record is not created; a field with `writes: mechanics` — a check error. Where the source calls an absent key a program defect (`unreachable`, `required`), `field[key] = { ...require(field[key]), field: expr }` is written (4.4, Н-11) | rows, “On accept” |
| `field = without_key(field, key)`; `field = remove(field, element)` | removing a key and elements | rows, “On accept” |
| `journal(code, name: expr, …)` | a journal event: `code` is a Latin one from the template table, the parameter values are `text` | rows, “On entry” of an end, the body of `for each` in the “On entry” of an end |
| `journal(value)` | an event assembled by `journal_event(…)` or `transition_note` | rows, “On entry” of an end |
| `journal(all_data)` | an abbreviation of `journal(machine_data, data: <data record>)`: the event `machine_data` with **one** parameter `data`; the encoding is below (И-2); the composition is in section 2. The name `all_data` in an expression is a record value (3.1) | “On entry” of ERROR |
| `let name = expr` | a binding until the end of “On entry” and for all rows of the state; also `let name = call(…)` | “On entry”, “On accept” |
| `let name = expr in actions` | a local binding | everywhere |
| `if expr then (actions) [else (actions)]` | conditional; the condition is an expression without `call` (catalog functions are allowed, ША5) | rows, “On accept”, “On entry” of an end |
| `for each name in expr: actions` | a finite list or range; the body — assignments, `+=` and the short record (in rows, “On accept”); `journal(…)` and `if` (in the “On entry” of an end); **the boundary of the body** (Я-24): the body is one action, up to the nearest `;` of the list, or a list of actions in parentheses `for each x in xs: (a; b)`, as with `if`; an action after `;` outside the parentheses does not enter the body | rows, “On accept”, “On entry” of an end |
| `call(primitive, arg, …)` | a writing and irreversible primitive without a result (admissibility by class — section 7) | by class |
| `machine_error(code, name: expr, …)` | the journal `code` and the end ERROR; “To” is `—`; the only entry into ERROR by the will of the table (the second is an executor machine error, 3.3); after both `transition_note` is defined (А4, ША8) | rows, common events |
| `pass(nested, signal)` | the signal `Signal` to the machines `nested` (a fragment parameter, section 9) from `open_requests` at the moment of the action (the addressees are taken at the point of writing, before the `cancel_open` of the same row), sent after the commit; the journal `signal_passed` for each (T4) | fragment only |
| `cancel_open[(except: nested)]` | cancel the open requests without an accepted response (rule 18): with `except: nested` — except the requests to the named nested machines, without an argument — all, including the nested ones; the effect is by the parameter `request_cancel` (section 9); returning the parties of the cancelled requests of a set to `to_send` is rule 18, for any value of the parameter; it is disabled only by `without_return_to_send`, and only in COMMON 1, 2 (Н-2); the change of `open_requests` and `to_send` is contract mechanics (rule 29), the check “writes ⊆ `writes`” does not count it as a row write | fragment only |

**Product journal codes** (Я-31). The code in `journal(code, …)` and `machine_error(code, …)` is taken from the template table of the [journal](state-machine-journal.md) (section 2 and the subsection “Events of the table format”) — these are the methodology codes. A product that needs its own events (a record of executor mechanics: an edit of a response under “Edits”, a form return, a request repetition, an order of a signal — for example `answer_edited`, `form_returned`, `request_repeated`, `signal_ordered`) declares them by a **product template table** of the same form (`Machine | Event code | Russian template | Parameters`) next to the methodology table; where it lies is named by the host registry (as the definitions files, section 8). Rules: a product code is a Latin `snake_case` by the rules of a journal code; it does not repeat a methodology code (a coincidence is a check error, even with the same template); a code that the format itself or the contract mechanics writes (`signal_passed` of `pass`, `input_rejected`, `machine_error`, `machine_data`, the codes of the “Pause” fragment) is not replaced by the product with its own code: its own event (for example, `signal_ordered` when a signal is ordered before the commit) is written next to the methodology code, not instead of it. The check (section 10) compares the code and the parameters of a row with the union of the two tables; a code outside the union is an error. The methodology script [check-tables.py](check-tables.py) reads only the methodology table; the product table is read by the product check. Product codes are not entered into the methodology table.

**Encoding of `journal(all_data)`** (И-2; ША1; checked by an implementation). The event `machine_data` with **one** parameter `data`. The parameter value is pairs `name=value` (the name is the JSON name of the datum, 1a), the separator is `; ` (a semicolon and a space); the order is the order of the rows of the “Data” table of the machine (first the data of the included fragments in the order of inclusion, then the data of the machine); field paths inside a map (`name[*].field`) are not in the composition — they are part of the map value. The value of a pair:

| Value | Record |
|---|---|
| integer | decimal record |
| float | `text(x)` (the shortest reversible record, an integral one with `.0`; 3.3) |
| text, literal set, `id` | as is, without quotes; empty text is empty after `=` (`stop=`) |
| `bool` | `yes`, `no` |
| optional `none` | `none` |
| enumeration | the value of the element (the Latin text of the code); for an element without a value — its JSON name (Я-15, Я-46) |
| `State` | the JSON name of the state |
| list | a JSON array `[…]`; empty is `[]` |
| map | a JSON object `{…}`; empty is `{}`; for a map with non-text keys — an array of pairs `[[key,value],…]` in the order of the first write of the key |
| record | a JSON object; the keys are the JSON names of the fields, the order is the order of the type's fields |
| variant | with fields — `{"Var":{fields}}`; without fields — the string `"Var"` (JSON names) |
| tuple | an array; positions in order |

Composite values are encoded in JSON without loss: without spaces (the separators `,` and `:`), UTF-8, non-ASCII signs are not escaped, text escaping is by RFC 8259 (`\"`, `\\`, `\b`, `\f`, `\n`, `\r`, `\t`, other control signs — `\u00xx` in lowercase); inside a composite, text is a JSON string, `none` is `null`, `bool` is `true`, `false`, float is a number by `text(x)`, an enumeration and `State` are a string by the table rows. Encoding and parsing back and forth are without loss: Cyrillic and 4-byte letters are preserved, integer and float are distinguished (`1` and `1.0`).

Examples (`data=` is the name of the event parameter): `data=count=0; label=abc; began=1000; log=[]; table={}; stop=` and `data=total=99; label=; log=[]; counts={}; items={}; p_attempt=0`; the map `lenses map[text, Lens]` (the fields of `Lens` with the JSON names `id`, `lost`, `probes`, `attempt`) — `lenses={"l1":{"id":"l1","lost":0,"probes":0,"attempt":2}}`; `turn_before_retry=none` — an empty optional.

## 6. JSON tree

**The file name of the tree** (Я-19). A tree compiled from `<name>.portolan.md` lies next to it in `<name>.portolan.json` (`agent_step.portolan.md` ↔ `agent_step.portolan.json`). JSON is the executable form of the language itself, not another format: a hand-written tree is also Portolan in the JSON form; the key `format: "machine/2"` inside the tree does not change. The former name `*.machine.json` is not used and loading does not accept it (Я-22). The rules by which a tree is written back to a Portolan file are in section 1b.

The JSON tree and its schema are outside this file: the schema version is kept by the product, the keys in it are English. The tree is the same for a Russian and an English file: the words of both languages correspond to one key and one value (the word table, 1a); the party kind “human or agent by setting” is called `gatekeeper` in the tree (section 1). Listed here are the constructs of versions 2, 2.1, 2.2 and 2.5 (versions 2.8–2.13 have no new nodes: the tree does not depend on the file language, 1a; version 2.7 has one new key — `words`, in version 2.13 it is called `values`, below; versions 2.3, 2.4 and 2.6 have no new machine nodes: the result by role is a record of the host registry; version 2.5's new nodes are the literal set and the type `id`) that need nodes (some of them had no nodes in version 1): `in` of `failure`, “when” and “Except” of ends, “On entry” of a fork, an operation and an end, the alternatives `|` in `match`, the literal sets `"a" | "b"` (in the schema — a list of strings, `enum`), the type `id` (a string of UUID format: `^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$`), `int>=n`, `?`, a tuple, a full map, `non_decreasing, <= expr`, `writes` (five values), the field path `name[*].field` in the “Data” and the short record `name[key].field = expr`, `unreachable`, grouping parentheses, a call with named arguments, a party identifier, `parse` of a party `machine`, `Edits` with `check`, `Initial state`, `for each` with `journal` at the end, an include with parameters, `signal(…)` with fields (a party signal and a machine signal), a field binding with renaming, “On accept”, `let` in “On entry”, a conditional action, `journal_event`, `journal(value)`, a set of parties, a party `machine`, the `## Input` of a machine with invariants, the values of enumerations; from version 2.2 — `result` of a party and `GateOutcome`, the column `counter`, the role literal of `parse`, the qualified `response: Type.Variant`, `cancel_open` without an argument, `non_empty`, the header of a definitions file. **Enumeration values** (П-7, Я-41). For an enumeration with values (section 2) the enumeration node carries the key `values` (before version 2.13 — `words`) — a list of pairs “JSON name of the element → value” in the order of declaration (`[["NoResult", "no_result"], …]`); an enumeration without values has no such key. The encoding of `all_data` (section 5) and `text(x)` take the value from `values`; an element without a value gives its JSON name (Я-15). **Names in the tree** are JSON names (1a, Я-46); the `Request` table of an appeal is the key `inputs`, the `Reads` line is the key `reads` (Я-39). The include of a definitions file is `includes: [{ "name", "version", "hash" }]` and a copy of its types, constants and definitions in the machine tree: the interpreter needs only one tree (С30).

## 7. Primitive registry and admissibility of classes

A registry entry: `name`, `parameters` with types, `result`, `class`, `reads`, `writes`, a note. The JSON name of a primitive is the name in the host registry; a non-Latin name in a file carries it in parentheses (`профиль_стороны (party_profile)`; 1a, Я-46). Pure functions over data are written not here but in “Definitions”; text parsing, reading objects, time, closing a turn, effects remain primitives.

| Class | What it does | The call `call(name, …)` is allowed |
|---|---|---|
| `pure` | a pure host function | as a function `name(arg)` everywhere |
| `reading` | reads an object, a store, time; does not change machine data | in the “Request” of an appeal, in `profile`, in `let` of “On entry” (operations, forks, ends) and “On accept” (in any position of an expression, 3.1), as `parse` of a party `machine` and `check` of the property “Edits” (4.2); not in conditions and not in row actions; `new_id` — only in `let` of the “On entry” of an operation (below) |
| `writing` | writes inside the commit (machine data, objects, a buffer) | in the “On entry” of an operation and an end (including `let name = call(…)`) and in row actions; not in conditions, not in the “Request”, not in the “On entry” of a fork |
| `irreversible` | an external action that cannot be rolled back; the last stage of the commit, repeatable without harm (rule 13) | where `writing` is |

- `reads:` — machine data, objects, service records that the primitive reads hidden (not through arguments). These names enter the reads of the state (`Request`, `Reads`) at the point of the call (rule 11).
- `writes:` for `writing` — the machine data that the primitive changes in place; the check “writes ⊆ data” counts it. For `reading` — only service records of the executor (not machine data, not objects); the record names who reads it (the primitive or the turn mechanics) so that the dependence is visible (for example, the remarks of the form check for the turn “fix”).

Example of a registry (pilots). Changed: for `reply_validation` the hidden reads and the write are named; for `remove_unsound` — the reads and the written data; the rows after `proposal_changed_since_attempt` — `parse` with a result by role (Н-12), functions without a body of different classes, including the pure `not_included_in` and `merge_unique` (Н-4) and `build_summary` (Н-7) (see below); `proposal_fingerprint` and `proposal_changed_since_attempt` — primitives for a nested read and for `Edits` (4.2, 4.6). The journal primitives `journal_findings`, `journal_decision` are not in the registry: these are journal rows (4.7).

```
| name | parameters | result | class | reads | writes |
| time_now | — | int | reading | — | — |
| new_id | — | id | reading | — | — |
| reply_validation | — | ReplyCheck | reading | reply_text, reply_artifact, agent_request; objects: session files | service record “form remarks” (read by the turn “fix”) |
| close_agent_turn | — | — | irreversible | — | — |
| remove_unsound | number int>=1 | — | writing | lens_order, lens_findings, witness_answers | lens_findings |
| proposal_fingerprint | — | text | reading | objects: proposal (not read — `unreachable`) | — |
| proposal_changed_since_attempt | — | bool | reading | objects: proposal; service record: fingerprints of the attempt (written by the executor when the request is sent) | — |
| parse_agent_reply | result AgentReply; role text | by role { "witness": []WitnessAnswer, "author": EditResult, "lens": LensResult } | reading | objects: reply artifact; for the role "witness" also the proposal | service record: remarks of the excerpt comparison (only the role "witness"; read by the party return) |
| lenses_without_critical | — | []text | reading | lens_order, lens_findings, number | — |
| not_included_in | findings []Finding; among []Finding | []Finding | pure | — | — |
| merge_unique | first_list []Finding; second_list []Finding | []Finding | pure | — | — |
| all_lens_findings | number int>=0 | []Finding | reading | lens_order, lens_findings | — |
| build_summary | number int>=1 | ?Summary | reading | lens_order, lens_findings, lenses | — |
```

**`new_id`** (Т-2; a built-in host primitive, like `time_now`; the Latin name in the host registry and in JSON is `new_id`, a word of the word table, the kind `catalog`; the host implements it through `Uuid.v7()` with the time and randomness effects — this is a host detail). Without parameters, the result is `id` (section 2), class `reading`, `reads` and `writes` are `—`; the result is non-deterministic: the value is issued by the executor. The non-determinism is removed in the same way as for time (Start, section 4.5): the value enters a `let` binding and is fixed in the `immediate` event of the step; when a step is repeated (rules 12–13) it is taken from the saved event, not issued again. Therefore `call(new_id)` is allowed **only** in `let` of the “On entry” of an operation with the binding written into data by the row `immediate`. A conservative decision: in the “Request” of an appeal it is not allowed even with `reads: executor` — the “Request” is evaluated again on re-entry and a new request (4.2, rule 12), and the value would change; in a fork, an end, conditions, actions, `profile` — also not (section 10).

Example (an illustration; the datum `session_id` is `?id`, initial `none`; a state not from a pilot).

```
### Opening — operation
- On entry: let fresh_id = call(new_id)

| 1 | immediate | — | session_id = fresh_id | AgentTurn |
```

**Result by role** (Н-12). A result that depends on the role literal of `parse` is written in the registry by the record `by role { "<role>": Type, … }` — a closed table “role → type” in the registry itself, the primitive has no other results. The check (section 10) takes the role literal from the `parse` of the party, looks it up in the registry table and compares the found type with the type after `->` of `parse`: a literal absent from the table or different types are a check error; the first parameter of the primitive (`result AgentReply`) must coincide with the `result` type of the party. The record `by role` stands only in the `result` column of the registry and nowhere else serves as a type.

**The meaning of the table “by role”** (Я-33). The type is chosen at the check, not at execution: for a party with `parse` the role literal is constant, therefore the response value of this party has one type — the type of its table row; the events `response: Variant` and “On accept” of the party are checked by it. At execution the executor calls the primitive with the role literal as the second argument and gets a value of this type or a refusal (a parse failure, section 1). The table is a record of the host registry: it does not enter the machine tree (section 6), the tree carries at the party the role literal and the type after `->`. The `reads` of a primitive may differ by role (in `parse_agent_reply` the role `"witness"` also reads the proposal): the reads of a state include the reads of the role with which the parse of its party is called.

The other primitives of the examples (`party_profile`, `role_context`, `close_for_writing`) are written in the same way; the definitions `add_usage`, `collect_usage` are not spelled out in the examples, their records are in the excerpts of the pilots. The hidden reads of `remove_unsound` are `lens_order`, `lens_findings`, `witness_answers` (СВ6).

**A function without a body in the source** (ИС6, Н-3, Н-4; decision of the methodology, 2026-10-19): a function that has no body in the source (in the automaton code only a signature) is written as a **host primitive** with a class and a description by the tables of the primary source; it will become a definition in the language when the body appears in the source (then the record is moved to `## Definitions`). One rule for all such functions, pure or not; **the class is by the signature of the source**: a free function without `mut` and without `Objects` is `pure` (called as `name(arg)` everywhere); a method of machine data without `mut` or a function with `Objects` without `mut` is `reading` (reads data or objects, changes nothing); with `mut` — `writing` (writes data, objects or a buffer); `irreversible` is not derived from a signature, it is named by the body or a comment of the source. This includes all such functions of the automata that the tables of “Meeting” call: `pure` — `merge_unique`, `not_included_in`, `has_critical`, `desirable`, `desirable_and_significant`, `desirable_and_significant_repeated`, `critical_and_significant_not_repeated`; `reading` — `has_reviewer_questions`, `reviewer_questions`, `all_lens_findings`, `lenses_without_critical`, `build_summary` (the row of SummaryBuilding writes `summary[…]` by the result, the function itself does not change data), `proposal_changed_since_attempt`; `writing` — `remove_unsound` (writes `lens_findings`) and `count_in_model_tally` (the tables do not call it). The journal primitives without a body (`journal_findings`, `journal_decision`, `journal_machine_data`) are written by the format as journal rows (4.7). The pilot count counts such functions as written as primitives. Bodies are not entered into the automata by this.

## 8. Definitions, constants, parameters

`define name(arg type, …) -> type = expr` is a pure function; arity 0 is allowed; there is no recursion. A constant is a named value with a type. A parameter is a default value and a project override (`project.<key>`).

Example (pilots; changed: `usage_event` instead of the event function of the code, a tuple key instead of the pilot's record; `yes_no_word` — for the values of journal parameters, 4.7; `merge_unique` is removed: it has no body in the source, it is a host primitive, section 7, Н-4).

```
define sum_ints(a ?int, b ?int) -> ?int =
  if has(a) and has(b) then (a ?? 0) + (b ?? 0) else a ?? b

define yes_no_word(b bool) -> text =
  if b then "yes" else "no"

define usage_event(u Usage) -> JournalEvent =
  journal_event("agent_usage", session: u.session, result: u.result, model: u.model.id,
                input: text(u.tokens.input), output: text(u.tokens.output), reasoning: text(u.tokens.reasoning),
                cache_read: text(u.tokens.cache_read), cache_write: text(u.tokens.cache_write), cost: text(u.cost))
```

**Definitions files** (С30). Definitions common to several machines lie in an included file and are included by a line of the section `## Includes`:

```
definitions: <name> version <N> hash <hex12>
```

- **Registry** (СГ4, СЖ4). `<name>` is the name of the definitions file by the registry of included files (not a path). The registry is part of the host registry, the same one where the primitives (section 7) and the machines (rule 35, [call protocol](state-machine-call-protocol.md), section J, item 6) are written: an entry `name → file` (a path relative to the registry). The format of the registry file is set by the host; the table format requires one thing: exactly one file is found by name, otherwise it is a table check error.
- **The header of a definitions file:** `# Definitions: <name>`, list items `- definitions_version: <N>` (an integer), `- format: 2.13` and optionally `- language: ru`/`en` (1a). The `version` of the include line must match `definitions_version` exactly.
- **Sections** — `## Types`, `## Constants`, `## Definitions` in order, **all three are required**; an empty section is the line `—`. Only pure definitions, types and constants; without `## States`, without `call` of the classes reading, writing, irreversible, without `## Includes`: a definitions file does not include other files (there are no cycles by construction).
- **Hash** — the first 12 signs of the SHA-256 of the file content in UTF-8 after normalization (Н-8): a leading BOM is dropped (a file with and without a BOM give one hash); line breaks are LF (CRLF and a lone CR are replaced by LF); trailing spaces and tabs are removed from every line; at the end of the file there is exactly one LF (empty lines at the end are removed, a missing LF is added); the 12 signs of the hash are hexadecimal, in lowercase. The normalization is unambiguous: a file without a final LF and a file with it give one hash.
- Names from an included file are visible without a prefix; a coincidence with a local name or with a name of another included file is a table check error; a mismatch of the version or the hash is a table check error, not a warning.

Example (“Meeting”: the arithmetic of a cycle is common to the meeting and the cycle check). Changed: the pilot's `ceiling_reached` was a copy in the machine file, here it is from an included file; the header is supplemented with the line `format`, therefore the hash is not equal to the hash of the pilot's file (that has no `format`). The hash below is the SHA-256 of the given file (12 signs); it differs from the hash of the Russian sample (`f2075d080095`) because this file is in the English form and contains the line `- language: en`. The method was verified: for the Russian file with `format: 2.9` it gives the earlier `d2db7f5322a9`, and for the English one with `format: 2.9` the earlier `f99d947d3040`, with `format: 2.11` the earlier `afe05e9a1e4d`, with `format: 2.12` the earlier `eee8c3a13a08`; at the move 2.12 → 2.13 the hash was recomputed.

```
# Definitions: cycle_arithmetic

- definitions_version: 1
- format: 2.13
- language: en

## Types
—

## Constants
—

## Definitions

define ceiling_reached(pass_number int>=1, origin int>=1, limit int>=0) -> bool =
  (pass_number - 1) - origin + 1 >= limit
```

```
## Includes
definitions: cycle_arithmetic version 1 hash d90613513d2a
```

## 9. Included fragments

A fragment (rule 36) is a file of the format `fragment`: the header `# Fragment: <Name>`, list items `- fragment: <latin_name>`, `- format: 2.13` (optionally `- language: ru`/`en`, 1a) and sections in order: `## Parameters`, `## Requires`, `## Data`, `## Common events`, `## States`. In the text a parameter stands as `<parameter>` and is substituted before the check (rule 34).

**Parameters** — `name`, `kind`, allowed values. The kinds: `signal` (a party signal, Я-38), `text`, `[]machine` (names of nested machines), `behavior` (a closed list of fragment words; the meaning is the executor's description in the fragment text), `note` (text for the reader). An include names all parameters; an omitted one is an error.

**Requires** — what the fragment requires from the machine: the values of `stop_reason`, the rows of “Ends”, the ends Halted and Errored, the party `enhanced` of kind `enhanced` in “Parties” with the signals `continue(human_word text, author text, source text)` and `<halt_signal>` (Pause addresses it); the value `previous` is always an appeal: the machine stands only in appeals and ends, and in the ends and in Pause the COMMON 1 and 2 are dropped by a condition (rule 24; ШМ2).

**Names of the fragment:** `state` (the current state, type `State`), `previous` (`?State`), `call_request_id` (text; the identifier of the request by which the machine was started is given by the executor), `event.id`, `end(state)` (catalog), `nested`. `state` is an executor name (type `State`); `previous` (`?State`) and `call_request_id` (text; the identifier of the request by which the machine was started, the value is set by the executor at the start) are **data of the fragment** (the “Data” table below), not executor names (T6). The common events read the data of the fragment, `state` and `event.…` without a reads line; the states of the fragment — only their own reads (`Request`, `Reads`).

**Values of parameters of the kind `behavior`** (А5, E10) are closed lists of words; a value outside the list is a check error. The effect is named formally and applied where indicated; `write_right` is a note for the reader, the executor does not evaluate it.

| Parameter | Word | Effect | Where it acts |
|---|---|---|---|
| `request_cancel` | `mechanics` | cancelling the open requests without an accepted response — only contract mechanics (requests to a human are closed); the parties of the cancelled requests of a set are returned to `to_send` (rule 18) | `cancel_open`: COMMON 1, 2 — except `nested`; COMMON 5 — all open ones, including the nested ones (the signal “cancel” went to them a row earlier), as the engine code and the fragment text (ША6) |
| `request_cancel` | `without_return_to_send` | as `mechanics`, but the parties of the cancelled requests of a set are not returned to `to_send` (the fragment text: “by the pause”); in “Meeting” the Lenses requests are nested, COMMON 1, 2 do not cancel them, there is nothing to return | only COMMON 1, 2 (the pause); in COMMON 5 the parameter does not act: the parties of the set are returned to `to_send` by rule 18, like `cancel_open_without_accepted(false)` of the engine (Н-2) |
| `request_cancel` | `stop_transport_turn` | as `mechanics`; besides that, the turn at the agent transport is stopped; closing the held turn is not an effect of the parameter: it is done by `call(close_agent_turn)` in the ends of the machine (ША7) | `cancel_open`: COMMON 1, 2, 5, as for `mechanics` |
| `reentry` | `nothing` | re-entry into the saved state — only by rule 12 (a new request if there is no accepted one for it) | `To: previous` (Pause 1, 3) |
| `reentry` | `requests_from_to_send` | after re-entry into the appeal of a set, the requests go to the parties listed in `to_send` | the same |

An include in a machine (the section `## Includes`): `Pause(halt_signal: halt, halt_code: "pause_halt", nested: [], request_cancel: stop_transport_turn, reentry: nothing, write_right: "files that the agent edits; the pause does not touch their rights")` — “Agent step”; “Meeting” — `halt_signal: halt meeting`, `halt_code: "pause_halt_meeting"`, `nested: [agent_step]`, `request_cancel: without_return_to_send`, `reentry: requests_from_to_send`. The states, events and data of the fragment enter the machine and are not repeated in its sections (П-2): in `## Includes` there is **only** the include line; in `## States` writing the heading of a fragment state (`### Pause — appeal (Pause)`) is forbidden — a repeat of a state that the include brought is a check error (“declared twice”). There is no reference section with a fragment expansion (Я-44): what a fragment brings (parameters, obligations, data, events, states) is described by its file (for “Pause” — the definition below); in the section `## States` of a machine a paragraph-reference (prose, 4.1) stands if needed.

The definition of the “Pause” fragment in the format. Composed from the fragment expansion in the “Meeting” pilot and the text of [state-machine-pause-states.md](state-machine-pause-states.md); the fragment file itself in the format was not checked by a pilot, its comparison with the text of rules 23, 24, 35 is by rows. There is no fragment file in Portolan (`*.portolan.md` with the header `# Fragment: Pause`) (Я-35): the definition below is a sample, the include `Pause(…)` is not resolved by the methodology scripts (section 14). Changed against the pilot: `halt_signal` and `halt_code` are parameters; the events from a parent are `signal(…)`; the values of `stop_reason` are `<halt_code>`; `pass(nested, …)`; COMMON 6 is `machine_error`; in the “Request” of Pause `require(previous)` (the field is visible only to the party, the rows of Pause read the datum `previous`, 4.2); COMMON 5 is `cancel_open` without an exception, as the code and the fragment text (ША6); returning the parties of a set to `to_send` in COMMON 5 is rule 18, for any value of `request_cancel` (Н-2); `open_requests` is data of the fragment, `human_words` is not entered into the table (section 2).

```
## Parameters
| name | kind | allowed_values |
| halt_signal | signal | party signal of the party “enhanced” |
| halt_code | text | a value of the machine's set `stop_reason` |
| nested | []machine | machines to which the chain signals go (rule 35, item 8) |
| request_cancel | behavior | `mechanics`, `without_return_to_send`, `stop_transport_turn` (the effects — the table above) |
| reentry | behavior | `nothing`, `requests_from_to_send` (the effects — the table above) |
| write_right | note | text |

## Requires
stop_reason contains <halt_code> and "cancel_request"; in “Ends” — rows for both values (the codes StoppedByHuman and Cancelled); the ends Halted and Errored.

## Data
| name | type | initial | non_decreasing | writes |
| previous | ?State | none | — | fragment |
| call_request_id | text | "" | — | mechanics |
| open_requests | []text | [] | — | mechanics |

## Common events     // parsed before the state rows (rule 23)
| № | Event | Condition | Actions | To |
| 1 | signal(human_stop(human_word, author, source)) | not end(state) and state != Pause | journal(human_stop, author: author, source: source, event: event.id); previous = state; pass(nested, stop); cancel_open(except: nested) | Pause |
| 2 | signal(parent_stop(id)) | not end(state) and state != Pause and id == call_request_id | journal(pause_by_parent_stop, request: id, event: event.id); previous = state; pass(nested, stop); cancel_open(except: nested) | Pause |
| 3 | signal(request_cancelled(id)) | id != call_request_id | journal(cancel_discarded_foreign_request, request: id, event: event.id) | same |
| 4 | signal(request_cancelled(id)) | id == call_request_id and end(state) | journal(cancel_discarded_already_replied, request: id, event: event.id) | same |
| 5 | signal(request_cancelled(id)) | id == call_request_id and not end(state) | journal(request_cancelled, request: id, event: event.id); stop_reason = "cancel_request"; pass(nested, cancel); cancel_open | Halted |
| 6 | signal(request_cancelled(id)) | else | machine_error("cancel_parse_no_match") | — |

## States
### Pause — appeal
- Party: enhanced
- Request:

| request_field | expression | reads |
| previous | require(previous) | party |
| call_request_id | call_request_id | party |

| № | Event | Condition | Actions | To |
| 1 | signal(continue(author, source)) | — | journal(human_continue, previous: text(require(previous)), author: author, source: source, event: event.id); pass(nested, continue) | previous |
| 2 | signal(<halt_signal>) | — | stop_reason = <halt_code>; pass(nested, halt) | Halted |
| 3 | signal(continue_from_parent(id)) | id == call_request_id | journal(parent_continue, previous: text(require(previous)), request: id, event: event.id); pass(nested, continue) | previous |
| 4 | signal(halt_from_parent(id)) | id == call_request_id | stop_reason = <halt_code>; pass(nested, halt) | Halted |
```

- The signals “continue” and “halt” (and those from a parent) outside Pause are superfluous signals: the executor drops them with a journal entry (rule 17).
- `To: previous` leads by re-entry into the saved state (rule 12; the parameter `reentry`); `previous` is not written in this (rules 13, 24).
- JSON names of the fragment (1a, Я-46): the data of the fragment (`previous`, `call_request_id`, `open_requests`) are readable names of the word table; the machine signals (`human_stop`, `parent_stop`, `request_cancelled`, `continue_from_parent`, `halt_from_parent`), their fields and the parameters of the fragment will be declared in parentheses by the fragment file (Я-35); while there is none, their JSON names are an open item (section 14).
- The bindings of the fragment rows (`human_word`, `author`, `source`, `id`) are internal names (1a, Я-46): their Russian names are set by the Russian fragment file, they are not in the word table. After substitution they are bindings of the machine rows: a machine datum with such a name is a check error (4.3, Я-26).
- The words of a human (`human_words`) are a store of rule 31, written by the contract mechanics (rule 19); it is not entered into the “Data” table (section 2) and is not included in `all_data`; it is not in the rows. `open_requests` is entered by the fragment (it is read by `pass` and `cancel_open`); the machine does not repeat the row (section 2, ША1).

## 10. Table checks

The word table and the language (Я-1…Я-3): the `ru` and `en` words of the table [portolan-keywords.tsv](portolan-keywords.tsv) are unique within a kind; the `language` line ∈ {`ru`, `en`}; the header language matches the declared one; a keyword not of the file language is an error with the line number of the first foreign word (1a); the script [check-portolan-keywords.py](check-portolan-keywords.py) checks the table (the kinds of words, including `operator`), compares the sample machines with it and checks in them the operator signs (ASCII only, Я-42) and the JSON names (Я-46).

The extension of [check-tables.py](check-tables.py): names of fields, types and states; expression reads ⊆ the reads of the state (`Request`, `Reads`) by rule 11 (by both values of `reads`, by the `reads` lists of primitives, for ERROR — `all_data`), writes ⊆ data (including the `writes` of writing primitives); the bounds `int>=n`, `non_decreasing` and `<=`; reachability of states; completeness of forks (a default, an `else` row is allowed); exhaustion of the “Ends” taking `Except` into account; the values of `To`; appeal events ⊆ machine events; party signals (Я-38): the signal of an event of an appeal row ∈ the list of signals of the appeal's party, every signal of a party is used (a signal with no row in the current state is an open item, section 14); `failure(reason in …)` ⊆ `FailCode`; the primitive class is allowed in the call position; literal sets (the inclusion of the computed set, a value outside the set is an error, `match` over a set is exhausted, 3.2); a literal of the type `id` is of UUID format; `call(new_id)` only in `let` of the “On entry” of an operation, and the binding is written by the row `immediate` (section 7); an event field binding does not coincide with data (together with the data of fragments, after substitution, Я-26); for an appeal without a `Request` line the rows, “On accept” and “Idle term” read no data (Я-23, Я-40); a full map; the types `T`/`?T`; the journal: code ↔ the methodology template table or the product table, a product code does not repeat a methodology code (section 5, Я-31), parameter names ↔ template (`fork`), the values are `text`; enumeration values are `[a-z][a-z0-9_]*` (Я-41); JSON names (1a, Я-46): a non-Latin name that leaves the machine has a Latin JSON name in parentheses, internal and readable names need no parentheses; the parameters of an included fragment are named and fit by kind; the `stop_reason` values of a fragment ∈ the machine's set and in the “Ends”; no executor and envelope data in the reads of conditions (rule 31); `Initial state` is named; party identifiers are Latin and distinct; the JSON names of states are Latin and distinct; `Idle term` reads only the names of `Request`; `parse` is a reading primitive with a parameter of the type `result` and a result of the named type (for a result `by role {…}` — of the registry type for the role literal, section 7, Н-12), `response: Variant` — only for a variant; `Edits`: the primitive is reading without parameters, the result `bool`, the datum is written in the “On accept” of the state; a write by the path `name[*].field` is compared with the marks `writes` and `non_decreasing` by the template `[*]`, a write into a field with `writes: mechanics` from a row is an error; the value of a `behavior` parameter ∈ the list; the line `definitions:`: the name is found in the registry in exactly one file, the version and the hash (by the normalization of section 8) match the file, the names do not repeat, there is no `call`, `## States`, `## Includes` in the file, the three sections are in place; “Parties”: the column `counter` is named for every party, the datum is `int>=0`, `non_decreasing: yes`, `writes: mechanics`; `result` is named for every party, the variant of the event `response` belongs to the `result` type of the party (the result of `parse`), the signal of the event `signal` of a party belongs to its column “signals” (Я-38); `open_requests` is declared once; a `failure` outside the state's list is brought to `NoResult` (4.3); `non_empty`: the argument is a set with `""`; the codes of the journal of the table format are in the template table (the subsection “Events of the table format” of the journal file).

- **Formatting** (С-1): a state key line (4.1) without the marker `- ` is allowed in parsing (the record of version 2.5), but the formatting check warns — this is a warning, not a table error; a table standing right next to a list item or to another table (without an empty line) also warns. Prose (П-1): a paragraph line that begins with a word from the list of keys (4.1) without the marker `- ` or with a typo in it (`-Party:`, `– Reads:`) is a warning, otherwise the typo would remain a silent comment. The other prose causes no checks. A paragraph (Я-12): a text line pressed against a table, a heading or a list without an empty line is a warning. A declaration (`type`, `enum`, `variant`, `define`) outside a code block is a warning (Я-13). The file extension is checked only by this script (Я-18).
- **Includes and fragments** (П-2): in `## Includes` — only include lines (prose, a list are a check error); a fragment state declared by a heading in the section `## States` of a machine is a “declared twice” error.

**Release for the interpreter** (И-3). `unreachable` and `require(none)` are a program defect: the process is stopped by the executor (not the table); the machine state is not rolled back; the call response is an end with `NoResult`; the journal of the defect is at the executor's discretion. This is not a machine error (3.3): a defect does not lead to ERROR. A call refusal on a wrong input is a separate case: the event `input_rejected` (section 1, И-1).

## 11. Scenarios

A scenario is events and an expectation: an event (`start` with input, `response`, `failure`, `signal` of a party or of the machine with data, a term) → the state, the structured journal (code and parameters, rule 31), a subset of data, the queue. The comparison is by these four; the runner is in the product; the same scenario is run on the methodology automaton. The form of a scenario record is in general not set here (the runner format is in the product); the format fixes three things. **The file name** (Я-20): a scenario (`scenario/0`) is called `<name>.scenario.test.json`; the scenario format does not change. **Event data** (П-8): a signal (of a party or of the machine) with one data field carries the value of that field — text (for example, `continue` with the field `author` — the value `"ivan"`, not an object); with several fields — an object `{field: value}`; without fields — only the name. **Parameters** (П-9): a scenario may carry `params` — a “key → value” table with the keys `project.<key>` (section 1, “passing values from outside”); a parameter not named keeps its default value.

## 12. Catalog of built-in functions

The names of the catalog functions are quoted here in the English form (`has`, `require`, `non_empty`, `record_text`, `without_key`, `first_where`, `fold`, `new_id`, etc.); the Russian names are in the [word table](portolan-keywords.tsv), the kind `catalog` (1a).

All functions and macros are of the class `pure`: they are called wherever an expression is allowed; the exception is the built-in primitive `new_id` (the last row). The other host primitives are the registry of the machine (section 7), they are not in the catalog.

| Name | Signature | Class | Meaning |
|---|---|---|---|
| `has` | `(x ?T) -> bool` | pure | true if `x` is not `none` |
| `require` | `(x ?T) -> T` | pure | the value; with `none` — `unreachable` (3.3) |
| `non_empty` | `(x "" \| … ) -> the set of x without ""` | pure | a value different from `""`; on `""` — `unreachable`; the result set is the set of `x` without `""` (3.2) (СГ3) |
| `text` | `(x A) -> text` | pure | `A` is int, float, text, a literal set, `id`, an enumeration, `State` or `?A`; the format is in 3.3 |
| `record_text` | `(e JournalEvent) -> text` | pure | `событие <код>` (the Russian word “event” and the code) if there are no parameters, otherwise `событие <код>: имя=значение, …` (through commas, in the order of writing) — the same display of the code without a template as in the [journal](state-machine-journal.md), section 3 (E8, СГ10) |
| `float` | `(x int) -> float` | pure | |
| `int` | `(x float) -> int` | pure | the fractional part is dropped toward zero; out of range — a machine error |
| `length` | `(x text \| []T \| map[K, V]) -> int>=0` | pure | |
| `range` | `(a int, b int) -> []int` | pure | `[a, b)`, empty when `b <= a` |
| `max`, `min` | `(a T, b T) -> T`, `T` is int or float | pure | |
| `keys`, `values` | `(map[K, V]) -> []K`, `-> []V` | pure | the order is the order of the first write of the key; open, see section 14 |
| `without_key` | `(map[K, V], K) -> map[K, V]` | pure | no key — the same map |
| `remove` | `([]T, T) -> []T` | pure | removes all elements equal to the second argument |
| `journal_event` | `(code literal, name text, …) -> JournalEvent` | pure | an event value for `journal(value)` |
| `end` | `(s: State) -> bool` | pure | true for states of the kind “end”; needed by fragments |
| `filter` | `([]T, x -> bool) -> []T` | pure | a macro |
| `map` | `([]T, x -> U) -> []U` | pure | a macro |
| `any`, `all` | `([]T, x -> bool) -> bool` | pure | macros; on an empty list `false` and `true` |
| `count` | `([]T, x -> bool) -> int>=0` | pure | a macro |
| `first_where` | `([]T, x -> bool) -> ?T` | pure | a macro |
| `dict` | `([]T, x -> K, x -> V) -> map[K, V]` | pure | a macro: a map from a list; a repeated key is a machine error |
| `fold` | `([]T, A, (a, x) -> A) -> A` | pure | a macro; left to right |
| `new_id` | `() -> id` | reading | **not a pure function**: a built-in host primitive, non-deterministic; allowed only in `let` of the “On entry” of an operation, the value is fixed in the event `immediate` (section 7, Т-2) |

Actions are section 5; their class: `journal`, `machine_error`, assignments are writing (a write into data and the journal in one commit with the step); `pass`, `cancel_open` are writing (after the commit); `call` is by the class of the primitive.

## 13. Correspondence to the rules of the specification

| Rule | How it is expressed in the format |
|---|---|
| 11 | The reads of a state: the table `Request:` of an appeal and the line `Reads:` of the others (4.1, Я-39); no line — the state reads nothing (Я-40); the reads of expressions, conditions, actions, “On accept” and “Idle term” ⊆ the reads of the state (any value of `reads`, T9); the column `profile` of “Parties” is not limited by the rule (section 1); a reading primitive — by the `reads` list; the `Reads` of ERROR is `all_data` (the composition is in section 2); constants are not written in the reads; the envelope (rule 31) is not read, except in a request to a nested machine |
| 12 | Re-entry is executor mechanics; `, rerun` in “To”; the fragment parameter `reentry` |
| 13 | A step is one commit: the order of actions, the visibility of the results of the previous ones, `irreversible` last (section 5); `event.<field>` along the chain; the record “state” is implicit; the “On entry” of an operation is without data changes, they are in the row `immediate` |
| 14 | The block `On accept` (4.4); recording the accepted result is contract mechanics. The appeal property `Edits` with `check` (4.2, E3): the edit object changed since the beginning of the attempt — the result is not accepted, the request goes again; the order of acceptance is in 4.4 |
| 16 | `response`, `failure`, `failure(reason in {…})`; a code outside the state's list is brought by the executor to “no result” (the state's list is in 4.3); `unreachable` — only if “no result” is also outside the list; machine errors without `machine_error` — the event `machine_error` and ERROR (3.3) |
| 22 | Ends: `On entry` and the “Ends” table; entering an end cancels the open requests and gates — mechanics; open gates are shown again with the same identifier at a restart — mechanics; the remainder of a restart is executor mechanics |
| 24 | `To: previous`, `preparation_return`; `previous = state` is written only by the fragment; the restrictions of the value are the fragment's check |
| 29 | Actions are in the “Actions” of a row, “On accept”, “On entry” of an end; the journal is in the same places; the exceptions of mechanics are `writes: mechanics`, `rows_and_mechanics`; “On accept” is a part of the table (`writes: rows`, E5) |
| 31 | The envelope is written by the executor; a journal call does not repeat its fields; `event.id`; `trace` and `step` — only in a request to a nested machine; the type `id` does not change the envelope (section 2, Т-2) |
| 34 | The checks of section 10: (а) names — search over the file; (б) Latin — only journal codes, journal parameter names, JSON names (1a), party identifiers, enumeration values, text literals of closed sets (`"first"`, `"no_result"`; Latin in them is allowed but not required, Я-25), the names of registry primitives, constants (АМ5); (в) reads ⊆ the reads of the state (`Request`, `Reads`); (г) the type and `initial` of every datum, the initial state is named; (д) journal templates |
| 35 | The “Ends” table with `Result` — “end → response”; a nested machine is a party `machine`, the input and result types are named, the parse of the result is `parse` (section 1); `Refusal` with a code; `## Input` is the machine input |
| 19, 28 | Gate words — party signals, the column “signals” (Я-38); one row per signal; the words of a human are written by the mechanics; the open gates of a human and their identifier, the replacement of an accepted answer of the agent gatekeeper by the word of a human and the discarding of a word of a foreign party — mechanics; a wall has no record (section 14) |
| 15 | The column `counter` of “Parties”: a datum `int>=0`, `yes`, `mechanics`; the attempt number and the request identifier, at a gate of a human — the gate identifier of the same form (section 1); the format of the request identifier `<id>-<number>` does not change and it does not have the type `id` (section 2, Т-2) |
| 21 | `set:`; `to_send` — `rows_and_mechanics`, `open_requests` — `mechanics` (section 2); `Request limit` |
| 23, 36 | An include of a fragment (section 9); the order of parsing the common events is fixed, the parameters are named |
| 25 | The names of data, fields and parameters are Russian in a Russian file (in an English file — English), snake case; Latin — as in the line “34(б)”; a name and its JSON name in parentheses (1a) are one quantity |
| 27 | A fork: the default is `machine_error("fork_no_match", …)`; an explicit `else` row equals it, is written last and leads to `—` (4.1, АМ2) |
| 30 | `[]`, `""`, `0`, `none` — literals by type; the “no” of the specification is `none` of `?T`; `+` between lists is concatenation; `merge_unique` is a `pure` host primitive (section 7, Н-4) |
| 33 | The label `NAME #n` = the row number; the default label is the next number |

## 14. Open items

- **Equivalence by journal is confirmed partially.** Version 2.2 was implemented by an interpreter; equality with the automaton by journal is confirmed on 39 scenarios of one small machine (the chat machine); the expressibility of “Agent step” and “Meeting” was checked by pilots, running their scenarios on the automaton and on the description was not done; not implemented: nested machines, `Edits`, the party profile, `Request limit`, `Form returns`, `pass`. The record of a float (`0.0`, `2.0`, `0.42`, `1e-7`) is defined by the format, and the code does not define it: the coincidence with the code executor is checked by a scenario (ША11).
- **Discrepancies of the sources of the “Meeting” pilot:** ИС2 — corrected in the source: Void moves the objects of a pass to the archive and clears the findings, the witness answers and the summary of the voided pass (`without_key`), as the primary source (“Void”, “On entry”) and the code (`Void`) do; the former text of the item (“remain in the data”) is stale and replaced (Я-36); ИС6 — for the functions `merge_unique`, `not_included_in`, `has_critical`, `desirable*`, `critical_and_significant_not_repeated`, `has_reviewer_questions`, `reviewer_questions`, `all_lens_findings`, `lenses_without_critical`, `build_summary`, `remove_unsound`, `proposal_changed_since_attempt` (the full list by classes is in section 7) the code has only signatures: by the rule of section 7 they are written as host primitives with a class by the signature and a description by the tables of the primary source, they will become definitions in the language when the body appears in the source (what to count as a “lens” for a dropped lens, the four signs of an unsound opinion — the source does not say); ИС8 — forbidden lens identifiers: the invariant of the source names the Russian “witness”, “author”, “gatekeeper”, “human”, and the code distinguishes the parties by the Latin `witness`, `author`, `gatekeeper`, `enhanced`; ИС9, ИС10 — the journal of the failure reason writes `"${reason}"` instead of the word of the failure code, the refusal text of ERROR from `JournalEvent` is not defined; the keys `project.<key>` of the parameters are not named in the sources.
- **Definitions that are not code.** The bodies of the reading primitives (`proposal_changed_since_attempt`, `role_context`, `parse_agent_reply`); the four signs of an unsound opinion in `remove_unsound`; K and P in `build_summary`; the gate texts. The meaning of `write_right` is text only.
- **Journal.** The codes `input_rejected`, `machine_data`, `machine_error`, `unclosed_finding`, `meeting_decision`, `open_finding` are defined by the format ([state-machine-journal.md](state-machine-journal.md)), but the automata so far write part of these events by primitives without a body (`journal_machine_data`, `journal_findings`, `journal_decision`) and do not mark machine errors with a code: the comparison of the code with the table does not see them.
- **Implementation proposals not included in the format** (И-4; the interpreter run, version 2.2):
  - **A part of a response and a term.** The appeal events “part of a response” (Progress: the request remains open, the term is extended) and “term” (Expired) with a separate journal code. In the engine and the methodology protocol there are no intermediate parts ([protocol](state-machine-call-protocol.md), the section “What the contract did not cover”, items 15, 17); `RequestExpired` produces `failure(Timeout)`. If an implementation needs a separate journal code, it is proposed to add it to “Events of the table format”.
  - **A word of another party in the rows of an appeal to an agent** (a cancel by the user during waiting). In the methodology there is the common event “human stop” (rule 23) and the “Pause” fragment; the format does not introduce `signal` rows in appeals; a cancel without a pause would require a correction of the specification.
  - **The event `start`.** The machine input sets the initial data (`initial: input.<field>`, section 2); there is no start event — this is executor mechanics.
- **The registry of included definitions files** is part of the host registry (section 8); the format of the registry file is set by the host, the table format requires exactly one file by name. A common file of the types of an agent call (`AgentProfile`, `AgentLimits`, `AgentRequest`, `AgentReply`, `CallerKind`, `FailCode`, etc.) is allowed by the format (`## Types` of a definitions file) but is not created: now these types are repeated in three machines (СГ4(д) is not entered).
- **The call types of a nested machine in two files** (Я-34). The type `input` and the type `result` of a party `machine` are declared by the calling machine in its own `## Types`, and the called machine has its own `## Input`, `## Types` and `- Result:`; the rule (section 1, Я-30) requires their equality, but the comparison between the two files is not done by the methodology scripts — the product does it (the registry check). A common file of call types (a definitions file with `## Types`, section 8), included by the line `definitions:` into both machines, would remove the copies; it is not created, and no new file kind is introduced. Open: whether to create the file `agent_call_types` and include it into all machines that call “Agent step”.
- **A file of the “Pause” fragment in Portolan** (Я-35). There is no normative file of the fragment (`*.portolan.md`, the header `# Fragment: Pause`): section 9 holds a sample of the definition, and the include `Pause(…)` is not resolved by the scripts; the JSON names of the fragment's signals, their fields and the fragment parameters (1a, Я-46) will be set by this file. Open: create the fragment file and the record `Pause → file` in the host registry, and compare the sample of section 9 with it.
- **The gate of a human as an event without a request** (Я-38) — closed by rules 15, 17, 19, 22, 31 of [state-machine-spec.md](state-machine-spec.md) (task 063): the gate of a human is an open gate with the identifier `<party>-<attempt>`, and the word of a human carries it.
- **A party signal with no row in the current state** (Я-38) — closed by rules 14, 17, 19 of [state-machine-spec.md](state-machine-spec.md) (task 063): a gate word is accepted only if it is one of the gate words of the state of that gate; otherwise it is discarded, and the gate stays open and does not hang.
- **An appeal without gates (a “wall”)** (rule 19 of [state-machine-spec.md](state-machine-spec.md), task 064). A free input of a human without a gate identifier (a chat at rest) cannot be written by the format: a party of the kind `human` always has open gates with an identifier, and the column `counter` is mandatory for every party. The smallest record is the value `—` in the column `counter` of a party of the kind `human`: a party without gates, the counter does not grow; this is a format change. Open: the owner's decision.
- **Two records `Находка`** (Я-37, glossary). In the methodology layer, the runner, the review and the session `Находка` is `{ severity, level, evidence }`, in “Meeting” — `{ severity, evidence, repeat, question }`; both with the JSON name `Finding`. Proposal: name the meeting record `НаходкаСовещания` → `MeetingFinding`. Open: a question to the owner.
- **The order of `keys` and `values`** is the order of the first write of the key; the automata code on hash tables does not guarantee an order, so far the output must not depend on the order. The same order sets the write of a map in `all_data` (section 5).
- **Names of primitives:** the JSON name of a primitive is the host registry name in parentheses at the declaration (section 7, 1a, Я-46); the glossary ([state-machine-glossary.md](state-machine-glossary.md)) is a source of suggested names: a new name is suggested there together with the primitive (СГ11).
- **The source, not the format.** The invariant “counters are bounded” of the agent step is wrong for the number of turns with a limit below 1 (Start sets 1); the bound `<=` is not written for it. The primary sources of the pilots say “all variables and stores” for the Input of ERROR: by the format these are all data of the tables of the machine and the fragments, including external objects and the assignment, without executor data and the stores of rule 31 (section 2, Н-1); the record carries the proposal and the findings in full, compressing it is the source's decision; the correction of the text is in the source. **The correction of the fragment is a separate task of the source** (Н-10): the text of [state-machine-pause-states.md](state-machine-pause-states.md), “The fragment requires” (б), names `human_words` as data of the fragment, while the format does not enter a human's word into the table (a store of rule 31) and adds `open_requests`; the format is left as is.
- **Records of the format that Nova does not have** (checked 2026-10-19; the Russian names and operator words are a translation by the glossary, not an extension): §2 `?T` (`Option[T]`), `none` (`None`), `int>=n`, the literal set `"a" | "b"` (there are no literal unions; in Nova `str` or an enumeration), `id` (a UUID type; Nova has the type `Uuid` — `std.identifiers.uuid`, a text record 8-4-4-4-12 in lowercase hex; in the value of machine data and in JSON `id` is text with a format check), `full map[K, V]`, the values of an enumeration (`enum Name = El "value" | …`; in Nova `type X enum A | B`), a JSON name in parentheses at the declaration, `variant Name { Var {…} Var }` (in Nova `type X enum | Var {…}`), the field path `name[*].field`; §3 `expr[key]` of a map as a read (the Nova `HashMap` has `get` and `insert`, no `[]`), the short record `name[key].field = expr`, `in` in `failure(reason in {…})`, `match … {alt | alt if expr -> expr; else -> expr}` (`match` with `=>`), `let name = expr in expr` (`ro` in a block), the macros `filter`, `map`, `any`, `all`, `count`, `first_where`, `dict`, `fold` and the lambda `x -> expr` (iterator methods and `|x| …`), `unreachable`, `require` (`unreachable`, `required`), `range(a, b)` (`a..b`); §4–5 the state tables themselves and the key lines `Request`, `Reads`, `Edits`, `On accept`, `On entry`, `Idle term`, `Party`, `set`, `To`, the event patterns `response: Variant(field, field: name)` (in Nova the record pattern `Var { field, field: name }`), the actions `journal(…)`, `machine_error(…)`, `call(primitive, …)` with the classes `pure`, `reading`, `writing`, `irreversible` (in Nova — effects in the signature, `mut`, `environment.add_irreversible`), `pass`, `cancel_open`, `for each name in expr: actions` (`for x in xs {…}`), `journal(all_data)`; §1 the party kinds `agent`, `human`, `enhanced`, `machine`, `human or agent by setting`, the columns `signals` and `counter`, `Request limit`; §7 the record of the result `by role {…}`; §8 `define name(…) -> type = expr` (`fn name(…) -> type => expr`), definitions files with a version and a hash; §9 fragment files, the substitution `<parameter>`, parameters of the kind `behavior`.
- **The canonical form (1b)** is the recommended form of the text of a “tree → file” generator; only the equality of the cycle “md → JSON → md → JSON” is required (Я-45); it is checked by the consumer product, the methodology scripts ([check-portolan-samples.py](check-portolan-samples.py) and others) do not check the canon, and the samples are not brought to the canonical form (1b).
- **JSON schema and interpreter** are outside this file (section 6).

## Terminology used in this translation

Russian → English. Keywords are translated by the `en` column of [portolan-keywords.tsv](portolan-keywords.tsv); the names of the examples are English (the glossary [state-machine-glossary.md](state-machine-glossary.md) is the source of the suggested names). Where the Russian text quotes a Russian keyword in prose, this translation quotes the English one (the Russian form of a keyword is in the word table); the mappings quoted as Russian → English in section 1a are kept.

| Russian | English |
|---|---|
| Портолан, таблица машины | Portolan, machine table |
| стейт-машина, автомат | state machine, automaton |
| сторона (запроса) | party |
| ворота, слово ворот; сигнал стороны | gate, gate word; party signal |
| вратарь; усиленный вратарь | gatekeeper; enhanced gatekeeper |
| заход | pass |
| фрагмент, подключаемый фрагмент | fragment, included fragment |
| примитив хозяина; хозяин; реестр хозяина | host primitive; host; host registry |
| класс примитива | primitive class |
| фиксация шага | commit of a step |
| исполнитель; движок | executor; engine |
| обращение, операция, развилка, конец | appeal, operation, fork, end |
| запрос, ответ, сбой, отказ | request, response, failure, refusal |
| «При входе», «При приёме» | “On entry”, “On accept” |
| «Срок тишины», «Правит», «Возвратов формы», «Предел запросов» | “Idle term”, “Edits”, “Form returns”, “Request limit” |
| набор (сторон); набор литералов | set (of parties); literal set |
| вложенная машина | nested machine |
| разбор (результата стороны) | parse (of a party's result) |
| проверка (таблицы, форматирования) | check (of a table, of formatting) |
| дефект программы; ошибка машины | program defect; machine error |
| механика (исполнителя, контракта) | mechanics (of the executor, of the contract) |
| первоисточник; источник | primary source; source |
| пилот | pilot |
| слово человека | word of a human |
| привязка | binding |
| умолчание | default |
| JSON-имя | JSON name |
| значение (элемента перечисления) | value (of an enumeration element) |
| «Запрос», «Читает» (строки-ключи состояния) | “Request”, “Reads” (state key lines) |
