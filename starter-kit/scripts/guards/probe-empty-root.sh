#!/bin/sh
# Зачем: пустота не бывает чистой. Страж, который на пустом корне печатает «ок», проверяет не то, что
#     нужно: переименование папки или потеря мишени сделали бы его вечно зелёным.
# Проверяет: каждого стража дерева (check-* и guard-secrets.py в режиме дерева) на трёх мишенях: пустой
#     репозиторий git, папка без git, пустой каркас (репозиторий с пустыми папками doc/ и tests/). Ни один
#     вердикт не должен начинаться с «ок:»: допустимы «FAIL: мишень потеряна», «FAIL: предпосылка» и
#     «судить нечего: ...». Печатает таблицу страж, мишень, вердикт, код возврата.
# Не проверяет: страж сообщения (пустое сообщение проверяет его самотест) и стража индекса на пустом индексе
#     (его вердикт «судить нечего» проверяет test-guard-secrets.py).
# Правило: docs/guards.md (README комплекта), «Пустота не бывает чистой».
#
# Использование: sh <папка стражей>/probe-empty-root.sh [--dir <папка стражей>]
# Список запрещённых имён для проб - временный, выдуманный: настоящий список не нужен и не читается
# (переменная с путём к нему - PRIVATE_NAMES_FILE_VAR из guards.conf). Стражи судят по параметрам проекта:
# страж, выключенный параметром (off), печатает «судить нечего» с этой причиной.
set -u

here=$(cd "$(dirname "$0")" && pwd)
# shellcheck disable=SC1091
. "$here/lib/find-python.sh"
find_python || exit 1

guards_dir=$here
while [ $# -gt 0 ]; do
  case "$1" in
    --dir) guards_dir=$2; shift 2 ;;
    *) echo "FAIL: предпосылка: неизвестный аргумент $1"; exit 2 ;;
  esac
done

tmp=$(mktemp -d 2>/dev/null) || { echo "FAIL: предпосылка: не создать временную папку"; exit 1; }
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

names_var=$($PYTHON "$here/lib/conf.py" get PRIVATE_NAMES_VAR) || { echo "FAIL: предпосылка: параметры стражей не читаются"; exit 1; }
file_var=$($PYTHON "$here/lib/conf.py" get PRIVATE_NAMES_FILE_VAR) || { echo "FAIL: предпосылка: параметры стражей не читаются"; exit 1; }
printf 'zorblax-demo\n' > "$tmp/names.txt"
unset "$names_var"
eval "$file_var=\"\$tmp/names.txt\""
export "${file_var?}"

mkdir -p "$tmp/t1" "$tmp/t2" "$tmp/t3"
git -C "$tmp/t1" init -q 2>/dev/null
git -C "$tmp/t3" init -q 2>/dev/null
mkdir -p "$tmp/t3/doc" "$tmp/t3/tests"

probes=0
bad=0
# порядок не зависит от локали: вывод двух прогонов под разными локалями совпадает построчно
for g in "$guards_dir"/check-*.py "$guards_dir"/check-*.sh "$guards_dir"/guard-secrets.py; do
  [ -f "$g" ] && printf '%s\n' "$g"
done | LC_ALL=C sort > "$tmp/list"
while IFS= read -r guard; do
  name=$(basename "$guard")
  for target in t1 t2 t3; do
    case "$target" in
      t1) label="пустой репозиторий git" ;;
      t2) label="папка без git" ;;
      t3) label="пустой каркас" ;;
    esac
    extra=
    [ "$name" = "guard-secrets.py" ] && extra=--tree
    case "$guard" in
      *.py) $PYTHON "$guard" --root "$tmp/$target" $extra > "$tmp/out" 2>&1 < /dev/null ;;
      *) sh "$guard" --root "$tmp/$target" $extra > "$tmp/out" 2>&1 < /dev/null ;;
    esac
    rc=$?
    verdict=$(tail -n 1 "$tmp/out")
    probes=$((probes + 1))
    echo "$name | $label | $verdict | код $rc"
    case "$verdict" in
      "ок:"*) bad=$((bad + 1)); echo "  ^ ПРОВАЛ: «ок» на пустоте" ;;
      "судить нечего:"*|"FAIL"*) ;;
      *) bad=$((bad + 1)); echo "  ^ ПРОВАЛ: вердикт не из допустимых" ;;
    esac
  done
done < "$tmp/list"

if [ "$probes" -eq 0 ]; then
  echo "FAIL: мишень потеряна: нет ни одного стража дерева"
  exit 1
fi
if [ "$bad" -gt 0 ]; then
  echo "FAIL: на пустоте нет красного или «судить нечего»: $bad из $probes запусков"
  exit 1
fi
echo "ок: осмотрено $probes запусков, «ок» на пустоте нет"
