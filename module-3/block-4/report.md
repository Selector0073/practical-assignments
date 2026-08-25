# Report — 39. (P19) Asynchronous Task Creation, Execution, and Management in asyncio

**Student:** Selector0073

This assignment implements two small programs that demonstrate asynchronous task
management in asyncio: choosing how to wait for a group of tasks
(`asyncio.wait` vs `asyncio.as_completed`), and working with timeouts and
cancellation (`asyncio.timeout` and manual `task.cancel()`).

The `STUDENT` constant is declared in every file and printed as the first line
of every run.

---

## Part 1 — `waiting_strategies.py`

### Implementation

The file declares the coroutine:

```python
async def fetch(name: str, delay: float) -> str
```

which prints `start {name}`, waits `delay` seconds via `asyncio.sleep`, prints
`done {name}`, and returns `f"data-{name}"`.

`main()` runs the same three tasks (delays 3, 1, 2 seconds) twice in a row:

- **Block A — `asyncio.wait(..., return_when=asyncio.FIRST_COMPLETED)`:**
  measures elapsed time with `time.perf_counter`, wakes up as soon as the
  fastest task finishes, prints its result as `first done: {result}`, cancels
  the remaining tasks with `task.cancel()`, and drains them through
  `await asyncio.gather(*pending, return_exceptions=True)` so their
  `CancelledError` does not propagate. It then prints `block A elapsed: ...`.

- **Block B — `asyncio.as_completed(...)`:**
  measures elapsed time and iterates over `for coro in asyncio.as_completed(...)`
  printing `got: {await coro}` as each task completes. It then prints
  `block B elapsed: ...`.

### Program output

```
Student: Selector0073
start task-1
start task-2
start task-3
done task-2
first done: data-task-2
block A elapsed: 1.00s
start task-3
start task-2
start task-1
done task-2
got: data-task-2
done task-3
got: data-task-3
done task-1
got: data-task-1
block B elapsed: 3.00s
```

### Why the time differs

`asyncio.wait(FIRST_COMPLETED)` returns as soon as the single fastest task
`task-2` (1s) finishes, and cancels the rest, so the whole block ends in ~1s.
`asyncio.as_completed`, by contrast, must yield every single task's result, so
the loop keeps running until the slowest task (`task-1`, 3s) completes, giving
a total of ~3s — even though both blocks run exactly the same three tasks.

---

## Part 2 — `timeouts_and_cancel.py`

### Part 2A — `asyncio.timeout`

Three argument-less coroutines `step_one` (0.5s), `step_two` (0.5s) and
`step_three` (2s) print `"step one: start"`, `"step two: start"` and
`"step three: start"` on start. They are awaited sequentially inside

```python
async with asyncio.timeout(1.5):
```

so the first two steps complete, then the 2s `step_three` is interrupted when
the 1.5s deadline fires. The raised `TimeoutError` is caught and printed as
`"timeout reached"`.

### Part 2B — manual cancellation

`worker()` increments a counter `i` and, in an infinite loop, prints
`f"tick {i}"` and sleeps 1s. Inside a `try/except asyncio.CancelledError` block
its handler prints `f"worker: cleanup after {i} ticks"` and then re-raises.

`main()` starts the worker with `create_task`, waits 2.5s, calls
`task.cancel()`, and handles the `CancelledError` raised by `await task` with
`"main: task cancelled"`.

### Program output

```
Student: Selector0073
step one: start
step two: start
step three: start
timeout reached
tick 1
tick 2
tick 3
worker: cleanup after 3 ticks
main: task cancelled
```

### What would change if `raise` were removed from the `except CancelledError` block

If `raise` were removed, the handler would swallow the `CancelledError` and the
`worker` task would finish successfully instead of being cancelled. As a
result, `await task` in `main()` would not raise `CancelledError`, so the line
`"main: task cancelled"` would not be printed, and the task would be reported as
completed rather than cancelled.
