"""Part 1 (buggy/before-fix version).

Uses time.sleep(1.2) directly inside the process() coroutine, which blocks
the event loop thread. When running with debug=True, asyncio detects the slow
callback and warns about it.
"""
import asyncio
import time

STUDENT = "Stanislav Dukhnevych"


async def load():
    print("load: start")
    await asyncio.sleep(0.3)
    return "raw"


async def process():
    print("process: start")
    # Blocking call: blocks the whole event loop thread for 1.2s.
    time.sleep(1.2)
    return "clean"


async def save():
    print("save: start")
    await asyncio.sleep(0.5)
    return None


async def step(name, coro):
    start = time.perf_counter()
    result = await coro
    elapsed = time.perf_counter() - start
    print(f"[{name}] {elapsed:.2f}s")
    return result


async def main():
    await step("load", load())
    await step("process", process())
    await step("save", save())


if __name__ == "__main__":
    print(f"Student: {STUDENT}")
    asyncio.run(main(), debug=True)
