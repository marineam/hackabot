"""The admin command!"""

from zope.interface import implements
from twisted.plugin import IPlugin

from hackabot import plugin

class Admin(object):
    implements(IPlugin, plugin.IHackabotPlugin)

    @staticmethod
    def command_admin(conn, sent_by, sent_to, reply_to, text):
        request, space, args = text.partition(" ")

        if request == "reload":
            conn.msg(reply_to, "This is reload #%s since startup." % count)
            plugin.manager.reload()
        else:
            conn.msg(reply_to, "Unknown admin request: '%s'" % request)

# Count the number of loads
try:
    count += 1
except NameError:
    count = 1

admin = Admin()
