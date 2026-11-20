import configparser
import math
from contextlib import closing
import os
import sqlite3
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
import wave
from unittest import mock

from dr14tmeter import collection_paths
from dr14tmeter import database
from dr14tmeter import dr14_config


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DatabaseTestBase(unittest.TestCase):
    """Temporary config and databases shared by the tests below."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        config_dir = os.path.join(self.temp.name, "dr14tmeter")
        os.mkdir(config_dir)
        self.normal_path = os.path.join(self.temp.name, "normal.db")
        self.dev_path = self.normal_path + ".developer"
        config = configparser.ConfigParser()
        config["database"] = {
            "path": self.normal_path,
            "enabled": "True",
            "collection_dir": "/",
        }
        with open(os.path.join(config_dir, "dr14.cfg"), "w") as config_file:
            config.write(config_file)
        self.env = mock.patch.dict(os.environ, {
            "XDG_CONFIG_HOME": self.temp.name,
            "DR14_DEVELOPER_DB": "1",
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.db = database.dr_database()
        self.addCleanup(self.reset_singleton)

    def reset_singleton(self):
        database.unique_db_object = 0

    def create_normal_database(self, version=2):
        conn = sqlite3.connect(self.normal_path)
        conn.executescript(self.db.dr14_db_main_structure_v1())
        if version >= 2:
            conn.executescript(self.db.dr14_db_migrate_v1_to_v2())
        if version >= 3:
            conn.executescript(self.db.dr14_db_migrate_v2_to_v3())
        conn.close()

    def query(self, path, sql):
        with closing(sqlite3.connect(path)) as conn:
            return conn.execute(sql).fetchall()

    def run_cli(self, *args, **env):
        process_env = os.environ.copy()
        process_env.update(env)
        return subprocess.run(
            [sys.executable, os.path.join(ROOT, "dr14_tmeter")] + list(args),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True,
            env=process_env, cwd=ROOT, timeout=30)

    def make_dir(self, *parts):
        path = os.path.join(self.temp.name, *parts)
        os.makedirs(path, exist_ok=True)
        return os.path.realpath(path)


class DeveloperDatabaseTests(DatabaseTestBase):
    def test_normal_mode_keeps_version_two(self):
        self.create_normal_database(version=1)
        os.environ["DR14_DEVELOPER_DB"] = "0"
        self.assertEqual(dr14_config.get_db_path(), self.normal_path)
        database.prepare_developer_database()
        self.db.upgrade_db()
        self.assertEqual(self.db.db_version, 2)
        self.assertFalse(os.path.exists(self.dev_path))
        self.assertEqual(self.query(self.normal_path,
                                    "select name from sqlite_master where name='TrackPath'"), [])

    def test_snapshot_migration_reuse_and_wal(self):
        self.create_normal_database()
        conn = sqlite3.connect(self.normal_path)
        self.addCleanup(conn.close)
        conn.execute("pragma journal_mode=wal")
        conn.execute("insert into Artist (Name) values ('from wal')")
        conn.commit()
        database.prepare_developer_database()
        self.db.upgrade_db()
        self.assertEqual(self.db.db_version, 3)
        self.assertEqual(self.query(self.dev_path, "select Name from Artist"), [("from wal",)])
        self.assertEqual(self.query(self.normal_path, "select max(Version) from Db_Version"), [(2,)])
        self.assertEqual(self.query(self.dev_path,
                                    "select name from sqlite_master where name='TrackPath'"),
                         [("TrackPath",)])
        conn.execute("insert into Artist (Name) values ('later')")
        conn.commit()
        database.prepare_developer_database()
        self.db.upgrade_db()
        self.assertEqual(self.query(self.dev_path, "select Name from Artist"), [("from wal",)])

    def test_environment_switch_selects_database_for_reads_and_writes(self):
        self.create_normal_database()
        database.prepare_developer_database()
        self.db.upgrade_db()

        self.db.open_insert_session()
        self.db.insert_track("dev-track", "Developer track", 12, 0.1, 0.5,
                             60, "wav", 16, 1411, 44100)
        self.db.commit_insert_session()

        self.assertEqual(self.db.query("select Title from Track"),
                         [("Developer track",)])
        self.assertEqual(self.query(self.normal_path, "select Title from Track"), [])
        self.assertEqual(self.db.db_version, 3)

        del os.environ["DR14_DEVELOPER_DB"]
        self.assertEqual(self.db.query("select Title from Track"), [])
        self.assertEqual(self.db.db_version, 2)

        os.environ["DR14_DEVELOPER_DB"] = "1"
        self.assertEqual(self.db.query("select Title from Track"),
                         [("Developer track",)])
        self.assertEqual(self.db.db_version, 3)

    def test_missing_and_invalid_source_are_not_copied(self):
        with self.assertRaisesRegex(ValueError, "normal database does not exist"):
            database.prepare_developer_database()
        self.assertFalse(os.path.exists(self.normal_path))
        self.assertFalse(os.path.lexists(self.dev_path))
        with open(self.normal_path, "w") as source:
            source.write("not sqlite")
        with self.assertRaisesRegex(RuntimeError, "Unable to create"):
            database.prepare_developer_database()
        self.assertFalse(os.path.lexists(self.dev_path))
        self.assertFalse(any(name.startswith(".dr14-developer-")
                             for name in os.listdir(self.temp.name)))

    def test_incomplete_schema_is_not_published(self):
        self.create_normal_database()
        with closing(sqlite3.connect(self.normal_path)) as conn:
            conn.execute("drop table Artist")
            conn.commit()
        with self.assertRaisesRegex(ValueError, "normal database is invalid"):
            database.prepare_developer_database()
        self.assertFalse(os.path.exists(self.dev_path))

    def test_snapshot_without_sqlite_backup_api(self):
        self.create_normal_database()
        with closing(sqlite3.connect(self.normal_path)) as conn:
            conn.execute("insert into Artist (Name) values ('fallback')")
            conn.commit()

        connect = sqlite3.connect

        class LegacyConnection:
            def __init__(self, conn):
                self.conn = conn

            def execute(self, statement):
                return self.conn.execute(statement)

            def iterdump(self):
                return self.conn.iterdump()

            def close(self):
                self.conn.close()

        def legacy_connect(*args, **kwargs):
            conn = connect(*args, **kwargs)
            return LegacyConnection(conn) if kwargs.get("uri") else conn

        with mock.patch.object(database.sqlite3, "connect", side_effect=legacy_connect):
            database.prepare_developer_database()
        self.db.upgrade_db()
        self.assertEqual(self.query(self.dev_path, "select Name from Artist"), [("fallback",)])
        self.assertEqual(self.db.db_version, 3)

    def test_simultaneous_copy_does_not_replace_published_database(self):
        self.create_normal_database()
        barrier = threading.Barrier(2)
        failures = []
        original_link = os.link

        def link_after_both_copies(source, destination):
            barrier.wait(timeout=10)
            original_link(source, destination)

        def prepare():
            try:
                database.prepare_developer_database()
            except Exception as error:
                failures.append(error)

        with mock.patch.object(database.os, "link", side_effect=link_after_both_copies):
            threads = [threading.Thread(target=prepare) for _ in range(2)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=15)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(failures, [])
        self.assertEqual(self.query(self.dev_path, "select max(Version) from Db_Version"), [(2,)])
        self.assertFalse(any(name.startswith(".dr14-developer-")
                             for name in os.listdir(self.temp.name)))

    def test_v1_source_migrates_all_the_way(self):
        self.create_normal_database(version=1)
        database.prepare_developer_database()
        self.db.upgrade_db()
        self.assertEqual(self.db.db_version, 3)
        self.assertEqual(self.query(self.normal_path, "select max(Version) from Db_Version"), [(1,)])

    def test_alias_to_normal_database_is_rejected(self):
        self.create_normal_database()
        for alias in (os.link, os.symlink):
            with self.subTest(alias=alias):
                alias(self.normal_path, self.dev_path)
                try:
                    with self.assertRaisesRegex(ValueError, "must not be the normal"):
                        database.prepare_developer_database()
                    self.assertEqual(self.query(self.normal_path,
                                                "select max(Version) from Db_Version"), [(2,)])
                finally:
                    os.unlink(self.dev_path)

    def test_latest_future_migration_and_missing_migration(self):
        self.create_normal_database()
        database.prepare_developer_database()
        self.db._migrations[3] = lambda: "insert into Db_Version values (4);"
        self.db.upgrade_db()
        self.assertEqual(self.db.db_version, 4)
        self.db._migrations[5] = lambda: "insert into Db_Version values (6);"
        with self.assertRaisesRegex(Exception, "no migration from version 4 to 5"):
            self.db.upgrade_db()

    def test_failed_migration_rolls_back(self):
        self.create_normal_database()
        database.prepare_developer_database()
        self.db._migrations[2] = lambda: (
            "create table should_rollback (id integer); invalid SQL;")
        with self.assertRaisesRegex(Exception, "migration 2 -> 3 failed"):
            self.db.upgrade_db()
        self.assertEqual(self.db.db_version, 2)
        self.assertEqual(self.query(self.dev_path,
                                    "select name from sqlite_master where name='should_rollback'"), [])

    def test_newer_database_rejected_in_both_modes(self):
        self.create_normal_database(version=3)
        os.environ["DR14_DEVELOPER_DB"] = "0"
        with self.assertRaisesRegex(Exception, "newer than the supported one"):
            self.db.upgrade_db()
        os.environ["DR14_DEVELOPER_DB"] = "1"
        database.prepare_developer_database()
        with closing(sqlite3.connect(self.dev_path)) as conn:
            conn.execute("insert into Db_Version values (4)")
            conn.commit()
        with self.assertRaisesRegex(Exception, "newer than the supported one"):
            self.db.upgrade_db()

    def test_cli_dump_creates_copy_and_reuses_it(self):
        self.create_normal_database()
        result = self.run_cli("--dump_database")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CREATE TABLE TrackPath", result.stdout)
        self.assertEqual(self.query(self.normal_path, "select max(Version) from Db_Version"), [(2,)])
        self.assertEqual(self.query(self.dev_path, "select max(Version) from Db_Version"), [(3,)])
        result = self.run_cli("--dump_database", DR14_DEVELOPER_DB="0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("CREATE TABLE TrackPath", result.stdout)

    def test_existing_copy_does_not_require_the_normal_file(self):
        self.create_normal_database()
        database.prepare_developer_database()
        self.db.upgrade_db()
        os.unlink(self.normal_path)
        database.prepare_developer_database()
        self.db.upgrade_db()
        self.assertEqual(self.db.db_version, 3)

    def test_cli_enabled_startup_prepares_before_analysis(self):
        self.create_normal_database()
        result = self.run_cli(os.path.join(self.temp.name, "missing-audio"))
        self.assertIn("does not exist", result.stderr)
        self.assertEqual(self.query(self.dev_path, "select max(Version) from Db_Version"), [(3,)])
        self.assertEqual(self.query(self.normal_path, "select max(Version) from Db_Version"), [(2,)])

    def test_cli_enable_keeps_normal_path_and_reports_missing(self):
        result = self.run_cli("--enable_database")
        self.assertIn("normal database does not exist", result.stderr)
        self.assertFalse(os.path.exists(self.dev_path))
        self.create_normal_database()
        dr14_config.enable_db(False)
        result = self.run_cli("--enable_database")
        self.assertIn("ready and enabled", result.stderr)
        self.assertEqual(dr14_config.get_normal_db_path(), self.normal_path)
        self.assertTrue(dr14_config.db_is_enabled())
        self.assertEqual(self.query(self.dev_path, "select max(Version) from Db_Version"), [(3,)])

    def test_cli_query_and_invalid_developer_database(self):
        self.create_normal_database()
        result = self.run_cli("-q", "info")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Error:", result.stderr)
        self.assertEqual(self.query(self.dev_path, "select max(Version) from Db_Version"), [(3,)])
        os.unlink(self.dev_path)
        with open(self.dev_path, "w") as developer:
            developer.write("invalid")
        result = self.run_cli("-q", "info")
        self.assertIn("Error:", result.stderr)
        self.assertEqual(self.query(self.normal_path, "select max(Version) from Db_Version"), [(2,)])

    def test_migration_copies_config_collection(self):
        music = self.make_dir("music")
        dr14_config.set_collection_dir(music)
        self.create_normal_database()
        database.prepare_developer_database()
        self.db.upgrade_db()
        self.assertEqual(self.db.get_collections(), [music])
        self.assertEqual(self.db.find_collection(self.make_dir("music", "album")), music)
        self.assertIsNone(self.db.find_collection(self.make_dir("other")))

    def test_migration_copies_any_collection(self):
        self.create_normal_database()
        database.prepare_developer_database()
        self.db.upgrade_db()
        self.assertEqual(self.db.get_collections(), ["/"])
        self.assertEqual(self.db.find_collection(self.make_dir("anything")), "/")

    def test_failed_data_migration_rolls_back(self):
        self.create_normal_database()
        database.prepare_developer_database()

        def fail(conn):
            raise sqlite3.OperationalError("data step failed")
        self.db._data_migrations[2] = fail
        with self.assertRaisesRegex(Exception, "migration 2 -> 3 failed"):
            self.db.upgrade_db()
        self.assertEqual(self.db.db_version, 2)
        self.assertEqual(self.query(self.dev_path,
                                    "select name from sqlite_master where name='TrackPath'"), [])

    def test_add_and_remove_collections(self):
        music = self.make_dir("music")
        self.create_normal_database()
        database.prepare_developer_database()
        self.db.upgrade_db()
        self.assertTrue(self.db.remove_collection("/"))
        self.assertFalse(self.db.remove_collection("/"))

        first = self.make_dir("music", "rock")
        second = self.make_dir("music", "jazz")
        self.assertTrue(self.db.add_collection(first))
        self.assertTrue(self.db.add_collection(second + os.sep))
        self.assertFalse(self.db.add_collection(first))
        self.assertEqual(sorted(self.db.get_collections()), sorted([first, second]))
        with self.assertRaisesRegex(ValueError, "not a directory"):
            self.db.add_collection(os.path.join(music, "missing"))

        self.assertEqual(self.db.find_collection(self.make_dir("music", "jazz", "a")), second)
        self.assertIsNone(self.db.find_collection(music))
        self.assertTrue(self.db.remove_collection(second))
        self.assertIsNone(self.db.find_collection(self.make_dir("music", "jazz", "a")))

    def test_collections_need_v3(self):
        self.create_normal_database()
        os.environ["DR14_DEVELOPER_DB"] = "0"
        with self.assertRaisesRegex(ValueError, "schema v3"):
            self.db.add_collection(self.make_dir("music"))

    def insert_track_with_path(self, sha1, path):
        self.db.open_insert_session()
        self.db.insert_track(sha1, "Track", 12, 0.1, 0.5, 60, "wav", 16, 1411, 44100,
                             path=path)
        self.db.commit_insert_session()

    def test_track_paths_are_recorded(self):
        self.create_normal_database()
        database.prepare_developer_database()
        self.db.upgrade_db()
        first = os.path.join(self.make_dir("music"), "a.flac")
        copy = os.path.join(self.make_dir("backup"), "a.flac")
        self.insert_track_with_path("same-track", first)
        self.insert_track_with_path("same-track", copy)
        self.insert_track_with_path("same-track", copy)

        self.assertEqual(self.db.query("select count(*) from Track"), [(1,)])
        self.assertEqual(self.db.query(
            "select Track.sha1, TrackPath.path from TrackPath "
            "join Track on Track.Id = TrackPath.IdTrack order by TrackPath.Id"),
            [("same-track", first), ("same-track", copy)])

    def test_track_paths_ignored_before_v3(self):
        self.create_normal_database()
        os.environ["DR14_DEVELOPER_DB"] = "0"
        self.insert_track_with_path("v2-track", "/music/a.flac")
        self.assertEqual(self.db.query("select Title from Track"), [("Track",)])

    def test_cli_manage_collections(self):
        self.create_normal_database()
        music = self.make_dir("music")
        result = self.run_cli("--add_collection", music)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Collection added", result.stderr)
        result = self.run_cli("--remove_collection", "/")
        self.assertIn("Collection removed", result.stderr)
        result = self.run_cli("--list_collections")
        self.assertEqual(result.stdout.split(), [music])
        result = self.run_cli("--remove_collection", "/")
        self.assertIn("no such collection", result.stderr)
        result = self.run_cli("--add_collection", music, DR14_DEVELOPER_DB="0")
        self.assertIn("schema v3", result.stderr)
        self.assertEqual(self.query(self.normal_path, "select max(Version) from Db_Version"), [(2,)])


class UpdatePathsTests(DatabaseTestBase):
    """--update_paths: link files to stored tracks without computing DR."""

    def make_wav(self, path, seconds, period=20.0):
        frames = 44100 * seconds
        w = wave.open(path, "w")
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(b"".join(
            struct.pack("<hh", int(10000 * math.sin(i / period)), 0)
            for i in range(frames)))
        w.close()
        return os.path.realpath(path)

    def analysed_album(self, *lengths):
        """Analyse music/album through the CLI and forget its paths."""
        self.create_normal_database()
        self.album = self.make_dir("music", "album")
        self.files = [self.make_wav(os.path.join(self.album, "%02d.wav" % n), s, 10 + n)
                      for (n, s) in enumerate(lengths)]
        result = self.run_cli("--skip_version_check", "-o", self.make_dir("out"),
                              self.album)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.db.query("select count(*) from Track"), [(len(lengths),)])
        self.db.delete_track_paths([i for (i, _) in self.db.get_track_paths(self.album)])
        self.tracks_before = self.db.query(
            "select Track.*, DR_Track.IdDr from Track join DR_Track on IdTrack = Track.Id")

    def stored_paths(self):
        return sorted(p for (_, p) in self.db.get_track_paths(self.temp.name))

    def update(self, *roots):
        def no_dr(*args, **kwargs):
            raise AssertionError("the DR must not be computed")
        with mock.patch("dr14tmeter.dynamic_range_meter.compute_dr14", no_dr), \
                mock.patch("dr14tmeter.compute_dr14.compute_dr14", no_dr):
            return collection_paths.update_collection_paths(
                self.db, list(roots) or [self.make_dir("music")])

    def test_paths_restored_by_metadata_without_dr(self):
        self.analysed_album(1, 2)
        report = self.update()
        self.assertEqual(report["by_metadata"], 2)
        self.assertEqual(report["by_sha1"], 0)
        self.assertEqual(self.stored_paths(), self.files)
        self.assertEqual(self.db.query(
            "select Track.*, DR_Track.IdDr from Track join DR_Track on IdTrack = Track.Id"),
            self.tracks_before)

        again = self.update()
        self.assertEqual((again["known"], again["by_metadata"], again["by_sha1"]), (2, 0, 0))

    def test_same_size_files_matched_by_sha1(self):
        # Two WAVs of the same length have the same size and duration.
        self.analysed_album(1, 1)
        report = self.update()
        self.assertEqual((report["by_metadata"], report["by_sha1"]), (0, 2))
        self.assertEqual(self.stored_paths(), self.files)

    def test_no_metadata_match_falls_back_to_sha1(self):
        self.analysed_album(1)
        with mock.patch.object(self.db, "find_tracks_by_metadata", return_value=[]):
            report = self.update()
        self.assertEqual(report["by_sha1"], 1)
        self.assertEqual(self.stored_paths(), self.files)

    def test_moved_folder_replaces_stale_paths(self):
        self.analysed_album(1, 2)
        self.update()
        moved = os.path.join(os.path.dirname(self.album), "renamed")
        os.rename(self.album, moved)
        report = self.update()
        self.assertEqual(report["removed"], 2)
        self.assertEqual(self.stored_paths(),
                         [os.path.join(moved, os.path.basename(f)) for f in self.files])

    def test_unknown_file_is_reported_not_stored(self):
        self.analysed_album(1)
        new = self.make_wav(os.path.join(self.make_dir("music", "new"), "x.wav"), 3, 3.0)
        report = self.update()
        self.assertEqual(report["unknown"], [new])
        self.assertEqual(self.db.query("select count(*) from Track"), [(1,)])

    def test_any_collection_is_skipped(self):
        self.analysed_album(1)
        report = self.update("/")
        self.assertEqual(report["skipped_roots"], ["/"])
        self.assertEqual(self.stored_paths(), [])

    def test_cli_update_paths(self):
        self.analysed_album(1)
        result = self.run_cli("--update_paths", self.album)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("New paths (metadata):      1", result.stderr)
        self.assertEqual(self.stored_paths(), self.files)

        result = self.run_cli("--update_paths")
        self.assertIn("Skipped the collection '/'", result.stderr)
        result = self.run_cli("--update_paths", self.album, DR14_DEVELOPER_DB="0")
        self.assertIn("schema v3", result.stderr)


if __name__ == "__main__":
    unittest.main()
