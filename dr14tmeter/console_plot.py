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


import math


# every console char is a braille pattern of 2x4 dots:
# _braille_dots[x][y] is the bit of the dot in the column x and row y
_braille_dots = ((0x01, 0x02, 0x04, 0x40),
                 (0x08, 0x10, 0x20, 0x80))


def nice_step(span, max_intervals):
    # the smallest step among 1, 2, 5, 10, 20, 50, ... that splits span in
    # at most max_intervals intervals
    step = 1
    while True:
        for m in (1, 2, 5):
            if span <= max_intervals * step * m:
                return step * m
        step *= 10


def line_plot(xs, ys, width, height):
    # plot the line through the points (xs, ys) with the axes and the ticks;
    # xs are integers (e.g. years) in ascending order.
    # width and height are the size of the plot in console chars

    if len(xs) == 0:
        return ""

    y_step = nice_step(max(ys) - min(ys), max(height // 2, 1))
    y0 = math.floor(min(ys) / y_step) * y_step
    y1 = math.ceil(max(ys) / y_step) * y_step
    if y1 == y0:
        y1 = y0 + y_step

    x0 = xs[0]
    x1 = xs[-1] if xs[-1] > xs[0] else xs[0] + 1

    y_ticks = range(y0, y1 + 1, y_step)
    lab_w = max(len(str(t)) for t in y_ticks)

    # " " + y label + " ┤" on the left, room for the last x label on the right
    cols = max(width - lab_w - 3 - 3, 10)

    dots_w = 2 * cols
    dots_h = 4 * height

    def x_dot(x):
        return int(round((x - x0) * (dots_w - 1) / float(x1 - x0)))

    def y_dot(y):
        return int(round((y1 - y) * (dots_h - 1) / float(y1 - y0)))

    grid = [[0] * cols for r in range(height)]

    def set_dot(x, y):
        grid[y // 4][x // 2] |= _braille_dots[x % 2][y % 4]

    pts = [(x_dot(x), y_dot(y)) for x, y in zip(xs, ys)]

    set_dot(*pts[0])
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(abs(xb - xa), abs(yb - ya), 1)
        for i in range(n + 1):
            set_dot(xa + int(round(i * (xb - xa) / float(n))),
                    ya + int(round(i * (yb - ya) / float(n))))

    tick_rows = dict((y_dot(t) // 4, t) for t in y_ticks)

    lines = []
    for r in range(height):
        if r in tick_rows:
            txt = " %*d ┤" % (lab_w, tick_rows[r])
        else:
            txt = " " * (lab_w + 2) + "│"
        txt += "".join(chr(0x2800 + b) if b else " " for b in grid[r])
        lines.append(txt.rstrip())

    # at least 8 chars between two x labels
    x_step = nice_step(x1 - x0, max(cols // 8, 1))
    axis = ["─"] * cols
    labels = [" "] * (cols + 3)
    for t in range(int(math.ceil(x0 / float(x_step))) * x_step, x1 + 1, x_step):
        c = x_dot(t) // 2
        axis[c] = "┬"
        lab = str(t)
        start = min(max(c - (len(lab) - 1) // 2, 0), len(labels) - len(lab))
        labels[start:start + len(lab)] = lab

    lines.append(" " * (lab_w + 2) + "└" + "".join(axis))
    lines.append((" " * (lab_w + 3) + "".join(labels)).rstrip())

    return "\n".join(lines) + "\n"
