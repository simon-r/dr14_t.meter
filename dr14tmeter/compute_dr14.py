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


from dr14tmeter.audio_math import *
from dr14tmeter.out_messages import *

import numpy as np

import math
import time


def compute_dr14(Y, Fs, duration=None, Dr_lr=None):

    s = Y.shape

    if len(Y.shape) > 1:
        ch = s[1]
    else:
        ch = 1

    if Fs == 44100:
        delta_fs = 60
    else:
        delta_fs = 0

    dr14_log_debug("compute_dr14: Y: Fs: %d ; ch: %d ; shape: %d " %
                   (Fs, ch, s[0]))
    time_a = time.time()

    block_time = 3
    cut_best_bins = 0.2
    block_samples = block_time * (Fs + delta_fs)

    seg_cnt = int(math.floor(s[0] / block_samples) + 1)

    if seg_cnt < 1:
        dr14_log_debug("compute_dr14: EXIT - too short")
        return (0, -100, -100)

    curr_sam = 0
    rms = np.zeros((seg_cnt, ch))
    peaks = np.zeros((seg_cnt, ch))

    for i in range(seg_cnt - 1):
        rms[i, :] = np.sqrt(2.0 * np.sum(Y[curr_sam:curr_sam + block_samples, :]**2.0, 0) /
                            float(block_samples))
        peaks[i, :] = np.max(
            np.abs(Y[curr_sam:curr_sam + block_samples, :]), 0)
        curr_sam = curr_sam + block_samples

    i = seg_cnt - 1

    if curr_sam < s[0]:
        rms[i, :] = dr_rms(Y[curr_sam:s[0] - 1, :])
        peaks[i, :] = np.max(np.abs(Y[curr_sam:s[0] - 1, :]), 0)

    peaks = np.sort(peaks, 0)
    rms = np.sort(rms, 0)

    n_blk = int(math.floor(seg_cnt * cut_best_bins))
    if n_blk == 0:
        n_blk = 1

    r = np.arange(seg_cnt - n_blk, seg_cnt)

    rms_sum = np.sum(rms[r, :]**2, 0)

    ch_dr14 = -20.0 * np.log10(np.sqrt(rms_sum / n_blk)
                               * 1.0 / peaks[seg_cnt - 2, :])

    err_i = np.logical_or(rms_sum < audio_min(),
                          np.abs(ch_dr14) > max_dynamic(24))
    ch_dr14[err_i] = 0.0

    dr14 = round(np.mean(ch_dr14))

    db_peak = decibel_u(np.max(peaks), 1.0)

    #y_rms = np.sqrt(np.sum(((np.sum(Y, 1) / 2)**2)) / Y.shape[0])

    y_rms = dr_rms(Y)
    y_rms = np.mean(y_rms)

    db_rms = decibel_u(y_rms, 1.0)

    if duration != None:
        duration.set_samples(s[0], Fs)

    if Dr_lr != None:
        Dr_lr = ch_dr14

    time_b = time.time()
    dr14_log_info("compute_dr14: Clock: %2.8f" % (time_b - time_a))

    return (dr14, db_peak, db_rms)
