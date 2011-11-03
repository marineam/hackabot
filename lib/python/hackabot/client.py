# Hackabot utilities for external Python hooks and commands

import os
import sys
import socket

from hackabot import parse_config

class ClientError(Exception):
    """An error in the HB Client class"""

class Client(object):

    def __init__(self, path=None, xml=None):
        assert not (path and xml)

        if not (path or xml):
            xml = os.environ.get("HB_XML", None)

        self.conn = None
        self.conf = parse_config(path, xml)

    def connect(self, path=None):
        if not path:
            path = os.path.join(self.conf.get("root"), "sock")

        sock = socket.socket(socket.AF_UNIX)
        sock.connect(path)
        # Use the file API, it is better than the sockets.
        self.conn = sock.makefile('w+', bufsize=1)
        sock.close()

        to = self.reply_to()
        if to:
            ret = self.cmd("to %s" % to)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def cmd(self, send):
        """Send a command to the hackabot control socket"""

        assert '\n' not in send
        if not self.conn:
            self.connect()

        network = os.environ.get("HB_NETWORK", None)
        if network
           self.conn.write("net %s\n" % network)
           ret = self.conn.readline()

        self.conn.write("%s\n" % send)
        ret = self.conn.readline()

        if not ret:
            raise ClientError("Hackabot connection lost with no result")

        return ret.rstrip()

    def check_cmd(self, send):
        """Raise an exception of cmd does not return 'ok'"""
        ret = self.cmd(send)
        if ret != "ok":
            raise ClientError("Command failed, expected 'ok', got %r" % ret)

    def readall(self):
        data = sys.stdin.read()
        return data.rstrip()

    def readline(self):
        line = sys.stdin.readline()
        return line.rstrip()

    def private(self):
        return (os.environ.get("HBEV_PRIVATE", None) == "True")

    def sent_by(self):
        return os.environ.get("HBEV_SENT_BY", None)

    def sent_to(self):
        return os.environ.get("HBEV_SENT_TO", None)

    def reply_to(self):
        return os.environ.get("HBEV_REPLY_TO", None)

    def channel(self):
        if self.private():
            return None
        else:
            return self.sent_to()
