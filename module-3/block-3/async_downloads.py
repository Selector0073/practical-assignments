import asyncio
import time

import aiohttp

STUDENT = "Selector0073"


def build_urls() -> list[str]:
    base = "https://httpbin.org"
    return [
        f"{base}/delay/3",
        f"{base}/delay/2",
        f"{base}/delay/1",
        f"{base}/delay/2",
    ]


async def download(session: aiohttp.ClientSession, url: str) -> tuple[str, int, int]:
    print(f"start {url}")
    async with session.get(url) as response:
        content = await response.read()
        print(f"done {url} -> {response.status}, {len(content)} bytes")
        return url, response.status, len(content)


async def run_concurrent(urls: list[str]) -> float:
    start = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[download(session, url) for url in urls])
    elapsed = time.perf_counter() - start

    for url, status, size in results:
        print(f"{url}: {status}, {size} bytes")
    print(f"Concurrent: {elapsed:.2f}s")
    return elapsed


async def run_sequential(urls: list[str]) -> float:
    start = time.perf_counter()
    results = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            result = await download(session, url)
            results.append(result)
    elapsed = time.perf_counter() - start

    for url, status, size in results:
        print(f"{url}: {status}, {size} bytes")
    print(f"Sequential: {elapsed:.2f}s")
    return elapsed


async def main() -> None:
    print(f"Student: {STUDENT}")

    urls = build_urls()

    print("\n--- Sequential ---")
    await run_sequential(urls)

    print("\n--- Concurrent ---")
    await run_concurrent(urls)


asyncio.run(main())