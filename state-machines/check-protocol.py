#!/usr/bin/env python3
"""Прогонщик набора проверок протокола вызова стейт-машин (`state-machine-call-protocol.md`, раздел H).

Зачем: набор H задан блоками JSON-строк, но без исполнителя соответствие проверялось бы вручную. Скрипт играет
«проверяющую сторону» — вызывающего: запускает проверяемую программу дочерним процессом (привязка J: стандартные
ввод и вывод, JSON Lines), шлёт ей строки случаев и сверяет ответы с критериями.
Строки случаев берутся из блоков markdown раздела H (файл протокола разбирается при каждом запуске), в код они
не скопированы; критерий каждого случая записан кодом по тексту случая («Критерий:»).

Режимы:
  python state-machines/check-protocol.py -- <команда запуска программы...>   проверка получателя
  python state-machines/check-protocol.py --reference                         встроенный эталонный получатель
  python state-machines/check-protocol.py --selftest                          самопроверка мутациями
Необязательно: `--cases C5,C6` — только эти случаи. Из корня: `python state-machines/check-protocol.py -- python
state-machines/check-protocol.py --reference` — набор исполним без стороннего получателя.

Что проверяет (получатель, колонка «Проверяет» таблицы H с «П»): C1, C2, C3 (если сторона `agent` открыта), C4–C13,
C17, C18, C21, C22, C24, C26, C28, C32–C37 — проводная часть критериев; проверочные стороны `echo`, `wait`, `refuse`
по условию H.3. Сигнальные случаи (C10–C13, П*) идут, только если получатель называет `signal` в `methods`.
Итог по случаю: «ок», «ПРОВАЛ», «частично» (проводная часть проверена, строка журнала не наблюдается — условие H.4),
«пропущено: причина». «Пропущено» и «частично» зелёными не считаются: код возврата 0, если нет «ПРОВАЛ», но они в сводке.
Чего не проверяет:
  - строки журнала получателя (H.4: формат не задан, журнал снаружи не виден);
  - C20 (перезапуск получателя): нужно хранилище состояния и управляемый перезапуск, режим `--` их не задаёт;
  - C3 без стороны `agent`: в условиях H.3 её нет;
  - случаи проверки вызывающего (В): C14–C16, C19, C23, C25, C27, C29–C31, C38 — прогонщик играет только вызывающего;
  - режим «долгоживущий процесс» и «процесс на запрос» не различается: C32 запускает программу дважды подряд;
  - значение ответа «не позже срока» и нагрузку: сроки ожидания фиксированы, медленная программа может дать ложный провал.
Код возврата 1 при любом «ПРОВАЛ» (и в самопроверке — при непойманной мутации); вывод — UTF-8.
"""
import io, json, os, queue, re, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROTOCOL = os.path.join(HERE, 'state-machine-call-protocol.md')
FAIL_CODES = ['NoResult', 'ModelRefused', 'ConnectionLost', 'FormNotFixed', 'Timeout', 'StoppedByHuman',
              'CeilingReached', 'Cancelled', 'MaxTokens', 'MaxTurnRequests']
METHODS = ['hello', 'call', 'cancel', 'signal']
LOG = 'проводная часть проверена, строка журнала не наблюдается (H.4)'
REPLY_WAIT = 5.0  # сколько ждём ответ сверх задержки работы, секунд


class Fail(Exception):
    pass


class Skip(Exception):
    pass


# --------------------------------------------------------------------------- разбор файла протокола

def load_protocol():
    """Строки блоков случаев (по порядку блоков), условие 2 (hello) и множество случаев «П» из таблицы H."""
    text = io.open(PROTOCOL, encoding='utf-8').read()
    cond = text.split('### Условия набора', 1)[1].split('### C1.', 1)[0]
    m = re.search(r'`(\{"jsonrpc":"2\.0","method":"hello"[^`]*\})`', cond)
    hello = m.group(1) if m else None
    receiver = set()
    for r in re.finditer(r'^\| C(\d+) [^|]*\| ([^|]*) \|', text, re.M):
        if 'П' in r.group(2):
            receiver.add(int(r.group(1)))
    lines = {}
    parts = re.split(r'^### C(\d+)\. [^\n]*$', text, flags=re.M)
    for i in range(1, len(parts), 2):
        n = int(parts[i])
        body = re.split(r'^## ', parts[i + 1], flags=re.M)[0]
        out = []
        for b in re.finditer(r'^```(json|text)\n(.*?)\n```', body, re.M | re.S):
            out.extend(l for l in b.group(2).split('\n') if l.strip())
        lines[n] = out
    return lines, hello, receiver


# --------------------------------------------------------------------------- соединение с процессом

