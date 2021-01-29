# SPDX-License-Identifier: AGPL-3.0-or-later

from searx import logger
import threading

__all__ = ["Measure", "MeasureStorage", "CounterStorage"]

logger = logger.getChild('searx.metrics')


class Measure:

    _slots__ = '_lock', '_size', '_sum', '_quartiles', '_count', '_width'

    def __init__(self, width=10, size=200):
        self._lock = threading.Lock()
        self._width = width
        self._size = size
        self._quartiles = [0] * size
        self._count = 0
        self._sum = 0

    def record(self, value):
        q = int(value / self._width)
        if q < 0:
            """Value below zero is ignored"""
            return
        if q >= self._size:
            """Value above the maximum is replaced by the maximum"""
            q = self._size - 1
        with self._lock:
            self._quartiles[q] += 1
            self._count += 1
            self._sum += value

    @property
    def quartiles(self):
        return list(self._quartiles)

    @property
    def count(self):
        return self._count

    @property
    def sum(self):
        return self._sum

    @property
    def average(self):
        with self._lock:
            if self._count != 0:
                return self._sum / self._count
            else:
                return 0

    @property
    def quartile_percentage(self):
        ''' Quartile in percentage '''
        with self._lock:
            if self._count > 0:
                return [int(q * 100 / self._count) for q in self._quartiles]
            else:
                return self._quartiles

    @property
    def quartile_percentage_map(self):
        result = {}
        x = 0
        with self._lock:
            if self._count > 0:
                for y in self._quartiles:
                    yp = int(y * 100 / self._count)
                    if yp != 0:
                        result[x] = yp
                    x += self._width
        return result

    def __repr__(self):
        return "Measure<avg: " + str(self.average) + ", count: " + str(self._count) + ">"


class MeasureStorage:

    __slots__ = 'measures'

    def __init__(self):
        self.clear()

    def clear(self):
        self.measures = {}

    def configure(self, width, size, *args):
        measure = Measure(width, size)
        self.measures[args] = measure
        return measure

    def get(self, *args):
        return self.measures.get(args, None)

    def dump(self):
        logger.debug("Measures:")
        ks = sorted(self.measures.keys(), key='/'.join)
        for k in ks:
            logger.debug("- %-60s %s", '|'.join(k), self.measures[k])


class CounterStorage:

    __slots__ = 'counters', 'lock'

    def __init__(self):
        self.lock = threading.Lock()
        self.clear()

    def clear(self):
        with self.lock:
            self.counters = {}

    def configure(self, *args):
        with self.lock:
            self.counters[args] = 0

    def get(self, *args):
        return self.counters[args]

    def add(self, value, *args):
        with self.lock:
            self.counters[args] += value

    def dump(self):
        with self.lock:
            ks = sorted(self.counters.keys(), key='/'.join)
        logger.debug("Counters:")
        for k in ks:
            logger.debug("- %-60s %s", '|'.join(k), self.counters[k])
