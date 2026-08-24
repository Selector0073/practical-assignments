import asyncio

STUDENT = "Selector0073"


async def greet(name: str) -> str:
    await asyncio.sleep(1)
    return f"Hello, {name}"


async def main() -> None:
    print(f"Student: {STUDENT}")
    # Intentionally missing 'await' to reproduce the RuntimeWarning
    message = greet("asyncio")
    print(message)


asyncio.run(main())
