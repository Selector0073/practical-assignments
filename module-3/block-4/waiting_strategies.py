import asyncio
import time

STUDENT = "Selector0073"


async def fetch(name: str, delay: float) -> str:
    print(f"start {name}")
    await asyncio.sleep(delay)
    print(f"done {name}")
    return f"data-{name}"


async def main() -> None:
    print(f"Student: {STUDENT}")

    tasks = [
        ("task-1", 3),
        ("task-2", 1),
        ("task-3", 2),
    ]

    # ---- Block A: asyncio.wait with FIRST_COMPLETED ----
    start = time.perf_counter()

    pending = [
        asyncio.create_task(fetch(name, delay)) for name, delay in tasks
    ]
    done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

    fastest = next(iter(done))
    result = fastest.result()
    print(f"first done: {result}")

    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)

    print(f"block A elapsed: {time.perf_counter() - start:.2f}s")

    # ---- Block B: asyncio.as_completed ----
    start = time.perf_counter()

    for coro in asyncio.as_completed(
        [fetch(name, delay) for name, delay in tasks]
    ):
        print(f"got: {await coro}")

    print(f"block B elapsed: {time.perf_counter() - start:.2f}s")


asyncio.run(main())
