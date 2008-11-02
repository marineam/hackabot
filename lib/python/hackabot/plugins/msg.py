"""Send messages, notices, and actions"""

import re

from zope.interface import implements
from twisted.plugin import IPlugin
from hackabot.plugin import IHackabotPlugin

class Messages(object):
    implements(IPlugin, IHackabotPlugin)

    def command_msg(self, conn, sent_by, sent_to, reply_to, text):
        """Send a message to a user or channel.
        !msg [--to somewhere] something to say
        """
        reply_to, text = self._parse(reply_to, text)
        conn.msg(reply_to, text)

    def command_me(self, conn, sent_by, sent_to, reply_to, text):
        """Send an action message to a user or channel.
        !me [--to somewhere] something to do
        """
        reply_to, text = self._parse(reply_to, text)
        conn.me(reply_to, text)

    def command_notice(self, conn, sent_by, sent_to, reply_to, text):
        """Send a notice to a user or channel.
        !notice [--to somewhere] something to say
        """
        reply_to, text = self._parse(reply_to, text)
        conn.notice(reply_to, text)

    def _parse(self, reply_to, text):
        match = re.match("\s*--to\s+(\S+)\s+(\S.*)", text)
        if match:
            return match.group(1), match.group(2)
        else:
            return reply_to, text

msg = Messages()
