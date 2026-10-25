
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


# Colors and bold for the console, as ANSI escape sequences. Only the colors
# that are readable on both a light and a dark background are used.

import os
import re
import sys

CODES = {"bold": 1, "red": 31, "green": 32, "blue": 34, "magenta": 35}

_SGR = re.compile(r"\x1b\[([0-9;]*)m")


def enabled(stream=None):
    # colors only on a terminal, and not when NO_COLOR is set
    # ( https://no-color.org )
    if os.environ.get("NO_COLOR"):
        return False

    stream = stream or sys.stdout
    return hasattr(stream, "isatty") and stream.isatty()


def style(txt, *names):
    if txt == "" or len(names) == 0:
        return txt

    return "\x1b[%sm%s\x1b[0m" % (";".join(str(CODES[n]) for n in names), txt)


def strip(txt):
    return _SGR.sub("", txt)


def parse(txt):
    # a list of ( text , codes ), codes is the tuple of the SGR codes active
    # for that text
    out = []
    codes = ()
    pos = 0

    for m in _SGR.finditer(txt):
        if m.start() > pos:
            out.append((txt[pos:m.start()], codes))
        pos = m.end()

        new = [int(c) if c else 0 for c in m.group(1).split(";")]
        for c in new:
            if c == 0:
                codes = ()
            else:
                codes = codes + (c,)

    if pos < len(txt):
        out.append((txt[pos:], codes))

    return out
