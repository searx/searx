from __future__ import division, with_statement
from searx import logger
import threading

__all__ = ["Measure", "MeasureStorage", "CounterStorage"]

logger = logger.getChild('metrology')


class Measure(object):

    def __init__(self, width=10, size=200):
        self.lock = threading.RLock()
        self.quartiles = [0] * size
        self.count = 0
        self.width = width
        self.size = size
        self.sum = long(0)

    def record(self, value):
        with self.lock:
            q = int(value / self.width)
            if q < 0:
                '''FIXME ? Ignore value below zero'''
                return
            if q >= self.size:
                q = self.size - 1
            self.quartiles[q] += 1
            self.count += 1
            self.sum += value

    def get_count(self):
        return self.count

    def get_sum(self):
        return self.sum

    def get_average(self):
        with self.lock:
            if self.count != 0:
                return self.sum / self.count
            else:
                return 0

    def get_quartile(self):
        return self.quartiles

    def get_qp(self):
        ''' Quartile in percentage '''
        with self.lock:
            if self.count > 0:
                return [int(q*100/self.count) for q in self.quartiles]
            else:
                return self.quartiles

    def get_qpmap(self):
        result = {}
        x = 0
        with self.lock:
            if self.count > 0:
                for y in self.quartiles:
                    yp = int(y*100/self.count)
                    if yp != 0:
                        result[x] = yp
                    x += self.width
        return result

    def __repr__(self):
        return "Measure<avg: " + str(self.get_average()) + ", count: " + str(self.get_count()) + ">"


class MeasureStorage(object):

    def __init__(self):
        self.measures = {}
        self.lock = threading.RLock()

    def configure(self, width, size, *args):
        with self.lock:
            measure = Measure(width, size)
            self.measures[args] = measure
        return measure

    def get(self, *args):
        measure = self.measures.get(args, None)
        if measure is None:
            with self.lock:
                measure = self.measures.get(args, None)
                if measure is None:
                    measure = Measure()
                    self.measures[args] = measure
        return measure

    def dump(self):
        ks = None
        with self.lock:
            ks = sorted(self.measures.keys(), key=lambda k: '/'.join(k))
        logger.debug("Measures:")
        for k in ks:
            logger.debug("- %-60s %s", '|'.join(k), self.measures[k])


class CounterStorage(object):

    def __init__(self):
        self.counters = {}
        self.lock = threading.RLock()

    def reset(self, *args):
        with self.lock:
            self.counters[args] = 0

    def get(self, *args):
        # logger.debug("Counter for {0} : {1}".format(args, self.counters.get(args, 0)))
        return self.counters.get(args, 0)

    def add(self, value, *args):
        with self.lock:
            self.counters[args] = value + self.counters.get(args, long(0))
            # logger.debug("Counter for {0} : {1}".format(args, self.counters[args]))

    def dump(self):
        with self.lock:
            ks = sorted(self.counters.keys(), key=lambda k: '/'.join(k))
        logger.debug("Counters:")
        for k in ks:
            logger.debug("- %-60s %s", '|'.join(k), self.counters[k])
