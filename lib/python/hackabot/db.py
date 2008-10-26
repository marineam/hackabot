"""Hackabot Database"""

from twisted.enterprise import adbapi

from hackabot import log, env

_dbpool = None

class DBError(Exception):
    pass

def init(dbcfg):
    """Create db pool and check/upgrade schema revision"""
    # Yeah, this is a bit ugly :-( I should break it up into pieces
    global _dbpool

    schema_file = "%s/schema-version" % env.HB_MYSQL

    try:
        schema_fd = open(schema_file)
        required = schema_fd.readline()
        schema_fd.close()
    except IOError, (errno, errstr):
        raise DBError("Failed to read %s: %s" % (schema_file, errstr))

    try:
        required = int(required)
    except ValueError:
        raise DBError("Invalid version '%s' in %s" % (required, schema_fd))

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

    cursor = db.cursor()
    try:
        cursor.execute("SELECT `value` FROM `metadata` WHERE `name` = 'schema'")
    except MySQLdb.Error, (errno, errstr):
        cursor.close()
        db.close()
        raise DBError("Failed to get schema version: [%s] %s"%(errno, errstr))

    version = cursor.fetchone()
    try:
        version = int(version[0])
    except ValueError:
        raise DBError("Invalid DB version: '%s'" % version)
    except TypeError:
        raise DBError("Missing DB version!")

    log.info("Current DB version: %s" % version)

    if (version < required):
        log.info("Upgrading to DB version: %s" % required)

    while version < required:
        raise Exception("DB upgrades are unimplemented")

    cursor.close()
    db.close()

    _dbpool = adbapi.ConnectionPool("MySQLdb", host=dbcfg['hostname'],
            db=dbcfg['database'], user=dbcfg['username'],
            passwd=dbcfg['password'])
