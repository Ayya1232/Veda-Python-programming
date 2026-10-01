"""
Task 24: Compare Threading, Multiprocessing, and AsyncIO

Two workloads, each run with all three approaches plus a sequential baseline:
  1. I/O-bound  : 10 simulated network calls (each waits 1 second)
  2. CPU-bound  : 4 heavy computations (sum of squares up to 20 million)

Expected pattern:
  I/O-bound  -> threading and asyncio win big; multiprocessing works but has overhead
  CPU-bound  -> multiprocessing wins; threading/asyncio give no speedup (GIL)
"""

import asyncio
import os
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

IO_TASKS = 10
IO_DELAY = 1.0
CPU_TASKS = 4
CPU_N = 20_000_000


# ---------------------------------------------------------------- workloads
def io_task(_):
    """Simulates a blocking I/O call (network request, disk read, DB query)."""
    time.sleep(IO_DELAY)


async def io_task_async(_):
    """Same simulated I/O, but using a non-blocking sleep."""
    await asyncio.sleep(IO_DELAY)


def cpu_task(n):
    """Pure computation: keeps the CPU busy and holds the GIL."""
    return sum(i * i for i in range(n))


# ------------------------------------------------------------- I/O runners
def io_sequential():
    for i in range(IO_TASKS):
        io_task(i)


def io_threading():
    with ThreadPoolExecutor(max_workers=IO_TASKS) as ex:
        list(ex.map(io_task, range(IO_TASKS)))


def io_multiprocessing():
    with ProcessPoolExecutor(max_workers=IO_TASKS) as ex:
        list(ex.map(io_task, range(IO_TASKS)))


def io_asyncio():
    async def main():
        await asyncio.gather(*(io_task_async(i) for i in range(IO_TASKS)))

    asyncio.run(main())


# ------------------------------------------------------------ CPU runners
def cpu_sequential():
    for _ in range(CPU_TASKS):
        cpu_task(CPU_N)


def cpu_threading():
    with ThreadPoolExecutor(max_workers=CPU_TASKS) as ex:
        list(ex.map(cpu_task, [CPU_N] * CPU_TASKS))


def cpu_multiprocessing():
    with ProcessPoolExecutor(max_workers=CPU_TASKS) as ex:
        list(ex.map(cpu_task, [CPU_N] * CPU_TASKS))


def cpu_asyncio():
    # asyncio is single-threaded: CPU work blocks the event loop,
    # so "concurrent" coroutines still run one after another.
    async def worker(n):
        return cpu_task(n)

    async def main():
        await asyncio.gather(*(worker(CPU_N) for _ in range(CPU_TASKS)))

    asyncio.run(main())


# ----------------------------------------------------------------- harness
def timed(fn):
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def report(title, runners):
    print(f"\n=== {title} ===")
    results = {name: timed(fn) for name, fn in runners.items()}
    baseline = results["sequential"]
    print(f"{'approach':<16}{'time (s)':>10}{'speedup':>10}")
    print("-" * 36)
    for name, t in results.items():
        print(f"{name:<16}{t:>10.2f}{baseline / t:>9.2f}x")


if __name__ == "__main__":
    print(f"CPU cores available: {os.cpu_count()}")

    report(
        f"I/O-bound: {IO_TASKS} tasks x {IO_DELAY}s wait",
        {
            "sequential": io_sequential,
            "threading": io_threading,
            "multiprocessing": io_multiprocessing,
            "asyncio": io_asyncio,
        },
    )

    report(
        f"CPU-bound: {CPU_TASKS} tasks x sum of squares to {CPU_N:,}",
        {
            "sequential": cpu_sequential,
            "threading": cpu_threading,
            "multiprocessing": cpu_multiprocessing,
            "asyncio": cpu_asyncio,
        },
    )