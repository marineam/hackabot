"""
Express extreme, possibly religious enthusiasm whenever the topic of
smaller-than-average equine creatures comes up.

~ Corbin Simpson <simpsoco@osuosl.org>
"""

from zope.interface import implements
from twisted.plugin import IPlugin
from hackabot.plugin import IHackabotPlugin

equines = ("pony", "ponies", "horse")

class Ponies(object):
    implements(IPlugin, IHackabotPlugin)

    @staticmethod
    def msg(conn, event):
        if event["sent_by"] == conn.nickname:
            return

        message = event["text"].lower()

        if any(x in message for x in equines):
            conn.msg(event["reply_to"], "OMG Ponies!!!")

    me = msg

ponies = Ponies()
