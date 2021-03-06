"""
Timepiece
---------

Tools for dealing with time

"""

from __future__ import print_function
import numpy as np
import time
import sys
from .ionic import unicodes
from functools import wraps

# exports
__all__ = ['hrtime', 'Stopwatch', 'profile']


class Stopwatch():
    def __init__(self, name=''):
        self.name = name
        self.start = time.time()
        self.absolute_start = time.time()

    def __str__(self):
        return u'\u231a  Stopwatch for: ' + self.name

    @property
    def elapsed(self):
        current = time.time()
        elapsed = current - self.start
        self.start = time.time()
        return elapsed

    def checkpoint(self, name=''):
        print("{timer} {checkpoint} took {elapsed}".format(
            timer = self.name,
            checkpoint = name,
            elapsed = hrtime(self.elapsed),
        ).strip())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        print(u'{timer} Finished! \u2714\nTotal elapsed time: {total}'.format(
            timer=self.name,
            total=hrtime(time.time() - self.absolute_start)
        ))


def hrtime(t):
    """
    Converts a time in seconds to a reasonable human readable time

    Parameters
    ----------
    t : float
        The number of seconds

    Returns
    -------
    time : string
        The human readable formatted value of the given time

    """

    try:
        t = float(t)
    except (ValueError, TypeError):
        raise ValueError("Input must be numeric")

    # weeks
    if t >= 7*60*60*24:
        weeks = np.floor(t / (7.*60.*60.*24.))
        timestr = "{:0.0f} weeks, ".format(weeks) + hrtime(t % (7*60*60*24))

    # days
    elif t >= 60*60*24:
        days = np.floor(t / (60.*60.*24.))
        timestr = "{:0.0f} days, ".format(days) + hrtime(t % (60*60*24))

    # hours
    elif t >= 60*60:
        hours = np.floor(t / (60.*60.))
        timestr = "{:0.0f} hours, ".format(hours) + hrtime(t % (60*60))

    # minutes
    elif t >= 60:
        minutes = np.floor(t / 60.)
        timestr = "{:0.0f} min., ".format(minutes) + hrtime(t % 60)

    # seconds
    elif (t >= 1) | (t == 0):
        timestr = "{:g} s".format(t)

    # milliseconds
    elif t >= 1e-3:
        timestr = "{:g} ms".format(t*1e3)

    # microseconds
    elif t >= 1e-6:
        timestr = u"{:g} {}s".format(t*1e6, unicodes['micro'])

    # nanoseconds or smaller
    else:
        timestr = "{:g} ns".format(t*1e9)

    return timestr


def profile(func):
    calls = list()
    @wraps(func)
    def wrapper(*args, **kwargs):
        tstart = time.time()
        results = func(*args, **kwargs)
        tstop = time.time()
        calls.append(tstop-tstart)
        return results

    wrapper.calls = calls
    wrapper.mean = lambda: np.mean(calls)
    wrapper.serr = lambda: np.std(calls) / np.sqrt(len(calls))
    wrapper.summary = lambda: print('Runtimes: {} {} {}'.format(
        hrtime(wrapper.mean()), unicodes['pm'], hrtime(wrapper.serr())))
    return wrapper
