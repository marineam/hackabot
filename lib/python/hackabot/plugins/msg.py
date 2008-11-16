"""Send messages, notices, and actions"""

import re

from zope.interface import implements
from twisted.plugin import IPlugin
from hackabot.plugin import IHackabotPlugin

class Messages(object):
    implements(IPlugin, IHackabotPlugin)

    def command_msg(self, conn, event):
        """Send a message to a user or channel.
        !msg [--to somewhere] something to say
        """
        reply_to, text = self._parse(event)
        conn.msg(reply_to, text)

    def command_me(self, conn, event):
        """Send an action message to a user or channel.
        !me [--to somewhere] something to do
        """
        reply_to, text = self._parse(event)
        conn.me(reply_to, text)

    def command_notice(self, conn, event):
        """Send a notice to a user or channel.
        !notice [--to somewhere] something to say
        """
        reply_to, text = self._parse(event)
        conn.notice(reply_to, text)

    def _parse(self, event):
        match = re.match("\s*--to\s+(\S+)\s+(\S.*)", event['text'])
        if match:
            return match.group(1), match.group(2)
        else:
            return event['reply_to'], event['text']

msg = Messages()
