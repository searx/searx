# -*- coding: utf-8 -*-
if __name__ == '__main__':
    from sys import path
    from os.path import realpath, dirname
    path.append(realpath(dirname(realpath(__file__)) + '/../../'))

    import concurrent.futures
    from searx.httpclient import Sessions, logger

    import yappi
    import cProfile
    import time

    yappi.start(builtins=True)

    r = Sessions()
    # time.sleep(10)

    start_time = time.time()
    a = time.time()
    allresponses = []

    # r1 = r.request('GET', 'https://httpbin.org/delay/0', headers={'User-Agent': 'x'})
    allresponses.append(r.async_request('GET', 'https://a.searx.space/404',
                                        timeout=5.1, params={'q': 'test'}, debug=False))
    allresponses.append(r.async_request('GET', 'https://a-v2.sndcdn.com/assets/app-55ad8b3-d95005d-3.js',
                                        timeout=20, debug=True))
    # r2 = r.request('GET', 'https://a.searx.space/config', cookies={'as': 'sa', 'bb': 'cc'})
    # r3 = r.request('GET', 'https://a.searx.space', timeout=1.0, headers={'User-Agent': 'x'})
    # for i in range(1, 100):
    #    allresponses.append(r.async_request('GET', 'https://a.searx.space/dummmy/' + str(i), timeout=5.0))

    for async_response in concurrent.futures.as_completed(allresponses):
        try:
            response = async_response.result()
            print(response.request)
            print(response)
            print(response.request.url, response.status_code, response.reason, response.headers, response.cookies)
        except Exception as e:
            logger.exception(e)
        # print(v.text)
        # print(v.headers)

    print(time.time() - start_time)

    r.close()
    yappi.stop()
    pr = yappi.convert2pstats(yappi.get_func_stats())
    pr.dump_stats('curl.prof')
