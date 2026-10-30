
# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011  Simone Riva
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Minimal console interface, based on the curses of the standard library:
# a menu selectable with the arrow keys, a multiple selection and a pager.
# Every function returns None when curses is not usable ( see available() ),
# so the callers can fall back to the plain text interface.

import sys

try:
    import curses
except ImportError:
    curses = None

from dr14tmeter import ansi
from dr14tmeter.table import char_width, wrap_text

KEY_ESC = 27


def available():
    if curses is None:
        return False

    return sys.stdin.isatty() and sys.stdout.isatty()


def _run(fun):
    # curses.wrapper restores the terminal even when fun raises
    try:
        return curses.wrapper(fun)
    except curses.error:
        return None


def _put(win, y, x, txt, attr=0):
    # writing in the bottom right cell raises an error, the text is cut to
    # the window width considering the wide characters
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x >= w:
        return

    out = ""
    used = 0
    for ch in txt:
        cw = char_width(ch)
        if x + used + cw > w:
            break
        out += ch
        used += cw

    try:
        win.addstr(y, x, out, attr)
    except curses.error:
        pass


def _clip(txt, start, width):
    # the part of txt that is visible after skipping start columns
    out = ""
    col = 0
    for ch in txt:
        cw = char_width(ch)
        if col >= start and col + cw - start <= width:
            out += ch
        col += cw
        if col - start >= width:
            break
    return out


