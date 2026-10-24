# DR14 T.meter

DR14 T.meter is a free and open-source command-line tool for computing the dynamic range of your music, following the procedure used by the offline meter released by the [Pleasurize Music Foundation](https://web.archive.org/web/20130111082140/http://www.pleasurizemusic.com/) (archived site).

This tool is useful for measuring how loud your music is, for seeing that a good-quality album always has good dynamics too, and for understanding the effects of the so-called loudness war.

DR14 T.meter is released under the terms of the GNU GPLv3 license. It is intended for Linux users who cannot use the Windows application released by the Pleasurize Music Foundation or the foobar2000 plugin.

I have tested this application extensively, and it has always returned results identical to those of the official offline meter.

## How to use

> 📖 **A short guide to every feature, including the local DR database and its queries, is in [how_to_use.md](how_to_use.md).**

**Requirements:** Python 3 with NumPy, and `ffmpeg` (or `avconv`) for decoding. MP3 files are decoded with `lame` and Ogg Vorbis files with `oggdec` (from vorbis-tools). Matplotlib, SciPy and Mutagen are only needed for the plotting, `--compress` and `--tag` options.

You can run the tool directly from the cloned repository as `./dr14_tmeter`, or install it with [pipx](https://pipx.pypa.io), which also installs NumPy and the man page:

```sh
git clone https://github.com/simon-r/dr14_t.meter.git
cd dr14_t.meter
pipx install .
```

Use `pipx install '.[plot,compress,tag]'` to also install the optional dependencies, or `pip install .` inside a virtual environment instead of pipx.

On Debian and Ubuntu you can build and install a `.deb` package instead:

```sh
sudo apt build-dep .
dpkg-buildpackage -us -uc -b
sudo apt install ../dr14tmeter_*_all.deb
```

Avoid `sudo python setup.py install --prefix=usr`: on Debian and Ubuntu it puts the package in a directory that Python does not search, and `dr14_tmeter` then fails with `ImportError: No module named dr14tmeter.dr14_tmeter`.

```sh
# Measure all the audio files in an album directory
dr14_tmeter /path/to/album

# Measure a whole music collection, one result per directory
dr14_tmeter -r /path/to/music

# Measure a single file and print its DR, peak and RMS values
dr14_tmeter -f /path/to/track.flac
```

When measuring a directory, the results are written to a text table named after the DR value (for example `dr14-DR12.txt`) in that directory. Useful options:

- `-t a` also writes the results as HTML, BBCode and MediaWiki tables,
- `-o DIR` writes the result files to `DIR` instead,
- `-p` prints the full table to the terminal, and `-n` skips writing files.

See [how_to_use.md](how_to_use.md) for all the other features, or run `dr14_tmeter --help` for the full list of options.

## How the DR value is computed

> 📐 **The full mathematical description of the algorithm, with every quantity defined, is in [dr14_algorithm.md](dr14_algorithm.md).**

In short, each channel of the track is split into blocks of about 3 seconds, and the RMS level and the peak level of every block are measured. Then, for each channel $c$ out of the $C$ channels of the track:

- $\bar{R}_c$ is the quadratic mean of the RMS levels of the loudest 20% of the blocks,
- $\hat{P}_c$ is the second-highest block peak.

The DR value is the ratio between the two in decibels, averaged over the channels and rounded to an integer:

$$
\mathrm{DR} = \mathrm{round}\left( \frac{1}{C} \sum_{c=1}^{C} 20 \log_{10} \frac{\hat{P}_c}{\bar{R}_c} \right)
$$

## More information

Visit <https://github.com/simon-r/dr14_t.meter>.
