"""Base Hackabot TestCase"""

import re

from twisted.internet import defer
from twisted.python import log
from twisted.trial import unittest

from hackabot import core, parse_config
from hackabot.etree import ElementTree
from hackabot.unittests import dummy_server

# There got to be a less retarded way to do this
SRE_Pattern = type(re.compile('x'))

class IRCTestCase(unittest.TestCase):

    channel = "#hackabot"

    def setUp(self):
        self.tester = dummy_server.Tester(self.channel)
        return self.tester.ready()

    def send(self, msg, to=channel):
        self.tester.client.msg(to, msg)

    def action(self, msg, to=channel):
        self.tester.client.me(to, msg)

    def tearDown(self):
        return self.tester.loseConnection()

class HBTestCase(IRCTestCase):

    nickname = "hackabot"
    username = "Hackabot Test"
    channel = "#hackabot"

    def buildConfig(self):
        cfg = ElementTree.Element("hackabot")
        net = ElementTree.SubElement(cfg, "network")
        net.attrib['nick'] = self.nickname
        net.attrib['name'] = self.username
        svr = ElementTree.SubElement(net, "server")
        svr.attrib['hostname'] = "127.0.0.1"
        svr.attrib['port'] = str(self.tester.port)
        join = ElementTree.SubElement(net, "autojoin")
        join.attrib['chan'] = self.channel
        return cfg

    def setUp(self):
        def start(_):
            config = ElementTree.tostring(self.buildConfig())
            self.manager = core.HBotManager(xml=config)
            return self.tester.notify('join', self.nickname)

        d = super(HBTestCase, self).setUp()
        d.addCallback(start)
        return d

    def expect(self, expect, autojoin=True):
        if autojoin:
            expect = [('join', self.nickname, None)] + list(expect)

        # Sanity check!
        for item in expect:
            self.assertEquals(len(item), 3)

        if len(self.tester.log) >= len(expect):
            self.assertEquals(len(self.tester.log), len(expect))
            for result, expect in zip(self.tester.log, expect):
                self.assertEquals(result[0], expect[0])
                self.assertEquals(result[1], expect[1])
                if isinstance(expect[2], SRE_Pattern):
                    self.assert_(expect[2].search(result[2]))
                else:
                    self.assertEquals(expect[2], result[2])
        else:
            log.msg('Waiting for %d more event(s)' %
                    (len(expect) - len(self.tester.log)))
            d = self.tester.notify()
            d.addCallback(lambda _: self.expect(expect, False))
            return d

    def tearDown(self):
        d = self.manager.disconnect()
        d.addCallback(lambda _: super(HBTestCase, self).tearDown())
        return d
