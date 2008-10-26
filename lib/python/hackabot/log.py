"""Hackabot Logger"""

import time
import sys

from twisted.python import log, util, failure

LEVELS = [ 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE' ]

_log_fallback = sys.stdout

def _logger(event):
    # This is a twisted log observer
    # Attempt to report all exceptions to stdout since they will be lost

    try:
        level = event.get('log_level', 'INFO')

        if level in LEVELS and _log_level < LEVELS.index(level):
            return

        prefix = event.get('prefix', event.get('system', '-'))
        text = log.textFromEventDict(event).replace("\n", "\n\t")
        date = time.strftime("%b %d %H:%M:%S",
                time.localtime(event.get('time', None)))

        line = "%s %s %s: %s\n" % (date, level, prefix, text)
        util.untilConcludes(_log_file.write, line)
        util.untilConcludes(_log_file.flush)
    except:
        _log_fallback.write("%s" % failure.Failure())


def init(log_file, log_level):
    global _log_file, _log_level

    assert log_level in LEVELS

    _log_file = log_file
    _log_level = LEVELS.index(log_level)

    log.startLoggingWithObserver(_logger, setStdout=0)

def error(text, **kw):
    log.msg(text, log_level='ERROR', **kw)

def warn(text, **kw):
    log.msg(text, log_level='WARN', **kw)

def info(text, **kw):
    log.msg(text, log_level='INFO', **kw)

def debug(text, **kw):
    log.msg(text, log_level='DEBUG', **kw)

def trace(text, **kw):
    log.msg(text, log_level='TRACE', **kw)
