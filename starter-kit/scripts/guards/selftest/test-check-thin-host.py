# -*- coding: utf-8 -*-
"""Самотест стража тонкости хозяина check-thin-host.py.

Зачем: машина, вызывающая эффекты сама, и хозяин, импортирующий машину, делают правило «хозяин минимален»
    мёртвой буквой; страж обязан находить оба нарушения по образцам проекта и краснеть на потере мишени.
Проверяет: на временном guards.conf (машины src/machines/*.py, хозяева src/host/*.py, эффект — os.system(,
    subprocess. и «notify(» в начале слова после пробела, импорт машины — from/import machines): честные
    машина (возвращает перечень эффектов данными) и хозяин (ведёт машину через исполнителя) зелёны; файл
    вне образцов не судится; MACHINE_FILES=off — «судить нечего» с причиной; пометка guard-allow с причиной
    снимает находку; вызов эффекта в машине и импорт машины в хозяине красные с адресом строки; пометка
    без причины красная; похожие строки (имя эффекта в данных, machineshop, текст импорта в литерале) —
    не нарушение; нет MACHINE_EFFECT при включённом страже — красная предпосылка; переименование папки
    машин или хозяев — красный с названной стороной; пустой репозиторий — мишень потеряна; коммит, не
    трогающий мишень, — «судить нечего».
Не проверяет: смысл правила и динамическую проверку (замена хозяина на тестового).
Правило: docs/guards.md (README комплекта), «Хозяин машины минимален».
"""
import sys

sys.dont_write_bytecode = True

import os

import stlib

CONF = {"MACHINE_FILES": r"^src/machines/[^/]+\.py$",
        "MACHINE_EFFECT": r"\bos\.system\s*\(|\bsubprocess\.|(?:^|\s)notify\s*\(",
        "HOST_FILES": r"^src/host/[^/]+\.py$",
        "MACHINE_IMPORT": r"^[ \t]*(?:from[ \t]+machines\b|import[ \t]+machines\b)"}

MACHINE = "src/machines/door.py"
HOST = "src/host/main.py"

# машина: шаг возвращает состояние и перечень эффектов данными, вызовов эффектов нет
LEGIT_MACHINE = "def step(state, event):\n    return state, [(\"notify\", event[\"topic\"])]\n"
# хозяин: ведёт машину через исполнителя, машину не импортирует
LEGIT_HOST = ("import engine\n\n\ndef run(machine_ref, events):\n"
              "    for event in events:\n"
              "        state, effects = engine.step(machine_ref, event)\n")


