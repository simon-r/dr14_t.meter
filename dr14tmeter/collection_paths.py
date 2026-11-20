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

"""Link the audio files of the collections to the tracks already stored in
the local DR database, without computing the DR again (database schema v3)."""

import os

from dr14tmeter.audio_decoder import AudioDecoder
from dr14tmeter.audio_math import sha1_track_v1
from dr14tmeter.audio_track import AudioTrack
from dr14tmeter.dr14_utils import list_rec_dirs
from dr14tmeter.dynamic_range_meter import progress_line
from dr14tmeter.out_messages import print_msg
from dr14tmeter.read_metadata import RetirveMetadata


def new_report():
    return {"known": 0, "by_metadata": 0, "by_sha1": 0,
            "unknown": [], "removed": 0, "skipped_roots": []}


def update_collection_paths(db, roots):
    """Update TrackPath for every audio file below the given roots.

    A file is matched to a stored Track by its ffprobe size and duration;
    when that is not unique, by the sha1 of the decoded audio. The DR is
    never computed. Stored paths below the roots whose files no longer exist
    are deleted. Return a report dict (see new_report).
    """
    report = new_report()
    formats = AudioDecoder().formats

    for root in roots:
        root = os.path.realpath(root)
        if root == os.sep or not os.path.isdir(root):
            # "/" is the "any" collection: walking the whole filesystem is
            # not useful.
            report["skipped_roots"].append(root)
            continue

        known = set(path for (_, path) in db.get_track_paths(root))
        new_pairs = []

        for folder in list_rec_dirs(root):
            files = sorted(f for f in os.listdir(folder)
                           if os.path.splitext(f)[1] in formats and
                           os.path.isfile(os.path.join(folder, f)))
            todo = []
            for f in files:
                if os.path.realpath(os.path.join(folder, f)) in known:
                    report["known"] += 1
                else:
                    todo.append(f)
            if not todo:
                continue

            print_msg(folder)
            meta = RetirveMetadata()
            meta.scan_dir(folder, files_list=todo)

            for (i, f) in enumerate(todo):
                full = os.path.realpath(os.path.join(folder, f))
                (id_track, how) = _match_file(db, meta, f, full)
                if id_track is None:
                    report["unknown"].append(full)
                    status = "not in the database"
                else:
                    report[how] += 1
                    new_pairs.append((id_track, full))
                    known.add(full)
                    status = "ok"
                print_msg(progress_line(i + 1, len(todo), f, status))

        db.add_track_paths(new_pairs)

        missing = [i for (i, path) in db.get_track_paths(root)
                   if not os.path.exists(path)]
        report["removed"] += db.delete_track_paths(missing)

    return report


def _match_file(db, meta, file_name, full_path):
    """Return (IdTrack or None, "by_metadata" | "by_sha1")."""
    size = meta.get_value(file_name, "size")
    duration = meta.get_value(file_name, "duration")
    if size is not None and duration is not None:
        ids = db.find_tracks_by_metadata(int(size), float(duration))
        if len(ids) == 1:
            return (ids[0], "by_metadata")

    # Not unique or no metadata: decode the audio for the sha1 only.
    at = AudioTrack()
    if not at.open(full_path):
        return (None, "by_sha1")
    sha1 = sha1_track_v1(at.Y, at.get_file_ext_code())
    return (db.find_track_by_sha1(sha1), "by_sha1")
