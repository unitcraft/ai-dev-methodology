#!/bin/sh
# Зачем: приёмка комплекта проектом, который его берёт. Самотесты гоняют стражей в одноразовых репозиториях,
#     но рядом с исходником комплекта; здесь комплект ставится в чистый новый репозиторий по шагам README,
#     без единого файла источника, и стражи судят этот новый репозиторий.
# Проверяет: каждый кейс — отдельный свежий репозиторий во временной папке: комплект скопирован в корень,
#     README положен в docs/guards.md, биты исполнения поставлены, хуки подключены установщиком. Кейсы:
#     честный вход зелёный (коммит и пуш через хуки, стражи, мета-проверка, пустой корень, ссылки файлов
#     проекта на docs/guards.md ведут в существующие разделы); секрет, путь машины и запрещённое имя —
#     красный коммит с адресом; храповик: подмена нарушения при том же счёте, откат исправленного без записи
#     и исправленное с оставленной записью — красные; потерянная мишень — не «ок»; убранный обязательный
#     ключ guards.conf — красный с подсказкой; из коробки — зелёный без «ок» храповика; таблица «Параметры
#     проекта» совпадает с ключами lib/conf.py. Печатает таблицу «кейс -> вердикт»; любое расхождение
#     с ожидаемым — общий красный вердикт с названиями кейсов.
# Не проверяет: задание CI на сервере и хук агента в настоящем агенте (их синтаксис принадлежит продуктам,
#     README, «Привязки к окружению»); самотесты и доказательство красного в новом репозитории — только
#     с флагом --full (прогон долгий).
# Правило: README комплекта, «Приёмка переносимости».
#
# Использование: sh verify-portability.sh [--worktree] [--full] [--only <начало имени кейса>]
# По умолчанию комплект берётся из закоммиченного HEAD (git archive папки комплекта): принимается то, что
# лежит в истории. --worktree — из рабочей копии (проверка правки до коммита). Скрипт — инструмент осмотра
# комплекта: в новый проект он не копируется. Все образцы нарушений выдуманы и собираются при прогоне.
set -u

here=$(cd "$(dirname "$0")" && pwd)

source_mode=archive
full=0
only=
while [ $# -gt 0 ]; do
  case "$1" in
    --worktree) source_mode=worktree; shift ;;
    --full) full=1; shift ;;
    --only) [ $# -ge 2 ] || { echo "FAIL: предпосылка: --only без имени кейса"; exit 2; }; only=$2; shift 2 ;;
    *) echo "FAIL: предпосылка: неизвестный аргумент $1"; exit 2 ;;
  esac
done

tmp=$(mktemp -d 2>/dev/null) || { echo "FAIL: предпосылка: не создать временную папку"; exit 1; }
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
kit="$tmp/kit"
mkdir -p "$kit"

# --- Комплект: из истории или из рабочей копии ------------------------------------------------------
if [ "$source_mode" = archive ]; then
  prefix=$(git -C "$here" rev-parse --show-prefix 2>/dev/null) || {
    echo "FAIL: предпосылка: папка комплекта не в репозитории git; запустите с --worktree"
    exit 1
  }
  prefix=${prefix%/}
  top=$(git -C "$here" rev-parse --show-toplevel) || exit 1
  # архив — от корня репозитория: запущенный из подпапки, git archive ещё раз сужает дерево до неё
  if ! git -C "$top" archive --format=tar "HEAD${prefix:+:$prefix}" > "$tmp/kit.tar" 2>"$tmp/archive.err"; then
    cat "$tmp/archive.err"
    echo "FAIL: предпосылка: комплекта нет в HEAD (не закоммичен?); закоммитьте или запустите с --worktree"
    exit 1
  fi
  tar -xf "$tmp/kit.tar" -C "$kit" || { echo "FAIL: предпосылка: архив комплекта не распаковался"; exit 1; }
else
  cp -R "$here/." "$kit/" || { echo "FAIL: предпосылка: комплект не скопировался"; exit 1; }
  find "$kit" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
