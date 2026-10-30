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


import shutil
import sys
import unicodedata

from dr14tmeter import ansi


def char_width(ch):
    # number of console columns used by ch: CJK chars (e.g. Japanese) take 2
    # columns, combining marks and format chars take none
    if unicodedata.category(ch) in ("Mn", "Me", "Cf"):
        return 0
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    return 1


def text_width(txt):
    return sum(char_width(ch) for ch in txt)


def wrap_text(txt, width):
    # split txt on lines no wider than width console columns: words are kept
    # whole when possible, longer words (e.g. Japanese text, that has no
    # spaces) are broken between chars
    lines = []
    line = ""
    line_w = 0

    for word in txt.split():
        word_w = text_width(word)
        sep_w = 1 if line else 0

        if line_w + sep_w + word_w <= width:
            line += " " * sep_w + word
            line_w += sep_w + word_w
            continue

        if word_w <= width:
            lines.append(line)
            line = word
            line_w = word_w
            continue

        if line:
            line += " "
            line_w += 1

        for ch in word:
            ch_w = char_width(ch)
            if line_w + ch_w > width and line.strip():
                lines.append(line.rstrip())
                line = ""
                line_w = 0
            line += ch
            line_w += ch_w

    if line:
        lines.append(line)

    return lines


def ljust_text(txt, width):
    return txt + " " * (width - text_width(txt))


def histogram_bar(value, max_value, width):
    # the bar of max_value is width chars long, the bars are drawn with a
    # resolution of 1/8 of char
    if max_value <= 0:
        return ""

    eighths = int(round(8.0 * width * value / max_value))
    if value > 0:
        eighths = max(eighths, 1)

    full, part = divmod(eighths, 8)
    return "█" * full + ("", "▏", "▎", "▍", "▌", "▋", "▊", "▉")[part]


class one_decimal(float):
    # a float shown with one decimal digit, like the mean DR
    pass


def one_decimal_formatter(el):
    return "%.1f" % el


def float_formatter(el):
    if abs(el) >= 1.0:
        return "%.2f" % el
    else:
        return "%.2E" % el


def default_formatter(el):
    if sys.version_info[0] == 2:
        return unicode(el)
    else:
        return str(el)


def string_formatter(el):
    if sys.version_info[0] == 2:
        return unicode(el)
    else:
        return str(el)


