"""Part 2: manual event loop management.

Creates an event loop by hand, runs a recurring tick task, and shuts the loop
down cleanly on Ctrl+C (KeyboardInterrupt) by cancelling the task and letting
it finish the cancellation before closing the loop.
"""
import asyncio

STUDENT = "Stanislav Dukhnevych"


async def tick():
    i = 1
    try:
        while True:
            print(f"tick {i}")
            i += 1
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("tick: stopped")
        raise


def main():
    loop = asyncio.new_event_loop()
    task = loop.create_task(tick())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        task.cancel()
        try:
            loop.run_until_complete(task)
        except asyncio.CancelledError:
            pass
    finally:
        loop.close()
        print("loop closed")


if __name__ == "__main__":
    print(f"Student: {STUDENT}")
    main()
