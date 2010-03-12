"""Test DB management code"""

import os
from twisted.trial import unittest
from hackabot import db, parse_config

try:
    import MySQLdb
except ImportError:
    MySQLdb = None

class SchemaTestCase(unittest.TestCase):

    unittest_db = os.environ.get('HB_UNITTEST_DB', None)

    # Should we skip these tests?
    if not MySQLdb:
        skip = "MySQLdb not found"
    elif not unittest_db:
        skip = "HB_UNITTEST_DB is undefined"

    def setUp(self):
        self.config = parse_config(self.unittest_db)
        self._drop()

    def tearDown(self):
        self._drop()

    def _drop(self):
        args = db._db_args(self.config)
        name = args.pop('db')
        assert '`' not in name
        conn = MySQLdb.connect(**args)
        cursor = conn.cursor()
        cursor.execute('SHOW DATABASES')
        existing = [r[0] for r in cursor.fetchall()]
        if name in existing:
            cursor.execute('DROP DATABASE `%s`' % name)
        cursor.close()
        conn.close()

    def test_load_latest(self):
        sch = db.SchemaManager(self.config)
        latest = sch.required_schema()
        sch._load_schema(latest)
        self.assertEquals(latest, sch.current_schema())
        sch.close()

    def test_upgrade_all(self):
        sch = db.SchemaManager(self.config)
        sch._load_schema(0)
        sch.upgrade()
        sch.close()
