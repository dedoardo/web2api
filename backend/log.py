"""
Simple logging facility.
"""

# termcolor is an optional import
import imp
import time, datetime

try:
    imp.find_module('termcolor')
    TERMCOLOR_ENABLED = True
except ImportError:
    TERMCOLOR_ENABLED = False

if TERMCOLOR_ENABLED:
    from termcolor import colored

def _build_msg(*arg):
    msg = ''
    for a in arg[0]:
        msg += str(a)

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')

    return timestamp, msg

def info(*arg):
    ts, tmp_msg = _build_msg(arg)
    msg = '[{0}]'.format(ts) + '[INFO]' + tmp_msg

    if TERMCOLOR_ENABLED:
        msg = colored(msg, 'green')
    
    print(msg)

def warning(*arg):
    ts, tmp_msg = _build_msg(arg)
    msg = '[{0}]'.format(ts) + '[WARNING]' + tmp_msg

    if TERMCOLOR_ENABLED:
        msg = colored(msg, 'yellow')
    
    print(msg)

def error(*arg):
    ts, tmp_msg = _build_msg(arg)
    msg = '[{0}]'.format(ts) + '[ERROR]' + tmp_msg

    if TERMCOLOR_ENABLED:
        msg = colored(msg, 'red')
    
    print(msg)