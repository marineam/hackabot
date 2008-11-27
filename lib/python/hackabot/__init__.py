"""Hackabot"""

import sys
from os import path
from optparse import OptionParser
from xml.etree import ElementTree

from twisted.internet import reactor

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

def load_conf(conffile):
    """Configuration stuff!"""

    # Assuming the normal svn layout, find the source root
    root = path.abspath(__file__).rsplit("/",4)[0]

    vars = {
        'conf': conffile,
        'root': root,
        'perl': "%s/lib/perl" % root,
        'mysql': "%s/lib/mysql" % root,
        'python': "%s/lib/python" % root,
        'commands': "%s/commands" % root,
        'hooks': "%s/hooks" % root,
    }

    fd = open(conffile)
    vars['xml'] = fd.read()
    fd.close()

    _conf = ElementTree.fromstring(vars['xml'])
    _conf.attrib.update(vars)
    conf._set_target_(_conf)

def run(argv=sys.argv):
    """Start up Hackabot"""

    global env

    from hackabot import core, db, plugin, remote, log

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
        load_conf(conffile)
    except IOError, (exno, exstr):
        log.error("Failed to open %s: %s" % (conffile, exstr))
        sys.exit(1)

    try:
        db.init()
        core.init()
        plugin.init()
        remote.init()
    except core.ConfigError, ex:
        log.error(str(ex))
        sys.exit(1)
    except db.DBError, ex:
        log.error(str(ex))
        sys.exit(1)

    # Delay taking over stdio so any startup errors can go to stderr
    log.init_stdio()

    reactor.callWhenRunning(core.manager.connect)
    reactor.callWhenRunning(remote.listen)
    reactor.run()

class _Wrapper(object):
    """Dummy wrapper object that can be imported but the actual
    value object inside can be replaced at any time.
    """

    def __init__(self, target=None):
        self.__target = target

    def _set_target_(self, target):
        self.__target = target

    def __getattr__(self, key):
        return getattr(self.__target, key)

conf = _Wrapper()
__version__ = "2.0"
__all__ = [ "client", "conf", "core", "db", "load_conf", "log",
            "plugin", "protocol", "remote", "run" ]
