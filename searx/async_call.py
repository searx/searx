import threading
import Queue
import time
from searx import logger

logger = logger.getChild('async_call')


class AsyncCall(object):

    def __init__(self, thread_name):
        super(AsyncCall, self).__init__()
        self.lock = threading.Lock()
        self.lock.acquire()
        self.thread = threading.Thread(
            target=self.wrapper(),
            name=thread_name,
            )
        self.thread.daemon = True
        self.thread.start()

    def wrapper(self):
        def thread_loop():
            while True:
                self.lock.acquire()
                result = None
                try:
                    result = self.f(*self.args, **self.kwargs)
                    logger.debug("Time : {0} second(s)".format(time.time() - self.start_time))
                except Exception, e:
                    logger.exception(e)
                    if self.on_exception is not None:
                        try:
                            self.on_exception(self, e, *self.args, **self.kwargs)
                        except:
                            pass
                finally:
                    self.f = None
                    if self.callback is not None:
                        try:
                            self.callback(self, result)
                        except Exception, e:
                            logger.error("Error in callback {0}".format(e))
                            pass

        return thread_loop

    def call(self, callback, on_exception, f, *args, **kwargs):
        self.callback = callback
        self.on_exception = on_exception
        self.f = f
        self.args = args
        self.kwargs = kwargs
        self.start_time = time.time()
        self.lock.release()
        return self

    def simple_call(self, f, *args, **kwargs):
        return self.call(None, None, f, *args, **kwargs)

    def close(self):
        pass


class AsyncCallPool(object):

    def __init__(self, thread_name):
        super(AsyncCallPool, self).__init__()
        self.thread_name = thread_name
        self.thread_count = 1
        self.pool = Queue.Queue()

    def call(self, callback, on_exception, f, *args, **kwargs):

        def inner_callback(ac, result):
            self.pool.put(ac)
            if callback is not None:
                callback(ac, result)

        ac = None
        if self.pool.empty():
            ac = AsyncCall(self.thread_name + '_' + str(self.thread_count))
            self.thread_count += 1
        else:
            ac = self.pool.get_nowait()
        return ac.call(inner_callback, on_exception, f, *args, **kwargs)


class AsyncBatchCall(object):

    def __init__(self, async_call_pool, on_exception, requests, timeout):
        self.async_call_pool = async_call_pool
        self.requests = requests
        self.calls = set()
        self.max_time = time.time() + timeout
        self.result = []
        self.on_exception = on_exception

    def call(self):
        def callback(ac, result):
            self.calls.remove(ac)
            self.result.append(result)

        for f, args, kwargs in self.requests:
            ac = self.async_call_pool.call(callback, self.on_exception, f, *args, **kwargs)
            self.calls.add(ac)

    def get_remaining_time(self):
        if len(self.calls) > 0:
            return max(0.0, self.max_time - time.time())
        else:
            return 0

    def is_terminated(self):
        return len(self.calls)
