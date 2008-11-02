
from zope.interface import implements
from twisted.plugin import IPlugin
from hackabot.plugin import IHackabotPlugin
from hackabot import log, db

class DBLogger(object):
    implements(IPlugin, IHackabotPlugin)

    def msg(self, conn, sent_by, sent_to, reply_to, text):
        if sent_to == conn.nickname:
            channel=None
        else:
            channel=sent_to

        self._logger('msg', sent_by, sent_to, channel, text)

    def me(self, conn, sent_by, sent_to, reply_to, text):
        if sent_to == conn.nickname:
            channel=None
        else:
            channel=sent_to

        self._logger('action', sent_by, sent_to, channel, text)

    def notice(self, conn, sent_by, sent_to, reply_to, text):
        if sent_to == conn.nickname:
            channel=None
        else:
            channel=sent_to

        self._logger('notice', sent_by, sent_to, channel, text)

    def topic(self, conn, sent_by, channel, text):
        self._logger('topic', sent_by, channel, channel, text)

    def join(self, conn, sent_by, channel):
        self._logger('join', sent_by, channel, channel, None)

    def part(self, conn, sent_by, channel, text):
        self._logger('part', sent_by, channel, channel, text)

    def kick(self, conn, kicker, kickee, channel, text):
        self._logger('kick', kicker, kickee, channel, text)

    def quit(self, conn, sent_by, text):
        self._looger('quit', sent_by, None, None, text)

    def rename(self, conn, old, new):
        # We abuse sent_to slightly here
        self._logger('rename', old, new, None, None)

    def names(self, conn, channel, userlist):
        self._logger('stats', None, channel, channel, userlist)

    def _logger(self, event, sent_by, sent_to, channel, text):
        """Record an event to the log table"""

        if not db.pool:
            log.warn("The db logger plugin is active but there is no db!")
            return

        # These correspond to the type column's enum values
        assert event in ('msg', 'action', 'notice', 'join', 'part',
                'quit', 'stats', 'topic', 'kick', 'rename')

        if event == 'stats':
            # for stats text is actually a list of users
            count = len(text)
            text = ' '.join(text)
        else:
            count = None

        db.pool.runOperation("INSERT INTO `log` "
            "(`sent_by`,`sent_to`,`channel`,`text`,`count`,`type`,`date`) "
            "VALUES (%s, %s, %s, %s, %s, %s, NOW())",
            (sent_by, sent_to, channel, text, count, event))

# Only activate plugin if there is a db
if db.pool:
    logger = DBLogger()
