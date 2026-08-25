"""Part 1: find and fix the slow step (fixed version).

Demonstrates why a blocking call (time.sleep) inside a coroutine stalls the
event loop, and fixes it by offloading the blocking work to a thread via
asyncio.to_thread so the loop is no longer blocked.
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
    # Blocking call: time.sleep(1.2) blocks the whole event loop thread.
    # Fix: run it in a worker thread so the loop is not blocked.
    await asyncio.to_thread(time.sleep, 1.2)
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
