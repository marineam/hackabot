"""The basic of basics: the echo command"""

from zope.interface import implements
from twisted.plugin import IPlugin
from hackabot.plugin import IHackabotPlugin

class Echo(object):
    implements(IPlugin, IHackabotPlugin)

    @staticmethod
    def command_echo(conn, sent_by, sent_to, reply_to, text):
        """Echo something.
        !echo some text
        """
        conn.msg(reply_to, text)

echo = Echo()
