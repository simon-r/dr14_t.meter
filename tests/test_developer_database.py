import configparser
from contextlib import closing
import os
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock

from dr14tmeter import database
from dr14tmeter import dr14_config


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DeveloperDatabaseTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
