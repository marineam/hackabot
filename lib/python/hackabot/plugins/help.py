"""Get help!"""

from zope.interface import implements
from twisted.plugin import IPlugin
from hackabot import plugin

class Help(object):
    implements(IPlugin, plugin.IHackabotPlugin)

    def command_help(self, conn, sent_by, sent_to, reply_to, text):
        """List commands or get help on one command
        !help [command]
        """

        text = text.strip()
        if text:
            if text in plugin.manager.commands:
                send = plugin.manager.commands[text].__doc__
                if send is None:
                    send = "Command '%s' is missing a help message." % text
            else:
                send = "Unknown command '%s'" % text
        else:
            commands = plugin.manager.commands.keys()
            commands.sort()
            send = "Commands: %s" % " ".join(commands)

        for line in send.splitlines():
            line = line.strip()
            conn.msg(reply_to, line)

help = Help()
