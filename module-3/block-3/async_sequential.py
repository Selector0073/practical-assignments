import asyncio
import time

STUDENT = "Selector0073"


async def fake_download(url: str, delay: float) -> str:
    print(f"start {url}")
    await asyncio.sleep(delay)
    print(f"done {url}")
    return f"<content of {url}>"


async def main() -> None:
    print(f"Student: {STUDENT}")

    urls = [
        ("https://example.com/a", 3),
        ("https://example.com/b", 1),
        ("https://example.com/c", 2),
    ]

    start = time.perf_counter()
    results = []
    for url, delay in urls:
        result = await fake_download(url, delay)
        results.append(result)
    print(f"Sequential: {time.perf_counter() - start:.2f}s")


asyncio.run(main())
