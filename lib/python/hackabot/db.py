"""Hackabot Database"""

import glob

from twisted.enterprise import adbapi

from hackabot import log, env

# These are all the tables included in the schema prior to the introduction of
# schema versions. If all these exist it is probably safe to assume that the
# version is 0 as the last change was only to add some tables.
OLDTABLES = ("bar_adj","bar_location","bar_n","blame","fire","group",
        "hangman","log","lunch_adj","lunch_location","lunch_n","quotes",
        "reminder","score","tard","topic","whip","wtf")

pool = None

class DBError(Exception):
    pass

def required_schema():
    """Get the required version from the schema-version file"""

    schema_file = "%s/schema-version" % env.HB_MYSQL

    try:
        schema_fd = open(schema_file)
        required = schema_fd.readline()
        schema_fd.close()
    except IOError, (errno, errstr):
        raise DBError("Failed to read %s: %s" % (schema_file, errstr))

    try:
        return int(required)
    except ValueError:
        raise DBError("Invalid version '%s' in %s" % (required, schema_file))

def current_schema(db):
    """Get the current version from the configured database"""
    # This is a bit icky to account for an empty db or a version before 1

    cursor = db.cursor()

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
                    "version, and is missing tables: %s" % " ,".join(missing))

        else:
            version = 0

    cursor.close()
    return version

def _load_sql(db, dump):
    """Execute a chunk of SQL from a file"""

    try:
        dumpfd = open(dump)
        sql = dumpfd.read()
        dumpfd.close()
    except IOError, (errno, errstr):
        raise DBError("Failed to read %s: %s" % (schema_file, errstr))

    cursor = db.cursor()

    try:
        cursor.execute(sql)
    except MySQLdb.Error, (errno, errstr):
        raise DBError("Loading schema file %s failed: [%s] %s" %
                (dump, errno, errstr))

    cursor.close()

def _load_schema(db, required):
    """Load the latest available schema version"""

    dumps = glob.glob("%s/schema-???.sql" % env.HB_MYSQL)

    if not dumps:
        raise DBError("No schema files found in %s" % env.HB_MYSQL)

    dumps.sort()
    dump = dumps[-1]

    log.info("Loading DB schema from %s" % dump)

    # Goofy way of grabbing the ??? out of the above glob
    version = int(dump[-7:-4])

    assert version <= required

    _load_sql(db, dump)
    _set_version(db, version)

    return version

def _load_update(db, version):
    """Load a single update file"""

    update = "%s/schema/%03d.sql" % (env.HB_MYSQL, version)

    _load_sql(db, update)
    _set_version(db, version)

def _set_version(db, version):
    """Update the schema version metadata"""

    if version <= 0:
        return

    cursor = db.cursor()

    log.debug("Setting schema version to %s" % version)

    try:
        cursor.execute("INSERT `metadata` (`name` , `value`) "
                "VALUES ('schema', '%s') "
                "ON DUPLICATE KEY UPDATE `value` = %s",
                (version, version))
    except MySQLdb.Error, (errno, errstr):
        raise DBError("DB error: [%s] %s"%(errno, errstr))

    cursor.close()

def init(dbcfg):
    """Create db pool and check/upgrade schema revision"""
    global pool, MySQLdb


    # Use MySQLdb directly for check/upgrade since we don't need
    # to be asynchronous during the init phase
    try:
        import MySQLdb
    except ImportError, ex:
        raise DBError("%s" % ex)

    try:
        db = MySQLdb.connect(host=dbcfg['hostname'], db=dbcfg['database'],
                user=dbcfg['username'], passwd=dbcfg['password'])
    except MySQLdb.Error, (errno, errstr):
        raise DBError("Failed to connect to db: [%s] %s" % (errno, errstr))

    required = required_schema()
    current = current_schema(db)

    if (current < 0):
        # Empty DB!
        current = _load_schema(db, required)
    else:
        log.info("Current DB version: %s" % current)

    while current < required:
        current += 1
        log.info("Upgrading to DB version: %s" % current)

        _load_update(db, current)

    db.close()

    # Everything is in order, setup the pool for all to use.
    pool = adbapi.ConnectionPool("MySQLdb", host=dbcfg['hostname'],
            db=dbcfg['database'], user=dbcfg['username'],
            passwd=dbcfg['password'], cp_noisy=False)
