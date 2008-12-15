
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
            deferred = db.pool.runInteraction(self._insert, event)
            deferred.addErrback(self._error)

    def me(self, conn, event):
        if not db.pool or event['sent_by'] == conn.nickname:
            return
        event['text'] = "/me %s" % event['text']
        self.msg(conn, event)

    def rebuild(self, ignore):
        """Drop and rebuild the *entire* index.

        Ignore messages sent by nick (presumably this bot)
        """

        deferred = db.pool.runInteraction(self._rebuild, ignore)
        deferred.addErrback(self._error)
        return deferred

    def _answer(self, cursor, conn, event):
        answers = []
        for i in range(0,5):
            keyword = self._get_keyword(cursor, event['text'])
            if not keyword:
                continue

            answer = self._get_answer(cursor, keyword)
            if answer:
                answers.append(answer)

        if not answers:
            return

        answers.sort(key=lambda x: x[1])
        # The weighting system is slightly bogus, however the middle value
        # seems to be a reasonable one most of the time so far...
        answer = answers[len(answers)//2][0]

        reactor.callFromThread(conn.msg, event['reply_to'], answer)

    def _get_keyword(self, cursor, text):
        words = re.findall("\w+", text)
        keyword = None

        if words:
            sql = ("SELECT `word` FROM `brain_keywords` "
                    "WHERE `weight` > 1 AND (0")
            for i in xrange(0, len(words)):
                sql += " OR `word` = %s"
            sql += ") ORDER BY `weight` ASC"

            cursor.execute(sql, words)
            keywords = cursor.fetchall()

            for word in keywords:
                if random.random() < 1.0/len(keywords):
                    keyword = word[0]
                    break

        if not keyword:
            cursor.execute("SELECT `word` FROM `brain_keywords` "
                "ORDER BY `weight` DESC LIMIT 50")
            keywords = cursor.fetchall()

            if keywords:
                keyword = random.choice(keywords)[0]

        return keyword

    def _get_answer(self, cursor, keyword):
        cursor.execute("SELECT * FROM `brain_chains` WHERE `key_1` = %s"
                "ORDER BY `weight` DESC LIMIT 50", keyword)
        answers = cursor.fetchall()

        if not answers:
            log.error("brain: Failed to find keyword '%s'" % keyword)
            return

        answer = answers[0][:-2] # fallback answer
        weight = 0
        for row in answers:
            weight -= 1.0/(2*len(answers))
            if random.random() < 1.0/len(answers):
                answer = row[:-2] # chop of weight, date
                break

        answer, weight = self._build_forward(cursor, answer, weight)
        answer, weight = self._build_reverse(cursor, answer, weight)

        return "".join(answer), weight

    def _build_forward(self, cursor, answer, weight):
        if not answer[-1]:
            return answer, weight

        cursor.execute("SELECT `sep_4`, `key_5` FROM `brain_chains` "
                "WHERE `key_1` = %s AND `key_2` = %s AND `key_3` = %s "
                "AND `key_4` = %s ORDER BY `weight` DESC LIMIT 50",
                (answer[-7], answer[-5], answer[-3], answer[-1]))
        answers = cursor.fetchall()

        if answers:
            new = answers[0]
            for row in answers:
                weight -= 1.0/(2*len(answers))
                if random.random() < 1.0/len(answers):
                    new = row
                    break
            return self._build_forward(cursor, answer+new, weight)
        else:
            return answer, weight

    def _build_reverse(self, cursor, answer, weight):
        if not answer[0]:
            return answer, weight

        cursor.execute("SELECT `key_1`, `sep_1` FROM `brain_chains` "
                "WHERE `key_2` = %s AND `key_3` = %s AND `key_4` = %s "
                "AND `key_5` = %s ORDER BY `weight` DESC LIMIT 50",
                (answer[0], answer[2], answer[4], answer[6]))
        answers = cursor.fetchall()

        if answers:
            new = answers[0]
            for row in answers:
                weight -= 1.0/(2*len(answers))
                if random.random() < 1.0/len(answers):
                    new = row
                    break
            return self._build_reverse(cursor, new+answer, weight)
        else:
            return answer, weight

    def _rebuild(self, cursor, ignore):
        # We don't want transactions for this process...
        cursor.execute("SET autocommit=1")

        log.info("The following nicks are ignored: %s" % " ".join(ignore))

        log.info("Truncating tables...")
        cursor.execute("TRUNCATE TABLE `brain_keywords`")
        cursor.execute("TRUNCATE TABLE `brain_chains`")

        log.info("Fetching log...")
        cursor.execute("SELECT `id` FROM `log` ORDER BY `id` DESC LIMIT 1")

        lastid = cursor.fetchone()
        if not lastid:
            log.warn("The log is empty! Aborting rebuild.")
            return
        else:
            lastid = float(lastid[0])

        cursor.execute("SELECT `id`, `sent_by`, `channel`, `type`, `text` "
                "FROM `log` WHERE `type` = 'msg' OR `type` = 'action'")
        log.info("Starting rebuild...")

        i = 0
        for id, sent_by, channel, type, text in cursor:
            if not reactor.running:
                log.warn("Aborting rebuild!")
                break

            for nick in ignore:
                # Ignore some nicks, ie bots
                if sent_by.startswith(nick):
                    continue

            # Strip of nicks in targeted messages
            text = re.sub("^\w+:\s*", "", text)

            if not re.match("^\w", text):
                continue

            i += 1
            if i % 100 == 0:
                log.info("At row %s (%.1f%%)" % (id, (id/lastid)*100))

            event = {'channel': channel}
            if type == 'action':
                event['text'] = "/me %s" % text
            else:
                event['text'] = text
            self._insert(cursor, event)

        if reactor.running:
            log.info("Finished rebuild!")

    def _insert(self, cursor, event):
        words = re.findall("(^/me|\w+)(\W*)", event['text'])

        # Words longer that 20 chars probably are urls or other bogus crap
        # but since simply removing said crap may create bogus chains just
        # drop the entire chain in such cases. Likewise for large separators.
        for word, sep in words:
            if len(word) > 20 or len(sep) > 5:
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
