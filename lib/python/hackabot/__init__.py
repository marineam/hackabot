"""Hackabot"""

__version__ = "2.0"

import os
import sys
from optparse import OptionParser

from twisted.internet import reactor

def daemonize(pid_file):
    """Background the current process"""

    log.debug("daemonizing process")

    try:
        # A trivial check to see if we are already running
        pidfd = open(pid_file)
        pid = int(pidfd.readline().strip())
        pidfd.close()

        if os.path.isdir('/proc/%s' % pid):
            log.error("PID file exits and process %s is running!" % pid)
            sys.exit(1)
    except:
        # Assume all is well if the test fails
        pass

    try:
        null = os.open("/dev/null", os.O_RDWR)
    except IOError, ex:
        log.error("Failed to open /dev/null: %s" % ex)
        sys.exit(1)

    try:
        pidfd = open(pid_file, 'w')
    except IOError, ex:
        log.error("Failed to open PID file %s" % ex)
        sys.exit(1)

    if os.fork() > 0:
        os._exit(0)

    os.dup2(null, 0)
    os.dup2(null, 1)
    os.dup2(null, 2)
    os.close(null)
    os.chdir("/")
    os.setsid()

    if os.fork() > 0:
        os._exit(0)

    pidfd.write("%s\n" % os.getpid())
    pidfd.close()

def parse_options(argv):
    """Parse Hackabot command line parameters"""

    parser = OptionParser("usage: %prog [options] hackabot.ini")
    parser.add_option("-l", "--log-file", dest="file")
    parser.add_option("-v", "--log-level", dest="level", default="INFO",
            help="one of: %s" % ", ".join(log.LEVELS))
    parser.add_option("-p", "--pid-file", dest="pid",
            help="daemonize the process, write pid to the given file")

    (options, args) = parser.parse_args(argv[1:])

    if len(args) != 1:
        parser.error("One config file is required!")
    if options.level not in log.LEVELS:
        parser.error("Invalid log level '%s'" % options.level)

    return options, args[0]

def load_conf(conffile):
    """Configuration stuff!"""

    from hackabot.etree import ElementTree

    # Assuming the normal svn layout, find the source root
    root = os.path.abspath(__file__).rsplit("/",4)[0]

    vars = {
        'conf': conffile,
        'root': root,
        'perl': "%s/lib/perl" % root,
        'mysql': "%s/lib/mysql" % root,
        'python': "%s/lib/python" % root,
        'commands': "%s/commands" % root,
        'hooks': "%s/hooks" % root,
    }

    if conffile:
        fd = open(conffile)
        vars['xml'] = fd.read()
        fd.close()

        _conf = ElementTree.fromstring(vars['xml'])
    else:
        _conf = ElementTree.Element("hackabot")

    _conf.attrib.update(vars)
    conf._set_target_(_conf)

def basic(conffile):
    """Start up the Hackabot framework, but don't actually fire up"""

    log.init(sys.stdout, "INFO")

    try:
        load_conf(conffile)
    except IOError, (exno, exstr):
        log.error("Failed to open %s: %s" % (conffile, exstr))
        sys.exit(1)

    try:
        db.init()
    except db.DBError, ex:
        log.error(str(ex))
        sys.exit(1)

def run(argv=sys.argv):
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
        load_conf(conffile)
    except IOError, (exno, exstr):
        log.error("Failed to open %s: %s" % (conffile, exstr))
        sys.exit(1)

    try:
        db.init()
    except db.DBError, ex:
        log.error(str(ex))
        sys.exit(1)

    try:
        core.init(conf)
        plugin.init()
        remote.init()
    except core.ConfigError, ex:
        log.error(str(ex))
        sys.exit(1)

    if (options.pid):
        daemonize(options.pid)

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

# Import late to avoid circles...
from hackabot import core, db, plugin, remote, log