class Conn:
    def __init__(self, cmd, env):
        e = dict(os.environ)
        e.update(env or {})
        e['PYTHONIOENCODING'] = 'utf-8'
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=e)
        self.q = queue.Queue()
        self.final_quiet = True
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for raw in iter(self.p.stdout.readline, b''):
            self.q.put(raw.decode('utf-8', 'replace').rstrip('\r\n'))
        self.q.put(None)

    def send(self, raw):
        try:
            self.p.stdin.write((raw + '\n').encode('utf-8'))
            self.p.stdin.flush()
        except OSError:
            raise Fail('процесс закрыл стандартный ввод раньше времени')

    def send_obj(self, obj):
        self.send(json.dumps(obj, ensure_ascii=False, separators=(',', ':')))

    def recv(self, timeout, allow_eof=False):
        """Следующее сообщение (разобранное); None — тишина за timeout; 'EOF' — вывод закрыт (если разрешено)."""
        deadline = time.monotonic() + timeout
        while True:
            try:
                line = self.q.get(timeout=max(0.0, deadline - time.monotonic()))
            except queue.Empty:
                return None
            if line is None:
                self.q.put(None)
                if allow_eof:
                    return 'EOF'
                raise Fail('процесс завершился или закрыл стандартный вывод')
            if not line.strip():
                continue
            try:
                return json.loads(line)
            except ValueError:
                raise Fail('в стандартный вывод попала строка, не являющаяся сообщением протокола (J, п. 2.1): %r' % line[:80])

    def quiet(self, sec):
        m = self.recv(sec)
        if m is not None:
            raise Fail('лишнее сообщение от программы: ' + short(m))

    def close(self):
        try:
            self.p.stdin.close()
        except OSError:
            pass
        try:
            self.p.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.p.kill()
            self.p.wait()
        self.p.stdout.close()


def short(m):
    s = json.dumps(m, ensure_ascii=False) if not isinstance(m, str) else m
    return s if len(s) <= 220 else s[:220] + '…'


def need(cond, msg):
    if not cond:
        raise Fail(msg)


def expect(c, timeout=REPLY_WAIT):
    m = c.recv(timeout)
    need(m is not None, 'ответа нет за %.1f с' % timeout)
    need(isinstance(m, dict), 'ожидался объект, пришло ' + short(m))
    return m


# --------------------------------------------------------------------------- общие проверки

def check_hello_fields(d, what):
    need(isinstance(d, dict), '%s: не объект' % what)
    need(d.get('version') == 1, '%s: version не равен 1' % what)
    need(d.get('role') in ('caller', 'receiver', 'both'), '%s: role вне списка' % what)
    need(d.get('kind') in ('machine', 'program'), '%s: kind вне списка' % what)
    fc, ms = d.get('fail_codes'), d.get('methods')
    need(isinstance(fc, list) and all(x in FAIL_CODES for x in fc), '%s: fail_codes не из раздела F: %s' % (what, short(fc)))
    need(isinstance(ms, list) and all(x in METHODS for x in ms), '%s: methods не из раздела D: %s' % (what, short(ms)))


def do_hello(c, line):
    """Обмен hello по условию 2 (проверки C1); возвращает params hello проверяемой программы."""
    ours = json.loads(line)
    c.send(line)
    theirs, resp = None, None
    end = time.monotonic() + REPLY_WAIT
    while theirs is None or resp is None:
        m = c.recv(max(0.1, end - time.monotonic()))
        need(m is not None, 'обмен hello не завершён за %.0f с' % REPLY_WAIT)
        need(isinstance(m, dict), 'в обмене hello пришло ' + short(m))
        need(m.get('method') != 'call', 'запрос call до завершения обмена hello (B, п. 5)')
        if m.get('method') == 'hello' and 'id' in m:
            theirs = m
            check_hello_fields(m.get('params'), 'hello программы')
            # пока мы не ответили, программа не вправе слать call: слушаем чуть-чуть
            extra = c.recv(0.3)
            if extra is not None:
                need(isinstance(extra, dict) and extra.get('method') != 'call',
                     'запрос call до ответа на её hello: ' + short(extra))
                need(extra.get('id') == ours['id'] and 'result' in extra, 'лишнее сообщение в обмене hello: ' + short(extra))
                resp = extra
            c.send_obj({'jsonrpc': '2.0', 'id': m['id'], 'result': ours['params']})
        elif 'result' in m and m.get('id') == ours['id']:
            resp = m
        else:
            raise Fail('неожиданное сообщение в обмене hello: ' + short(m))
    check_hello_fields(resp['result'], 'ответ на hello')
    for k in ('version', 'role', 'kind', 'fail_codes', 'methods'):
        need(resp['result'].get(k) == theirs['params'].get(k), 'ответ на hello не повторяет поля о себе (%s)' % k)
    return theirs['params']


