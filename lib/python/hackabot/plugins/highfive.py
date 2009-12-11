"""
High five, dude!

~ Corbin Simpson <simpsoco@osuosl.org>
"""

import re

from zope.interface import implements
from twisted.plugin import IPlugin

from hackabot.plugin import IHackabotPlugin
from hackabot import log

class HighFive(object):
    implements(IPlugin, IHackabotPlugin)

    @staticmethod
    def msg(conn, event):
        if event["sent_by"] == conn.nickname:
            return

        regex = re.compile(r"^\s*%s[:,]?\s+(o\/|\\o)\s*$" % conn.nickname)
        m = regex.match(event["text"])

        if m:
            if m.group(1) == "o/":
                conn.msg(event["reply_to"], "%s: \o" % event["sent_by"])
            elif m.group(1) == "\o":
                conn.msg(event["reply_to"], "%s: o/" % event["sent_by"])

highfive = HighFive()
