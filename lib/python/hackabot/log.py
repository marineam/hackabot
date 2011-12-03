"""Hackabot Logger"""

import time
import sys

from twisted.python import log, util, failure

LEVELS = [ 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE', 'RAINMAN' ]

_log_level = 2
_log_fallback = sys.stderr
_loud_init = False
_ctrl_chars = ''.join(chr(c) for c in xrange(1, 32))

def _logger(event):
    # This is a twisted log observer
    # Attempt to report all exceptions to stderr since they will be lost

    try:
        level = event.get('log_level', 'INFO')

        if level in LEVELS and _log_level < LEVELS.index(level):
            return

        # Use the smarter function if available
        if hasattr(log, 'textFromEventDict'):
            text = log.textFromEventDict(event)
        else:
            text = "\n".join(event['message'])
            if not text:
                text = str(event.get('failure', ''))

        # IRC reuses ASCII control characters for text formatting,
        # these are meaningless to anything reading the log.
        text = text.translate(None, _ctrl_chars)

        prefix = event.get('prefix', event.get('system', '-'))
        date = time.strftime("%b %d %H:%M:%S",
                time.localtime(event.get('time', None)))

        line = "%s %s %s: %s\n" % (date, level, prefix, text)
        util.untilConcludes(_log_file.write, line)
        util.untilConcludes(_log_file.flush)

        if _loud_init and level in ('ERROR', 'WARN'):
            util.untilConcludes(sys.stderr.write, line)
            util.untilConcludes(sys.stderr.flush)

    except:
        _log_fallback.write("%s" % failure.Failure())


def init(log_file, log_level):
    """Start up logging system"""
    global _log_file, _log_level, _loud_init

    assert log_level in LEVELS

    _log_file = log_file
    _log_level = LEVELS.index(log_level)

    if _log_file != sys.stdout:
        _loud_init = True

    log.startLoggingWithObserver(_logger, setStdout=0)

def init_stdio():
    """Take over sys.stderr and sys.stdout

    Do this here instead of init so we can be loud about startup errors.
    """
    global _loud_init

    sys.stdout = log.logfile
    sys.stderr = log.logerr
    _loud_init = False

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

def rainman(text, **kw):
    log.msg(text, log_level='RAINMAN', **kw)
