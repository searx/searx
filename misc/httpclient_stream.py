# -*- coding: utf-8 -*-


urls1 = [
    'https://a.searx.space/0',
    'https://a.searx.space/1',
    'https://a.searx.space/2',
    'https://a.searx.space/3',
    'https://a.searx.space/4',
    'https://a.searx.space/5',
    'https://a.searx.space/6',
    'https://a.searx.space/7',
    'https://a.searx.space/8',
    'https://a.searx.space/9',
    # 'https://github.com',
    'https://en.wikipedia.org/wiki/List_of_Unicode_characters',
    'https://en.wikipedia.org/wiki/Windows-1252'
    # 'https://google.com',
]

urls2 = [
    # 'https://yandex.com/search/?text=test&p=0',
    'https://www.wikidata.org/w/index.php?search=test&ns0=1',
    'https://duckduckgo.com/html?q=test&kl=us-en&s=0&dc=0',
    'https://en.wikipedia.org/w/api.php?action=query&format=json&titles=test%7CTest'\
    + '&prop=extracts%7Cpageimages&exintro&explaintext&pithumbsize=300&redirects',
    'https://www.bing.com/search?q=language%3AEN+test&first=1',
    'https://api.duckduckgo.com/?q=test&format=json&pretty=0&no_redirect=1&d=1'
]

urls3 = [
    'https://a.searx.space/9'
]

urls4 = [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Parque_Eagle_River%2C_Anchorage%2C_Alaska%2C_Estados_Unidos%2C_2017-09-01%2C_DD_21.jpg/800px-Parque_Eagle_River%2C_Anchorage%2C_Alaska%2C_Estados_Unidos%2C_2017-09-01%2C_DD_21.jpg'  # noqa
]

urls = urls1 + urls2 + urls3 + urls4

if __name__ == '__main__':
    from sys import path
    import gc
    # from guppy import hpy; h=hpy()
    from os.path import realpath, dirname
    path.append(realpath(dirname(realpath(__file__)) + '/../'))

    import searx.httpclient
    import requests

    # import yappi
    # import cProfile
    import time
    import linecache
    import os
    # import tracemalloc

    def mean(t):
        total = 0
        count = 0
        for i in t:
            total = total + i
            count = count + 1
        if count > 0:
            return total / count
        else:
            return 0

    def stdev(t):
        return 0

    try:
        from statistics import mean, stdev
    except:
        pass

    def memory_dump():
        # Add to leaky code within python_script_being_profiled.py
        from pympler import muppy, summary
        all_objects = muppy.get_objects()
        sum1 = summary.summarize(all_objects)# Prints out a summary of the large objects
        summary.print_(sum1)# Get references to certain types of objects such as dataframe


    def display_top(snapshot, key_type='lineno', limit=10):
        #snapshot = snapshot.filter_traces((
        #    tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        #    tracemalloc.Filter(False, "<unknown>"),
        #))
        top_stats = snapshot.statistics(key_type)

        print("Top %s lines" % limit)
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            # replace "/path/to/module/file.py" with "module/file.py"
            filename = os.sep.join(frame.filename.split(os.sep)[-2:])
            print("#%s: %s:%s: %.1f KiB"
                % (index, filename, frame.lineno, stat.size / 1024))
            line = linecache.getline(frame.filename, frame.lineno).strip()
            if line:
                print('    %s' % line)

        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024))
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))


    def fetch_url(r, u):
        start_time = time.time()
        response = r.request('GET', u, timeout=5.1, stream=False)
        # print(response.request)
        # print(response)
        # print(response.request.url, response.status_code, response.reason, response.headers, response.cookies)
        return time.time() - start_time 

    @profile
    def test():
        print('start')
        # with requests.Session() as r:
        with searx.httpclient.Session() as r:
            t = []
            for u in urls:
                t.append(fetch_url(r, u))
            time.sleep(30)
            for u in urls:
                t.append(fetch_url(r, u))
        gc.collect()
        print('end\n--> avg={0} s. stdev={1} s.'.format(mean(t), stdev(t)))

    # yappi.start(builtins=True)
    
    tmalloc = False

    if tmalloc:
        tracemalloc.start(100)
        snapshot1 = tracemalloc.take_snapshot()

    test()

    if tmalloc:
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        print("[ Top 10 ]")
        for stat in top_stats[:10]:
            print(stat)

        display_top(snapshot2, key_type='lineno')
    # memory_dump()
    # print(h.heap())
    # yappi.stop()
    # pr = yappi.convert2pstats(yappi.get_func_stats())
    # pr.dump_stats('curl.prof')