def check_reply(m, sent):
    p = sent['params']
    need(m.get('id') == sent['id'], 'id ответа %s вместо %s: %s' % (short(m.get('id')), sent['id'], short(m)))
    need('result' in m and 'error' not in m, 'ожидался reply, пришло: ' + short(m))
    r = m['result']
    need(isinstance(r, dict), 'result не объект')
    for k in ('party', 'trace', 'step'):
        need(r.get(k) == p.get(k), 'в reply поле %s = %s, в запросе %s' % (k, short(r.get(k)), short(p.get(k))))
    return r


def check_refusal(m, sent_id, params, reason=None, text=None):
    need(m.get('id') == sent_id, 'id отказа %s вместо %s: %s' % (short(m.get('id')), sent_id, short(m)))
    need('error' in m and 'result' not in m, 'ожидался refusal, пришло: ' + short(m))
    e = m['error']
    need(isinstance(e, dict) and e.get('code') == -32000, 'у отказа code не −32000: ' + short(e))
    d = e.get('data')
    need(isinstance(d, dict), 'у отказа нет error.data')
    if reason is not None:
        need(d.get('reason') == reason, 'reason %s вместо %s' % (short(d.get('reason')), reason))
    if text is not None:
        need(d.get('text') == text and e.get('message') == text, 'text/message отказа не равны тексту запроса')
    for k in ('trace', 'step', 'party'):
        if k in params:
            need(d.get(k) == params[k], 'в отказе поле %s = %s, в запросе %s' % (k, short(d.get(k)), short(params[k])))


def check_error(m, code, rid):
    need(m.get('id') == rid, 'id ошибки %s вместо %s: %s' % (short(m.get('id')), short(rid), short(m)))
    need('error' in m and 'result' not in m, 'ожидалась ошибка, пришло: ' + short(m))
    need(isinstance(m['error'], dict) and m['error'].get('code') == code, 'код ошибки %s вместо %d' % (short(m['error']), code))


class Ctx:
    def __init__(self, cmd, env, lines, hello):
        self.cmd, self.env, self.L, self.hello = cmd, env, lines, hello
        self.conns = []
        self.methods = []

    def conn(self, hello_line=None, handshake=True):
        c = Conn(self.cmd, self.env)
        self.conns.append(c)
        if handshake:
            self.methods = do_hello(c, hello_line or self.hello).get('methods', [])
        return c

    def need_signal(self):
        if 'signal' not in self.methods:
            raise Skip('получатель не называет signal в methods (П*: не обязателен)')

    def close(self):
        for c in self.conns:
            c.close()


def J(line):
    return json.loads(line)


def wait_timeout(sent):
    return sent['params']['input'].get('delay', 0) / 1000.0 + REPLY_WAIT


# --------------------------------------------------------------------------- случаи получателя

def case_c1(x):
    c = x.conn(x.L[0], handshake=False)
    do_hello(c, x.L[0])


def case_c2(x):
    c = x.conn(x.L[0], handshake=False)
    c.final_quiet = False
    c.send(x.L[0])
    while True:
        m = expect(c)
        if m.get('method') == 'hello':
            continue
        break
    check_error(m, -32001, 'hello-1')
    need(isinstance(m['error'].get('data'), dict) and m['error']['data'].get('version') == 1, 'в error.data нет version равного 1')
    end = time.monotonic() + 3
    while True:
        r = c.recv(max(0.1, end - time.monotonic()), allow_eof=True)
        need(r is not None, 'соединение не закрыто после ошибки −32001')
        if r == 'EOF':
            break
    try:
        c.send(x.L[2])
    except Fail:
        pass
    need(c.recv(0.5, allow_eof=True) in (None, 'EOF'), 'ответ на запрос после неподдержанной версии')


def case_c3(x):
    c = x.conn()
    s = J(x.L[0])
    c.send(x.L[0])
    m = expect(c)
    if 'error' in m and isinstance(m['error'], dict) and (m['error'].get('data') or {}).get('reason') == 'NoResult':
        raise Skip('сторона agent не открыта (в условии H.3 её нет), AgentReply не проверен')
    r = check_reply(m, s)
    res = r.get('result')
    need(isinstance(res, dict) and isinstance(res.get('usage'), dict), 'result.result не AgentReply: нет usage (G)')
    u = res['usage']
    for k in ('session', 'result', 'family', 'model', 'tokens', 'created', 'updated', 'trace', 'step'):
        need(k in u, 'в usage нет обязательного поля ' + k)
    need(isinstance(u['model'], dict) and 'id' in u['model'] and 'provider' in u['model'], 'в usage.model нет id или provider')
    need(isinstance(u['tokens'], dict), 'usage.tokens не объект')
    need(all(isinstance(u[k], int) and not isinstance(u[k], bool) for k in ('created', 'updated')), 'created/updated не целые')


