"""Hackabot ACL Checks"""

from hackabot import conf, log
from hackabot.etree import ElementTree

class ACL(object):
    """Process the acl xml file"""

    def __init__(self, net=None):
        if net is not None and net.find("acl"):
            conffile = conf.find("acl").get("file", None)
        elif conf.find("acl") is not None:
            conffile = conf.find("acl").get("file", None)
        else:
            self._conf = None
            return

        if conffile is None:
            log.error("<acl> tag is missing the file attribute!");
            self._conf = None
            return

        self._conf = ElementTree.parse(conffile)

    def check(self, event):
        """Check if a command can be run by a user.
        
        Returns a tuple: (True/False, message)
        """

        if self._conf is None:
            acl = None
        elif event['private']:
            acl = self.check_private(event['command'], event['sent_by'])
        else:
            acl = self.check_public(event['command'], event['sent_by'],
                    event['sent_to'])

        if acl is None:
            log.debug("No acl")
            return (True, "")
        else:
            log.debug("Using acl: %s" % ElementTree.tostring(acl))
            action = acl.get("action", "")
            if action == "" or action not in ("allow", "deny"):
                log.error('Invalid acl action="%s", allowing.' % action)
            return (action != "deny", acl.get("msg", ""))

    def check_public(self, command, nick, channel):
        """Helper for check()"""

        acl = None

        # This could be greatly improved by using lxml with proper
        # xpath support but this one case didn't seem important enough
        # to add lxml as a dependency.
        for cmd in self._conf.findall("command")+[self._conf.find("default")]:
            if cmd.get("name", None) == command or cmd.tag == "default":
                acl = cmd
                for chan in cmd.findall("command"):
                    if chan.get("chan", None) == channel:
                        acl = chan
                        for person in chan.findall("person"):
                            if person.get("nick", None) == nick:
                                acl = person
                                break
                        break
                for person in cmd.findall("person"):
                    if person.get("nick", None) == nick:
                        acl = person
                        break
                break

        return acl

    def check_private(self, command, nick):
        """Helper for check()"""

        acl = None

        for cmd in self._conf.findall("command")+[self._conf.find("default")]:
            if cmd.get("name", None) == command or cmd.tag == "default":
                acl = cmd
                private = cmd.find("private", None)
                if private is not None:
                    acl = private
                    for person in private.findall("person"):
                        if person.get("nick", None) == nick:
                            acl = person
                            break
                else:
                    for person in cmd.findall("person"):
                        if person.get("nick", None) == nick:
                            acl = person
                            break
                break

        return acl
