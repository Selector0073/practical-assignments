import asyncio

STUDENT = "Selector0073"


# ---------- Part 2A: asyncio.timeout ----------

async def step_one() -> None:
    print("step one: start")
    await asyncio.sleep(0.5)


async def step_two() -> None:
    print("step two: start")
    await asyncio.sleep(0.5)


async def step_three() -> None:
    print("step three: start")
    await asyncio.sleep(2)


async def demo_timeout() -> None:
    try:
        async with asyncio.timeout(1.5):
            await step_one()
            await step_two()
            await step_three()
    except TimeoutError:
        print("timeout reached")


# ---------- Part 2B: manual cancellation ----------

async def worker() -> None:
    i = 0
    try:
        while True:
            i += 1
            print(f"tick {i}")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print(f"worker: cleanup after {i} ticks")
        raise


async def demo_cancel() -> None:
    task = asyncio.create_task(worker())
    await asyncio.sleep(2.5)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("main: task cancelled")


async def main() -> None:
    print(f"Student: {STUDENT}")
    await demo_timeout()
    await demo_cancel()


asyncio.run(main())
