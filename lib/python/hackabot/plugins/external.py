
import os
from glob import glob

from zope.interface import implements
from twisted.internet import reactor, defer
from twisted.plugin import IPlugin

from hackabot.plugin import IHackabotPlugin
from hackabot.protocol import HBProcessProtocol
from hackabot.etree import ElementTree
from hackabot import log

class ExternalPlugins(object):
    """Pass off events to external plugins,
    run as independent processes.
    """
    implements(IPlugin, IHackabotPlugin)

    def _handle_event(self, conn, event):
        if 'internal' in event and event['internal']:
            return

        conf = conn.manager.config
        if event['type'] == "command":
            commands = glob("%s/commands/%s" %
                    (conf.get('root'), event['command']))
        else:
            commands = glob("%s/hooks/%s/*" %
                (conf.get('root'), event['type']))

        if not commands:
            return

        vars = os.environ.copy()
        for key, val in conf.items():
            vars["HB_%s" % key.upper()] = str(val)

        if conn.network.id:
            vars['HB_NETWORK'] = conn.network.id

        vars['HB_NICK'] = conn.nickname
        vars['HB_XML'] = ElementTree.tostring(conn.manager.config)
        text = ""
        for key, val in event.iteritems():
            if key == 'text':
                text = val
            else:
                vars['HBEV_%s' % key.upper()] = str(val)

        if 'PERL5LIB' in vars:
            vars['PERL5LIB'] = "%s:%s" % (conf.get('perl'), vars['PERL5LIB'])
        else:
            vars['PERL5LIB'] = conf.get('perl')

        if 'PYTHONPATH' in vars:
            vars['PYTHONPATH'] = ("%s:%s" %
                    (conf.get('python'), vars['PYTHONPATH']))
        else:
            vars['PYTHONPATH'] = conf.get('python')

        deferreds = []
        for cmd in commands:
            if os.access(cmd, os.X_OK):
                log.debug("Running %s" % cmd)
                deferred = defer.Deferred()
                deferreds.append(deferred)
                proto = HBProcessProtocol(conn, event, deferred)
                reactor.spawnProcess(proto, cmd, [cmd], vars)

        if len(deferreds) == 1:
            return deferreds[0]
        elif len(deferreds) > 1:
            return defer.DeferredList(deferreds, consumeErrors=True)

    msg = _handle_event
    me = _handle_event
    notice = _handle_event
    topic = _handle_event
    join = _handle_event
    part = _handle_event
    kick = _handle_event
    quit = _handle_event
    names = _handle_event
    rename = _handle_event
    command = _handle_event

external = ExternalPlugins()