class Table:

    def __init__(self):
        self.__float_format = "%.2f"
        self.__col_cnt = 5
        self.__ini_txt = ""
        self.__txt = ""
        self.__formatter = {}

        self.add_formatter(float, float_formatter)
        self.add_formatter(one_decimal, one_decimal_formatter)
        self.add_formatter(str, string_formatter)
        if sys.version_info[0] == 2:
            self.add_formatter(unicode, string_formatter)

    def _get_txt(self):
        return self.__txt

    def _set_txt(self, txt):
        self.__txt = txt

    def _append_txt(self, txt):
        self.__txt += txt

    def init_txt(self, txt=""):
        self.__ini_txt = txt

    def get_init_txt(self):
        return self.__ini_txt

    def new_table(self):
        NotImplementedError(
            " %s : is virutal and must be overridden." % sys._getframe().f_code.co_name)

    def end_table(self):
        NotImplementedError(
            " %s : is virutal and must be overridden." % sys._getframe().f_code.co_name)

    def write_table(self):
        return self.__ini_txt + self._get_txt()

    def nl(self):
        if sys.platform.startswith('win'):
            return '\n\r'
        else:
            return '\n'

    def add_formatter(self, _type, formatter):
        self.__formatter[_type] = formatter

    def format_element(self, el):
        return self.__formatter.get(type(el), default_formatter)(el)

    def append_row(self, row_el, cell_type='d'):

        if cell_type == 'd':
            n_cell = self.new_cell
            e_cell = self.end_cell
        elif cell_type == 'h':
            n_cell = self.new_hcell
            e_cell = self.end_hcell

        self.new_row()

        for i in row_el:
            n_cell()
            self.add_value(i)
            e_cell()

        self.end_row()

    def get_col_cnt(self):
        return self.__col_cnt

    def set_col_cnt(self, col_cnt):
        self.__col_cnt = col_cnt

    col_cnt = property(get_col_cnt, set_col_cnt)

    def append_separator_line(self):
        self._append_txt(self.format_element(""))

    def append_closing_line(self):
        self._append_txt(self.format_element(""))

    def append_empty_line(self):
        self.append_row([""] * self.col_cnt)

    def add_title(self, title):
        NotImplementedError(
            " %s : is virutal and must be overridden." % sys._getframe().f_code.co_name)

    def add_value(self, val):
        self._append_txt(self.format_element(val))

    def new_head(self):
        self._append_txt(self.format_element(""))

    def end_head(self):
        self._append_txt(self.format_element(""))

    def new_tbody(self):
        self._append_txt(self.format_element(""))

    def end_tbody(self):
        self._append_txt(self.format_element(""))

    def new_foot(self):
        self._append_txt(self.format_element(""))

    def end_foot(self):
        self._append_txt(self.format_element(""))

    def new_row(self):
        NotImplementedError(
            " %s : is virutal and must be overridden." % sys._getframe().f_code.co_name)

    def end_row(self):
        NotImplementedError(
            " %s : is virutal and must be overridden." % sys._getframe().f_code.co_name)

    def new_cell(self):
        NotImplementedError(
            " %s : is virutal and must be overridden." % sys._getframe().f_code.co_name)

    def end_cell(self):
        NotImplementedError(
            " %s : is virutal and must be overridden." % sys._getframe().f_code.co_name)

    def new_hcell(self):
        return self.new_cell()

    def end_hcell(self):
        return self.end_cell()

    def new_bold(self):
        NotImplementedError(
            " %s : is virutal and must be overridden." % sys._getframe().f_code.co_name)

    def end_bold(self):
        NotImplementedError(
            " %s : is virutal and must be overridden." % sys._getframe().f_code.co_name)


class TextTable (Table):

    def append_separator_line(self):
        self.append_row(
            ["----------------------------------------------------------------------------------------------"])

    def append_closing_line(self):
        self.append_row(
            ["=============================================================================================="])

    def append_empty_line(self):
        self.append_row([""])

    def add_title(self, title):
        self._append_txt(title + self.nl())

    def new_table(self):
        self._set_txt("")

    def end_table(self):
        self._append_txt(self.nl())

    def new_row(self):
        self._append_txt("")

    def end_row(self):
        self._append_txt(self.nl())

    def new_cell(self):
        self._append_txt("")

    def end_cell(self):
        self._append_txt("\t")

    def new_bold(self):
        self._append_txt("")

    def end_bold(self):
        self._append_txt("")


class BBcodeTable (Table):

    def append_separator_line(self):
        self.append_row(["------------"] * self.col_cnt)

    def append_closing_line(self):
        self.append_row(["============"] * self.col_cnt)

    def add_title(self, title):
        self._append_txt(self.nl() + "[tr]" + self.nl() + " [td  colspan=%d] " %
                         self.col_cnt + title + " [/td] " + self.nl() + "[/tr]" + self.nl())

    def new_table(self):
        self._set_txt("")
        self._append_txt('[table]' + self.nl())

    def end_table(self):
        self._append_txt(self.nl() + '[/table]' + self.nl())

    def new_row(self):
        self._append_txt(self.nl() + '[tr]' + self.nl())

    def end_row(self):
        self._append_txt(self.nl() + '[/tr]' + self.nl())

    def new_cell(self):
        self._append_txt(' [td]')

    def end_cell(self):
        self._append_txt('[/td]')

    def new_bold(self):
        self._append_txt('[b]')

    def end_bold(self):
        self._append_txt('[/b]')


