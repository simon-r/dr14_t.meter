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

import numpy 
import math
from dr14tmeter.audio_math import *

try:
    import matplotlib.pyplot as pyplot
    import matplotlib.mlab as mlab
    from matplotlib.lines import Line2D
except:
    pass


def compute_hist(Y, Fs, duration=None, bins=100, block_duration=0.2, plot=True, title=None):
    s = Y.shape

    if len(Y.shape) > 1:
        ch = s[1]
    else:
        ch = 1

    saples_per_block = int(Fs * block_duration)

    seg_cnt = int(math.floor(float(s[0]) / saples_per_block)) + 1

    if seg_cnt < 3:
        return False

    curr_sam = 0
    rms = numpy.zeros((seg_cnt, ch))

    #peaks = numpy.zeros((seg_cnt,ch))

    for i in range(seg_cnt - 1):
        #r = numpy.arange( curr_sam , curr_sam + saples_per_block )
        rms[i, :] = u_rms(Y[curr_sam: curr_sam + saples_per_block, :])
        curr_sam = curr_sam + saples_per_block

    i = seg_cnt - 1
    r = numpy.arange(curr_sam, s[0])

    if r.shape[0] > 0:
        rms[i, :] = dr_rms(Y[r, :])

    rms = numpy.sum(rms, 1) / float(ch)

    rms[rms == 0.0] = audio_min16()
    rms = decibel_u(rms, 1.0)

    rms_mean = numpy.mean(rms)
    rms_std = numpy.std(rms)
    rms_max = numpy.max(rms)

    abs_peak = decibel_u(numpy.max(numpy.abs(Y)), 1.0)

    if plot == True:
        (hist, bin_edges, patches) = pyplot.hist(rms, 100, density=True)

        mean_x = numpy.array([rms_mean, rms_mean])
        mean_y = numpy.array([0.0, numpy.max(hist) * 1.01])

        (mean_line,) = pyplot.plot(mean_x, mean_y, linewidth=2, color='g')

        # std dev: shaded +/- 1 sigma band plus a capped bar centred on the mean
        std_color = '#d95f02'
        std_y = numpy.max(hist) * 0.7

        std_band = pyplot.axvspan(rms_mean - rms_std, rms_mean + rms_std,
                                  color=std_color, alpha=0.12, linewidth=0, zorder=0)
        std_bar = pyplot.errorbar(rms_mean, std_y, xerr=rms_std, fmt='none', ecolor=std_color,
                                  elinewidth=2, capsize=8, capthick=2, zorder=3)
        pyplot.annotate(r'$\pm 1\sigma$', xy=(rms_mean + rms_std, std_y),
                        xytext=(8, 0), textcoords='offset points',
                        ha='left', va='center', fontsize=12, color='#333333',
                        bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.8))

        pyplot.axis([-92, 0, 0, numpy.max(hist) * 1.05])

        # peak and max rms have no mark on the plot: list them as text-only rows
        no_mark = Line2D([], [], linestyle='none')

        pyplot.legend([mean_line, (std_band, std_bar), no_mark, no_mark],
                      [r'mean  $\mu$ = %.2f dB' % rms_mean,
                       r'std dev  $\sigma$ = %.2f dB' % rms_std,
                       'peak = %.2f dB' % abs_peak,
                       'max RMS = %.2f dB' % rms_max],
                      loc='best', fontsize=11, handlelength=1.6, framealpha=0.9)

        pyplot.xlabel('RMS dB')
        pyplot.ylabel('Relative frequency')

        if title != None:
            hist_title = title
        else:
            hist_title = "Hystogram of dynamic"

        pyplot.title(r'%s' % hist_title)

        pyplot.grid(True)
        pyplot.show()

    else:
        (hist, bin_edges) = numpy.histogram(rms, bins=bins, density=True)

    return (hist, bin_edges)
