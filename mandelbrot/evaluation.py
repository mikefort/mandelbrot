# Copyright 2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Mandelbrot.
#
# Mandelbrot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mandelbrot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mandelbrot.  If not, see <http://www.gnu.org/licenses/>.

import time

class Health:
    HEALTHY  = 'healthy'
    DEGRADED = 'degraded'
    FAILED   = 'failed'
    UNKNOWN  = 'unknown'

class Evaluation(object):
    """
    """
    def __init__(self, health, summary, detail=None, timestamp=None, metrics=None, events=None, snapshot=None):
        self._health = health
        self._summary = summary
        self._detail = detail
        self._timestamp = timestamp if timestamp is not None else time.time()
        self._metrics = metrics
        self._events = events
        self._snapshot = snapshot

    def __str__(self):
        return "%s @ %s: %s" % (self._health, time.asctime(time.gmtime(self._timestamp)), self._summary)

    @property
    def health(self):
        return self._health

    @property
    def summary(self):
        return self._summary

    @property
    def detail(self):
        return self._detail

    @property
    def timestamp(self):
        return long(self._timestamp * 1000.0)

    @property
    def metrics(self):
        return self._metrics

    @property
    def events(self):
        return self._events

    @property
    def snapshot(self):
        return self._snapshot
