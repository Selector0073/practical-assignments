# Practical Assignment 41 — Debugging Asynchronous Code and Working with the Event Loop

**Student:** Stanislav Dukhnevych
**Module 3 / Block 5**
**Python:** 3.14 (Poetry virtualenv `block-5`)

---

## Overview

Two small programs were implemented to demonstrate basic asyncio debugging
skills and manual event loop management:

1. `slow_step.py` — a pipeline of three coroutines (`load`, `process`, `save`)
   that originally blocked the event loop with a synchronous `time.sleep`, and
   the fix (`asyncio.to_thread`) that removes the blocker.
2. `manual_loop.py` — manual event loop creation/management with a recurring
   `tick` task that is stopped cleanly via `Ctrl+C` (`KeyboardInterrupt`).

Both files declare `STUDENT = "Stanislav Dukhnevych"` and print it on the first
line of every run.

---

## Part 1: find and fix the slow step (`slow_step.py`)

Three coroutines were declared:

| Coroutine | Behavior |
|---|---|
| `load()` | prints `load: start`, `await asyncio.sleep(0.3)`, returns `"raw"` |
| `process()` | prints `process: start`, `time.sleep(1.2)`, returns `"clean"` |
| `save()` | prints `save: start`, `await asyncio.sleep(0.5)`, returns nothing |

The wrapper `step(name, coro)` records `time.perf_counter()`, awaits the
coroutine, and prints `[{name}] {elapsed:.2f}s`.

### Output BEFORE the fix (`slow_step_buggy.py` — original code)

The original version uses `time.sleep(1.2)` directly inside `process()`. Run
with `asyncio.run(main(), debug=True)`, asyncio's slow-callback detector fires:

```text
Executing <Task pending name='Task-1' coro=<main() running at .../slow_step_buggy.py:43>
wait_for=<Future pending ...> cb=[_run_until_complete_cb() ...] created at .../asyncio/runners.py:110>
took 1.201 seconds
Student: Stanislav Dukhnevych
load: start
[load] 0.30s
process: start
[process] 1.20s
save: start
[save] 0.50s
```

### Output AFTER the fix (`slow_step.py`)

`process()` now wraps the blocking call in `asyncio.to_thread`, so the event
loop is no longer blocked. The asyncio warning is gone:

```text
Student: Stanislav Dukhnevych
load: start
[load] 0.30s
process: start
[process] 1.20s
save: start
[save] 0.50s
```

### Why asyncio warned specifically about `process`

asyncio warned about `process` and not `load`/`save` because `load` and `save`
yield control to the loop via `await asyncio.sleep(...)` (they are truly
asynchronous and non-blocking), whereas `process` called the synchronous
`time.sleep(1.2)`, which occupies the event loop thread for 1.2 seconds without
ever yielding — blocking every other task — which debug mode detects and reports
as a slow callback taking `1.201 seconds`.

---

## Part 2: manual event loop management (`manual_loop.py`)

The `tick()` coroutine runs an infinite loop printing `tick {i}` every second
via `asyncio.sleep`, and on `CancelledError` prints `tick: stopped` and re-raises.

`main()` creates a loop with `asyncio.new_event_loop()`, registers the task with
`loop.create_task(tick())`, runs `loop.run_forever()`, and in the
`KeyboardInterrupt` handler cancels the task and drains the cancellation with
`loop.run_until_complete(task)`, finally closing the loop and printing
`loop closed`.

### Output with stop via Ctrl+C (SIGINT delivered after a few ticks)

```text
Student: Stanislav Dukhnevych
tick 1
tick 2
tick 3
tick 4
tick: stopped
loop closed
```

### Why `run_until_complete(task)` is needed after `task.cancel()`

Calling `task.cancel()` only *requests* cancellation — it schedules the
`CancelledError` to be thrown into the task the next time the loop runs, but does
not wait for the task to actually process it. `run_until_complete(task)` drives
the loop until the task finishes (i.e. until `tick` catches the cancellation,
prints `tick: stopped`, and re-raises, which finalizes the done state). If we
simply called `loop.close()` immediately after `cancel()`, the task would never
be granted a chance to run its cancellation handler, its `CancelledError` would
be left unretrieved, the loop would be closed while work is still pending (which
logs a "closing a loop with a pending task/unhandled exception" warning), and the
clean `tick: stopped` shutdown path would never execute.
