"""Hackabot Plugin Interface"""

from zope.interface import Interface
from twisted.plugin import getPlugins
from twisted.python import modules, failure

from hackabot import log, plugins


def init():
    global manager
    manager = PluginManager()


class PluginManager(object):
    """Keep an index of available plugins and call them"""

    hook_types = ('msg', 'me', 'notice', 'topic', 'join', 'part',
                  'kick', 'quit', 'rename', 'names', 'command')

    def __init__(self):
        self.load()

    def reload(self):
        """Reload all available plugins"""

        log.debug("Reloading all plugins...")

        # Is this the best way to do this?
        for module in modules.getModule(plugins.__name__).iterModules():
            reload(module.load())

        self.load()

    def load(self):
        """Load all available plugins"""

        self.plugins = getPlugins(IHackabotPlugin, plugins)
        self.commands = {}
        self.hooks = {}

        for hook in self.hook_types:
            self.hooks[hook] = []

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
        if cmd in self.commands:
            log.error("Redefining command: %s" % cmd)
        else:
            log.debug("Registering command: %s" % cmd)
            self.commands[cmd] = func

    def _add_hook(self, type, func):
        assert type in self.hook_types
        assert callable(func)
        self.hooks[type].append(func)

    def command(self, conn, event):
        log.trace("command: %s: %s" % (event['command'], event['text']))

        if event['command'] in self.commands:
            try:
                self.commands[event['command']](conn, event)
            except:
                log.error(failure.Failure())
        else:
            self.hook(conn, event)

    def hook(self, conn, event):
        for func in self.hooks[event['type']]:
            try:
                func(conn, event)
            except:
                log.error(failure.Failure())


class IHackabotPlugin(Interface):
    """Hackabot Plugin Interface

    Implementors are not required to define all functions.
    Hackabot will check which functions are implemented.

    When implementing a function you MUST do things in the twisted way,
    wrapping any blocking code in a deferred and offloading long running
    code in a different thread. Otherwise you will hurt performance!
    """

    def command_z(conn, event):
        """Implement a command named z.

        Replace z with the name of the command!

        conn = connection object
        event = {
            type: "command"
            command: "command_name"
            sent_by: "nick"
            sent_to: "nick or channel"
            reply_to: "nick or channel"
            text: "command arguments"
            time: seconds
        }
        """

    def command(conn, event):
        """Handle a command that is not implemented explicitly.

        conn = connection object
        event = {
            type: "command"
            command: "command_name"
            sent_by: "nick"
            sent_to: "nick or channel"
            reply_to: "nick or channel"
            text: "command arguments"
            time: seconds
        }
        """

    def msg(conn, event):
        """Respond to a message.

        conn = connection object
        event = {
            type: "msg"
            sent_by: "nick"
            sent_to: "nick or channel"
            reply_to: "nick or channel"
            text: "message"
            time: seconds
        }
        """

    def me(conn, event):
        """Respond to a /me message.

        conn = connection object
        event = {
            type: "me"
            sent_by: "nick"
            sent_to: "nick or channel"
            reply_to: "nick or channel"
            text: "message"
            time: seconds
        }
        """

    def notice(conn, event):
        """Respond to a /notice message.

        conn = connection object
        event = {
            type: "notice"
            sent_by: "nick"
            sent_to: "nick or channel"
            reply_to: "nick or channel"
            text: "message"
            time: seconds
        }
        """

    def topic(conn, event):
        """Respond to a channel topic change.

        conn = connection object
        event = {
            type: "topic"
            user: "nick"
            channel: "channel"
            text: "topic"
            time: seconds
        }
        """

    def join(conn, event):
        """Respond to a user joining a channel.

        conn = connection object
        event = {
            type: "join"
            user: "nick"
            channel: "channel"
            time: seconds
        }
        """

    def part(conn, event):
        """Respond to a user leaving a channel.

        conn = connection object
        event = {
            type: "part"
            user: "nick"
            channel: "channel"
            text: "message"
            time: seconds
        }
        """

    def kick(conn, event):
        """Respond to a user being kicked from a channel.

        conn = connection object
        event = {
            type: "kick"
            kicker: "nick"
            kickee: "nick"
            channel: "channel"
            text: "message"
            time: seconds
        }
        """

    def quit(conn, event):
        """Respond to a user quitting.

        conn = connection object
        event = {
            type: "quit"
            user: "nick"
            text: "message"
            time: seconds
        }
        """

    def rename(conn, event):
        """Respond to a user's nick changing.

        conn = connection object
        event = {
            type: "rename"
            old: "old nick"
            new: "new nick"
            time: seconds
        }
        """

    def names(conn, event):
        """Respond to a /names #channel command

        conn = connection object
        event = {
            type: "names"
            channel: "channel"
            users: [ "user1", "user2", ... ]
            time: seconds
        }
        """
