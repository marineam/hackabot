"""Hackabot startup"""

import sys
from optparse import OptionParser
from xml.etree import ElementTree

from twisted.internet import reactor

from hackabot import core, log, db, plugin

def parse_options(argv):
    """Parse Hackabot command line parameters"""

    parser = OptionParser("usage: %prog [options] hackabot.ini")
    parser.add_option("-l", "--log-file", dest="file")
    parser.add_option("-v", "--log-level", dest="level", default="INFO",
            help="one of: %s" % ", ".join(log.LEVELS))

    (options, args) = parser.parse_args(argv[1:])

    if len(args) != 1:
        parser.error("One config file is required!")
    if options.level not in log.LEVELS:
        parser.error("Invalid log level '%s'" % options.level)

    return options, args[0]

def main(argv=sys.argv):
    """Start up Hackabot"""

    options, conffile = parse_options(argv)

    if options.file:
        try:
            logfile = open(options.file, 'a')
        except IOError, (exno, exstr):
            sys.stderr.write("Failed to open %s: %s\n" % (options.file, exstr))
            sys.exit(1)
    else:
        logfile = sys.stdout

    log.init(logfile, options.level)

    try:
        config = ElementTree.parse(conffile).getroot()
    except IOError, (exno, exstr):
        log.error("Failed to open %s: %s" % (conffile, exstr))
        sys.exit(1)

    try:
        core.init(config)
        db.init(config)
        plugin.init()
    except core.ConfigError, ex:
        log.error(str(ex))
        sys.exit(1)
    except db.DBError, ex:
        log.error(str(ex))
        sys.exit(1)

    # Delay taking over stdio so any startup errors can go to stderr
    log.init_stdio()

    reactor.run()
