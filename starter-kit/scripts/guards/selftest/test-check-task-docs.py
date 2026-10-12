# -*- coding: utf-8 -*-
"""Самотест стража формата документов задач check-task-docs.py.

Зачем: машинные места документов задач читает программа цикла; испорченная первая строка или строка
    журнала не видна в обзоре, а последствия (проверка заново поверх утверждённого документа, потерянный
    заход) дороги. Формат задаёт проект, поэтому страж проверяется на правилах, собранных в прогоне.
Проверяет: на временном guards.conf с правилами трёх видов (first-line, every-line, unique): правильные
    документы зелёные; BOM и CRLF не мешают; файлы вне образцов путей не судятся; номер в имени файла и в
    первой строке сверяется (группа n); упоминание номера не в начале строки — не объявление; красные —
    чужая первая строка, номер не равен номеру в имени, строка журнала не по форме, повтор номера; режим
    коммита судит только изменённые файлы; TASK_DOC_RULE=off — «судить нечего» с причиной; нет ключа,
    неизвестный вид, битое регулярное выражение — красная предпосылка с подсказкой; нет файлов под
    образцами (в том числе после переименования папки) и пустой репозиторий — мишень потеряна.
Не проверяет: содержание документов и формы конкретного проекта (их выбирает проект).
Правило: docs/guards.md (README комплекта), «Формат документов задач».

Формы в правилах ниже — данные пробы (похожи на формы документов методологии), а не формат комплекта.
"""
import sys

sys.dont_write_bytecode = True

import os

import stlib

RULES = [
    r"first-line ^tasks/[^/]+/(spec|plan)\.md$ ^Статус: (черновик|утверждено)",
    r"first-line ^tasks/[^/]+/[a-z-]*review-(?P<n>[0-9]+)\.md$ ^Заход (?P<n>[0-9]+): существенных [0-9]+, поверхностных [0-9]+, проб [0-9]+",
    r"every-line ^tasks/[^/]+/progress\.log$ ^[^ \t]+ [0-9]+/[0-9]+ .+$",
    r"unique ^tasks/[^/]+/spec\.md$ ^(?P<id>(Т|П)-[0-9]+)\b",
]
GOOD_REVIEW = "Заход %d: существенных 1, поверхностных 2, проб 3\n\nтекст\n"


