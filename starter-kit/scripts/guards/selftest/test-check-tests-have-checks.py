# -*- coding: utf-8 -*-
"""Самотест стража пустых тестов check-tests-have-checks.py.

Зачем: тест без проверок всегда зелёный; страж должен находить его по образцам проекта, не требуя
    особого стиля проверок.
Проверяет: на временном guards.conf с образцами (файлы tests/*.test.mjs, проверка — вызов cell( или
    слово assert, комментарии // и /* */): файл с cell( зелёный; файл с assert зелёный; литерал true
    внутри cell( не нарушение; служебный файл вне образца не судится; пустой файл и файл, где слова
    проверки только в комментариях, красные; похожие слова не проверка; другой язык теми же ключами
    (файлы *_test.py, комментарий #); TEST_FILES=off — «судить нечего» с причиной; нет TEST_CHECK при
    включённом TEST_FILES — красная предпосылка; нет файлов под образцом (в том числе после переименования
    папки) и пустой репозиторий — мишень потеряна.
Не проверяет: качество проверок, прогон тестов.
Правило: README комплекта, «Тест без проверок».
"""
import sys

sys.dont_write_bytecode = True

import os

import stlib

JS = {"TEST_FILES": r"^tests/[^/]+\.test\.mjs$", "TEST_CHECK": r"\bcell\s*\(|\bassert\b",
      "TEST_COMMENT": r"/\*[\s\S]*?\*/|^[ \t]*//.*$"}
PY = {"TEST_FILES": r"^tests/test_[^/]+\.py$", "TEST_CHECK": r"\bassert\b", "TEST_COMMENT": r"#.*$"}


def main():
    pr = stlib.Probes("check-tests-have-checks")
    base = pr.mkdtemp()
    env0 = stlib.isolated_env(base)
    env = dict(env0, GUARDS_CONF=stlib.conf_file(base, JS))
    counter = [0]
    T = "tests/"

    def fresh(files):
        counter[0] += 1
        return stlib.make_repo(base, env, files, name="r%d" % counter[0])

    def check(repo, *args, **kw):
        return stlib.guard("check-tests-have-checks.py", repo, kw.get("env", env), *args)

    def legit_two_styles():
        files = {T + "a.test.mjs": "import x from 'y';\ncell('works', () => x());\n",
                 T + "b.test.mjs": "import assert from 'node:assert';\nassert.equal(1, 1);\n",
                 T + "cleanup-tmp.mjs": "// helper, not a test\n"}
        stlib.expect(check(fresh(files)), 0, "ок: осмотрено 2 файлов тестов")

    def legit_true_literal():
        files = {T + "a.test.mjs": "cell('literal', true);\n"}
        stlib.expect(check(fresh(files)), 0, "ок: осмотрено 1 файлов тестов")

    def other_language():
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, PY))
        files = {T + "test_a.py": "def test_a():\n    assert 1 == 1\n", T + "test_b.py": "def test_b():\n    pass  # assert later\n"}
        proc = check(fresh(files), env=e)
        stlib.expect(proc, 1, "FAIL: check-tests-have-checks: 1 нарушений")
        assert stlib.has_line(proc, "FAIL %stest_b.py: empty-test:" % T), proc.out

    def red_empty():
        files = {T + "a.test.mjs": "cell('x', 1);\n", T + "empty.test.mjs": "console.log('hi');\n"}
        proc = check(fresh(files))
        stlib.expect(proc, 1, "FAIL: check-tests-have-checks: 1 нарушений")
        assert stlib.has_line(proc, "FAIL %sempty.test.mjs: empty-test:" % T), proc.out

    def red_comment_only():
        text = "// assert something\n/* cell( not a call */\nconsole.log(1);\n"
        stlib.expect(check(fresh({T + "c.test.mjs": text})), 1, "FAIL: check-tests-have-checks: 1 нарушений")

    def red_zero_byte():
        stlib.expect(check(fresh({T + "z.test.mjs": ""})), 1, "FAIL: check-tests-have-checks: 1 нарушений")

    def similar_words_are_not_checks():
        text = "const assertion = 1; const cellar = 2; cells(3);\n"
        stlib.expect(check(fresh({T + "w.test.mjs": text})), 1, "FAIL: check-tests-have-checks: 1 нарушений")

    def off_is_nothing_to_judge():
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"TEST_FILES": "off"}))
        stlib.expect(check(fresh({T + "z.test.mjs": ""}), env=e), 0,
                     "судить нечего: файлы тестов не заданы проектом (TEST_FILES=off")

    def check_key_missing():
        changes = dict(JS)
        changes["TEST_CHECK"] = None
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, changes))
        proc = check(fresh({T + "a.test.mjs": "cell('x', 1);\n"}), env=e)
        stlib.expect(proc, 1, "FAIL: предпосылка")
        assert "нет обязательного ключа TEST_CHECK" in proc.out, proc.out

    def target_lost_no_tests():
        stlib.expect(check(fresh({T + "cleanup-tmp.mjs": "x\n", "a.txt": "x\n"})), 1, "FAIL: мишень потеряна")

    def target_lost_moved():
        stlib.expect(check(fresh({"test/a.test.mjs": "cell('x', 1);\n"})), 1, "FAIL: мишень потеряна")

    def empty_repo():
        base2 = pr.mkdtemp()
        repo = os.path.join(base2, "e")
        os.makedirs(repo)
        stlib.git(repo, env, "init", "-q")
        stlib.expect(check(repo), 1, "FAIL: мишень потеряна")

    pr.probe("законное", "cell( и assert, служебный файл вне образца не судится", legit_two_styles)
    pr.probe("законное", "литерал true в проверке — не нарушение", legit_true_literal)
    pr.probe("законное", "TEST_FILES=off: судить нечего с причиной", off_is_nothing_to_judge)
    pr.probe("красная", "файл без проверок называется по имени", red_empty)
    pr.probe("красная", "слова проверки только в комментариях", red_comment_only)
    pr.probe("красная", "другой язык теми же ключами: assert только в комментарии", other_language)
    pr.probe("иной-синтаксис", "пустой файл", red_zero_byte)
    pr.probe("иной-синтаксис", "похожие слова assertion, cellar, cells( — не проверка", similar_words_are_not_checks)
    pr.probe("мишень", "нет TEST_CHECK при включённом TEST_FILES — красная предпосылка", check_key_missing)
    pr.probe("мишень", "в папке нет файлов под образцом — мишень потеряна", target_lost_no_tests)
    pr.probe("мишень", "папка тестов переименована — мишень потеряна", target_lost_moved)
    pr.probe("мишень", "пустой репозиторий — мишень потеряна", empty_repo)
    return pr.done()


if __name__ == "__main__":
    sys.exit(main())
