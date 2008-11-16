"""The basic of basics: the echo command"""

from zope.interface import implements
from twisted.plugin import IPlugin
from hackabot.plugin import IHackabotPlugin

class Echo(object):
    implements(IPlugin, IHackabotPlugin)

    @staticmethod
    def command_echo(conn, event):
        """Echo something.
        !echo some text
        """
        conn.msg(event['reply_to'], event['text'])

echo = Echo()
