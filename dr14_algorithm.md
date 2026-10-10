# DR14 algorithm: mathematical description

This document describes the computation performed by `compute_dr14()` in
`dr14tmeter/compute_dr14.py`. Given a track, it returns three values:

- $\mathrm{DR}$: the integer dynamic range score,
- $\mathrm{Peak}_{\mathrm{dB}}$: the peak level in dBFS,
- $\mathrm{RMS}_{\mathrm{dB}}$: the overall RMS level in dBFS.

## 0. Notation

### Symbols

| Symbol | Meaning | Unit | Code |
| --- | --- | --- | --- |
| $N$ | Track length: number of samples in each channel | samples | `s[0]` = `Y.shape[0]` |
| $C$ | Number of audio channels (1 = mono, 2 = stereo, …) | – | `ch` |
| $n$ | Sample index (time position), $0 \le n \le N-1$ | – | row of `Y` |
| $c$ | Channel index, $1 \le c \le C$ | – | column of `Y` (0-based in code) |
| $y_c[n]$ | Value of sample $n$ in channel $c$, normalized to full scale | – | `Y[n, c-1]` |
| $F_s$ | Sampling rate | Hz (samples/s) | `Fs` |
| $T$ | Nominal block duration, $T = 3$ | s | `block_time` |
| $q$ | Fraction of loudest blocks used, $q = 0.2$ | – | `cut_best_bins` |
| $\Delta$ | Sampling-rate correction (60 at 44.1 kHz, otherwise 0) | samples/s | `delta_fs` |
| $L$ | Block length | samples | `block_samples` |
| $M$ | Number of blocks | – | `seg_cnt` |
| $k$ | Block index, $0 \le k \le M-1$ | – | `i` |
| $N_{\mathrm{rem}}$ | Samples left over after the last full block | samples | `s[0] - curr_sam` |
| $B_k$ | Set of sample indices that belong to block $k$ | – | slice of `Y` |
| $\lvert B_k \rvert$ | Number of samples in block $k$ | samples | slice length |
| $R_{k,c}$ | RMS level of block $k$, channel $c$ | linear, full scale = 1 | `rms[k, c-1]` (before sort) |
| $P_{k,c}$ | Peak level of block $k$, channel $c$ | linear, full scale = 1 | `peaks[k, c-1]` (before sort) |
| $j$ | Rank after sorting, $1 \le j \le M$ (1 = smallest) | – | row of sorted array |
| $R_{(j),c}$ | $j$-th smallest block RMS of channel $c$ | linear | `rms[j-1, c-1]` (after sort) |
| $P_{(j),c}$ | $j$-th smallest block peak of channel $c$ | linear | `peaks[j-1, c-1]` (after sort) |
| $K$ | Number of loudest blocks used for the RMS average | – | `n_blk` |
| $S_c$ | Sum of the squared RMS of the $K$ loudest blocks | linear² | `rms_sum[c-1]` |
| $\bar{R}_c$ | Quadratic mean of the $K$ loudest block RMS values | linear | `np.sqrt(rms_sum / n_blk)` |
| $\hat{P}_c$ | Reference peak: second-highest block peak | linear | `peaks[seg_cnt - 2, c-1]` |
| $\mathrm{DR}_c$ | Dynamic range of channel $c$ | dB | `ch_dr14[c-1]` |
| $\varepsilon$ | Silence threshold, $\varepsilon = 2^{-24}$ | linear² | `audio_min()` |
| $D_{\max}$ | Largest accepted DR, $D_{\max} = 20\log_{10}(2^{24})$ | dB | `max_dynamic(24)` |
| $\mathrm{DR}$ | Final dynamic range score | dB (integer) | `dr14` |
| $\mathrm{Peak}_{\mathrm{dB}}$ | Peak level of the track | dBFS | `db_peak` |
| $\mathrm{RMS}_c$ | RMS of channel $c$ over the whole track | linear | `dr_rms(Y)[c-1]` |
| $\overline{\mathrm{RMS}}$ | Mean of $\mathrm{RMS}_c$ over channels | linear | `y_rms` |
| $\mathrm{RMS}_{\mathrm{dB}}$ | Overall RMS level of the track | dBFS | `db_rms` |

