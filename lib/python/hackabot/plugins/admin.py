"""The admin command!"""

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.internet import reactor

from hackabot import core, plugin

class Admin(object):
    implements(IPlugin, plugin.IHackabotPlugin)

    @staticmethod
    def command_admin(conn, event):
        """Various administrative commands.
        !admin reload | quit
        """
        request, space, args = event['text'].partition(" ")

        if request == "reload":
            conn.msg(event['reply_to'],
                    "This is reload #%s since startup." % count)
            plugin.manager.reload()
        elif request == "quit":
            core.manager.disconnect(args)
        else:
            conn.msg(event['reply_to'],
                    "Unknown admin request: '%s'" % request)

# Count the number of loads
try:
    count += 1
except NameError:
    count = 1

admin = Admin()
