
import re
import random

from zope.interface import implements
from twisted.plugin import IPlugin
from twisted.internet import reactor, defer

from hackabot.plugin import IHackabotPlugin
from hackabot import log, db

class Brain(object):
    """Pretend to know stuff!"""
    implements(IPlugin, IHackabotPlugin)

    def msg(self, conn, event):
        if (not db.pool or event['sent_by'] == conn.nickname
                or not re.match("^(\w|/me\s+\w)", event['text'])):
            return

        if conn.nickname.lower() in event['text'].lower():
            event['text'] = re.sub("^%s:?\s*" % conn.nickname,
                    "", event['text'], 1)
            deferred = db.pool.runInteraction(self._answer, conn, event)
            deferred.addErrback(self._error)
        else:
            deferred = db.pool.runInteraction(self._insert, conn, event)
            deferred.addErrback(self._error)

    def me(self, conn, event):
        if not db.pool or event['sent_by'] == conn.nickname:
            return
        event['text'] = "/me %s" % event['text']
        self.msg(conn, event)

    def _answer(self, cursor, conn, event):
        keyword = self._get_keyword(cursor, event['text'])
        if not keyword:
            return

        answer = self._get_answer(cursor, keyword)
        if not answer:
            return

        reactor.callFromThread(conn.msg, event['reply_to'], answer)

    def _get_keyword(self, cursor, text):
        words = re.findall("\w+", text)
        keyword = None

        if words:
            sql = "SELECT `word`, `weight` FROM `brain_keywords` WHERE 0"
            for i in xrange(0, len(words)):
                sql += " OR `word` = %s"

            cursor.execute(sql, words)
            keywords = cursor.fetchall()

            if keywords:
                # TODO: use weight
                keyword = random.choice(keywords)[0]

        if not keyword:
            cursor.execute("SELECT `word` FROM `brain_keywords` "
                "SORT BY `weight` DESC LIMIT 50")
            keywords = cursor.fetchall()

            if keywords:
                keyword = random.choice(keywords)[0]

        return keyword

    def _get_answer(self, cursor, keyword):
        cursor.execute("SELECT * FROM `brain_chains` WHERE `key_1` = %s",
                keyword)
        # TODO: this might return too much stuff
        answers = cursor.fetchall()

        if not answers:
            log.error("brain: Failed to find keyword '%s'" % keyword)
            return

        # TODO: use weight
        answer = random.choice(answers)[:-2] # chop off weight, date

        answer = self._build_forward(cursor, answer)
        answer = self._build_reverse(cursor, answer)

        return "".join(answer)

    def _build_forward(self, cursor, answer):
        if not answer[-1]:
            return answer

        cursor.execute("SELECT `sep_4`, `key_5`, `weight` "
                "FROM `brain_chains` "
                "WHERE `key_1` = %s AND `key_2` = %s "
                "AND `key_3` = %s AND `key_4` = %s",
                (answer[-7], answer[-5], answer[-3], answer[-1]))
        answers = cursor.fetchall()

        if answers:
            # TODO: use weight
            new = random.choice(answers)
            return self._build_forward(cursor, answer+new[0:2])
        else:
            return answer

    def _build_reverse(self, cursor, answer):
        if not answer[0]:
            return answer

        cursor.execute("SELECT `key_1`, `sep_1`, `weight` "
                "FROM `brain_chains` "
                "WHERE `key_2` = %s AND `key_3` = %s "
                "AND `key_4` = %s AND `key_5` = %s",
                (answer[0], answer[2], answer[4], answer[6]))
        answers = cursor.fetchall()

        if answers:
            # TODO: use weight
            new = random.choice(answers)
            return self._build_reverse(cursor, new[0:2]+answer)
        else:
            return answer

    def _insert(self, cursor, conn, event):
        words = re.findall("(\w+)(\W*)", event['text'])

        # Words longer that 20 chars probably are urls or other bogus crap
        # but since simply removing said crap may create bogus chains just
        # drop the entire chain in such cases.
        for word in words:
            if len(word) > 20:
                return

        # Update keyword weights
        for keyword,sep in words:
            # TODO: figure out why executemany doesn't work
            cursor.execute("INSERT INTO `brain_keywords` "
                    "VALUES (%s, 1, NOW()) ON DUPLICATE KEY UPDATE "
                    "`date` = NOW(), `weight` = `weight` + 1", keyword)

        words.insert(0, ("", ""))

        for i in range(0, len(words)):
            group = []
            for word, sep in words[i:i+5]:
                # Flatten out the list of tuples
                group.append(word)
                group.append(sep)
            group += ([""] * (10-len(group)))
            group.pop() # remove sep5

            # group = [key1, sep1, key2, sep2, key3, sep3, key4, sep4, key5]
            cursor.execute("INSERT INTO `brain_chains` "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW()) "
                    "ON DUPLICATE KEY UPDATE `date` = NOW(), "
                    "`weight` = `weight` + 1", group)

    def _error(self, result):
        log.error(result)

brain = Brain()