def main():
    pr = stlib.Probes("check-task-docs")
    base = pr.mkdtemp()
    env0 = stlib.isolated_env(base)
    env = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"TASK_DOC_RULE": RULES}))
    counter = [0]

    def fresh(files):
        counter[0] += 1
        return stlib.make_repo(base, env, files, name="r%d" % counter[0])

    def check(repo, *args, **kw):
        return stlib.guard("check-task-docs.py", repo, kw.get("env", env), *args)

    good = {
        "tasks/001-x/spec.md": "Статус: черновик\n\nТ-01 a\nТ-02 b\nП-01 c\n",
        "tasks/001-x/plan.md": "Статус: утверждено, дата, кто\nБаза: ревизия abc\n",
        "tasks/001-x/spec-review-4.md": GOOD_REVIEW % 4,
        "tasks/001-x/review-3.md": GOOD_REVIEW % 3,
        "tasks/001-x/progress.log": "С1 0/2 старт\nС1 1/2 [10:05] шаг\nС1 2/2 готово\n",
    }

    def red(change, rule, where, count=1):
        def fn():
            files = dict(good)
            files.update(change)
            proc = check(fresh(files))
            stlib.expect(proc, 1, "FAIL: check-task-docs: %d нарушений" % count)
            assert stlib.has_line(proc, "FAIL %s: %s:" % (where, rule)), proc.out
        return fn

    def legit_all_kinds():
        stlib.expect(check(fresh(good)), 0, "ок: осмотрено 5 файлов задач")

    def legit_bom_crlf_and_extra():
        files = dict(good)
        files["tasks/001-x/spec.md"] = b"\xef\xbb\xbf" + "Статус: черновик\r\nТ-01 a\r\n".encode("utf-8")
        files["tasks/001-x/progress.log"] = "С1 0/1 старт\r\n\r\nС1 1/1 готово\r\n"
        files["tasks/001-x/nested/spec.md"] = "not judged: nested folder\n"
        files["tasks/001-x/result.md"] = "Статус: в работе\n"
        files["tasks/001-x/notes.md"] = "free text\n"
        stlib.expect(check(fresh(files)), 0, "ок: осмотрено 5 файлов задач")

    def legit_id_mentions_not_at_line_start():
        files = dict(good)
        files["tasks/001-x/spec.md"] = "Статус: черновик\n\nТ-01 a\nsee Т-01 and\n| Т-01 | table |\n  Т-01 indented\n"
        stlib.expect(check(fresh(files)), 0, "ок: осмотрено 5 файлов задач")

    def commit_mode_only_changed():
        repo = fresh(good)
        sha = stlib.commit_file(repo, env, "tasks/001-x/plan-review-3.md", "no numbers here\n", "bad")
        stlib.expect(check(repo, "--commit", sha), 1, "FAIL: check-task-docs: 1 нарушений")
        sha2 = stlib.commit_file(repo, env, "other.txt", "x\n", "other")
        stlib.expect(check(repo, "--commit", sha2), 0, "судить нечего: коммит не меняет файлов этой мишени")

    def off_is_nothing_to_judge():
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"TASK_DOC_RULE": "off"}))
        proc = check(fresh(good), env=e)
        stlib.expect(proc, 0, "судить нечего: формат документов задач не задан проектом (TASK_DOC_RULE=off")

    def key_missing():
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"TASK_DOC_RULE": None}))
        proc = check(fresh(good), env=e)
        stlib.expect(proc, 1, "FAIL: предпосылка")
        assert "нет обязательного ключа TASK_DOC_RULE" in proc.out and "docs/guards.md" in proc.out, proc.out

    def bad_rules():
        for value, words in ((["frist-line ^a$ ^b"], "вид «frist-line» неизвестен"),
                             (["first-line ^a$"], "нужно «<вид>"),
                             (["every-line ^(a$ ^b"], "не разбирается"),
                             (["off", RULES[0]], "off допустим только")):
            e = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"TASK_DOC_RULE": value}))
            proc = check(fresh(good), env=e)
            stlib.expect(proc, 1, "FAIL: предпосылка")
            assert words in proc.out, (value, proc.out)

    def no_task_docs():
        stlib.expect(check(fresh({"README.md": "x\n"})), 1, "FAIL: мишень потеряна")

    def folder_renamed():
        files = dict((k.replace("tasks/", "work/", 1), v) for k, v in good.items())
        stlib.expect(check(fresh(files)), 1, "FAIL: мишень потеряна")

    def empty_repo():
        base2 = pr.mkdtemp()
        repo = os.path.join(base2, "e")
        os.makedirs(repo)
        stlib.git(repo, env, "init", "-q")
        stlib.expect(check(repo), 1, "FAIL: мишень потеряна")

    pr.probe("законное", "правила трёх видов: правильные документы", legit_all_kinds)
    pr.probe("законное", "BOM и CRLF, пустая строка журнала, вложенные папки и чужие имена не судятся", legit_bom_crlf_and_extra)
    pr.probe("законное", "номер не в начале строки не считается объявлением", legit_id_mentions_not_at_line_start)
    pr.probe("законное", "режим коммита: только изменённые файлы", commit_mode_only_changed)
    pr.probe("законное", "TASK_DOC_RULE=off: судить нечего с причиной", off_is_nothing_to_judge)
    pr.probe("красная", "первая строка spec.md — чужая", red({"tasks/001-x/spec.md": "Status: draft\n"}, "first-line", "tasks/001-x/spec.md:1"))
    pr.probe("красная", "статус plan.md «в работе»", red({"tasks/001-x/plan.md": "Статус: в работе\n"}, "first-line", "tasks/001-x/plan.md:1"))
    pr.probe("красная", "заход без чисел", red({"tasks/001-x/spec-review-4.md": "Заход 4: существенных нет\n"}, "first-line", "tasks/001-x/spec-review-4.md:1"))
    pr.probe("красная", "номер захода не равен номеру в имени", red({"tasks/001-x/review-3.md": GOOD_REVIEW % 5}, "first-line", "tasks/001-x/review-3.md:1"))
    pr.probe("красная", "строка журнала без k/N", red({"tasks/001-x/progress.log": "С1 0/2 старт\nбез формы\n"}, "line-form", "tasks/001-x/progress.log:2"))
    pr.probe("красная", "строка журнала без подписи", red({"tasks/001-x/progress.log": "С1 0/2 старт\nС1 1/2\n"}, "line-form", "tasks/001-x/progress.log:2"))
    pr.probe("красная", "повтор номера требования", red({"tasks/001-x/spec.md": "Статус: черновик\nТ-05 a\nТ-05 b\n"}, "dup-id", "tasks/001-x/spec.md:3"))
    pr.probe("иной-синтаксис", "строка статуса не с начала строки", red({"tasks/001-x/plan.md": " Статус: утверждено\n"}, "first-line", "tasks/001-x/plan.md:1"))
    pr.probe("иной-синтаксис", "пустой файл spec.md", red({"tasks/001-x/spec.md": ""}, "first-line", "tasks/001-x/spec.md:1"))
    pr.probe("иной-синтаксис", "строка журнала из одних пробелов", red({"tasks/001-x/progress.log": "С1 0/2 старт\n   \n"}, "line-form", "tasks/001-x/progress.log:2"))
    pr.probe("иной-синтаксис", "неразрывный пробел вместо разделителя", red({"tasks/001-x/progress.log": "С1 0/2 старт\nС1 1/2 x\n"}, "line-form", "tasks/001-x/progress.log:2"))
    pr.probe("иной-синтаксис", "неизвестный вид, неполное правило, битое выражение, off вместе с правилом", bad_rules)
    pr.probe("мишень", "нет ключа TASK_DOC_RULE — красная предпосылка с подсказкой", key_missing)
    pr.probe("мишень", "нет документов задач — мишень потеряна", no_task_docs)
    pr.probe("мишень", "папка задач переименована — мишень потеряна", folder_renamed)
    pr.probe("мишень", "пустой репозиторий — мишень потеряна", empty_repo)
    return pr.done()


if __name__ == "__main__":
    sys.exit(main())