def main():
    pr = stlib.Probes("check-thin-host")
    base = pr.mkdtemp()
    env0 = stlib.isolated_env(base)
    env = dict(env0, GUARDS_CONF=stlib.conf_file(base, CONF))
    counter = [0]

    def fresh(files):
        counter[0] += 1
        return stlib.make_repo(base, env, files, name="r%d" % counter[0])

    def check(repo, *args, **kw):
        return stlib.guard("check-thin-host.py", repo, kw.get("env", env), *args)

    def legit_pair():
        files = {MACHINE: LEGIT_MACHINE, HOST: LEGIT_HOST,
                 "src/lib/util.py": "# helper, not a machine and not a host\n"}
        stlib.expect(check(fresh(files)), 0, "ок: осмотрено 2 файлов машин и хозяев")

    def off_is_nothing_to_judge():
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"MACHINE_FILES": "off"}))
        stlib.expect(check(fresh({MACHINE: LEGIT_MACHINE}), env=e), 0,
                     "судить нечего: код машин и хозяев не задан проектом (MACHINE_FILES=off")

    def allow_with_reason():
        machine = ("def step(state, event):\n"
                   "    os.system(\"echo hi\")  # guard-allow(machine-effect): проба самотеста\n"
                   "    return state, []\n")
        proc = check(fresh({MACHINE: machine, HOST: LEGIT_HOST}))
        stlib.expect(proc, 0, "ок: осмотрено 2 файлов машин и хозяев")
        assert stlib.has_line(proc, "принято %s:2: machine-effect: проба самотеста" % MACHINE), proc.out

    def red_effect_in_machine():
        machine = ("def step(state, event):\n"
                   "    os.system(\"echo hi\")\n"
                   "    return state, []\n")
        proc = check(fresh({MACHINE: machine, HOST: LEGIT_HOST}))
        stlib.expect(proc, 1, "FAIL: check-thin-host: 1 нарушений")
        assert stlib.has_line(proc, "FAIL %s:2: machine-effect:" % MACHINE), proc.out

    def red_host_imports_machine():
        host = "import engine\nimport machines.door\nfrom machines import door\n"
        proc = check(fresh({MACHINE: LEGIT_MACHINE, HOST: host}))
        stlib.expect(proc, 1, "FAIL: check-thin-host: 2 нарушений")
        assert stlib.has_line(proc, "FAIL %s:2: host-import:" % HOST), proc.out
        assert stlib.has_line(proc, "FAIL %s:3: host-import:" % HOST), proc.out

    def red_allow_without_reason():
        machine = ("def step(state, event):\n"
                   "    os.system(\"echo hi\")  # guard-allow(machine-effect):\n"
                   "    return state, []\n")
        proc = check(fresh({MACHINE: machine, HOST: LEGIT_HOST}))
        stlib.expect(proc, 1, "FAIL: check-thin-host: 1 нарушений")
        assert stlib.has_line(proc, "пометка без причины"), proc.out

    def similar_lines_are_not_violations():
        machine = ("def step(state, event):\n"
                   "    # os.systematic( is not a call; notify stays data\n"
                   "    return state, [(\"notify\", 1)]\n")
        host = "import engine\nimport machineshop\nhint = \"import machines.door\"\n"
        stlib.expect(check(fresh({MACHINE: machine, HOST: host})), 0, "ок: осмотрено 2 файлов")

    def empty_target_files():
        stlib.expect(check(fresh({MACHINE: "", HOST: ""})), 0, "ок: осмотрено 2 файлов")

    def effect_key_missing():
        changes = dict(CONF)
        changes["MACHINE_EFFECT"] = None
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, changes))
        proc = check(fresh({MACHINE: LEGIT_MACHINE, HOST: LEGIT_HOST}), env=e)
        stlib.expect(proc, 1, "FAIL: предпосылка")
        assert "нет обязательного ключа MACHINE_EFFECT" in proc.out, proc.out

    def machines_moved():
        files = {"src/engines/door.py": LEGIT_MACHINE, HOST: LEGIT_HOST}
        proc = check(fresh(files))
        stlib.expect(proc, 1, "FAIL: check-thin-host: 1 нарушений")
        assert stlib.has_line(proc, "target: образцу MACHINE_FILES"), proc.out
        assert stlib.has_line(proc, "машины потеряны"), proc.out

    def hosts_moved():
        files = {MACHINE: LEGIT_MACHINE, "src/runner/main.py": LEGIT_HOST}
        proc = check(fresh(files))
        stlib.expect(proc, 1, "FAIL: check-thin-host: 1 нарушений")
        assert stlib.has_line(proc, "хозяева потеряны"), proc.out

    def empty_repo():
        base2 = pr.mkdtemp()
        repo = os.path.join(base2, "e")
        os.makedirs(repo)
        stlib.git(repo, env, "init", "-q")
        stlib.expect(check(repo), 1, "FAIL: мишень потеряна")

    def commit_without_target():
        repo = fresh({MACHINE: LEGIT_MACHINE, HOST: LEGIT_HOST})
        head = stlib.commit_file(repo, env, "docs/notes.md", "# Notes\n", message="docs")
        stlib.expect(check(repo, "--commit", head), 0,
                     "судить нечего: коммит не меняет файлов этой мишени")

    pr.probe("законное", "машина без вызовов эффектов и хозяин без импорта зелёные, файл вне образцов не судится",
             legit_pair)
    pr.probe("законное", "MACHINE_FILES=off: судить нечего с причиной", off_is_nothing_to_judge)
    pr.probe("законное", "пометка guard-allow с причиной снимает находку", allow_with_reason)
    pr.probe("красная", "прямой вызов эффекта в машине красный с адресом строки", red_effect_in_machine)
    pr.probe("красная", "import и from машины в хозяине красные с адресами строк", red_host_imports_machine)
    pr.probe("красная", "пометка guard-allow без причины красная", red_allow_without_reason)
    pr.probe("иной-синтаксис", "имя эффекта в данных, machineshop, текст импорта в литерале — не нарушение",
             similar_lines_are_not_violations)
    pr.probe("иной-синтаксис", "пустые файлы мишени зелёны", empty_target_files)
    pr.probe("мишень", "нет MACHINE_EFFECT при включённом MACHINE_FILES — красная предпосылка",
             effect_key_missing)
    pr.probe("мишень", "папка машин переименована — красный с названной стороной", machines_moved)
    pr.probe("мишень", "папка хозяев переименована — красный с названной стороной", hosts_moved)
    pr.probe("мишень", "пустой репозиторий — мишень потеряна", empty_repo)
    pr.probe("мишень", "коммит, не трогающий мишень, — судить нечего", commit_without_target)
    return pr.done()


if __name__ == "__main__":
    sys.exit(main())