def case_c4(x):
    c = x.conn()
    for i in range(0, len(x.L), 2):
        s = J(x.L[i])
        c.send(x.L[i])
        m = expect(c)
        inp = s['params']['input']
        check_refusal(m, s['id'], s['params'], inp['reason'], inp['text'])


def case_c5(x):
    c = x.conn()
    s = J(x.L[0])
    c.send(x.L[0])
    c.send(x.L[1])
    m = expect(c, wait_timeout(s))
    r = check_reply(m, s)
    need(r.get('result') == J(x.L[2])['result']['result'], 'result %s, ожидалось starts равное 1' % short(r.get('result')))


def case_c6(x):
    c = x.conn()
    s1, s2 = J(x.L[0]), J(x.L[2])
    c.send(x.L[0])
    m1 = expect(c)
    need(m1 == J(x.L[1]), 'первый ответ не совпал с эталонным: ' + short(m1))
    c.send(x.L[2])
    m2 = expect(c)
    need(m2 == m1, 'повторный ответ не повторяет сохранённый: %s против %s' % (short(m2), short(m1)))


def case_c7(x):
    c = x.conn()
    s = J(x.L[0])
    c.send(x.L[0])
    c.send(x.L[1])
    m = expect(c)
    check_refusal(m, s['id'], s['params'], 'Cancelled')
    c.quiet(1.0)


def case_c8(x):
    c = x.conn()
    s = J(x.L[0])
    c.send(x.L[0])
    check_reply(expect(c), s)
    c.send(x.L[2])
    c.send(x.L[3])
    check_reply(expect(c), J(x.L[3]))
    return LOG


def case_c9(x):
    c = x.conn()
    c.send(x.L[0])
    c.send(x.L[1])
    m = expect(c)
    r = check_reply(m, J(x.L[1]))
    need(r.get('result') == J(x.L[2])['result']['result'], 'эхо не вернуло input')
    return LOG


def pause_case(x, call_i, stop_i, cont_i, min_after):
    c = x.conn()
    x.need_signal()
    s = J(x.L[call_i])
    c.send(x.L[call_i])
    c.send(x.L[stop_i])
    c.quiet(2.0)
    c.send(x.L[cont_i])
    t = time.monotonic()
    m = expect(c, wait_timeout(s))
    after = time.monotonic() - t
    r = check_reply(m, s)
    need(r['result'].get('starts') == 1, 'starts не равен 1: ' + short(r['result']))
    need(after >= min_after * s['params']['input']['delay'] / 1000.0,
         'ответ пришёл через %.2f с после «продолжить»: отсчёт delay шёл на паузе' % after)


def case_c10(x):
    pause_case(x, 0, 1, 2, 0.6)


def case_c11(x):
    pause_case(x, 0, 1, 2, 0.6)
    return LOG


def case_c12(x):
    c = x.conn()
    x.need_signal()
    s = J(x.L[0])
    c.send(x.L[0])
    t = time.monotonic()
    c.send(x.L[1])
    m = expect(c, wait_timeout(s))
    el = time.monotonic() - t
    r = check_reply(m, s)
    need(r['result'].get('starts') == 1, 'starts не равен 1')
    need(el < s['params']['input']['delay'] / 1000.0 + 1.5, 'ответ пришёл через %.2f с: работа вставала на паузу' % el)
    return LOG


def case_c13(x):
    c = x.conn()
    x.need_signal()
    for base in (0, 4):
        s = J(x.L[base])
        c.send(x.L[base])
        c.send(x.L[base + 1])
        c.send(x.L[base + 2])
        m = expect(c)
        check_refusal(m, s['id'], s['params'], 'StoppedByHuman')


def case_c17(x):
    c = x.conn()
    s = J(x.L[0])
    c.send(x.L[0])
    r = check_reply(expect(c), s)
    need(r.get('result') == J(x.L[1])['result']['result'], 'эхо не вернуло input')


def case_c18(x):
    c = x.conn()
    c.send(x.L[0])
    c.send(x.L[1])
    m = expect(c)
    check_reply(m, J(x.L[1]))
    return LOG


def case_c21(x):
    c = x.conn()
    s = J(x.L[0])
    c.send(x.L[0])
    r = check_reply(expect(c), s)
    need(r['trace'] == 'т-9.2.4' and r['step'] == 17, 'trace/step в reply не как в запросе')
    s2 = J(x.L[2])
    c.send(x.L[2])
    c.send(x.L[3])
    m = expect(c)
    check_refusal(m, s2['id'], s2['params'], 'Cancelled')
    need(m['error']['data'].get('trace') == 'т-9.2.4' and m['error']['data'].get('step') == 18, 'trace/step в refusal не как в запросе')


