# How to use DR14 T.meter

A short reference of every feature of `dr14_tmeter`. For installation, see the [README](README.md). Run `dr14_tmeter --help` for the raw list of options.

Supported formats: FLAC, MP3, Ogg Vorbis, Opus, MP4/M4A, WAV, WavPack, AC3, WMA, DSF and DFF.

## Measuring the DR

| Command | What it does |
| --- | --- |
| `dr14_tmeter DIR` | Measures every audio file in `DIR` (the current directory if omitted) and the album DR. |
| `dr14_tmeter -r DIR` | Also scans all subdirectories, one result per directory. |
| `dr14_tmeter -f FILE` | Measures a single file and prints its DR, peak and RMS. |
| `dr14_tmeter --files_list LIST` | Measures the files listed in `LIST`, one path per line, or read from standard input if `LIST` is omitted. |
| `--no_overwrite` | Skips the directories that already contain result files. With `-r`, it analyses only new albums. |
| `-1` | Uses a single CPU core. By default, half of the cores are used. |
| `--quiet` | Hides the progress messages. |
| `--skip_version_check` | Skips the online check for a newer version. |
| `-v` | Prints the version. |

## Result files

By default, a text table named after the album DR (for example `dr14-DR12.txt`) is written in each analysed directory.

| Option | What it does |
| --- | --- |
| `-t t\|h\|b\|w\|a` | Chooses the format: `t` text, `h` HTML, `b` BBCode, `w` MediaWiki, `a` all of them. |
| `-o DIR` | Writes the files to `DIR` instead of the analysed directory. |
| `-a` | Appends the results of all directories to the files in the top directory. Use it with `-r`. |
| `-b` | Writes the basic table, which lists file names and leaves out the track titles, codec, bitrate, sample rate and bit depth. |
| `-d` | Writes the text table in the format accepted by the [DR database](http://www.dr.loudness-war.info). |
| `-p` | Also prints the full table in the terminal. |
| `-n` | Writes no files. Note that this also skips the local database. |

## Local DR database

DR14 T.meter can keep every result in a local SQLite database, so that you can explore your whole collection: best and worst albums, DR per year, DR per codec, and more. The database is disabled by default.

### Enabling it

```sh
dr14_tmeter --enable_database
```

This command asks two questions:

1. **The database directory.** The default is `~/.config/dr14tmeter`. The file is named `dr14_database.db`.
2. **The collection directory.** Only tracks inside this directory are stored. Answer `any` (the default) to store everything.

The settings are saved in `~/.config/dr14tmeter/dr14.cfg` (or under `$XDG_CONFIG_HOME`).

### What is stored

Once enabled, the results of every directory scan, including `-r`, are stored automatically. For each track, the database stores the DR, peak, RMS, title, artist, album, genre, year, codec, duration, bit depth, bitrate, sample rate and file size. It also stores the DR of each album.

- Each track is identified by a hash of its audio data, so measuring an album again does not create duplicates, even if the files were moved or renamed.
- Single-file scans (`-f`) and runs with `-n` are **not** stored.
- Directories skipped by `--no_overwrite` are not stored either. To add an already measured collection to the database, run a plain `dr14_tmeter -r` on it once.

### Querying it

| Command | Result |
| --- | --- |
| `dr14_tmeter -q` | Opens an interactive menu with all the queries below. |
| `dr14_tmeter -q top [N]` | The `N` tracks with the highest DR (default 30). |
| `dr14_tmeter -q worst [N]` | The `N` tracks with the lowest DR. |
| `dr14_tmeter -q top_alb [N]` | The `N` albums with the highest DR. |
| `dr14_tmeter -q worst_alb [N]` | The `N` albums with the lowest DR. |
| `dr14_tmeter -q top_art [N] [MIN]` | The `N` artists with the highest mean DR, counting only artists with at least `MIN` tracks (default 10). |
| `dr14_tmeter -q artist NAME [N]` | The `N` albums and the `N` tracks of the artist `NAME` with the highest DR. Quote names containing spaces, for example `-q artist "Pink Floyd"`. The search finds all the artists whose name contains `NAME`, ignoring the case: `-q artist pink` finds both Pink and Pink Floyd. When more than one artist is found, a menu lets you choose one or more of them (press Enter for all). |
| `dr14_tmeter -q hist` | A histogram of how many tracks have each DR value. |
| `dr14_tmeter -q evol` | The mean DR per release year, as a table and a plot in the terminal. |
| `dr14_tmeter -q codec` | The number of tracks and the mean DR for each codec. |

### Maintenance

| Command | What it does |
| --- | --- |
| `dr14_tmeter --dump_database` | Prints the whole database as SQL. |
| `dr14_tmeter --disable_database` | Stops storing new results. The file is kept, and `--enable_database` turns it back on. |

If the database file is damaged, `dr14_tmeter` offers to rebuild it, keeping a backup of the old file with the extension `.d_save`, or to disable it.

The database is a plain SQLite file, so you can also open it with `sqlite3` or any SQLite browser to run your own queries.

## Writing DR tags

`--tag` writes the measured values into the tags of the audio files, during a directory scan or a `--files_list` scan. It requires [Mutagen](https://mutagen.readthedocs.io).

- FLAC, Ogg Vorbis and Opus files get a `DR` tag and an `ALBUM_DR` tag.
- MP3 files get a `TXXX:DR` frame, and MP4/M4A files a `----:com.apple.iTunes:DR` atom, with the track DR only.
- WAV, AC3 and WMA files cannot be tagged.

## Analysing a single track

These options take one audio file as `path_name`, show their result and exit. All of them require Matplotlib, except `--compress`, which requires SciPy.

| Option | What it shows |
| --- | --- |
| `--hist` | The histogram of the RMS levels of the track, measured in 0.2-second blocks, with their mean, standard deviation and the peak. |
| `--lev_hist` | The histogram of the sample levels. |
| `--dyn_vivacity` | The peak-to-RMS ratio of each second of the track. |
| `--plot_track` | The waveform of the track. |
| `--plot_track_dst` | The density of the sample values over time. |
| `--spectrogram` | The spectrogram of the track (beta). |
| `--compress MODE` | Writes a dynamically compressed copy of the track as WAV to the temp directory. `MODE` is one of `very_soft`, `soft`, `medium`, `hard` or `very_hard` (short forms `v`, `s`, `m`, `h`, `vh`). |
