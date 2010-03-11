"""Listen for remote commands"""

import os

from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory

from hackabot.protocol import HBLineProtocol
from hackabot import log

class HBRemoteControl(ServerFactory):
    """Remote Control connection factory"""

    protocol = HBLineProtocol
    noisy = False

    def __init__(self, manager):
        self._manager = manager
        self._socket = None

        if manager.config.find('listen') is not None:
            self._path = "%s/sock" % manager.config.get('root')
        else:
            self._path = None

    def buildProtocol(self, addr):
        p = self.protocol(self._manager)
        p.factory = self
        return p

    def connect(self):
        if not self._path:
            return

        try:
            os.unlink(self._path)
            log.warn("Removed an old socket: %s" % self._path)
        except OSError:
            pass

        self._socket = reactor.listenUNIX(self._path, self)

    def disconnect(self):
        if self._socket:
            sock = self._socket
            self._socket = None
            return sock.loseConnection()
