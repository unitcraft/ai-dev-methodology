# -*- coding: utf-8 -*-
"""Самотест храповика долга check-ratchet.py.

Зачем: храповик, который пропускает новое нарушение, не видит подмену при том же счёте или держит в
    базе исправленное, делает долг невидимым: база растёт или лжёт, а прогон зелёный.
Проверяет: храповик над стражем гигиены текста (временный guards.conf, RATCHET_GUARD=check-text-hygiene.py):
    чистое дерево и пустая база — зелёный с «долг: 0»; нарушение с записью — зелёный, долг напечатан, вставка
    строк выше нарушения ключ не меняет; исправление вместе с удалением записи — долг меньше; RATCHET_GUARD=off
    и пустая база — «судить нечего»; новое нарушение — красный с адресом и ключом; подмена (одно исправлено и
    убрано из базы, другое внесено) — красный на новом; удаление записи без исправления — красный; исправлено,
    запись оставлена — «запись устарела»; запись с поддельным токеном — красный без значения; строка не по
    форме, без причины, повтор ключа, запись при RATCHET_GUARD=off — красные; одинаковые строки различаются
    #n; режимы индекса и коммита; run-all.sh не зовёт стража под храповиком напрямую, а без храповика в
    папке зовёт; нет файла базы, оборачиваемый страж не найден, красный по предпосылке, с потерянной
    мишенью, папка без git — красный, не «ок».
Не проверяет: правила самого оборачиваемого стража (его самотест).
Правило: docs/guards.md (README комплекта), «Храповик долга».

Образцы порчи и поддельный токен собираются при прогоне; в файле самотеста литералов нарушений нет.
"""
import sys

sys.dont_write_bytecode = True

import hashlib
import os
import re
import shutil

import stlib

FFFD = chr(0xFFFD)
BASE = "scripts/guards/ratchet.txt"
HYG = "check-text-hygiene.py"
HEADER = "# база храповика\n"
KEY_RE = re.compile(r"ключ для базы: (\S+)$")


def bad(word):
    """Строка с порчей (символ замены), собранная при прогоне."""
    return word + FFFD + "\n"


