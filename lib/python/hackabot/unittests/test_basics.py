import re
from hackabot.unittests import HBTestCase

class BasicCommandsTestCase(HBTestCase):

    def test_about(self):
        self.send("!about")
        return self.expect([
            ('privmsg', self.nickname, re.compile('^Hackabot :: Version')),
            ('privmsg', self.nickname, re.compile('^URL:'))])

    def test_admin(self):
        self.send("!admin reload")
        return self.expect([('privmsg', self.nickname,
                            re.compile('^This is reload'))])

    def test_answer(self):
        self.send("%s: test?" % self.nickname)
        return self.expect([('privmsg', self.nickname, re.compile('\w'))])

    def test_echo(self):
        self.send("!echo zomg")
        return self.expect([('privmsg', self.nickname, "zomg")])

    def test_help_list(self):
        self.send("!help")
        return self.expect([('privmsg', self.nickname,
            re.compile('^Commands: .*about.*admin.*echo.*help'))])

    def test_help_echo(self):
        self.send("!help echo")
        return self.expect([('privmsg', self.nickname, "Echo something."),
                            ('privmsg', self.nickname, "!echo some text")])

    def test_highfive(self):
        self.send("%s: o/" % self.nickname)
        self.send("%s: \\o" % self.nickname)
        tester = self.tester.client.nickname
        return self.expect([('privmsg', self.nickname, "%s: \\o" % tester),
                            ('privmsg', self.nickname, "%s: o/" % tester)])

    def test_ponies(self):
        self.send("I see a pony!")
        self.send("ZOMG! I see lots of ponies!")
        return self.expect([('privmsg', self.nickname, "OMG!!! Ponies!!!"),
                            ('privmsg', self.nickname, "OMG!!! Ponies!!!")])
