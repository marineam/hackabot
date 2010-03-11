"""Base Hackabot TestCase"""

from twisted.trial import unittest

from hackabot.unittests import dummy_server

class IRCTestCase(unittest.TestCase):

    def setUp(self):
        self.tester = dummy_server.Tester()
        return self.tester.ready()

    def tearDown(self):
        return self.tester.loseConnection()