def _init(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.keypad(True)
    # keep the colors of the terminal, otherwise curses forces white on black
    # and the text is unreadable on a light background
    try:
        curses.use_default_colors()
    except curses.error:
        pass


def _move(key, cur, count, page):
    # common keys for moving a cursor in a list of count rows
    if key in (curses.KEY_UP, ord('k')):
        return max(cur - 1, 0)
    if key in (curses.KEY_DOWN, ord('j')):
        return min(cur + 1, count - 1)
    if key == curses.KEY_PPAGE:
        return max(cur - page, 0)
    if key == curses.KEY_NPAGE:
        return min(cur + page, count - 1)
    if key == curses.KEY_HOME:
        return 0
    if key == curses.KEY_END:
        return count - 1
    return cur


def _list(stdscr, title, items, hint, checks=None, default=0, help_lines=()):
    # shared loop of menu and multi_select. Returns the cursor position when
    # Enter is pressed, None on Esc / q
    _init(stdscr)
    cur = default
    top = 0

    while True:
        h, w = stdscr.getmaxyx()
        first = 2 + len(help_lines) + (1 if help_lines else 0)
        page = max(h - first - 2, 1)

        if cur < top:
            top = cur
        if cur >= top + page:
            top = cur - page + 1

        stdscr.erase()
        _put(stdscr, 0, 1, title, curses.A_BOLD)
        for i, l in enumerate(help_lines):
            _put(stdscr, 2 + i, 1, l)
        for i in range(top, min(top + page, len(items))):
            mark = ""
            if checks is not None:
                mark = "[x] " if checks[i] else "[ ] "
            attr = curses.A_REVERSE if i == cur else 0
            _put(stdscr, first + i - top, 1, " %s%s " % (mark, items[i]), attr)
        if checks is not None:
            hint = "%d/%d checked" % (sum(1 for c in checks if c), len(checks))
        _put(stdscr, h - 1, 1, hint)
        stdscr.refresh()

        key = stdscr.getch()

        if key in (curses.KEY_ENTER, 10, 13):
            return cur
        if key in (KEY_ESC, ord('q')):
            return None
        if checks is not None and key == ord(' '):
            checks[cur] = not checks[cur]
        elif checks is not None and key == ord('a'):
            flag = not all(checks)
            for i in range(len(checks)):
                checks[i] = flag
        else:
            cur = _move(key, cur, len(items), page)


def menu(title, items, default=0):
    # the index of the chosen item, -1 when the user quits, None if curses
    # can not be used
    def fun(stdscr):
        r = _list(stdscr, title, items,
                  "Up/Down: move   Enter: select   q/Esc: exit", default=default)
        return -1 if r is None else r

    return _run(fun)


def multi_select(title, labels, selected):
    # the list of the chosen indexes, None if curses can not be used
    checks = [i in selected for i in range(len(labels))]
    help_lines = [
        "Up/Down: move   Space: check / uncheck   a: check all / none",
        "Enter: confirm the checked items (if none is checked, the highlighted one is taken)",
        "Esc: take the default, the %d item%s checked at the start" % (
            len(selected), "" if len(selected) == 1 else "s"),
    ]

    def fun(stdscr):
        r = _list(stdscr, title, labels, "", checks=checks,
                  help_lines=help_lines)
        if r is None:
            return list(selected)
        if not any(checks):
            checks[r] = True
        return [i for i, c in enumerate(checks) if c]

    return _run(fun)


def prompt(label, default=""):
    # a line of text, the default is returned when the line is empty. None
    # if the user cancels with Esc
    def fun(stdscr):
        _init(stdscr)
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        txt = ""
        while True:
            h, w = stdscr.getmaxyx()
            stdscr.erase()
            _put(stdscr, 0, 1, label, curses.A_BOLD)
            if default != "":
                _put(stdscr, 1, 1, "Default: %s" % default)
            _put(stdscr, 3, 1, "> ")
            if txt == "":
                _put(stdscr, 3, 3, str(default), curses.A_BOLD)
            else:
                _put(stdscr, 3, 3, txt)
            if default != "":
                hint = "Enter: accept the default (%s), or type a value first   Esc: back" % default
            else:
                hint = "Enter: confirm   Esc: back"
            _put(stdscr, h - 1, 1, hint)
            stdscr.move(3, min(3 + sum(char_width(c) for c in txt), w - 1))
            stdscr.refresh()
            key = stdscr.get_wch()
            if key in ("\n", "\r"):
                return txt.strip() if txt.strip() != "" else str(default)
            if key == "\x1b":
                return None
            if key in ("\x7f", "\b", curses.KEY_BACKSPACE):
                txt = txt[:-1]
            elif isinstance(key, str) and key.isprintable():
                txt += key

    return _run(fun)


def _sgr_attr(codes, pairs):
    # the curses attribute for the SGR codes of ansi.parse
    attr = 0
    for c in codes:
        if c == 1:
            attr |= curses.A_BOLD
        elif c in pairs:
            attr = (attr & ~curses.A_COLOR) | curses.color_pair(pairs[c])
    return attr


def _init_pairs():
    # only the foreground changes, the background is the one of the terminal
    pairs = {}
    if not curses.has_colors():
        return pairs

    for n, (code, color) in enumerate([(31, curses.COLOR_RED),
                                       (32, curses.COLOR_GREEN),
                                       (34, curses.COLOR_BLUE),
                                       (35, curses.COLOR_MAGENTA)]):
        try:
            curses.init_pair(n + 1, color, -1)
            pairs[code] = n + 1
        except curses.error:
            pass
    return pairs


def _put_styled(win, y, segs, left, width, pairs):
    # segs is the ansi.parse of a line, left columns are skipped
    x = 0
    for txt, codes in segs:
        attr = _sgr_attr(codes, pairs)
        vis = _clip(txt, max(left - x, 0), width - max(x - left, 0))
        _put(win, y, max(x - left, 0), vis, attr)
        x += sum(char_width(c) for c in txt)
        if x - left >= width:
            break


def pager(text, title=""):
    # scrollable view of text, with the colors of the ANSI sequences. Returns
    # False when curses can not be used
    lines = [ansi.parse(l.expandtabs(4)) for l in text.split("\n")]
    wmax = max([sum(char_width(c) for t, _ in l for c in t)
                for l in lines] + [0])

    def fun(stdscr):
        _init(stdscr)
        pairs = _init_pairs()
        top = 0
        left = 0

        while True:
            h, w = stdscr.getmaxyx()
            page = max(h - 2, 1)
            top = max(min(top, len(lines) - page), 0)
            left = max(min(left, wmax - w + 1), 0)

            stdscr.erase()
            for i in range(page):
                if top + i < len(lines):
                    _put_styled(stdscr, i, lines[top + i], left, w - 1, pairs)
            status = " %s  lines %d-%d/%d   Up/Down PgUp/PgDn Home/End: scroll   Left/Right: pan   q: back " % (
                title, top + 1, min(top + page, len(lines)), len(lines))
            _put(stdscr, h - 1, 0, status.ljust(w - 1), curses.A_REVERSE)
            stdscr.refresh()

            key = stdscr.getch()
            if key in (KEY_ESC, ord('q'), curses.KEY_ENTER, 10, 13):
                return True
            if key == curses.KEY_RESIZE:
                continue
            if key in (curses.KEY_LEFT, ord('h')):
                left -= 8
            elif key in (curses.KEY_RIGHT, ord('l')):
                left += 8
            elif key == ord(' '):
                top += page
            else:
                top = _move(key, top, len(lines), page)

    r = _run(fun)
    return r is True


def _detail_lines(details, width):
    # the ( label , text ) lines of the box. A value is a text on the line of
    # its label, or a list of texts shown as a numbered list: the lines that
    # follow a wrapped item are indented under its text
    out = []
    for lab, val in details:
        if isinstance(val, str):
            out.append((lab + ":", val))
            continue

        out.append((lab + ":", ""))
        nw = len(str(len(val)))
        for i, item in enumerate(val):
            num = "%*d. " % (nw, i + 1)
            for k, l in enumerate(wrap_text(item, max(width - len(num), 10)) or [""]):
                out.append(("", (num if k == 0 else " " * len(num)) + l))
    return out


def track_browser(title, keys, rows, details_fn, header=""):
    # the rows of a query on tracks, selectable with the cursor. The metadata
    # of the highlighted track are shown in a box beside the list, or below
    # it on a narrow terminal. details_fn( id ) is a list of ( label , value ).
    # Returns False when curses can not be used
    keys = list(keys)
    def cols(txt):
        return sum(char_width(c) for c in str(txt))

    widths = [max([cols(k)] + [cols(r[k]) for r in rows]) for k in keys]

    def line(r):
        out = ""
        for k, wd in zip(keys, widths):
            v = str(r[k])
            out += v + " " * (wd - cols(v)) + "  "
        return out

    lines = [line(r) for r in rows]
    head = "".join(k + " " * (wd - cols(k)) + "  " for k, wd in zip(keys, widths))
    cache = {}

    def fun(stdscr):
        _init(stdscr)
        cur = 0
        top = 0
        dtop = 0
        shown = None

        while True:
            h, w = stdscr.getmaxyx()
            side = w >= 100
            list_w = min(sum(widths) + 2 * len(widths) + 2, w - 44) if side else w
            list_h = h - 4 if side else max((h - 4) // 2, 3)
            page = max(list_h - 1, 1)

            if cur < top:
                top = cur
            if cur >= top + page:
                top = cur - page + 1

            stdscr.erase()
            _put(stdscr, 0, 1, title, curses.A_BOLD)
            _put(stdscr, 2, 1, _clip(head, 0, list_w - 2), curses.A_UNDERLINE)
            for i in range(top, min(top + page, len(rows))):
                attr = curses.A_REVERSE if i == cur else 0
                _put(stdscr, 3 + i - top, 1,
                     _clip(lines[i], 0, list_w - 2).ljust(list_w - 2), attr)

            tid = rows[cur]["id"]
            if tid != shown:
                shown = tid
                dtop = 0
            if tid not in cache:
                cache[tid] = details_fn(tid)
            if side:
                y0, x0, bh, bw = 2, list_w + 1, h - 4, w - list_w - 2
            else:
                y0, x0, bh, bw = 3 + page + 1, 1, h - 5 - page, w - 2
            if bh >= 3 and bw >= 10:
                _put(stdscr, y0, x0, "+" + "-" * (bw - 2) + "+")
                _put(stdscr, y0 + bh - 1, x0, "+" + "-" * (bw - 2) + "+")
                for y in range(y0 + 1, y0 + bh - 1):
                    _put(stdscr, y, x0, "|")
                    _put(stdscr, y, x0 + bw - 1, "|")
                box = _detail_lines(cache[tid], bw - 4)
                dtop = max(min(dtop, len(box) - (bh - 2)), 0)
                for n in range(bh - 2):
                    if dtop + n < len(box):
                        lab, txt = box[dtop + n]
                        if lab:
                            _put(stdscr, y0 + 1 + n, x0 + 2, lab, curses.A_BOLD)
                        off = 12 if lab else 0
                        _put(stdscr, y0 + 1 + n, x0 + 2 + off,
                             _clip(txt, 0, bw - 4 - off))
                if len(box) > bh - 2:
                    _put(stdscr, y0 + bh - 1, x0 + 2,
                         " Left/Right: scroll %d/%d " % (dtop + 1, len(box)))

            _put(stdscr, h - 1, 1, "%d/%d   Up/Down PgUp/PgDn Home/End: select   q/Esc: back" % (
                cur + 1, len(rows)), curses.A_REVERSE)
            stdscr.refresh()

            key = stdscr.getch()
            if key in (KEY_ESC, ord('q'), curses.KEY_ENTER, 10, 13):
                return True
            if key == curses.KEY_RESIZE:
                continue
            if key == curses.KEY_RIGHT:
                dtop += 3
            elif key == curses.KEY_LEFT:
                dtop = max(dtop - 3, 0)
            else:
                cur = _move(key, cur, len(rows), page)

    return _run(fun) is True


def artist_browser(title, keys, rows, albums_fn, details_fn, tracks_fn=None, header=""):
    # the rows of a query on artists. The albums of the highlighted artist are
    # listed in the box beside the list (below it on a narrow terminal). With
    # the Right key an album can be selected and its metadata are shown in the
    # box; Left goes back to the artists. albums_fn( id ) is a list of rows
    # with id, Album_Title and DR (tracks if no albums, with kind = "track"), details_fn( row ) a list of ( label , value ).
    # Returns False when curses can not be used
    keys = list(keys)
    def cols(txt):
        return sum(char_width(c) for c in str(txt))

    widths = [max([cols(k)] + [cols(r[k]) for r in rows]) for k in keys]

    def line(r):
        out = ""
        for k, wd in zip(keys, widths):
            v = str(r[k])
            out += v + " " * (wd - cols(v)) + "  "
        return out

    lines = [line(r) for r in rows]
    head = "".join(k + " " * (wd - cols(k)) + "  " for k, wd in zip(keys, widths))
    albums = {}
    tracks = {}
    cache = {}

    def fun(stdscr):
        _init(stdscr)
        cur = 0
        top = 0
        acur = 0
        atop = 0
        dtop = 0
        in_albums = False
        in_tracks = False
        tcur = 0

        while True:
            h, w = stdscr.getmaxyx()
            side = w >= 100
            list_w = min(sum(widths) + 2 * len(widths) + 2, w - 44) if side else w
            list_h = h - 4 if side else max((h - 4) // 2, 3)
            page = max(list_h - 1, 1)

            if cur < top:
                top = cur
            if cur >= top + page:
                top = cur - page + 1

            stdscr.erase()
            _put(stdscr, 0, 1, title, curses.A_BOLD)
            _put(stdscr, 2, 1, _clip(head, 0, list_w - 2), curses.A_UNDERLINE)
            for i in range(top, min(top + page, len(rows))):
                attr = curses.A_REVERSE if i == cur and not in_albums else (
                    curses.A_BOLD if i == cur else 0)
                _put(stdscr, 3 + i - top, 1,
                     _clip(lines[i], 0, list_w - 2).ljust(list_w - 2), attr)

            aid = rows[cur]["id"]
            if aid not in albums:
                albums[aid] = albums_fn(aid)
            alb = albums[aid]
            if acur >= len(alb):
                acur = max(len(alb) - 1, 0)

            # the list of the box: the albums, or the tracks of the selected album
            lst, lcur = alb, acur
            if in_tracks:
                bkey = alb[acur]["id"]
                if bkey not in tracks:
                    tracks[bkey] = tracks_fn(bkey)
                lst, lcur = tracks[bkey], tcur
                if lcur >= len(lst):
                    lcur = tcur = max(len(lst) - 1, 0)

            if side:
                y0, x0, bh, bw = 2, list_w + 1, h - 4, w - list_w - 2
            else:
                y0, x0, bh, bw = 3 + page + 1, 1, h - 5 - page, w - 2
            if bh >= 3 and bw >= 10:
                _put(stdscr, y0, x0, "+" + "-" * (bw - 2) + "+")
                _put(stdscr, y0 + bh - 1, x0, "+" + "-" * (bw - 2) + "+")
                for y in range(y0 + 1, y0 + bh - 1):
                    _put(stdscr, y, x0, "|")
                    _put(stdscr, y, x0 + bw - 1, "|")
                inner = bh - 2
                what = "Tracks" if lst and lst[0].get("kind") == "track" else "Albums"
                _put(stdscr, y0, x0 + 2, " %s (%d) " % (what, len(lst)))

                # the albums take the whole box, or its upper part when the
                # details of the selected one are shown below
                ah = max(inner // 3, 3) if in_albums else inner
                ah = min(ah, max(len(lst), 1)) if in_albums else ah
                if lcur < atop:
                    atop = lcur
                if lcur >= atop + ah:
                    atop = lcur - ah + 1
                if not in_albums:
                    atop = 0
                for n in range(ah):
                    i = atop + n
                    if i >= len(lst):
                        break
                    txt = "%-5s %s" % (lst[i]["DR"], lst[i]["Album_Title"])
                    attr = curses.A_REVERSE if in_albums and i == lcur else 0
                    _put(stdscr, y0 + 1 + n, x0 + 2,
                         _clip(txt, 0, bw - 4).ljust(bw - 4), attr)

                if in_albums and lst:
                    dy = y0 + 1 + ah
                    _put(stdscr, dy, x0, "+" + "-" * (bw - 2) + "+")
                    bid = (lst[lcur].get("kind"), lst[lcur]["id"])
                    if bid not in cache:
                        cache[bid] = details_fn(lst[lcur])
                    box = _detail_lines(cache[bid], bw - 4)
                    dh = inner - ah - 1
                    dtop = max(min(dtop, len(box) - dh), 0)
                    for n in range(dh):
                        if dtop + n < len(box):
                            lab, txt = box[dtop + n]
                            if lab:
                                _put(stdscr, dy + 1 + n, x0 + 2, lab, curses.A_BOLD)
                            off = 12 if lab else 0
                            _put(stdscr, dy + 1 + n, x0 + 2 + off,
                                 _clip(txt, 0, bw - 4 - off))
                    if len(box) > dh:
                        _put(stdscr, y0 + bh - 1, x0 + 2,
                             " PgUp/PgDn: scroll %d/%d " % (dtop + 1, len(box)))

            if in_albums:
                can = tracks_fn and not in_tracks and lst and lst[0].get("kind") != "track"
                msg = "%d/%d   Up/Down: select   PgUp/PgDn: scroll details   %sLeft/Esc: back   q: quit" % (
                    lcur + 1, len(lst), "Right: tracks   " if can else "")
            else:
                msg = "%d/%d   Up/Down PgUp/PgDn Home/End: select   Right: albums/tracks   q/Esc: back" % (
                    cur + 1, len(rows))
            _put(stdscr, h - 1, 1, msg, curses.A_REVERSE)
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_RESIZE:
                continue
            if key == ord('q'):
                return True
            if in_albums:
                if key in (KEY_ESC, curses.KEY_LEFT):
                    if in_tracks:
                        in_tracks = False
                    else:
                        in_albums = False
                    dtop = 0
                elif key in (curses.KEY_RIGHT, ord('l')):
                    if tracks_fn and not in_tracks and lst and lst[0].get("kind") != "track":
                        in_tracks = True
                        tcur = 0
                        atop = 0
                        dtop = 0
                elif key == curses.KEY_PPAGE:
                    dtop = max(dtop - 5, 0)
                elif key == curses.KEY_NPAGE:
                    dtop += 5
                else:
                    new = _move(key, lcur, len(lst), 1)
                    if new != lcur:
                        if in_tracks:
                            tcur = new
                        else:
                            acur = new
                        dtop = 0
            else:
                if key in (KEY_ESC, curses.KEY_ENTER, 10, 13):
                    return True
                if key in (curses.KEY_RIGHT, ord('l')):
                    if alb:
                        in_albums = True
                        acur = 0
                        dtop = 0
                else:
                    new = _move(key, cur, len(rows), page)
                    if new != cur:
                        cur = new
                        acur = 0

    return _run(fun) is True
