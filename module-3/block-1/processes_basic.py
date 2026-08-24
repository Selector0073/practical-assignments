import multiprocessing
import threading
import time


STUDENT = "Selector0073"


def compute(n: int) -> None:
    result = sum(i * i for i in range(n))
    name = multiprocessing.current_process().name
    print(f"[{name}] sum of squares(0..{n}) = {result}")


if __name__ == "__main__":
    tasks = [10_000_000, 8_000_000, 12_000_000]

    print(f"Student: {STUDENT}")
    start = time.perf_counter()
    for n in tasks:
        compute(n)
    seq_time = time.perf_counter() - start
    print(f"Послідовно: {seq_time:.2f}с\n")

    start = time.perf_counter()

    print(f"Student: {STUDENT}")
    threads = [
        threading.Thread(target=compute, args=(n,), name=f"thread-{i}")
        for i, n in enumerate(tasks, start=1)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    threads_time = time.perf_counter() - start
    print(f"Потоки: {threads_time:.2f}с\n")

    start = time.perf_counter()

    processes = [
        multiprocessing.Process(target=compute, args=(n,), name=f"process-{i}")
        for i, n in enumerate(tasks, start=1)
    ]
    print(f"Student: {STUDENT}")
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    processes_time = time.perf_counter() - start
    print(f"Процеси: {processes_time:.2f}с\n")

    print(f"Student: {STUDENT}")
    print("Порівняльна таблиця (CPU-bound задача):")
    print(f"{'Варіант':<15}{'Час, с':>10}")
    print(f"{'Послідовно':<15}{seq_time:>10.2f}")
    print(f"{'Потоки':<15}{threads_time:>10.2f}")
    print(f"{'Процеси':<15}{processes_time:>10.2f}")