### Operators and units

| Notation | Meaning |
| --- | --- |
| $\lfloor x \rfloor$ | Floor: largest integer $\le x$ |
| $a \bmod b$ | Remainder of the integer division of $a$ by $b$ |
| $\lvert x \rvert$ | Absolute value of a number; for a set, its number of elements |
| $\max_{n \in B} f(n)$ | Largest value of $f(n)$ over all $n$ in the set $B$ |
| $\log_{10}$ | Base-10 logarithm |
| $\operatorname{round}(x)$ | Nearest integer to $x$; exact halves go to the even integer |
| $\lor$ | Logical "or" |
| dB | Decibel. For two amplitudes $a$ and $b$, $a$ is $20\log_{10}(a/b)$ dB relative to $b$ |
| dBFS | Decibel relative to full scale, i.e. relative to amplitude $1$ |
| linear | A plain amplitude value on the scale where full scale is $1$ |

## 1. Input

The input is a track with $C$ channels, each holding $N$ samples taken at
sampling rate $F_s$. The value of sample $n$ of channel $c$ is

$$
y_c[n] \in [-1, 1], \qquad n = 0, 1, \dots, N-1, \qquad c = 1, 2, \dots, C .
$$

The value $\pm 1$ is digital full scale (the largest amplitude the format can
store). Its duration in seconds is $N / F_s$.

## 2. Block segmentation

### Constants

$$
T = 3\ \mathrm{s} \quad \text{(nominal block duration)},
\qquad\qquad
q = 0.2 \quad \text{(fraction of loudest blocks used later)}.
$$

### Block length

Define the correction $\Delta$, in samples per second:

$$
\Delta =
\begin{cases}
60 & \text{if } F_s = 44100\ \mathrm{Hz} \\
0  & \text{otherwise}
\end{cases}
$$

The block length $L$, in samples, is

$$
L = T\,(F_s + \Delta).
$$

At $F_s = 44100$ Hz this gives $L = 3 \cdot 44160 = 132480$ samples
($L / F_s \approx 3.0041$ s). At any other rate $L = 3F_s$ samples, exactly 3 s.

### Number of blocks

The number of complete blocks is $\lfloor N / L \rfloor$. Leaving them out, the
number of samples still left is

$$
N_{\mathrm{rem}} = N - L \left\lfloor \frac{N}{L} \right\rfloor = N \bmod L,
\qquad 0 \le N_{\mathrm{rem}} \le L - 1 .
$$

One extra block is always reserved for that remainder, so the total number of
blocks is

$$
M = \left\lfloor \frac{N}{L} \right\rfloor + 1 .
$$

Since $M \ge 1$ for every $N \ge 0$, the "too short" early exit in the code is
never taken.

### Sample indices of each block

For $k = 0, 1, \dots, M-2$, block $k$ is a complete block containing the
samples

$$
B_k = \{\, kL,\; kL+1,\; \dots,\; (k+1)L - 1 \,\},
\qquad \lvert B_k \rvert = L .
$$

The last block, $k = M-1$, takes the remainder. Because the code slices
`Y[curr_sam : N-1]`, it stops one sample short of the end of the track
(sample $N-1$ is left out):

$$
B_{M-1} = \{\, (M-1)L,\; (M-1)L + 1,\; \dots,\; N-2 \,\},
\qquad \lvert B_{M-1} \rvert = N_{\mathrm{rem}} - 1
\qquad (\text{when } N_{\mathrm{rem}} \ge 2).
$$

If $N_{\mathrm{rem}} = 0$, the last block is not computed at all (see
section 3), and if $N_{\mathrm{rem}} = 1$ it is empty (see section 12).

## 3. Per-block RMS and peak

For every block $k = 0, \dots, M-1$ and channel $c = 1, \dots, C$, the block
RMS level $R_{k,c}$ and block peak level $P_{k,c}$ are

