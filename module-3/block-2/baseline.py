import threading
import time
import requests

STUDENT = "Selector0073"


def download(url: str) -> None:
    name = threading.current_thread().name
    print(f"[{name}] start: {url}")
    response = requests.get(url)
    print(f"[{name}] done: {url} -> {response.status_code}, {len(response.content)} bytes")


if __name__ == "__main__":
    print(f"Student: {STUDENT}")

    urls = [
        "https://httpbin.org/delay/3",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
    ]

    threads = []

    start = time.perf_counter()
    for url in urls:
        t = threading.Thread(target=download, args=(url,))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print(f"Sequential: {time.perf_counter() - start:.2f}s")