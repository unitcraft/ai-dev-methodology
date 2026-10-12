# -*- coding: utf-8 -*-
"""Самотест установщика хуков install-hooks.sh.

Зачем: установщик пишет общую конфигурацию всех рабочих деревьев репозитория; тихая подмена чужой
    настройки или повторный запуск, который что-то меняет, - вред, который заметят не сразу.
Проверяет: в свежем клоне: core.hooksPath = GITHOOKS_DIR и ключ EXPECTED_EMAIL_KEY = user.email;
    повтор ничего не меняет и говорит об этом; без user.email - громкий отказ; иной core.hooksPath или иной
    адрес - отказ без изменений, с флагом --reset - замена; предупреждение о действующих хуках в .git/hooks;
    дерево без хуков, нет интерпретатора, не репозиторий - отказ; запуск из подкаталога и связанного дерева;
    в guards.conf нет целевой ветки - отказ с подсказкой; COMMIT_AUTHOR_EMAIL_CHECK=no - адрес не нужен и не
    пишется.
Не проверяет: работу самих хуков (test-pre-commit.py, test-commit-msg.py, test-pre-push.py).
Правило: README комплекта, «Установка».
"""
import sys

sys.dont_write_bytecode = True

import os

import stlib


def main():
    pr = stlib.Probes("install-hooks")
    base = pr.mkdtemp()
    env = stlib.isolated_env(base)
    source = stlib.hooked_repo(base, env, name="source", install=False)
    counter = [0]

    def clone():
        counter[0] += 1
        path = os.path.join(base, "clone%d" % counter[0])
        stlib.git(base, env, "clone", "-q", source, path)
        return path

    def install(r, *args, **kw):
        e = kw.get("env", env)
        return stlib.run(("sh", stlib.INSTALLER) + args, cwd=kw.get("cwd", r), env=e)

    def cfg(r, key):
        return stlib.git(r, env, "config", "--get", key, check=False).out.strip()

    def fresh_clone():
        r = clone()
        assert cfg(r, "core.hooksPath") == "" and cfg(r, stlib.EMAIL_KEY) == ""
        proc = install(r)
        assert proc.returncode == 0, proc.out + proc.err
        assert cfg(r, "core.hooksPath") == stlib.GITHOOKS_DIR, cfg(r, "core.hooksPath")
        assert cfg(r, stlib.EMAIL_KEY) == "author@example.test"
        assert "общая для всех рабочих деревьев" in proc.out, proc.out

    def repeat_changes_nothing():
        r = clone()
        install(r)
        snapshot = open(os.path.join(r, ".git", "config"), "rb").read()
        proc = install(r)
        assert proc.returncode == 0 and "ничего не изменилось" in proc.out, proc.out
        assert open(os.path.join(r, ".git", "config"), "rb").read() == snapshot, "конфигурация изменилась"

    def no_user_email():
        r = clone()
        empty = os.path.join(base, "emptycfg")
        with open(empty, "w", encoding="utf-8") as handle:
            handle.write("[user]\n\tname = No Email\n")
        e = dict(env, GIT_CONFIG_GLOBAL=empty)
        proc = install(r, env=e)
        assert proc.returncode == 1 and "user.email" in proc.out, proc.out
        assert cfg(r, "core.hooksPath") == ""

    def other_hooks_path():
        r = clone()
        stlib.git(r, env, "config", "core.hooksPath", "my/own/hooks")
        proc = install(r)
        assert proc.returncode == 1 and "--reset" in proc.out, proc.out
        assert cfg(r, "core.hooksPath") == "my/own/hooks" and cfg(r, stlib.EMAIL_KEY) == ""
        proc = install(r, "--reset")
        assert proc.returncode == 0 and cfg(r, "core.hooksPath") == stlib.GITHOOKS_DIR, proc.out

    def other_expected_email():
        r = clone()
        stlib.git(r, env, "config", stlib.EMAIL_KEY, "old@example.test")
        proc = install(r)
        assert proc.returncode == 1 and "--reset" in proc.out, proc.out
        assert cfg(r, stlib.EMAIL_KEY) == "old@example.test"
        proc = install(r, "--reset")
        assert proc.returncode == 0 and cfg(r, stlib.EMAIL_KEY) == "author@example.test"

    def live_hooks_warning():
        r = clone()
        hooks = os.path.join(r, ".git", "hooks")
        with open(os.path.join(hooks, "pre-commit"), "w", encoding="utf-8", newline="\n") as handle:
            handle.write("#!/bin/sh\nexit 0\n")
        proc = install(r)
        assert proc.returncode == 0 and "предупреждение" in proc.out and "pre-commit" in proc.out, proc.out

    def tree_without_hooks():
        r = clone()
        stlib.rmtree(os.path.join(r, *stlib.GITHOOKS_DIR.split("/")))
        proc = install(r)
        assert proc.returncode == 1 and "нет хука" in proc.out, proc.out
        assert cfg(r, "core.hooksPath") == ""

    def no_interpreter():
        r = clone()
        e = dict(env, GUARDS_PYTHON_CANDIDATES="no-such-python")
        proc = install(r, env=e)
        assert proc.returncode == 1 and "Python" in proc.out + proc.err, proc.out + proc.err
        assert cfg(r, "core.hooksPath") == ""

    def not_a_repository():
        plain = os.path.join(base, "plain")
        os.makedirs(plain)
        proc = stlib.run(("sh", os.path.join(source, *stlib.INSTALLER.split("/"))), cwd=plain, env=env)
        assert proc.returncode == 1 and "FAIL" in proc.out, proc.out

    def from_subdir():
        r = clone()
        sub = os.path.join(r, "doc")
        os.makedirs(sub, exist_ok=True)
        proc = stlib.run(("sh", "../" + stlib.INSTALLER), cwd=sub, env=env)
        assert proc.returncode == 0 and cfg(r, "core.hooksPath") == stlib.GITHOOKS_DIR, proc.out + proc.err

    def from_linked_worktree():
        r = clone()
        wt = os.path.join(base, "iwt%d" % counter[0])
        stlib.git(r, env, "worktree", "add", "-q", "-b", "side", wt)
        proc = install(wt)
        assert proc.returncode == 0, proc.out + proc.err
        assert cfg(r, "core.hooksPath") == stlib.GITHOOKS_DIR, "настройка общая для деревьев"
        proc = install(r)
        assert "ничего не изменилось" in proc.out, proc.out

    def conf_without_main_branch():
        r = clone()
        e = dict(env, GUARDS_CONF=stlib.conf_file(base, {"MAIN_BRANCH": None}))
        proc = install(r, env=e)
        assert proc.returncode == 1 and "нет обязательного ключа MAIN_BRANCH" in proc.out + proc.err, proc.out + proc.err
        assert cfg(r, "core.hooksPath") == ""

    def email_check_off():
        r = clone()
        empty = os.path.join(base, "emptycfg2")
        with open(empty, "w", encoding="utf-8") as handle:
            handle.write("[user]\n\tname = No Email\n")
        e = dict(env, GIT_CONFIG_GLOBAL=empty, GUARDS_CONF=stlib.conf_file(base, {"COMMIT_AUTHOR_EMAIL_CHECK": "no"}))
        proc = install(r, env=e)
        assert proc.returncode == 0 and cfg(r, "core.hooksPath") == stlib.GITHOOKS_DIR, proc.out + proc.err
        assert cfg(r, stlib.EMAIL_KEY) == "", "адрес записан при выключенной сверке"

    pr.probe("законное", "свежий клон: хуки подключены, адрес записан", fresh_clone)
    pr.probe("законное", "COMMIT_AUTHOR_EMAIL_CHECK=no: адрес не нужен и не пишется", email_check_off)
    pr.probe("законное", "повтор ничего не меняет и говорит об этом", repeat_changes_nothing)
    pr.probe("законное", "запуск из подкаталога", from_subdir)
    pr.probe("законное", "связанное рабочее дерево: настройка общая", from_linked_worktree)
    pr.probe("законное", "действующие хуки в .git/hooks - предупреждение", live_hooks_warning)
    pr.probe("красная", "без user.email - громкий отказ", no_user_email)
    pr.probe("красная", "иной core.hooksPath: отказ, --reset заменяет", other_hooks_path)
    pr.probe("красная", "иной адрес автора: отказ, --reset заменяет", other_expected_email)
    pr.probe("иной-синтаксис", "дерево без папки хуков - отказ", tree_without_hooks)
    pr.probe("мишень", "нет рабочего интерпретатора - отказ", no_interpreter)
    pr.probe("мишень", "не репозиторий - отказ", not_a_repository)
    pr.probe("мишень", "в guards.conf нет целевой ветки - отказ с подсказкой", conf_without_main_branch)
    return pr.done()


if __name__ == "__main__":
    sys.exit(main())