def case_c22(x):
    c = x.conn()
    for i in (0, 2):
        s = J(x.L[i])
        c.send(x.L[i])
        m = expect(c)
        check_refusal(m, s['id'], s['params'], 'NoResult')
        need(isinstance(m['error']['data'].get('text'), str) and m['error']['data']['text'], 'text отказа пуст')


def case_c24(x):
    c = x.conn()
    s = J(x.L[0])
    c.send(x.L[0])
    r = check_reply(expect(c, wait_timeout(s)), s)
    need(r['result'].get('starts') == 1, 'starts не равен 1')


def case_c26(x):
    c = x.conn(x.L[0])
    s = J(x.L[1])
    c.send(x.L[1])
    m = expect(c)
    check_refusal(m, s['id'], s['params'], 'NoResult')
    need(len(m['error'].get('message', '')) <= 10 and len(m['error']['data'].get('text', '')) <= 10,
         'текст не обрезан до max_text 10: ' + short(m['error']))
    return LOG


def case_c28(x):
    c = x.conn()
    c.send(x.L[0])
    check_error(expect(c), -32600, 'echo-11')
    c.send(x.L[2])
    check_reply(expect(c), J(x.L[2]))
    return LOG


def case_c32(x):
    s = J(x.L[0])
    c1 = x.conn()
    c1.final_quiet = False
    c1.send(x.L[0])
    m1 = expect(c1)
    need(m1 == J(x.L[1]), 'первый ответ не совпал с эталонным: ' + short(m1))
    c1.close()
    c2 = x.conn()
    c2.send(x.L[2])
    m2 = expect(c2)
    r = check_reply(m2, s)
    need(r['result'].get('starts') == 1, 'starts не равен 1 во втором процессе')


def case_c33(x):
    c = x.conn()
    c.send(x.L[0])
    check_error(expect(c), -32600, None)
    c.send(x.L[2])
    check_reply(expect(c), J(x.L[2]))
    return LOG


def case_c34(x):
    c = x.conn()
    c.send(x.L[0])
    check_error(expect(c), -32700, None)
    c.send(x.L[2])
    check_reply(expect(c), J(x.L[2]))
    return LOG


def case_c35(x):
    c = x.conn()
    for i in (0, 2, 4):
        c.send(x.L[i])
        check_error(expect(c), -32600, J(x.L[i + 1])['id'])
    c.send(x.L[6])
    check_reply(expect(c), J(x.L[6]))


def case_c36(x):
    c = x.conn()
    c.send(x.L[0])
    check_error(expect(c), -32601, 's-1')
    c.send(x.L[2])
    check_reply(expect(c), J(x.L[2]))
    return LOG


def case_c37(x):
    c = x.conn()
    c.send(x.L[0])
    check_error(expect(c), -32602, 'echo-22')
    c.send(x.L[2])
    check_reply(expect(c), J(x.L[2]))


def case_c20(x):
    raise Skip('перезапуск процесса на том же хранилище состояния режим `--` не задаёт (нужно внешнее управление)')


CASES = {1: case_c1, 2: case_c2, 3: case_c3, 4: case_c4, 5: case_c5, 6: case_c6, 7: case_c7, 8: case_c8, 9: case_c9,
         10: case_c10, 11: case_c11, 12: case_c12, 13: case_c13, 17: case_c17, 18: case_c18, 20: case_c20,
         21: case_c21, 22: case_c22, 24: case_c24, 26: case_c26, 28: case_c28, 32: case_c32, 33: case_c33,
         34: case_c34, 35: case_c35, 36: case_c36, 37: case_c37}


# --------------------------------------------------------------------------- прогон

def run_suite(cmd, env=None, only=None, quiet=False):
    """Возвращает {номер: (статус, текст)}; статус: ok, log, fail, skip."""
    lines, hello, receiver = load_protocol()
    if hello is None:
        raise SystemExit('в файле протокола не найден hello условия 2')
    res = {}
    for n in sorted(receiver):
        if only and n not in only:
            continue
        if n not in CASES:
            res[n] = ('skip', 'нет проверки в прогонщике')
            continue
        x = Ctx(cmd, env, lines[n], hello)
        try:
            note = CASES[n](x)
            for c in x.conns:
                if c.final_quiet:
                    c.quiet(0.4)
            res[n] = ('log', note) if note else ('ok', '')
        except Fail as e:
            res[n] = ('fail', str(e))
        except Skip as e:
            res[n] = ('skip', str(e))
        except Exception as e:  # ошибка самого прогонщика или среды: честный провал, а не молчание
            res[n] = ('fail', 'ошибка прогона: %s: %s' % (type(e).__name__, e))
        finally:
            x.close()
        if not quiet:
            say(n, res[n])
    return res