def main():
    pr = stlib.Probes("check-ratchet")
    base = pr.mkdtemp()
    env0 = stlib.isolated_env(base)
    env = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"RATCHET_GUARD": HYG}))
    env_off = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"RATCHET_GUARD": "off"}))
    counter = [0]

    def fresh(files, baseline=HEADER, e=None):
        counter[0] += 1
        files = dict(files)
        if baseline is not None:
            files[BASE] = baseline
        return stlib.make_repo(base, e or env, files, name="r%d" % counter[0])

    def check(repo, *args, **kw):
        return stlib.guard("check-ratchet.py", repo, kw.get("env", env), *args)

    def keys_of(proc):
        return [m.group(1) for m in (KEY_RE.search(x) for x in proc.out.splitlines()) if m]

    def recorded(*keys):
        """База с записями по ключам; каждый ключ с причиной."""
        return HEADER + "".join("%s: долг принят до включения стража\n" % k for k in keys)

    def with_debt(text):
        """Репозиторий с нарушениями из text, база заполнена ключами из красного прогона."""
        repo = fresh({"doc/a.txt": text})
        keys = keys_of(check(repo))
        assert keys, "красный прогон не назвал ключей"
        stlib.commit_file(repo, env, BASE, recorded(*keys), "baseline")
        return repo, keys

    def legit_clean():
        repo = fresh({"doc/a.txt": "ok\n"})
        proc = check(repo)
        stlib.expect(proc, 0, "ок: осмотрено 1 стражей под храповиком; долг: 0")

    def legit_debt_and_drift():
        repo, keys = with_debt("ok\n" + bad("one"))
        proc = check(repo)
        stlib.expect(proc, 0, "ок: осмотрено 1 стражей под храповиком; долг: 1")
        assert stlib.has_line(proc, "принято doc/a.txt:2: fffd: долг: долг принят"), proc.out
        digest = hashlib.sha256(("one" + FFFD).encode("utf-8")).hexdigest()[:8]
        assert keys == ["%s:doc/a.txt:fffd:%s" % (HYG, digest)], keys
        stlib.commit_file(repo, env, "doc/a.txt", "new top\nmore\nok\n" + bad("one"), "drift")
        proc = check(repo)
        stlib.expect(proc, 0, "ок: осмотрено 1 стражей под храповиком; долг: 1")
        assert stlib.has_line(proc, "принято doc/a.txt:4: fffd:"), proc.out

    def legit_fix_with_entry_removed():
        repo, keys = with_debt(bad("one") + bad("two"))
        stlib.expect(check(repo), 0, "ок: осмотрено 1 стражей под храповиком; долг: 2")
        kept = [k for k in keys if k != keys[0]]
        fixed = "fixed\n" + bad("two") if "one" in open_line(repo, keys[0]) else bad("one") + "fixed\n"
        stlib.write_files(repo, {"doc/a.txt": fixed, BASE: recorded(*kept)})
        stlib.expect(check(repo), 0, "ок: осмотрено 1 стражей под храповиком; долг: 1")

    def open_line(repo, key):
        """Какая из строк файла дала ключ: сверка хэша (тест не полагается на порядок ключей)."""
        digest = key.split(":")[-1].split("#")[0]
        with open(os.path.join(repo, "doc", "a.txt"), "rb") as handle:
            for row in handle.read().split(b"\n"):
                if hashlib.sha256(row.strip()).hexdigest()[:8] == digest:
                    return row.decode("utf-8", "replace")
        return ""

    def legit_off():
        repo = fresh({"doc/a.txt": bad("one")}, e=env_off)
        stlib.expect(check(repo, env=env_off), 0,
                     "судить нечего: храповик не подключён ни к одному стражу (RATCHET_GUARD=off")

    def red_new():
        repo = fresh({"doc/a.txt": "ok\n" + bad("one")})
        proc = check(repo)
        stlib.expect(proc, 1, "FAIL: check-ratchet: 1 нарушений")
        assert stlib.has_line(proc, "FAIL doc/a.txt:2: ratchet-new: новое нарушение стража %s (fffd:" % HYG), proc.out
        assert keys_of(proc), proc.out

    def red_substitution():
        repo, keys = with_debt(bad("one"))
        stlib.write_files(repo, {"doc/a.txt": "fixed\n" + bad("other"), BASE: HEADER})
        proc = check(repo)
        stlib.expect(proc, 1, "FAIL: check-ratchet: 1 нарушений")
        assert stlib.has_line(proc, "вердикт стража: FAIL: check-text-hygiene: 1 нарушений"), proc.out
        assert stlib.has_line(proc, "FAIL doc/a.txt:2: ratchet-new:"), proc.out
        assert keys_of(proc) != keys, proc.out

    def red_entry_removed_not_fixed():
        repo, keys = with_debt(bad("one"))
        stlib.write_files(repo, {BASE: HEADER})
        proc = check(repo)
        stlib.expect(proc, 1, "FAIL: check-ratchet: 1 нарушений")
        assert keys_of(proc) == keys, proc.out

    def red_stale():
        repo, keys = with_debt(bad("one"))
        stlib.write_files(repo, {"doc/a.txt": "fixed\n"})
        proc = check(repo)
        stlib.expect(proc, 1, "FAIL: check-ratchet: 1 нарушений")
        assert stlib.has_line(proc, "FAIL %s:2: ratchet-stale: запись устарела: исправленное убирается из базы "
                                    "тем же изменением" % BASE), proc.out

    def red_edited_line():
        repo, keys = with_debt(bad("one"))
        stlib.write_files(repo, {"doc/a.txt": bad("one, edited")})
        proc = check(repo)
        stlib.expect(proc, 1, "FAIL: check-ratchet: 2 нарушений")
        assert stlib.has_line(proc, ": ratchet-new:") and stlib.has_line(proc, ": ratchet-stale:"), proc.out

    def red_secret_entry():
        token = "gh" + "p_" + "Z9" * 18
        repo = fresh({"doc/a.txt": "ok\n"}, baseline=HEADER + "%s:doc/a.txt:fffd:0123abcd: %s\n" % (HYG, token))
        proc = check(repo)
        stlib.expect(proc, 1, "FAIL: check-ratchet: 1 нарушений")
        assert stlib.has_line(proc, "FAIL %s:2: ratchet-secret: запись похожа на секрет" % BASE), proc.out
        assert token not in proc.out, proc.out

    def red_format():
        key = "%s:doc/a.txt:fffd:0123abcd" % HYG
        text = HEADER + "not an entry\n" + key + ":   \n" + key + ": причина\n" + key + ": снова\n"
        proc = check(fresh({"doc/a.txt": "ok\n"}, baseline=text))
        stlib.expect(proc, 1, "FAIL: check-ratchet: 4 нарушений")
        for where, what in ((2, "строка не вида"), (3, "запись без причины"), (5, "ключ повторяется"),
                            (4, "ratchet-stale")):
            assert stlib.has_line(proc, "FAIL %s:%d: " % (BASE, where)) and what in proc.out, (where, proc.out)

    def red_off_with_entries():
        text = HEADER + "%s:doc/a.txt:fffd:0123abcd: причина\n" % HYG
        repo = fresh({"doc/a.txt": "ok\n"}, baseline=text, e=env_off)
        proc = check(repo, env=env_off)
        stlib.expect(proc, 1, "FAIL: check-ratchet: 1 нарушений")
        assert stlib.has_line(proc, "FAIL %s:2: ratchet-unwired:" % BASE), proc.out

    def same_lines_numbered():
        repo = fresh({"doc/a.txt": bad("same") + "ok\n" + bad("same")})
        keys = keys_of(check(repo))
        assert len(keys) == 2 and keys[1] == keys[0] + "#2", keys
        stlib.commit_file(repo, env, BASE, recorded(keys[0]), "baseline")
        proc = check(repo)
        stlib.expect(proc, 1, "FAIL: check-ratchet: 1 нарушений")
        assert keys_of(proc) == [keys[1]], proc.out

    def index_mode():
        repo = fresh({"doc/a.txt": "ok\n"})
        stlib.write_files(repo, {"doc/a.txt": "ok\n" + bad("one")})
        stlib.expect(check(repo, "--index"), 0, "ок: осмотрено 1 стражей под храповиком; долг: 0")
        stlib.git(repo, env, "add", "--", "doc/a.txt")
        proc = check(repo, "--index")
        stlib.expect(proc, 1, "FAIL: check-ratchet: 1 нарушений")
        stlib.write_files(repo, {BASE: recorded(*keys_of(proc))})
        stlib.git(repo, env, "add", "--", BASE)
        stlib.expect(check(repo, "--index"), 0, "ок: осмотрено 1 стражей под храповиком; долг: 1")

    def commit_mode():
        repo, keys = with_debt(bad("one"))
        sha = stlib.commit_file(repo, env, "doc/a.txt", "top\n" + bad("one"), "touch file with debt")
        stlib.expect(check(repo, "--commit", sha), 0,
                     "ок: осмотрено 1 стражей под храповиком (файлы коммита); долг в файлах коммита: 1")
        sha = stlib.commit_file(repo, env, "doc/b.txt", bad("new"), "new violation")
        proc = check(repo, "--commit", sha)
        stlib.expect(proc, 1, "FAIL: check-ratchet: 1 нарушений")
        assert stlib.has_line(proc, "FAIL doc/b.txt:1: ratchet-new:"), proc.out

    def run_all_skips_wrapped():
        folder = os.path.join(pr.mkdtemp(), "g")
        os.makedirs(folder)
        shutil.copytree(os.path.join(stlib.GUARDS, "lib"), os.path.join(folder, "lib"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("check-ratchet.py", HYG, "guard-secrets.py"):
            shutil.copy(os.path.join(stlib.GUARDS, name), folder)
        repo, keys = with_debt(bad("one"))
        proc = stlib.guard("run-all.sh", repo, env, "--dir", folder, "--root", repo)
        assert proc.returncode == 0, proc.out
        assert "%s -> под храповиком" % HYG in proc.out, proc.out
        assert "check-ratchet.py -> ок: осмотрено 1 стражей под храповиком; долг: 1" in proc.out, proc.out
        os.remove(os.path.join(folder, "check-ratchet.py"))
        proc = stlib.guard("run-all.sh", repo, env, "--dir", folder, "--root", repo)
        assert proc.returncode == 1 and "%s -> FAIL" % HYG in proc.out, proc.out

    def lost_baseline():
        proc = check(fresh({"doc/a.txt": "ok\n"}, baseline=None))
        stlib.expect(proc, 1, "FAIL: мишень потеряна: нет файла базы %s" % BASE)

    def lost_wrapped_target():
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, {
            "RATCHET_GUARD": "check-tests-have-checks.py", "TEST_FILES": r"^tests/.*_test\.py$",
            "TEST_CHECK": r"\bassert\b", "TEST_COMMENT": "#.*$"}))
        proc = check(fresh({"doc/a.txt": "ok\n"}, e=e), env=e)
        stlib.expect(proc, 1, "FAIL: мишень потеряна: страж check-tests-have-checks.py:")

    def wrapped_premise():
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, {
            "RATCHET_GUARD": "check-tests-have-checks.py", "TEST_FILES": r"^tests/.*_test\.py$",
            "TEST_CHECK": None, "TEST_COMMENT": "#.*$"}))
        proc = check(fresh({"tests/a_test.py": "assert 1\n"}, e=e), env=e)
        stlib.expect(proc, 1, "FAIL: предпосылка: страж check-tests-have-checks.py не судил: FAIL: предпосылка")

    def wrapped_missing():
        e = dict(env0, GUARDS_CONF=stlib.conf_file(base, {"RATCHET_GUARD": "check-nope.py"}))
        proc = check(fresh({"doc/a.txt": "ok\n"}, e=e), env=e)
        stlib.expect(proc, 1, "FAIL: предпосылка: страж check-nope.py из RATCHET_GUARD не найден")

    def not_git():
        folder = os.path.join(pr.mkdtemp(), "plain")
        os.makedirs(folder)
        stlib.expect(check(folder, "--root", folder), 1, "FAIL: предпосылка")

    pr.probe("законное", "чистое дерево, пустая база: зелёный, долг 0", legit_clean)
    pr.probe("законное", "нарушение с записью: долг напечатан, сдвиг строк ключ не меняет", legit_debt_and_drift)
    pr.probe("законное", "исправление вместе с удалением записи: долг меньше", legit_fix_with_entry_removed)
    pr.probe("законное", "RATCHET_GUARD=off и пустая база: судить нечего", legit_off)
    pr.probe("красная", "новое нарушение: адрес и ключ", red_new)
    pr.probe("красная", "подмена при том же счёте: красный на новом", red_substitution)
    pr.probe("красная", "запись убрана без исправления: нарушение снова новое", red_entry_removed_not_fixed)
    pr.probe("красная", "исправлено, запись оставлена: запись устарела", red_stale)
    pr.probe("красная", "правка нарушающей строки: новое и устаревшее", red_edited_line)
    pr.probe("красная", "запись с поддельным токеном: красный без значения", red_secret_entry)
    pr.probe("красная", "строка не по форме, без причины, повтор ключа", red_format)
    pr.probe("красная", "RATCHET_GUARD=off, а в базе запись", red_off_with_entries)
    pr.probe("иной-синтаксис", "одинаковые строки различаются #n", same_lines_numbered)
    pr.probe("иной-синтаксис", "режим индекса", index_mode)
    pr.probe("иной-синтаксис", "режим коммита: долг в файлах коммита, новое нарушение", commit_mode)
    pr.probe("иной-синтаксис", "run-all.sh не зовёт стража под храповиком, без храповика зовёт", run_all_skips_wrapped)
    pr.probe("мишень", "нет файла базы: мишень потеряна", lost_baseline)
    pr.probe("мишень", "оборачиваемый страж потерял мишень: красный", lost_wrapped_target)
    pr.probe("мишень", "оборачиваемый страж красный по предпосылке: красный", wrapped_premise)
    pr.probe("мишень", "оборачиваемый страж не найден: красный", wrapped_missing)
    pr.probe("мишень", "папка без git: красная предпосылка", not_git)
    return pr.done()


if __name__ == "__main__":
    sys.exit(main())
