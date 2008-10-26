"""Global Hackabot Environment"""

import os

HB_ROOT=None
HB_PERL=None
HB_MYSQL=None
HB_PYTHON=None
HB_COMMANDS=None

def init(root):
    global HB_ROOT, HB_PERL, HB_MYSQL, HB_PYTHON, HB_COMMANDS

    HB_ROOT = root
    HB_PERL = "%s/lib/perl" % HB_ROOT
    HB_MYSQL = "%s/lib/mysql" % HB_ROOT
    HB_PYTHON = "%s/lib/python" % HB_ROOT
    HB_COMMANDS= "%s/commands" % HB_ROOT

    os.putenv('HB_ROOT', HB_ROOT)
    os.putenv('HB_PERL', HB_PERL)
    os.putenv('HB_MYSQL', HB_MYSQL)
    os.putenv('HB_PYTHON', HB_PYTHON)
    os.putenv('HB_COMMANDS', HB_PYTHON)
