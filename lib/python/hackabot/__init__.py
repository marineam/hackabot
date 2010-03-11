"""Hackabot"""

__version__ = "2.0"

import os
import sys
from optparse import OptionParser

from twisted.internet import reactor

class ConfigError(Exception):
    pass

class NotConnected(Exception):
    pass

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

def parse_config(path=None, xml=None):
    """Load configuration XML, return the root element"""
    assert not (path and xml)

    from hackabot.etree import ElementTree

    # Assuming the normal svn layout, find the source root
    root = os.path.abspath(__file__).rsplit("/",4)[0]

    defaults = {
        'root': root,
        'perl': "%s/lib/perl" % root,
        'mysql': "%s/lib/mysql" % root,
        'python': "%s/lib/python" % root,
        'commands': "%s/commands" % root,
        'hooks': "%s/hooks" % root,
    }

    if path:
        try:
            config = ElementTree.parse(path).getroot()
        except IOError, (exno, exstr):
            raise ConfigError("Failed to read %s: %s" % (path, exstr))
    elif xml:
        config = ElementTree.fromstring(xml)
    else:
        config = ElementTree.Element("hackabot")

    for key, value in defaults.iteritems():
        config.attrib.setdefault(key, value)

    return config

def run(argv=sys.argv):
    """Start up Hackabot"""

    options, conf = parse_options(argv)

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
        manager = core.HBotManager(conf, exit_cb=lambda: reactor.stop())
    except ConfigError, ex:
        log.error(str(ex))
        sys.exit(1)

    if (options.pid):
        daemonize(options.pid)

    # Delay taking over stdio so any startup errors can go to stderr
    log.init_stdio()

    reactor.run()

# Import late to avoid circles...
from hackabot import core, log
