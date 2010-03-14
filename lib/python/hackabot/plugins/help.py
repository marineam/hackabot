"""Get help!"""

import os
from glob import glob

from zope.interface import implements
from twisted.plugin import IPlugin
from hackabot.plugin import IHackabotPlugin

class Help(object):
    implements(IPlugin, IHackabotPlugin)

    def command_help(self, conn, event):
        """List commands or get help on one command
        !help [command]
        """

        plugins = conn.manager.plugins
        conf = conn.manager.config
        external = "%s/commands" % conf.get('root')
        text = event['text'].strip()
        if text:
            event['command'] = text
            ok, reply = conn.factory.acl.check(event)
            if not ok:
                if reply:
                    send = reply
            elif text in plugins.commands:
                send = plugins.commands[text].__doc__
                if send is None:
                    send = "Command '%s' is missing a help message." % text
            elif os.path.isfile("%s/%s" % (external, text)):
                cmd = "%s/%s" % (external, text)
                send = ""

                try:
                    fd = open(cmd)
                    found = False
                    for line in fd:
                        if not found and line.startswith("##HACKABOT_HELP##"):
                            found = True
                        elif line.startswith("##HACKABOT_HELP##"):
                            break
                        elif found:
                            send += line.lstrip("# ")
                    fd.close()
                except IOError:
                    send = "Error reading command '%s'" % text

                send = send.strip()

                if not send:
                    send = "Command '%s' is missing a help message." % text
            else:
                send = "Unknown command '%s'" % text
        else:
            commands = plugins.commands.keys()

            for cmd in glob("%s/*" % external):
                if (os.path.isfile(cmd) and not os.path.islink(cmd)
                        and os.access(cmd, os.X_OK)):
                    commands.append(os.path.basename(cmd))

            allowed = []
            for cmd in commands:
                event['command'] = cmd
                ok, nill = conn.factory.acl.check(event)
                if ok and cmd not in allowed:
                    allowed.append(cmd)

            allowed.sort()
            send = "Commands: %s" % " ".join(allowed)

        for line in send.splitlines():
            line = line.strip()
            conn.msg(event['reply_to'], line)

help = Help()
