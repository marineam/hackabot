
import os
import time
from glob import glob

from zope.interface import implements
from twisted.internet import reactor
from twisted.plugin import IPlugin

from hackabot.plugin import IHackabotPlugin
from hackabot.protocol import HBProcessProtocol
from hackabot import conf, log

class ExternalPlugins(object):
    """Pass off events to external plugins,
    run as independent processes.
    """
    implements(IPlugin, IHackabotPlugin)

    def _handle_event(self, conn, event):
        if 'internal' in event and event['internal']:
            return

        if event['type'] == "command":
            commands = glob("%s/%s" % (conf.get('commands'), event['command']))
        else:
            commands = glob("%s/%s/*" % (conf.get('hooks'), event['type']))

        if not commands:
            return

        vars = os.environ
        for key, val in conf.items():
            vars["HB_%s" % key.upper()] = str(val)

        vars['HB_NICK'] = conn.nickname
        text = ""
        for key, val in event.iteritems():
            if key == 'text':
                text = val
            else:
                vars['HBEV_%s' % key.upper()] = str(val)

        for cmd in commands:
            if os.access(cmd, os.X_OK):
                log.debug("Running %s" % cmd)
                proto = HBProcessProtocol(conn, event)
                reactor.spawnProcess(proto, cmd, [cmd], vars)

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
