"""The basic of basics: the echo command"""

from zope.interface import implements
from twisted.plugin import IPlugin
from hackabot.plugin import IHackabotPlugin
import hackabot

class About(object):
    implements(IPlugin, IHackabotPlugin)

    @staticmethod
    def command_about(conn, event):
        """About this bot!
        !about
        """

        version = hackabot.__version__
        conn.msg(event['reply_to'], "Hackabot :: Version %s" % version)
        conn.msg(event['reply_to'], "URL: http://code.google.com/p/hackabot/")

about = About()
