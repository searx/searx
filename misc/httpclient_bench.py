from sys import path
from os.path import realpath, dirname
path.append(realpath(dirname(realpath(__file__)) + '/../'))

import sys
import gc
import aiohttp
import asyncio
import time
import uvloop
from statistics import mean, stdev
import searx.httpclient
import searx.httpclient.requests
import concurrent.futures
import logging
from searx import settings, logger

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

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'


def timed(func):
    async def wrapper(*args):
        print('<', end='')
        sys.stdout.flush()
        start = time.time()
        await func(*args)
        t = round(time.time() - start, 4)
        await asyncio.sleep(0.125)
        print('>', end='')
        sys.stdout.flush()
        return t
    return wrapper


def timed_sync(func):
    def wrapper(*args):
        start = time.time()
        func(*args)
        return round(time.time() - start, 4)
    return wrapper


async def fetch_aiohttp(session, url):
    async with session.get(url) as response:
        return await response.text()


@timed
async def main_aiohttp(urls, client_session):
    coroutines = [fetch_aiohttp(client_session, url) for url in urls]
    await asyncio.gather(*coroutines)


async def fetch_curl(async_multi_request, url):
    # print('.', end='')
    response = await async_multi_request.async_request(method='GET', url=url, timeout=3)
    # print(':', end='')
    return response.text


@timed
async def main_curl(urls, async_multi_request):
    coroutines = [fetch_curl(async_multi_request, url) for url in urls]
    await asyncio.gather(*coroutines)
    # futures = [ async_multi_request.async_request(method='GET', url=url) for url in urls ]
    # responses = await asyncio.gather(futures, return_exceptions=True)
    # print(responses)
    # texts = [response.text() for response in responses]
    # print(futures[0].result())


async def bench_aiohttp(bench_urls):
    client_session = aiohttp.ClientSession()
    try:
        print('== aiohttp ==')
        r = [await main_aiohttp(bench_urls, client_session) for i in range(10)]
        # await asyncio.sleep(30)
        r = r + [await main_aiohttp(bench_urls, client_session) for i in range(10)]
        print(f'\n--> avg={mean(r)} s. stdev={stdev(r)} s.')
        print(r)
    finally:
        await client_session.close()


async def bench_curl(bench_urls):
    print('== curl ==')
    async_multi_request = searx.httpclient.AsyncioSession()
    async_multi_request.start()
    try:
        r = [await main_curl(bench_urls, async_multi_request) for i in range(10)]
        # await asyncio.sleep(30)
        r = r + [await main_curl(bench_urls, async_multi_request) for i in range(10)]
        print(f'\n--> avg={mean(r)} s. stdev={stdev(r)} s.')
        print(r)
    finally:
        async_multi_request.close()


def main(coroutine, prof_filename):
    import yappi
    import cProfile

    profiling = False

    logging.basicConfig(level=logging.DEBUG)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    if profiling:
        yappi.start(builtins=True)
        yappi.set_clock_type("cpu")

    try:
        searx.httpclient.requests.SESSION.stop()
        loop.run_until_complete(coroutine)

        gc.collect()
    finally:
        if profiling:
            yappi.stop()
            pr = yappi.convert2pstats(yappi.get_func_stats())
            pr.dump_stats(prof_filename)
            yappi.clear_stats()

if __name__ == '__main__':
    import pycurl
    print(pycurl.version)

    bench_urls = urls1 + urls2 + urls3

    main(bench_aiohttp(bench_urls), 'aiohttp.prof')
    # main(bench_curl(bench_urls), 'curl.prof')
