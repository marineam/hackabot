"""Hackabot Database"""

import os
import glob

from twisted.enterprise import adbapi

from hackabot import conf, core, log

# These are all the tables included in the schema prior to the introduction of
# schema versions. If all these exist it is probably safe to assume that the
# version is 0 as the last change was only to add some tables.
OLDTABLES = ("bar_adj","bar_location","bar_n","blame","fire","group",
        "hangman","log","lunch_adj","lunch_location","lunch_n","quotes",
        "reminder","score","tard","topic","whip","wtf")

MySQLdb = None
pool = None

# Make the ConnectionLost exception easier to find
ConnectionLost = adbapi.ConnectionLost

class DBError(Exception):
    pass

def _db_args(config):
    tag = config.find('database')
    if tag is None:
        return

    dbcfg = tag.attrib
    req = set(('hostname', 'database', 'username', 'password'))
    req.difference_update(set(dbcfg.keys()))
    if req:
        raise core.ConfigError(
                "<database> is missing the attribute(s): %s" %
                ', '.join(req))

    return {'db': dbcfg['database'],
            'host': dbcfg['hostname'],
            'user': dbcfg['username'],
            'passwd': dbcfg['password']}

class SchemaManager(object):
    """Tools for upgrading and dumping the DB schema"""

    def __init__(self, config, create=True):
        global MySQLdb
        if MySQLdb is None:
            import MySQLdb

        args = _db_args(config)
        if args is None:
            raise core.ConfigError("<database> tag is missing")

        self._dir = config.attrib['mysql']

        try:
            self._db = self._open(args)
        except MySQLdb.Error, (errno, errstr):
            raise DBError("DB connection failed: [%s] %s" % (errno, errstr))

    def _open(self, args, create=True):
        try:
            return MySQLdb.connect(**args)
        except MySQLdb.Error, (errno, errstr):
            if create and errno == 1049:
                self._create(args)
                return self._open(args, False)
            raise DBError("DB connection failed: [%s] %s" % (errno, errstr))

    @staticmethod
    def _create(args):
        """helper for creating the database"""
        args = args.copy()
        name = args.pop('db')
        assert '`' not in name
        db = MySQLdb.connect(**args)
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE `%s`" % name)
        cursor.close()
        db.close()

    def close(self):
        self._db.close()

    def upgrade(self):
        required = self.required_schema()
        current = self.current_schema()

        if (current < 0):
            # Empty DB!
            current = self._load_schema(required)
        else:
            log.info("Current DB version: %s" % current)

        while current < required:
            current += 1
            self._load_update(current)

    def required_schema(self):
        """Get the required version from the schema-version file"""

        schema_file = "%s/schema-version" % self._dir

        try:
            schema_fd = open(schema_file)
            required = schema_fd.readline()
            schema_fd.close()
        except IOError, ex:
            raise DBError(str(ex))

        try:
            return int(required)
        except ValueError:
            raise DBError("Invalid version %r in %s" %
                    (required, schema_file))

    def current_schema(self):
        """Get the current version from the configured database"""
        # This is a bit icky to account for an empty db or a version before 1

        cursor = self._db.cursor()

        try:
            cursor.execute("SHOW TABLES")
        except MySQLdb.Error, (errno, errstr):
            raise DBError("DB error: [%s] %s"%(errno, errstr))

        tables = cursor.fetchall()

        if not tables:
            # Empty!
            cursor.close()
            return -1

        tables = [row[0] for row in tables]

        if "metadata" in tables:
            # we are at >= version 1
            try:
                cursor.execute("SELECT `value` FROM `metadata` WHERE "
                        "`name` = 'schema'")
            except MySQLdb.Error, (errno, errstr):
                raise DBError("DB error: [%s] %s"%(errno, errstr))

            version = cursor.fetchone()

            if version is None:
                raise DBError("Unknown schema version! "
                        "(schema missing from metadata table)")
            try:
                version = int(version[0])
            except ValueError:
                raise DBError("Invalid schema version: '%s' "
                        "(schema in metadata table not an int)" % version)

        else:
            # we are at version 0 (hopefully)
            missing = set(OLDTABLES) - set(tables)

            if missing:
                raise DBError("The database is not empty, has an unknown "
                        "version, and is missing tables: %s" %
                        " ,".join(missing))

            else:
                version = 0

        cursor.close()
        return version

    def _load_sql(self, dump):
        """Execute a chunk of SQL from a file"""

        log.debug("Loading SQL from %s" % dump)

        try:
            dumpfd = open(dump)
            sql = dumpfd.read()
            dumpfd.close()
        except IOError, (errno, errstr):
            raise DBError("Failed to read %s: %s" % (dump, errstr))

        cursor = self._db.cursor()

        try:
            cursor.execute(sql)
        except MySQLdb.Error, (errno, errstr):
            raise DBError("Loading schema file %s failed: [%s] %s" %
                    (dump, errno, errstr))

        cursor.close()

    def _set_version(self, version):
        """Update the schema version metadata"""

        if version <= 0:
            return

        cursor = self._db.cursor()

        log.debug("Setting schema version to %s" % version)

        try:
            cursor.execute("INSERT `metadata` (`name` , `value`) "
                    "VALUES ('schema', '%s') "
                    "ON DUPLICATE KEY UPDATE `value` = %s",
                    (version, version))
        except MySQLdb.Error, (errno, errstr):
            raise DBError("DB error: [%s] %s"%(errno, errstr))

        cursor.close()

    def _load_schema(self, required):
        """Load the latest available schema version"""

        dump = "%s/schema-%03d.sql" % (self._dir, required)
        if not os.path.exists(dump):
            dumps = glob.glob("%s/schema-???.sql" % self._dir)
            if not dumps:
                raise DBError("No schema files found in %s" % self._dir)

            dumps.sort()
            dump = dumps[-1]

            # Goofy way of grabbing the ??? out of the above glob
            version = int(dump[-7:-4])
            assert version <= required
        else:
            version = required

        log.info("Loading DB schema version %s" % version)

        self._load_sql(dump)
        self._set_version(version)
        return version

    def _load_update(self, version):
        """Load a single update file"""

        log.info("Upgrading to DB schema version %s" % version)

        update = "%s/schema/%03d.sql" % (self._dir, version)
        self._load_sql(update)
        self._set_version(version)

def _connected(connection):
    log.debug("Created database connection...")

def init():
    """Create db pool and check/upgrade schema revision"""
    global pool

    config = conf

    args = _db_args(config)
    if args is None:
        log.info("No database configured.")
        return

    upgrader = SchemaManager(config)
    upgrader.upgrade()
    upgrader.close()

    # Everything is in order, setup the pool for all to use.
    pool = adbapi.ConnectionPool("MySQLdb", cp_noisy=False,
            cp_reconnect=True, cp_openfun=_connected, **args)