def say(n, r):
    st, txt = r
    tag = {'ok': 'ок', 'log': 'частично', 'fail': 'ПРОВАЛ', 'skip': 'пропущено'}[st]
    print('C%d: %s%s' % (n, tag, (': ' + txt) if txt else ''), flush=True)


def summary(res):
    cnt = {k: sum(1 for v in res.values() if v[0] == k) for k in ('ok', 'log', 'fail', 'skip')}
    print('\nИтого: ок %d, частично %d, пропущено %d, ПРОВАЛ %d (случаев получателя: %d)' %
          (cnt['ok'], cnt['log'], cnt['skip'], cnt['fail'], len(res)))
    print('Не покрыты (проверка вызывающего, В): остальные случаи таблицы H, включая C38.')
    return cnt['fail']


# --------------------------------------------------------------------------- эталонный получатель

class Reference:
    def __init__(self, mutation):
        self.mut = mutation
        self.lock = threading.RLock()
        self.done, self.open, self.paused, self.flags, self.starts = {}, set(), set(), {}, {}
        self.max_text = 4096

    def out(self, obj):
        with self.lock:
            sys.stdout.write(json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n')
            sys.stdout.flush()

    def log(self, text):
        sys.stderr.write(text + '\n')
        sys.stderr.flush()

    def err(self, code, msg, rid):
        self.out({'jsonrpc': '2.0', 'id': rid, 'error': {'code': code, 'message': msg, 'data': None}})

    def hello_params(self):
        fc = list(FAIL_CODES)
        if self.mut == 'bad_hello_fields':
            fc.append('QuotaExceeded')
        return {'version': 1, 'role': 'receiver', 'kind': 'program', 'fail_codes': fc, 'methods': list(METHODS),
                'max_text': 4096}

    def run(self):
        if self.mut == 'garbage_stdout':
            sys.stdout.write('загрузка модели...\n')
            sys.stdout.flush()
        if self.mut != 'no_hello':
            self.out({'jsonrpc': '2.0', 'method': 'hello', 'id': 'hello-1', 'params': self.hello_params()})
        while True:
            line = sys.stdin.readline()
            if line == '':
                return
            line = line.strip()
            if not line:
                self.log('пустая строка пропущена')
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                self.log('строка не JSON: ' + line[:80])
                if self.mut != 'bad_json_silent':
                    self.err(-32700, 'строка не разобрана как JSON', None)
                continue
            self.handle(msg, top=True)

    def handle(self, m, top=False):
        if isinstance(m, list):
            if self.mut == 'batch_executes':
                for item in m:
                    self.handle(item)
                return
            self.err(-32600, 'пакеты не поддерживаются', None)
            return
        if not isinstance(m, dict):
            self.err(-32600, 'не объект', None)
            return
        rid = m.get('id')
        readable = rid if isinstance(rid, str) else None
        if not isinstance(m.get('method'), str):
            if m.get('jsonrpc') == '2.0' and ('result' in m) != ('error' in m) and 'id' in m:
                self.log('ответ вызывающего отброшен: %s' % rid)
                return
            self.err(-32600, 'не запрос, не ответ и не уведомление', readable)
            return
        if m.get('jsonrpc') != '2.0' or ('result' in m or 'error' in m):
            self.err(-32600, 'версия конверта не 2.0', readable)
            return
        method = m['method']
        if 'id' not in m:
            if method == 'cancel':
                self.on_cancel(m.get('params'))
            elif method == 'signal':
                self.on_signal(m.get('params'))
            else:
                self.log('неизвестное уведомление игнорируется: ' + method)
            return
        if not isinstance(rid, str):
            self.err(-32600, 'id должен быть строкой', None)
            return
        if method == 'hello':
            p = m.get('params')
            if isinstance(p, dict) and p.get('version') != 1 and self.mut != 'no_version_check':
                self.out({'jsonrpc': '2.0', 'id': rid,
                          'error': {'code': -32001, 'message': 'версия не поддерживается', 'data': {'version': 1}}})
                sys.stdout.flush()
                os._exit(0)
            if isinstance(p, dict) and isinstance(p.get('max_text'), int):
                self.max_text = p['max_text']
            self.out({'jsonrpc': '2.0', 'id': rid, 'result': self.hello_params()})
        elif method == 'call':
            self.on_call(rid, m.get('params'))
        else:
            self.log('неизвестный метод в запросе: ' + method)
            if self.mut != 'unknown_method_silent':
                self.err(-32601, 'метод %s не поддерживается' % method, rid)

    # ---- вызовы
    def on_call(self, rid, p):
        ok = (isinstance(p, dict) and isinstance(p.get('party'), str) and self.is_int(p.get('attempt'))
              and self.is_int(p.get('idle_term')) and isinstance(p.get('trace'), str) and self.is_int(p.get('step')))
        if not ok and self.mut != 'loose_params':
            self.err(-32602, 'params: нет party, attempt, idle_term, trace или step, либо не тот тип', rid)
            return
        if not isinstance(p, dict):
            p = {}
        with self.lock:
            if rid in self.done:
                if self.mut != 'no_dedupe_done':
                    self.out(self.done[rid])
                return
            if rid in self.open and self.mut != 'dup_restarts':
                return
            self.open.add(rid)
        threading.Thread(target=self.work, args=(rid, p), daemon=True).start()

    @staticmethod
    def is_int(v):
        return isinstance(v, int) and not isinstance(v, bool)

    def cut(self, s):
        if self.mut == 'text_not_truncated':
            return s
        return s[:self.max_text]

    def finish(self, rid, resp):
        with self.lock:
            if rid in self.done:
                return
            self.done[rid] = resp
            self.open.discard(rid)
            self.paused.discard(rid)
            self.out(resp)
            if self.mut == 'double_reply':
                self.out(resp)

    def reply(self, rid, p, result):
        step = p.get('step')
        if self.mut == 'wrong_trace':
            step = (step or 0) + 1
        self.finish(rid, {'jsonrpc': '2.0', 'id': rid,
                          'result': {'party': p.get('party'), 'result': result, 'trace': p.get('trace'), 'step': step}})

    def refuse(self, rid, p, reason, text):
        text = self.cut(text)
        code = -32099 if self.mut == 'wrong_code' else -32000
        self.finish(rid, {'jsonrpc': '2.0', 'id': rid, 'error': {
            'code': code, 'message': text,
            'data': {'reason': reason, 'text': text, 'trace': p.get('trace'), 'step': p.get('step'), 'party': p.get('party')}}})

    def work(self, rid, p):
        party, inp = p.get('party'), p.get('input')
        if party == 'echo':
            self.reply(rid, p, inp)
        elif party == 'refuse':
            if isinstance(inp, dict) and isinstance(inp.get('reason'), str) and isinstance(inp.get('text'), str):
                self.refuse(rid, p, inp['reason'], inp['text'])
            else:
                self.refuse(rid, p, 'NoResult', 'вход не разобран: нужны reason и text')
        elif party == 'wait':
            d = inp.get('delay') if isinstance(inp, dict) else None
            if not self.is_int(d) or d < 0:
                self.refuse(rid, p, 'NoResult', 'вход не разобран: delay должен быть целым числом')
                return
            with self.lock:
                self.starts[rid] = self.starts.get(rid, 0) + 1
                n = self.starts[rid]
            left, last = d / 1000.0, time.monotonic()
            while left > 0:
                fl = self.flags.get(rid)
                if fl == 'cancel':
                    self.refuse(rid, p, 'Cancelled', 'отменено родителем')
                    return
                if fl == 'halt':
                    reason = 'Cancelled' if self.mut == 'halt_cancelled' else 'StoppedByHuman'
                    self.refuse(rid, p, reason, 'остановлено человеком')
                    return
                time.sleep(0.02)
                now = time.monotonic()
                if rid not in self.paused:
                    left -= now - last
                last = now
            self.reply(rid, p, {'delay': d, 'starts': n})
        else:
            self.refuse(rid, p, 'NoResult', 'неизвестная сторона')

    # ---- уведомления
    def on_cancel(self, p):
        rid = p.get('request') if isinstance(p, dict) else None
        with self.lock:
            if rid in self.open:
                if self.mut != 'ignore_cancel':
                    self.flags[rid] = 'cancel'
                return
            known_done = rid in self.done
        if known_done and self.mut == 'cancel_after_reply_refuses':
            self.out({'jsonrpc': '2.0', 'id': rid, 'error': {'code': -32000, 'message': 'отменено родителем', 'data': {
                'reason': 'Cancelled', 'text': 'отменено родителем', 'trace': None, 'step': None, 'party': None}}})
            return
        self.log('cancel отброшен: %s' % rid)

    def on_signal(self, p):
        if not isinstance(p, dict) or p.get('kind') not in ('stop', 'continue', 'halt') or p.get('origin') not in ('human', 'parent'):
            self.log('искажённый signal отброшен')
            return
        kind, origin, req = p['kind'], p['origin'], p.get('request')
        with self.lock:
            if origin == 'parent':
                if not isinstance(req, str):
                    self.log('signal родителя без request отброшен')
                    return
                if req not in self.open:
                    if kind == 'stop' and self.mut == 'foreign_signal_pauses':
                        self.paused |= self.open
                        return
                    self.log('signal родителя с чужим request отброшен: %s' % req)
                    return
                targets = {req}
            else:
                targets = set(self.open)
            if kind == 'stop':
                if self.mut != 'no_pause':
                    self.paused |= targets
            elif kind == 'continue':
                if targets & self.paused:
                    self.paused -= targets
                else:
                    self.log('continue вне паузы отброшен')
            else:
                hit = targets & self.paused
                if not hit:
                    self.log('halt вне паузы отброшен')
                for r in hit:
                    self.flags[r] = 'halt'


def run_reference():
    sys.stdin.reconfigure(encoding='utf-8', errors='replace')
    sys.stdout.reconfigure(encoding='utf-8', newline='\n')
    sys.stderr.reconfigure(encoding='utf-8', newline='\n')
    Reference(os.environ.get('CHECK_PROTOCOL_MUTATION', '')).run()


# --------------------------------------------------------------------------- самопроверка мутациями

# мутация -> случаи, из которых хотя бы один обязан упасть
MUTATIONS = {
    'no_dedupe_done': 'дубликат после ответа не получает сохранённый ответ',
    'dup_restarts': 'дубликат выполняющегося запроса запускает работу заново',
    'double_reply': 'два ответа на один запрос',
    'ignore_cancel': 'cancel игнорируется',
    'cancel_after_reply_refuses': 'cancel после ответа рождает отказ',
    'loose_params': 'принимает неверные params',
    'garbage_stdout': 'мусор в стандартном выводе',
    'no_version_check': 'нет ошибки −32001 на неизвестную версию',
    'batch_executes': 'пакет выполняется',
    'unknown_method_silent': 'нет ошибки −32601 на неизвестный метод',
    'foreign_signal_pauses': 'чужой сигнал родителя ставит работу на паузу',
    'halt_cancelled': 'halt даёт Cancelled вместо StoppedByHuman',
    'wrong_trace': 'ответ искажает номер шага',
    'wrong_code': 'отказ с кодом не −32000',
    'text_not_truncated': 'текст не обрезается по max_text',
    'bad_json_silent': 'нет ошибки −32700 на не-JSON',
    'no_pause': '«стоп» человека игнорируется',
    'no_hello': 'не шлёт свой hello',
    'bad_hello_fields': 'в hello код сбоя не из списка',
}
MUTATION_CASES = {
    'no_dedupe_done': [6], 'dup_restarts': [5], 'double_reply': [6, 17], 'ignore_cancel': [7],
    'cancel_after_reply_refuses': [8], 'loose_params': [37], 'garbage_stdout': [1], 'no_version_check': [2],
    'batch_executes': [33], 'unknown_method_silent': [36], 'foreign_signal_pauses': [12], 'halt_cancelled': [13],
    'wrong_trace': [21], 'wrong_code': [4], 'text_not_truncated': [26], 'bad_json_silent': [34], 'no_pause': [10],
    'no_hello': [1], 'bad_hello_fields': [1],
}


def selftest():
    ref = [sys.executable, os.path.abspath(__file__), '--reference']
    print('Эталон против полного набора:')
    base = run_suite(ref)
    bad = summary(base)
    print('\nМутации эталона (каждая должна быть поймана):')
    missed = []
    for name, what in MUTATIONS.items():
        r = run_suite(ref, {'CHECK_PROTOCOL_MUTATION': name}, set(MUTATION_CASES[name]), quiet=True)
        caught = [n for n, v in r.items() if v[0] == 'fail']
        if caught:
            print('  поймана  %-28s %s — случай C%d: %s' % (name, what, caught[0], r[caught[0]][1][:90]), flush=True)
        else:
            print('  НЕ ПОЙМАНА %-26s %s (проверены случаи %s)' % (name, what, ', '.join('C%d' % n for n in r)), flush=True)
            missed.append(name)
    print('\nСамопроверка: эталон — %s, мутаций поймано %d из %d' %
          ('зелёный' if not bad else 'КРАСНЫЙ', len(MUTATIONS) - len(missed), len(MUTATIONS)))
    return 1 if (bad or missed) else 0


def main(argv):
    sys.stdout.reconfigure(encoding='utf-8')
    cmd = None
    if '--' in argv:  # всё после первого `--` — команда проверяемой программы, её флаги не наши
        i = argv.index('--')
        argv, cmd = argv[:i], argv[i + 1:]
    if '--reference' in argv:
        return run_reference()
    if '--selftest' in argv:
        return selftest()
    only = None
    if '--cases' in argv:
        i = argv.index('--cases')
        only = {int(s.strip().lstrip('Cc')) for s in argv[i + 1].split(',')}
        del argv[i:i + 2]
    if cmd is not None:
        if not cmd:
            print('После `--` нужна команда запуска проверяемой программы.')
            return 2
        return 1 if summary(run_suite(cmd, None, only)) else 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