$$
R_{k,c} = \sqrt{\frac{2}{\lvert B_k \rvert} \sum_{n \in B_k} y_c[n]^2}
\qquad\qquad
P_{k,c} = \max_{n \in B_k} \bigl| y_c[n] \bigr| .
$$

Here $\sum_{n \in B_k}$ is the sum over all sample indices in block $k$.

The factor $2$ inside the square root scales the ordinary RMS by $\sqrt{2}$.
For example, take a sine wave $y[n] = A\sin(\omega n)$, where $A$ is its
amplitude and $\omega$ its angular frequency in radians per sample. Its
ordinary RMS is $A/\sqrt{2}$, so it gets $R = A$, the same value as its peak.
A full-scale sine ($A = 1$) therefore reads $0$ dBFS on both.

If $N_{\mathrm{rem}} = 0$ (the track length is an exact multiple of $L$),
the last block keeps its initial values: $R_{M-1,c} = P_{M-1,c} = 0$.

## 4. Sorting

For each channel $c$, the $M$ RMS values $R_{0,c}, \dots, R_{M-1,c}$ are sorted
in ascending order, and so are the $M$ peak values $P_{0,c}, \dots, P_{M-1,c}$.
The sorted values are written with the rank $j$ in parentheses, with
$j = 1$ for the smallest and $j = M$ for the largest:

$$
R_{(1),c} \le R_{(2),c} \le \dots \le R_{(M),c},
\qquad
P_{(1),c} \le P_{(2),c} \le \dots \le P_{(M),c}.
$$

The two lists are sorted **independently**, so $R_{(j),c}$ and $P_{(j),c}$
generally come from different blocks.

## 5. Loudest 20% of blocks

The number of blocks kept, $K$, is the fraction $q = 0.2$ of $M$, rounded down,
but at least 1:

$$
K = \max\bigl(1,\; \lfloor q M \rfloor\bigr).
$$

The $K$ loudest blocks are the ranks $j = M-K+1, \dots, M$. The sum of their
squared RMS values, $S_c$, and their quadratic mean, $\bar{R}_c$, are

$$
S_c = \sum_{j = M-K+1}^{M} R_{(j),c}^{\,2},
\qquad\qquad
\bar{R}_c = \sqrt{\frac{S_c}{K}} .
$$

$\bar{R}_c$ averages power (squared RMS), not RMS values directly.

## 6. Reference peak

The reference peak $\hat{P}_c$ is the **second-highest** block peak of channel
$c$. Skipping the highest one makes the measure robust against a single
isolated transient:

$$
\hat{P}_c =
\begin{cases}
P_{(M-1),c} & \text{if } M \ge 2 \\
P_{(1),c}   & \text{if } M = 1
\end{cases}
$$

The case $M = 1$ comes from the code index `seg_cnt - 2` evaluating to $-1$,
which in Python selects the last (here, the only) element.

## 7. Per-channel dynamic range

The dynamic range of channel $c$, $\mathrm{DR}_c$, is the ratio between the
reference peak and the loud-block RMS, in decibels:

$$
\mathrm{DR}_c = -20 \log_{10}\!\left( \frac{\bar{R}_c}{\hat{P}_c} \right)
             = 20 \log_{10}\!\left( \frac{\hat{P}_c}{\bar{R}_c} \right)
\quad [\mathrm{dB}].
$$

### Validity check

Define the silence threshold $\varepsilon$ (the smallest step of 24-bit audio,
in squared-amplitude units as used here) and the largest accepted dynamic
range $D_{\max}$ (the full range of 24-bit audio):

$$
\varepsilon = 2^{-24},
\qquad\qquad
D_{\max} = 20 \log_{10}\!\left(2^{24}\right) \approx 144.49\ \mathrm{dB}.
$$

A channel's value is replaced by zero if the channel is effectively silent or
the result is out of range:

$$
\mathrm{DR}_c \leftarrow 0
\quad \text{if} \quad
S_c < \varepsilon
\;\;\lor\;\;
\bigl|\mathrm{DR}_c\bigr| > D_{\max} .
$$

