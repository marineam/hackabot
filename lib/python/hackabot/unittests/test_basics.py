import re
from hackabot.unittests import HBTestCase

class BasicCommandsTestCase(HBTestCase):

    def test_about(self):
        self.send("!about")
        return self.expect([
            ('privmsg', self.nickname, re.compile('^Hackabot :: Version')),
            ('privmsg', self.nickname, re.compile('^URL:'))])
