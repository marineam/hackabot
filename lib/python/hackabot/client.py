# Hackabot utilities for external Python hooks and commands

import os
import sys
from xml.etree import ElementTree

class Client(object):

    def __init__(self):
        xml = os.getenv("HB_XML")
        self.conf = ElementTree.fromstring(xml)

    def connect(self):
        raise Exception("unimplemented")

    def close(self):
        raise Exception("unimplemented")

    def cmd(self):
        raise Exception("unimplemented")

    def readall(self):
        data = sys.stdin.read()
        return data.strip()

    def readline(self):
        line = sys.stdin.readline()
        return line.strip()

    def private(self):
        return (os.getenv("HBEV_PRIVATE", "") == "True")

    def sent_by(self):
        return os.getenv("HBEV_SENT_BY", "")

    def sent_to(self):
        return os.getenv("HBEV_SENT_TO", "")

    def channel(self):
        if self.private():
            return None
        else:
            return self.sent_to()