class HtmlTable (Table):

    def add_title(self, title):
        self._append_txt(self.nl() + "<tr>" + self.nl() + " <th colspan=\"%d\" > " %
                         self.col_cnt + title + "</th>" + self.nl() + "</tr>" + self.nl())

    def new_table(self):
        self._set_txt("")
        self._append_txt("<table>" + self.nl())

    def end_table(self):
        self._append_txt(self.nl() + "</table>" + self.nl())

    def new_head(self):
        self._append_txt(self.nl() + "<thead>" + self.nl())

    def end_head(self):
        self._append_txt(self.nl() + "</thead>" + self.nl())

    def new_tbody(self):
        self._append_txt(self.nl() + "<tbody>" + self.nl())

    def end_tbody(self):
        self._append_txt(self.nl() + "</tbody>" + self.nl())

    def new_foot(self):
        self._append_txt(self.nl() + "<tfoot>" + self.nl())

    def end_foot(self):
        self._append_txt(self.nl() + "</tfoot>" + self.nl())

    def new_row(self):
        self._append_txt(self.nl() + "<tr>" + self.nl())

    def end_row(self):
        self._append_txt(self.nl() + "</tr>" + self.nl())

    def new_cell(self):
        self._append_txt(' <td>')

    def end_cell(self):
        self._append_txt('</td>')

    def new_hcell(self):
        self._append_txt(' <th>')

    def end_hcell(self):
        self._append_txt('</th>')

    def new_bold(self):
        self._append_txt('<b>')

    def end_bold(self):
        self._append_txt('</b>')


class MediaWikiTable (Table):

    def add_title(self, title):
        self._append_txt("|-" + self.nl() + "!align=\"left\" colspan=\"%d\" | " %
                         self.col_cnt + title + self.nl())

    def new_table(self):
        self._set_txt("")
        self._append_txt("{| " + self.nl())

    def end_table(self):
        self._append_txt("|}" + self.nl())

    def new_row(self):
        self._append_txt("|-" + self.nl())

    def end_row(self):
        self._append_txt(self.nl())

    def new_cell(self):
        self._append_txt('||')

    def end_cell(self):
        self._append_txt("")

    def new_bold(self):
        self._append_txt("\'\'\'")

    def end_bold(self):
        self._append_txt("\'\'\'")


class row:

    def __init__(self):
        self.row = []
        self.cursor = 0
        self.inds = []
        self.rclass = "b"
        self.type = ""
        self.cell_type = []

    def set_type(self, t):
        self.type = t

    def set_rclass(self, c):
        self.rclass = c

    @property
    def set_row(self):
        self.set_type("r")
        return self.type

    @property
    def set_head(self):
        self.set_rclass("h")
        return self.rclass

    @property
    def set_body(self):
        self.set_rclass("b")
        return self.rclass

    @property
    def set_foot(self):
        self.set_rclass("f")
        return self.rclass

    @property
    def set_title(self):
        self.set_type("t")
        return self.type

    @property
    def set_separator_line(self):
        self.set_type("sl")
        return self.type

    @property
    def set_closing_line(self):
        self.set_type("cl")
        return self.type

    @property
    def is_row(self):
        if self.type == "r":
            return True
        else:
            return False

    @property
    def is_head(self):
        if self.rclass == "h":
            return True
        else:
            return False

    @property
    def is_body(self):
        if self.rclass == "b":
            return True
        else:
            return False

    @property
    def is_foot(self):
        if self.rclass == "f":
            return True
        else:
            return False

    @property
    def is_title(self):
        if self.type == "t":
            return True
        else:
            return False

    @property
    def is_separator_line(self):
        if self.type == "sl":
            return True
        else:
            return False

    @property
    def is_closing_line(self):
        if self.type == "cl":
            return True
        else:
            return False