fi
for need in README.md LICENSE-APACHE LICENSE-MIT scripts/guards/guards.conf scripts/guards/lib/find-python.sh scripts/install-hooks.sh; do
  [ -f "$kit/$need" ] || { echo "FAIL: мишень потеряна: в комплекте нет $need"; exit 1; }
done

# shellcheck disable=SC1091
. "$kit/scripts/guards/lib/find-python.sh"
find_python || exit 1
conf_get() {
  $PYTHON "$kit/scripts/guards/lib/conf.py" get "$1" || { echo "FAIL: предпосылка: guards.conf комплекта не читается"; exit 1; }
}
main=$(conf_get MAIN_BRANCH) || exit 1
names_var=$(conf_get PRIVATE_NAMES_VAR) || exit 1
names_file_var=$(conf_get PRIVATE_NAMES_FILE_VAR) || exit 1

# --- Среда без настроек хозяина: глобальный git, переменные CI и стражей, списки имён ----------------
for v in $(env | sed -n 's/^\(GIT_[A-Za-z0-9_]*\)=.*/\1/p; s/^\(GUARDS_[A-Za-z0-9_]*\)=.*/\1/p'); do
  unset "$v"
done
unset CI "$names_var" "$names_file_var"
HOME="$tmp/home"
USERPROFILE=$HOME
XDG_CONFIG_HOME="$HOME/xdg"
GIT_CONFIG_GLOBAL="$HOME/gitconfig"
GIT_CONFIG_NOSYSTEM=1
GIT_TERMINAL_PROMPT=0
export HOME USERPROFILE XDG_CONFIG_HOME GIT_CONFIG_GLOBAL GIT_CONFIG_NOSYSTEM GIT_TERMINAL_PROMPT
mkdir -p "$HOME"
printf '[user]\n\tname = Portability Probe\n\temail = probe@example.test\n[init]\n\tdefaultBranch = %s\n[core]\n\tautocrlf = false\n[commit]\n\tgpgsign = false\n' "$main" > "$GIT_CONFIG_GLOBAL"

# Выдуманные образцы нарушений: собираются здесь, в тексте скрипта их нет целиком.
fake_name="qwyx""zz-fake-org"
fake_token="gh""p_""Fake0Token1Sample2Only3x"
fake_path="E"":/""Work""/""fake-project""/notes.txt"
fffd=$(printf '\357\277\275')
eval "$names_var=\$fake_name"
export "${names_var?}"

# Сверка ссылок «docs/guards.md …, «раздел»» из файлов проекта с заголовками и абзацами «**Раздел.**».
REFS_PY='
import re, subprocess, sys
doc = "docs/guards.md"
text = open(doc, encoding="utf-8").read()
names = set(re.findall(r"(?m)^#+\s*(.+?)\s*$", text)) | set(re.findall(r"(?m)^\*\*([^*]+?)\.\*\*", text))
files = subprocess.run(["git", "ls-files", "--", "scripts", ".github", ".claude"],
                       stdout=subprocess.PIPE).stdout.decode("utf-8").split()
refs, bad = 0, []
for path in files:
    for number, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        if doc not in line:
            continue
        for name in re.findall(r"«([^»]+)»", line.split(doc, 1)[1]):
            refs += 1
            if name not in names:
                bad.append("%s:%d: нет раздела «%s»" % (path, number, name))
for line in bad:
    print(line)
if not refs:
    print("FAIL: мишень потеряна: ни одной ссылки на " + doc)
    sys.exit(1)
if bad:
    print("FAIL: ссылок на %s без раздела: %d из %d" % (doc, len(bad), refs))
    sys.exit(1)
print("ок: ссылок на %s с разделом: %d" % (doc, refs))
'

# Сверка таблицы «Параметры проекта» в docs/guards.md с ключами, которые разбирает lib/conf.py: каждый ключ
# описан, обязательность и умолчание совпадают, лишних строк нет.
PARAMS_PY='
import re, sys
sys.path.insert(0, "scripts/guards/lib")
import conf
rows = {}
for line in open("docs/guards.md", encoding="utf-8"):
    m = re.match(r"^\| `([A-Z][A-Z0-9_]*)` \| ([^|]+) \| ((?:[^|\\]|\\\|)+) \|", line)
    if m:
        rows[m.group(1)] = (m.group(2).strip(), m.group(3).strip().replace("\\|", "|"))
