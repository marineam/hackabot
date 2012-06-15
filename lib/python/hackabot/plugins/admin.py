"""The admin command!"""

from zope.interface import implements
from twisted.plugin import IPlugin
from hackabot.plugin import IHackabotPlugin

class Admin(object):
    implements(IPlugin, IHackabotPlugin)

    @staticmethod
    def command_admin(conn, event):
        """Various administrative commands.
        !admin reload | quit | join #chan | part #chan | nick newname
        """

        line = event['text'].split(None, 1)
        if not line:
            conn.msg(event['reply_to'], "Try !help admin")
            return
        else:
            request = line.pop(0)
            args = "".join(line)

        if request == "reload":
            conn.msg(event['reply_to'],
                    "This is reload #%s since startup." % count)
            conn.manager.reload()
        elif request == "quit":
            conn.manager.disconnect(args)
        elif not args:  # All further commands require an argument
            conn.msg(event['reply_to'], "Missing argument, try !help admin")
        elif request == "join":
            conn.join(args)
        elif request == "part":
            conn.part(args)
        elif request == "nick":
            conn.setNick(line[0])
        else:
            conn.msg(event['reply_to'],
                    "Unknown admin request: '%s'" % request)

# Count the number of loads
try:
    count += 1
except NameError:
    count = 1

admin = Admin()