class ExtendedTextTable (Table):

    # a column that has to be wrapped is never made narrower than this
    # (or than its header)
    min_wrap_sz = 8

    # with color on, the DR values are green when they are at least good_dr
    # and red when they are at most bad_dr
    good_dr = 14
    bad_dr = 7
    dr_cols = ["DR", "Mean", "Mean_DR"]

    # with color on, the cells in the columns "cols" of the rows whose "key"
    # column holds one of the texts in "rows" are written in bold with the
    # color of that text: {"key": head, "cols": [heads], "rows": {text: color}}
    highlight = {}

    def __init__(self):
        Table.__init__(self)
        self._cols_sz = [0] * Table.get_col_cnt(self)
        self._rows = []
        self._bold_state = False
        self._rclass_state = "b"
        self.color = False
        self._heads = []

    def get_col_cnt(self):
        return Table.get_col_cnt(self)

    def set_col_cnt(self, col_cnt):
        Table.set_col_cnt(self, col_cnt)

        if len(self._cols_sz) > col_cnt:
            self._cols_sz = self._cols_sz[:col_cnt]
        else:
            self._cols_sz += [0] * (col_cnt - len(self._cols_sz))

    col_cnt = property(get_col_cnt, set_col_cnt)

    def _eval_row_len(self):
        l = sum(self._cols_sz)
        l = l + len(self._cols_sz) * 3
        return l

    def _line_len(self, cols_sz):
        # " " + ( " " + cell + " " ) for each column
        return 1 + sum(cols_sz) + 2 * len(cols_sz)

    def _console_width(self):
        # 0 when the output is not a terminal: the table is not wrapped
        return shutil.get_terminal_size(fallback=(0, 0)).columns

    def _fit_cols_sz(self, width):
        cols_sz = list(self._cols_sz)

        if width <= 0:
            return cols_sz

        heads_sz = [0] * len(cols_sz)
        for r in self._rows:
            if r.is_row:
                for i, (cell, ct) in enumerate(zip(r.row, r.cell_type)):
                    if ct == "h":
                        heads_sz[i] = max(heads_sz[i], text_width(cell))

        min_sz = [min(sz, max(h_sz, self.min_wrap_sz))
                  for sz, h_sz in zip(cols_sz, heads_sz)]

        # keep the lines one char shorter than the console, some terminals
        # add an empty line when a line fills the whole width
        excess = self._line_len(cols_sz) - (width - 1)

        # shrink the widest column first, so short columns (DR, counters)
        # keep their natural size
        while excess > 0:
            shrinkable = [i for i in range(len(cols_sz))
                          if cols_sz[i] > min_sz[i]]
            if not shrinkable:
                break
            i = max(shrinkable, key=lambda c: cols_sz[c])
            cols_sz[i] -= 1
            excess -= 1

        return cols_sz

    def _update_col_sz(self):
        r = self._rows[-1]

        if r.is_row and len(r.row) == self.col_cnt:
            for c, i in zip(r.row, range(self.col_cnt)):
                if text_width(c) > self._cols_sz[i]:
                    self._cols_sz[i] = text_width(c)
        elif r.is_title:
            d = self._eval_row_len() - text_width(r.row[0])
            if d > 0:
                c = 0
                while d > 0:
                    self._cols_sz[c] += 1
                    d -= 1
                    c = (c + 1) % len(self._cols_sz)
        elif r.is_separator_line:
            pass
        elif r.is_closing_line:
            pass
        else:
            raise Exception("%s : Row model: Not Allowed " %
                            sys._getframe().f_code.co_name)

    def _style(self, txt, *names):
        return ansi.style(txt, *names) if self.color else txt

    def _cell_style(self, cell, head, ct, row_color=None):
        # the colored version of an already padded cell
        if not self.color:
            return cell

        if ct == "h":
            return ansi.style(cell, "bold")

        if row_color is not None and head in self.highlight["cols"]:
            return ansi.style(cell, "bold", row_color)

        if head == "Histogram":
            return ansi.style(cell, "blue")

        if head in self.dr_cols:
            try:
                v = float(cell)
            except ValueError:
                return cell
            if v >= self.good_dr:
                return ansi.style(cell, "bold", "green")
            if v <= self.bad_dr:
                return ansi.style(cell, "red")

        return cell

    def _write_title(self, r):
        txt = " "
        txt += self._style(r.row[0], "bold", "magenta")
        txt += self.nl()
        self._append_txt(txt)

    def _write_row(self, r, cols_sz):
        # a cell longer than its column is split on multiple lines
        cells = []
        for cell, sz in zip(r.row, cols_sz):
            if text_width(cell) <= sz:
                cells.append([cell])
            else:
                cells.append(wrap_text(cell, sz) or [""])

        is_head = "h" in r.cell_type
        if is_head:
            self._heads = [c.strip() for c in r.row]

        heads = self._heads + [""] * len(cols_sz)

        row_color = None
        if self.highlight and not is_head and self.highlight["key"] in heads:
            key = r.row[heads.index(self.highlight["key"])].strip()
            row_color = self.highlight["rows"].get(key)

        for l in range(max(len(c) for c in cells)):
            txt = " "
            last = len(cells) - 1
            for i, (c, sz, ct) in enumerate(zip(cells, cols_sz, r.cell_type)):
                t_txt = c[l] if l < len(c) else ""
                # the padding of the last column is not written
                t_txt = ljust_text(t_txt, sz) if i < last else t_txt
                txt += " " + self._cell_style(t_txt, heads[i], ct, row_color) + " "

            self._append_txt(txt.rstrip() + self.nl())

    def _write_separator_line(self, cols_sz):
        txt = " "
        txt += "=" * (self._line_len(cols_sz) - 1)
        txt += self.nl()
        self._append_txt(txt)

    def _write_closing_line(self, cols_sz):
        self._write_separator_line(cols_sz)

    def write_table(self):

        cols_sz = self._fit_cols_sz(self._console_width())

        for r in self._rows:
            if r.is_title:
                self._write_title(r)
            elif r.is_row:
                self._write_row(r, cols_sz)
            elif r.is_separator_line:
                self._write_separator_line(cols_sz)
            elif r.is_closing_line:
                self._write_closing_line(cols_sz)
            else:
                raise Exception("%s : Row model: Not Allowed " %
                                sys._getframe().f_code.co_name)

        return self.get_init_txt() + self._get_txt()

    def new_table(self):
        self._set_txt("")
        self._cols_sz = [0] * self.col_cnt
        self._rows = []

    def end_table(self):
        pass

    def append_separator_line(self):
        r = row()
        r.set_separator_line
        r.set_rclass(self._rclass_state)

        self._rows.append(r)

    def append_closing_line(self):
        r = row()
        r.set_closing_line
        r.set_rclass(self._rclass_state)

        self._rows.append(r)

    def append_empty_line(self):
        self.append_row([""] * self.col_cnt)
        self._update_col_sz()

    def add_title(self, title):
        r = row()
        r.set_title
        r.set_rclass(self._rclass_state)
        r.row.append(title)
        self._rows.append(r)
        self._update_col_sz()

    def new_row(self):
        r = row()
        r.set_row
        r.set_rclass(self._rclass_state)
        r.cursor = 0

        self._rows.append(r)

    def end_row(self):
        self._update_col_sz()

    def new_cell(self):
        self._rows[-1].inds.append(self._rows[-1].cursor)
        self._rows[-1].row.append("")
        self._rows[-1].cell_type.append("c")

    def end_cell(self):
        self._rows[-1].cursor += 1

    def add_value(self, val):
        c = self._rows[-1].cursor
        self._rows[-1].row[c] = self.format_element(val)

    def new_head(self):
        self._rclass_state = "h"

    def end_head(self):
        self._rclass_state = "b"

    def new_tbody(self):
        self._rclass_state = "b"

    def end_tbody(self):
        self._rclass_state = "b"

    def new_foot(self):
        self._rclass_state = "f"

    def end_foot(self):
        self._rclass_state = "b"

    def new_hcell(self):
        self._rows[-1].inds.append(self._rows[-1].cursor)
        self._rows[-1].row.append("")
        self._rows[-1].cell_type.append("h")

    def end_hcell(self):
        self.end_cell()

    def new_bold(self):
        self._bold_state = True

    def end_bold(self):
        self._bold_state = False
