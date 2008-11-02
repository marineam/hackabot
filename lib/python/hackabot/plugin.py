"""Hackabot Plugin Interface"""

from zope.interface import Interface
from twisted.plugin import getPlugins
from twisted.python.modules import getModule

from hackabot import log, plugins


def init():
    global manager
    manager = PluginManager()


class PluginManager(object):
    """Keep an index of available plugins and call them"""

    hooks = ('msg', 'me', 'notice', 'topic', 'join', 'part',
             'kick', 'quit', 'rename', 'names')

    def __init__(self):
        self.load()

    def reload(self):
        """Reload all available plugins"""

        log.debug("Reloading all plugins...")

        # Is this the best way to do this?
        for module in getModule(plugins.__name__).iterModules():
            reload(module.load())

        self.load()

    def load(self):
        """Load all available plugins"""

        self.plugins = getPlugins(IHackabotPlugin, plugins)
        self._commands = {}
        self._hooks = {}

        for hook in self.hooks:
            self._hooks[hook] = []

        for plugin in self.plugins:
            log.trace("Found plugin: %s" % plugin)
            for attr in dir(plugin):
                if attr[0] == '_':
                    continue
                log.trace("Found plugin attr: %s" % attr)
                self._check_attr(plugin, attr)

    def _check_attr(self, plugin, attr):
        if attr.startswith('command_') and attr != 'command_':
            cmd = attr.split('_', 1)[1]
            self._add_command(cmd, getattr(plugin, attr))
        elif attr in self.hooks:
            self._add_hook(attr, getattr(plugin, attr))

    def _add_command(self, cmd, func):
        assert callable(func)
        if cmd in self._commands:
            log.error("Redefining command: %s" % cmd)
        else:
            log.debug("Registering command: %s" % cmd)
            self._commands[cmd] = func

    def _add_hook(self, type, func):
        assert type in self.hooks
        assert callable(func)
        self._hooks[type].append(func)

    def command(self, name, conn, sent_by, sent_to, reply_to, text):
        log.trace("command: %s: %s" % (name, text))

        if name in self._commands:
            self._commands[name](conn, sent_by, sent_to, reply_to, text)

    def hook(self, type, *args, **kwargs):
        for func in self._hooks[type]:
            func(*args, **kwargs)


class IHackabotPlugin(Interface):
    """Hackabot Plugin Interface

    Implementors are not required to define all functions.
    Hackabot will check which functions are implemented.

    When implementing a function you MUST do things in the twisted way,
    wrapping any blocking code in a deferred and offloading long running
    code in a different thread. Otherwise you will hurt performance!
    """

    def command_z(conn, sent_by, sent_to, reply_to, text):
        """Implement a command named z

        Replace z with the name of the command!
        """

    def command(name, conn, sent_by, sent_to, reply_to, text):
        """Handle a command that is not implemented explicitly"""

    def msg(conn, sent_by, sent_to, reply_to, text):
        """Respond to a message"""

    def me(conn, sent_by, sent_to, reply_to, text):
        """Respond to a /me message"""

    def notice(conn, sent_by, sent_to, reply_to, text):
        """Respond to a /notice message"""

    def topic(conn, sent_by, channel, text):
        """Respond to a channel topic change"""

    def join(conn, sent_by, channel):
        """Respond to a user joining a channel"""

    def part(conn, sent_by, channel, text):
        """Respond to a user leaving a channel"""

    def kick(conn, kicker, kickee, channel, text):
        """Respond to a user being kicked from a channel"""

    def quit(conn, sent_by, text):
        """Respond to a user quitting"""

    def rename(conn, old, new):
        """Respond to a user's nick changing"""

    def names(conn, channel, userlist):
        """Respond to a /names #channel command"""
