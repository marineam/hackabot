"""Hackabot startup"""

import sys
from optparse import OptionParser
from ConfigParser import SafeConfigParser

from twisted.internet import reactor

from hackabot import core, log, db

class ConfigError(Exception):
    pass

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

def init(config):
    """Connect to each network defined in config, also start the db"""

    def addbynet(netdict, section, islist):
        secdict = dict(config.items(section))
        net = secdict.get("network", "__DEFAULT__")
        if not islist:
            netdict[net] = secdict
        elif net in netdict:
            netdict[net].append(secdict)
        else:
            netdict[net] = [secdict]

    dbsection = None
    networks = {}
    servers = {}
    autojoin = {}

    for section in config.sections():
        # group networks, servers, and joins by network name

        if section.lower().startswith("network"):
            if not config.has_option(section, "nick"):
                raise ConfigError("No nick in %s section" % section)

            network = dict(config.items(section))
            network.setdefault('network', None)
            network.setdefault('user', network['nick'])
            network.setdefault('name', network['nick'])
            networks[network['network']] = network

        elif section.lower().startswith("server"):
            if not config.has_option(section, "host"):
                raise ConfigError("No host in %s section" % section)

            server = dict(config.items(section))
            server.setdefault('network', None)
            server['port'] = int(server.get('port', 6667))

            if config.has_option(section, "ssl"):
                server['ssl'] = config.getboolean(section, "ssl")
            else:
                server['ssl'] = False

            if server['network'] in servers:
                servers[join['network']].append(server)
            else:
                servers[join['network']] = [server]

        elif section.lower().startswith("autojoin"):
            if not config.has_option(section, "channel"):
                raise ConfigError("No channel in %s section" % section)

            join = dict(config.items(section))
            join.setdefault('network', None)
            join.setdefault('password', None)

            if join['network'] in autojoin:
                autojoin[join['network']].append(join)
            else:
                autojoin[join['network']] = [join]

        elif section.lower() == "database":
            dbsection = section
        else:
            log.warn("Unknown section: %s" % section)

    if not networks:
        raise ConfigError("No networks defined")

    if not dbsection:
        log.info("No database section, running without a db...")
    else:
        dbcfg = dict(config.items(dbsection))

        for var in ('hostname', 'database', 'username', 'password'):
            if var not in dbcfg:
                raise ConfigError("Database section missing %s option"%var)

        db.init(dbcfg)

    for net in networks:
        if net not in servers:
            raise ConfigError("No server defined for network '%s'" % net)

        hb = core.HBotNetwork(networks[net], servers[net],
                autojoin.get(net, []))
        hb.connect()

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

    try:
        conffp = open(conffile)
    except IOError, (exno, exstr):
        sys.stderr.write("Failed to open %s: %s\n" % (conf, exstr))
        sys.exit(1)

    log.init(logfile, options.level)

    config = SafeConfigParser()
    config.readfp(conffp)

    try:
        init(config)
    except ConfigError, ex:
        log.error(str(ex))
        sys.exit(1)
    except db.DBError, ex:
        log.error(str(ex))
        sys.exit(1)

    # Delay taking over stdio so any startup errors can go to stderr
    log.init_stdio()

    reactor.run()
