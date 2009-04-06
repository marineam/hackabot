
import random
from zope.interface import implements
from twisted.plugin import IPlugin

from hackabot.plugin import IHackabotPlugin

class Answer(object):
    """Answer simple questions"""

    implements(IPlugin, IHackabotPlugin)

    answers = (
            "It is certain.",
            "My sources say no.",
            "My sources say yes.",
            "Most likely not.",
            "UMMM.. No.",
            "Without a doubt.",
            "Very doubtful.",
            "No",
            "Yes",
            "I don't care.",
            "Heck Yea!",
        )

    def msg(self, conn, event):
        if (event['text'].startswith(conn.nickname) and
                event['text'].endswith('?')):
            conn.msg(event['reply_to'], random.choice(self.answers))

answer = Answer()
