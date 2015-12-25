'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2015- by Alexandre Flament, <alex@al-f.net>
'''
import threading
import implementation
from time import time

__all__ = ["implementation",
           "initialize",
           "measure_storage", "record", "measure", "start_timer", "end_timer", "configure_measure",
           "counter_storage", "counter", "counter_inc", "counter_add", "reset_counter"]

measure_storage = implementation.MeasureStorage()
counter_storage = implementation.CounterStorage()

threadlocal_dict = threading.local()
threadlocal_dict.timers = {}
timers = threadlocal_dict.timers


def record(value, *args):
    global measure_storage
    measure_storage.get(*args).record(value)


def counter_inc(*args):
    global counter_storage
    counter_storage.add(1, *args)


def counter_add(value, *args):
    global counter_storage
    counter_storage.add(value, *args)


def start_timer(*args):
    global timers
    timers[args] = time()


def end_timer(*args):
    global timers
    if args in timers:
        previous_time = timers[args]
        if previous_time is not None:
            timers[args] = None
            duration = time() - previous_time
            record(duration, *args)


def measure(*args):
    global measure_storage
    return measure_storage.get(*args)


def counter(*args):
    global counter_storage
    return counter_storage.get(*args)


def configure_measure(width, size, *args):
    global measure_storage
    return measure_storage.configure(width, size, *args)


def reset_counter(*args):
    global counter_storage
    return counter_storage.reset(*args)
