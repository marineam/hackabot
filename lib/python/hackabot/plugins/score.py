
import re

from zope.interface import implements
from twisted.plugin import IPlugin

from hackabot.plugin import IHackabotPlugin
from hackabot import log

class Score(object):
    """Record something++ and something-- statements"""
    implements(IPlugin, IHackabotPlugin)

    def __init__(self):
        self._regex = re.compile("([\w\-]*\w+)(\+\+|--)(\s|$)")

    def msg(self, conn, event):
        if ('internal' in event and event['internal']
                or event['sent_to'] == conn.nickname):
            return

        dbpool = conn.manager.dbpool

        for match in re.finditer(self._regex, event['text']):
            if match.group(2) == "++":
                if match.group(1) == event['sent_by']:
                    conn.msg(event['reply_to'],
                            "%s: no self promotion! You lose 5 points." %
                            event['sent_by'])
                    inc = -5
                else:
                    inc = 1
            else:
                if match.group(1) == event['sent_by']:
                    conn.msg(event['reply_to'],
                            "%s: Aww, cheer up! You can keep your point." %
                            event['sent_by'])
                    return
                else:
                    inc = -1

            log.debug("score: %s += %s" % (match.group(1), inc))

            defer = dbpool.runOperation("INSERT INTO `score` "
                    "(`name`, `value`, `nick`, `chan`, `date`) "
                    "VALUES (%s, %s, %s, %s, FROM_UNIXTIME(%s)) "
                    "ON DUPLICATE KEY UPDATE "
                    "`value` = `value` + VALUES(`value`), "
                    "`nick` = VALUES(`nick`), "
                    "`chan` = VALUES(`chan`), "
                    "`date` = VALUES(`date`)",
                    (match.group(1), inc, event['sent_by'],
                        event['sent_to'], event['time']))
            defer.addErrback(log.error)

    me = msg

    def command_score(self, conn, event):
        """Get someone's score or get a list.
        !score name | --high | --low [ --nicks ]
        """

        if not event['text']:
            return

        dbpool = conn.manager.dbpool

        if "--nicks" in event['text'] and event['sent_to'] in conn.channels:
            # This looks weird, but MySQLdb doesn't provide a quote
            # function so we have to build a format string and tuple
            names = tuple(conn.channels[event['sent_to']]['users'])
            where = "WHERE 0" + " OR `name` = %s" * len(names)
        else:
            names = ()
            where = ""

        sql = "SELECT `name`, `value` FROM `score` "

        if "--high" in event['text']:
            defer = dbpool.runQuery("%s%s ORDER BY `value` DESC LIMIT 3"
                    % (sql, where), names)
            defer.addCallback(self._send_list, "High Scores:", conn, event)
            defer.addErrback(self._error, conn, event)

        elif "--low" in event['text']:
            defer = dbpool.runQuery("%s%s ORDER BY `value` ASC LIMIT 3"
                    % (sql, where), names)
            defer.addCallback(self._send_list, "Low Scores:", conn, event)
            defer.addErrback(self._error, conn, event)

        else:
            name = event['text'].split(None,1)[0]
            defer = dbpool.runQuery("SELECT `value` FROM `score` "
                    "WHERE `name` = %s", name)
            defer.addCallback(self._send_value, name, conn, event)
            defer.addErrback(self._error, conn, event)

    def _error(self, result, conn, event):
        conn.msg(event['reply_to'], "DB Failure :-(")
        log.error(result)
        return

    def _send_list(self, result, heading, conn, event):
        conn.msg(event['reply_to'], heading)
        for row in result:
            conn.msg(event['reply_to'], "  %s %s" % (row[1], row[0]))

    def _send_value(self, result, name, conn, event):
        if result:
            value = result[0][0]
        else:
            value = 0

        if value == 1:
            s = ""
        else:
            s = "s"

        conn.msg(event['reply_to'], "%s has %s point%s!" % (name, value, s))

score = Score()