This also catches the degenerate cases: $\hat{P}_c = 0$ gives
$\lvert \mathrm{DR}_c \rvert = \infty$, and a silent channel
($\hat{P}_c = \bar{R}_c = 0$) fails the $S_c < \varepsilon$ test.

## 8. Final DR score

The final score $\mathrm{DR}$ is the mean of $\mathrm{DR}_c$ over the $C$
channels, rounded to the nearest integer:

$$
\mathrm{DR} = \operatorname{round}\!\left( \frac{1}{C} \sum_{c=1}^{C} \mathrm{DR}_c \right).
$$

Python's `round()` rounds exact halves to the nearest even integer
(e.g. $8.5 \to 8$, $9.5 \to 10$).

## 9. Peak level

The peak level $\mathrm{Peak}_{\mathrm{dB}}$ is the largest block peak over
all blocks $k$ and all channels $c$, in dBFS:

$$
\mathrm{Peak}_{\mathrm{dB}} = 20 \log_{10}\!\left( \max_{\substack{0 \le k \le M-1 \\ 1 \le c \le C}} P_{k,c} \right)
\quad [\mathrm{dBFS}].
$$

This equals the largest absolute sample value of the track, except that
sample $N-1$ is not considered (see section 2).

## 10. Overall RMS level

For each channel $c$, $\mathrm{RMS}_c$ is the RMS over the whole track, with
the same $\sqrt{2}$ scaling as in section 3. The values are averaged linearly
over channels into $\overline{\mathrm{RMS}}$, then converted to dBFS:

$$
\mathrm{RMS}_c = \sqrt{\frac{2}{N} \sum_{n=0}^{N-1} y_c[n]^2},
\qquad
\overline{\mathrm{RMS}} = \frac{1}{C} \sum_{c=1}^{C} \mathrm{RMS}_c,
\qquad
\mathrm{RMS}_{\mathrm{dB}} = 20 \log_{10} \overline{\mathrm{RMS}}
\quad [\mathrm{dBFS}].
$$

Unlike the block values, this uses all $N$ samples, including sample $N-1$.

## 11. Worked example

A 4-minute stereo track ($C = 2$) at $F_s = 44100$ Hz:

$$
N = 240 \cdot 44100 = 10\,584\,000,
\qquad
L = 3 \cdot (44100 + 60) = 132\,480,
$$

$$
M = \left\lfloor \tfrac{10\,584\,000}{132\,480} \right\rfloor + 1 = 79 + 1 = 80,
\qquad
N_{\mathrm{rem}} = 10\,584\,000 - 79 \cdot 132\,480 = 118\,080,
\qquad
K = \lfloor 0.2 \cdot 80 \rfloor = 16 .
$$

So there are 79 full blocks plus a remainder block of
$N_{\mathrm{rem}} - 1 = 118\,079$ samples. For each channel, $\bar{R}_c$ is
computed from the 16 largest block RMS values, and $\hat{P}_c = P_{(79),c}$ is
the 79th of the 80 sorted block peaks. The two values $\mathrm{DR}_1$ and
$\mathrm{DR}_2$ are then averaged and rounded.

## 12. Edge cases in the implementation

- **$N_{\mathrm{rem}} = 1$ (one sample of remainder).** The last block
  $B_{M-1}$ is empty ($\lvert B_{M-1} \rvert = 0$). Its RMS evaluates to $0/0$
  (NaN, with a warning) and the peak computation raises
  `ValueError: zero-size array to reduction operation maximum which has no
  identity`. This happens whenever $N \bmod L = 1$.
- **$N_{\mathrm{rem}} = 0$ (exact multiple of $L$).** The unused remainder block
  contributes $R_{M-1,c} = P_{M-1,c} = 0$. It still counts toward $M$ and
  therefore toward $K = \max(1, \lfloor qM \rfloor)$.
- **Last sample dropped.** Sample $N-1$ never enters any block, so it does not
  affect $\mathrm{DR}$ or $\mathrm{Peak}_{\mathrm{dB}}$. It does enter
  $\mathrm{RMS}_{\mathrm{dB}}$, which is computed on the full signal.
