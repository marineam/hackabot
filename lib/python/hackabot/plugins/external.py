
import os
import time
from glob import glob

from zope.interface import implements
from twisted.internet import reactor
from twisted.plugin import IPlugin

from hackabot.plugin import IHackabotPlugin
from hackabot.protocol import HBProcessProtocol
from hackabot import log, env

class ExternalPlugins(object):
    """Pass off events to external plugins,
    run as independent processes.
    """
    implements(IPlugin, IHackabotPlugin)

    def _handle_event(self, conn, event):
        if 'internal' in event and event['internal']:
            return

        if event['type'] == "command":
            commands = glob("%s/%s" % (env.HB_COMMANDS, event['command']))
        else:
            commands = glob("%s/%s/*" % (env.HB_HOOKS, event['type']))

        if not commands:
            return

        vars = os.environ
        vars['HB_ROOT'] = env.HB_ROOT
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
