import threading
import time


STUDENT = "Selector0073"


def download(url: str, delay: float) -> None:
    name = threading.current_thread().name
    print(f"[{name}] Завантаження: {url}")
    time.sleep(delay)
    print(f"[{name}] Готово: {url}")


urls = [
    ("https://example.com/file1", 3),
    ("https://example.com/file2", 1),
    ("https://example.com/file3", 2),
]

start = time.perf_counter()
print(f"Student: {STUDENT}")
for url, delay in urls:
    download(url, delay)
print(f"Послідовно: {time.perf_counter() - start:.2f}с\n")

start = time.perf_counter()

threads = []
print(f"Student: {STUDENT}")
for i, (url, delay) in enumerate(urls, start=1):
    t = threading.Thread(
        target=download,
        args=(url, delay),
        name=f"downloader-{i}",
    )
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

print(f"Потоки: {time.perf_counter() - start:.2f}с")