bad = []
for key, (required, default, _, _) in sorted(conf.SPEC.items()):
    if key in conf.CONDITIONAL:
        want_req = "если `%s` не `%s`" % conf.CONDITIONAL[key]
    else:
        want_req = "да" if required else "нет"
    want_def = "—" if default is None else "`%s`" % default
    if key not in rows:
        bad.append("%s: нет строки в таблице" % key)
    elif rows[key] != (want_req, want_def):
        bad.append("%s: в таблице %r, в conf.py %r" % (key, rows[key], (want_req, want_def)))
for key in sorted(set(rows) - set(conf.SPEC)):
    bad.append("%s: в таблице, но conf.py его не разбирает" % key)
for line in bad:
    print(line)
if not conf.SPEC or not rows:
    print("FAIL: мишень потеряна: нет ключей в conf.py или строк в таблице")
    sys.exit(1)
if bad:
    print("FAIL: перечень параметров расходится: %d" % len(bad))
    sys.exit(1)
print("ок: ключей conf.py %d, строк таблицы %d, расхождений 0" % (len(conf.SPEC), len(rows)))
'

# --- Помощники кейса -------------------------------------------------------------------------------
# new_repo <кейс>: свежий репозиторий, комплект в корне, README в docs/guards.md (шаг 1 README).
new_repo() {
  repo="$tmp/case-$n_case"
  mkdir -p "$repo" && git -C "$repo" init -q || return 1
  cp -R "$kit/." "$repo/" || return 1
  rm -f "$repo/README.md" "$repo/verify-portability.sh"
  mkdir -p "$repo/docs" && cp "$kit/README.md" "$repo/docs/guards.md"
}
# stage_kit: шаг 4 README — файлы в git с битами исполнения.
stage_kit() {
  (cd "$repo" && git add -- scripts .github .claude .gitattributes docs/guards.md LICENSE-APACHE LICENSE-MIT &&
    git add --chmod=+x -- scripts/githooks/* scripts/*.sh scripts/guards/*.sh scripts/guards/lib/*.sh scripts/guards/selftest/*.sh)
}
# install_hooks: шаг 5 README.
install_hooks() {
  (cd "$repo" && sh scripts/install-hooks.sh) > "$repo.install" 2>&1
}
# set_conf <КЛЮЧ> [значение]: заменить ключ в guards.conf нового репозитория; без значения — убрать.
set_conf() {
  c="$repo/scripts/guards/guards.conf"
  grep -v "^$1=" "$c" > "$c.new"
  [ $# -ge 2 ] && printf '%s=%s\n' "$1" "$2" >> "$c.new"
  mv "$c.new" "$c"
}
# in_repo <файл вывода> <команда...>: выполнить в корне нового репозитория, код — в rc.
in_repo() {
  out=$1
  shift
  (cd "$repo" && "$@") > "$out" 2>&1 < /dev/null
  rc=$?
}
commit() {  # commit <файл вывода> <сообщение>: коммит через хуки с подписью автора
  in_repo "$1" git commit -q -s -m "$2"
}
head_rev() { git -C "$repo" rev-parse -q --verify HEAD 2>/dev/null || echo none; }
# ratchet_key <файл>: ключ для базы новой находки (храповик печатает его в красном прогоне)
ratchet_key() {
  in_repo "$repo.key" $PYTHON scripts/guards/check-ratchet.py --index
  sed -n 's/.*ключ для базы: \([^ ]*\).*/\1/p' "$repo.key" | grep -F ":$1:" | head -n 1
}

why=
need() { why="${why:+$why; }$1"; }
want_rc() {  # want_rc ok|red <что>
  case "$1" in
    ok) [ "$rc" -eq 0 ] || need "$2: ожидался код 0, получен $rc" ;;
    red) [ "$rc" -ne 0 ] || need "$2: ожидался красный, получен код 0" ;;
  esac
}
want_has() { grep -F -q -- "$2" "$1" || need "$(basename "$1"): нет «$2»"; }
want_not() { if grep -F -q -- "$2" "$1"; then need "$(basename "$1"): лишнее «$2»"; fi; }
want_last() {  # want_last <файл> <начало последней строки>
  last=$(grep -v '^[[:space:]]*$' "$1" | tail -n 1)
  case "$last" in "$2"*) ;; *) need "$(basename "$1"): последняя строка «$last», ожидалось «$2…»" ;; esac
}
# set_up [ключи храповика]: новый репозиторий с поставленным комплектом и первым коммитом; ошибка — в why.
set_up() {
  new_repo || { need "комплект не скопирован в новый репозиторий"; return 1; }
  [ $# -gt 0 ] && "$@"
  stage_kit || { need "шаг 4 README (git add с битами исполнения) не выполнился"; return 1; }
  install_hooks || { need "установщик хуков отказал: $(tail -n 1 "$repo.install")"; return 1; }
  commit "$repo.init" "Add starter kit of guards"
  [ "$rc" -eq 0 ] || { need "первый коммит комплекта отклонён хуками: $(grep -m 1 'FAIL' "$repo.init")"; return 1; }
}
# debt_a: храповик над гигиеной текста, в базе — запись о нарушении в docs/a.md (принятый долг)
debt_a() {
  set_conf RATCHET_GUARD check-text-hygiene.py
  printf '# A\n\nold text %s here\n' "$fffd" > "$repo/docs/a.md"
  stage_kit && git -C "$repo" add -- docs/a.md || return 1
  key=$(ratchet_key docs/a.md)
  if [ -z "$key" ]; then
    need "храповик не напечатал ключ для docs/a.md"
    return 1
  fi
  printf '%s: принятый долг пробы переносимости\n' "$key" >> "$repo/scripts/guards/ratchet.txt"
}

# --- Кейсы -----------------------------------------------------------------------------------------
case_honest() {
  set_up || return
  printf '# Notes\n\nSee [the guards](guards.md).\n' > "$repo/docs/notes.md"
  git -C "$repo" add -- docs/notes.md
  commit "$repo.c1" "Add notes"
  want_rc ok "коммит честного файла"
  git init -q --bare "$repo-remote.git" && git -C "$repo" remote add origin "$repo-remote.git"
  in_repo "$repo.push" git push -q origin "$main"
  want_rc ok "пуш через pre-push"
  in_repo "$repo.all" sh scripts/guards/run-all.sh --ci
  want_rc ok "run-all.sh --ci"
  want_last "$repo.all" "итого: "
  want_has "$repo.all" "FAIL 0"
  want_not "$repo.all" "-> FAIL"
  in_repo "$repo.tree" $PYTHON scripts/guards/guard-secrets.py --tree
  want_rc ok "guard-secrets.py --tree"
  want_last "$repo.tree" "ок: осмотрено "
  in_repo "$repo.wiring" $PYTHON scripts/guards/check-wiring.py
  want_rc ok "check-wiring.py"
  want_last "$repo.wiring" "ок: осмотрено "
  in_repo "$repo.empty" sh scripts/guards/probe-empty-root.sh
  want_rc ok "probe-empty-root.sh"
  # README лежит в docs/guards.md: каждая ссылка на него из файлов проекта ведёт в существующий раздел
  in_repo "$repo.refs" $PYTHON -c "$REFS_PY"
  want_rc ok "ссылки на docs/guards.md"
  want_last "$repo.refs" "ок: ссылок на docs/guards.md "
  if [ "$full" -eq 1 ]; then
    in_repo "$repo.st" sh scripts/guards/selftest/run-selftests.sh
    want_rc ok "run-selftests.sh"
    want_last "$repo.st" "ок: осмотрено "
    in_repo "$repo.prove" sh scripts/guards/prove-red.sh
    want_rc ok "prove-red.sh"
  fi
}

# Лицензии кода комплекта должны попасть в корень нового проекта и первый коммит.
case_licenses() {
  set_up || return
  for license in LICENSE-APACHE LICENSE-MIT; do
    if [ ! -f "$repo/$license" ]; then
      need "в корне нового репозитория нет $license"
      continue
    fi
    if ! git -C "$repo" ls-files --error-unmatch -- "$license" >/dev/null 2>&1; then
      need "$license не добавлен в git"
      continue
    fi
    if ! git -C "$repo" cat-file -e "HEAD:$license" 2>/dev/null; then
      need "$license не закоммичен"
    fi
  done
}

# leak <образец> <адрес и правило>: красный коммит с адресом, без значения образца, история не сдвинулась
leak() {
  set_up || return
  before=$(head_rev)
  printf 'first line\nsee %s now\n' "$1" > "$repo/docs/leak.md"
  git -C "$repo" add -- docs/leak.md
  commit "$repo.c1" "Add leak sample"
  want_rc red "коммит с нарушением"
  want_has "$repo.c1" "docs/leak.md:2"
  want_has "$repo.c1" "$2"
  want_not "$repo.c1" "$1"
  [ "$(head_rev)" = "$before" ] || need "коммит с нарушением попал в историю"
}
case_secret() { leak "$fake_token" "docs/leak.md:2: access-token"; }
case_path() { leak "$fake_path" "docs/leak.md:2: machine-path"; }
case_name() { leak "$fake_name" "docs/leak.md:2: forbidden-name"; }

case_swap() {
  set_up debt_a || return
  # исправить a.md и убрать запись, внести такое же нарушение в b.md: нарушений по-прежнему одно
  printf '# A\n\nold text here\n' > "$repo/docs/a.md"
  grep -v '^check-text-hygiene.py:docs/a.md:' "$repo/scripts/guards/ratchet.txt" > "$repo/r.new"
  mv "$repo/r.new" "$repo/scripts/guards/ratchet.txt"
  printf '# B\n\nnew text %s here\n' "$fffd" > "$repo/docs/b.md"
  git -C "$repo" add -- docs/a.md docs/b.md scripts/guards/ratchet.txt
  commit "$repo.c1" "Swap one violation for another"
  want_rc red "коммит с подменой"
  want_has "$repo.c1" "docs/b.md:3: ratchet-new"
}

case_revert() {
  set_up debt_a || return
  printf '# A\n\nold text here\n' > "$repo/docs/a.md"
  grep -v '^check-text-hygiene.py:docs/a.md:' "$repo/scripts/guards/ratchet.txt" > "$repo/r.new"
  mv "$repo/r.new" "$repo/scripts/guards/ratchet.txt"
  git -C "$repo" add -- docs/a.md scripts/guards/ratchet.txt
  commit "$repo.c1" "Fix docs/a.md and drop its record"
  want_rc ok "коммит исправления с удалением записи"
  in_repo "$repo.co" git checkout -q HEAD~1 -- docs/a.md
  commit "$repo.c2" "Bring old docs/a.md back"
  want_rc red "коммит отката без записи"
  want_has "$repo.c2" "docs/a.md:3: ratchet-new"
}

case_stale() {
  set_up debt_a || return
  printf '# A\n\nold text here\n' > "$repo/docs/a.md"
  git -C "$repo" add -- docs/a.md
  commit "$repo.c1" "Fix docs/a.md, keep the record"
  want_rc red "коммит исправления с оставленной записью"
  want_has "$repo.c1" "ratchet-stale"
  want_has "$repo.c1" "запись устарела"
}

case_lost_docs() {
  set_up || return
  set_conf TASK_DOC_RULE 'first-line ^docs/tasks/[^/]+/spec\.md$ ^Статус: (черновик|утверждено)'
  in_repo "$repo.all" sh scripts/guards/run-all.sh
  want_rc red "run-all.sh"
  want_has "$repo.all" "check-task-docs.py -> FAIL: мишень потеряна"
  want_not "$repo.all" "check-task-docs.py -> ок"
}

case_lost_base() {
  set_up || return
  set_conf RATCHET_GUARD check-text-hygiene.py
  rm -f "$repo/scripts/guards/ratchet.txt"
  in_repo "$repo.all" sh scripts/guards/run-all.sh
  want_rc red "run-all.sh"
  want_has "$repo.all" "check-ratchet.py -> FAIL: мишень потеряна"
  want_not "$repo.all" "check-ratchet.py -> ок"
}

case_no_key() {
  set_up || return
  set_conf COMMIT_SIGNOFF
  in_repo "$repo.all" sh scripts/guards/run-all.sh
  want_rc red "run-all.sh"
  want_has "$repo.all" "нет обязательного ключа COMMIT_SIGNOFF"
  want_has "$repo.all" "«Параметры проекта»"
  printf 'x\n' > "$repo/docs/x.md"
  git -C "$repo" add -- docs/x.md
  before=$(head_rev)
  commit "$repo.c1" "Commit without the key"
  want_rc red "коммит без ключа"
  want_has "$repo.c1" "нет обязательного ключа COMMIT_SIGNOFF"
  [ "$(head_rev)" = "$before" ] || need "коммит без ключа попал в историю"
}

case_out_of_box() {
  set_up || return
  in_repo "$repo.r" $PYTHON scripts/guards/check-ratchet.py
  want_rc ok "check-ratchet.py"
  want_last "$repo.r" "судить нечего: храповик не подключён"
  in_repo "$repo.all" sh scripts/guards/run-all.sh
  want_rc ok "run-all.sh"
  want_has "$repo.all" "check-ratchet.py -> судить нечего"
  want_not "$repo.all" "под храповиком; долг"
  want_has "$repo.all" "FAIL 0"
}

case_params() {
  new_repo || { need "комплект не скопирован в новый репозиторий"; return; }
  in_repo "$repo.params" $PYTHON -c "$PARAMS_PY"
  want_rc ok "сверка параметров"
  want_last "$repo.params" "ок: ключей conf.py "
}

# --- Прогон ----------------------------------------------------------------------------------------
n_case=0
n_bad=0
bad=
: > "$tmp/table"
run_case() {  # run_case <имя> <функция>
  if [ -n "$only" ]; then
    case "$1" in "$only"*) ;; *) return 0 ;; esac
  fi
  n_case=$((n_case + 1))
  why=
  "$2"
  if [ -z "$why" ]; then
    printf '%s -> ок\n' "$1" >> "$tmp/table"
  else
    n_bad=$((n_bad + 1))
    bad="${bad:+$bad, }$1"
    printf '%s -> РАСХОЖДЕНИЕ: %s\n' "$1" "$why" >> "$tmp/table"
    echo "== $1: вывод"
    for f in "$repo".*; do
      [ -f "$f" ] && { echo "-- ${f##*.}"; tail -n 15 "$f"; }
    done
  fi
}

run_case "а-честный-вход" case_honest
run_case "а2-лицензии-в-корне-и-коммите" case_licenses
run_case "б1-секрет" case_secret
run_case "б2-путь-машины" case_path
run_case "б3-запрещённое-имя" case_name
run_case "в-подмена-при-том-же-счёте" case_swap
run_case "г-откат-без-записи" case_revert
run_case "д-исправленное-с-записью" case_stale
run_case "е1-мишень-документов-задач" case_lost_docs
run_case "е2-мишень-базы-храповика" case_lost_base
run_case "ж-нет-обязательного-ключа" case_no_key
run_case "з-из-коробки" case_out_of_box
run_case "и-перечень-параметров" case_params

echo "кейс -> вердикт (комплект: $source_mode)"
cat "$tmp/table"
if [ "$n_case" -eq 0 ]; then
  echo "FAIL: мишень потеряна: ни один кейс не начинается с «$only»"
  exit 1
fi
if [ "$n_bad" -gt 0 ]; then
  echo "FAIL: приёмка переносимости: расхождение в $n_bad из $n_case: $bad"
  exit 1
fi
echo "ок: приёмка переносимости: кейсов $n_case, расхождений 0"
