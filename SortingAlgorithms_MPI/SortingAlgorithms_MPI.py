import random
import time
import csv
import os
from datetime import datetime


# ── Sorting algorithms ──────────────────────────────────────────────────────

def bubble_sort(arr):
    a = arr.copy()
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a


def selection_sort(arr):
    a = arr.copy()
    n = len(a)
    for i in range(n):
        min_index = i
        for j in range(i + 1, n):
            if a[j] < a[min_index]:
                min_index = j
        a[i], a[min_index] = a[min_index], a[i]
    return a


def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left   = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right  = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def insertion_sort(arr):
    a = arr.copy()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and key < a[j]:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid   = len(arr) // 2
    left  = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ── Timing helper ────────────────────────────────────────────────────────────

MIN_BENCH_SECONDS = 0.05
MAX_REPS          = 100_000


def measure(sort_fn, data):
   
    reps = 1
    t0 = time.perf_counter()
    sort_fn(data)
    elapsed = time.perf_counter() - t0

    if elapsed < MIN_BENCH_SECONDS:
        reps = min(MAX_REPS, max(1, int(MIN_BENCH_SECONDS / elapsed) + 1))

    # Actual timed run
    t0 = time.perf_counter()
    for _ in range(reps):
        sort_fn(data)
    total = time.perf_counter() - t0

    return total / reps          # average time for ONE call


# ── File logging ─────────────────────────────────────────────────────────────

LOG_FILE = "sort_results.csv"
FIELDNAMES = ["timestamp", "n", "algorithm", "avg_time_sec"]


def save_results(n, results: dict):
    """Append one row per algorithm to the CSV log file."""
    file_exists = os.path.isfile(LOG_FILE)
    timestamp   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()          # write header only once
        for algo, t in results.items():
            writer.writerow({
                "timestamp"   : timestamp,
                "n"           : n,
                "algorithm"   : algo,
                "avg_time_sec": SKIPPED_MARKER if t == SKIPPED_MARKER else f"{t:.10f}",
            })

    print(f"\n✔  Results appended to '{LOG_FILE}'")


# ── Skip thresholds ──────────────────────────────────────────────────────────
# If n exceeds an algorithm's limit it is skipped with an explanation instead
# of running for minutes.  Tweak these values to match your machine.

SKIP_THRESHOLDS = {
    #  algorithm      max n before skipping    reason shown to the user
    "Bubble"   : (10_000,  "O(n²) — would take several minutes for large n"),
    "Selection": (10_000,  "O(n²) — would take several minutes for large n"),
    "Insertion": (50_000,  "O(n²) — acceptable up to ~50 k, too slow beyond"),
    # Quick and Merge have no practical limit for typical inputs
}

SKIPPED_MARKER = "SKIPPED"   # stored in CSV so the row is still recorded


# ── Main ─────────────────────────────────────────────────────────────────────

def random_list(n):
    return [random.randint(0, 100_000) for _ in range(n)]


def main():
    n = int(input("Enter number of elements: "))
    data = random_list(n)

    algorithms = {
        "Bubble"   : bubble_sort,
        "Selection": selection_sort,
        "Quick"    : quick_sort,
        "Insertion": insertion_sort,
        "Merge"    : merge_sort,
    }

    print(f"\n{'Algorithm':<12}  {'Avg time (s)':>18}   {'Formatted':>14}")
    print("-" * 50)

    results = {}
    for name, fn in algorithms.items():

        # ── Check skip threshold ─────────────────────────────────────────────
        if name in SKIP_THRESHOLDS:
            limit, reason = SKIP_THRESHOLDS[name]
            if n > limit:
                print(f"{name:<12}  {'--- SKIPPED ---':>18} {reason}")
                results[name] = SKIPPED_MARKER
                continue

        # ── Run & time ───────────────────────────────────────────────────────
        t = measure(fn, data)
        results[name] = t

        # Pick the most readable unit
        if t < 1e-6:
            formatted = f"{t * 1e9:>10.4f} ns"
        elif t < 1e-3:
            formatted = f"{t * 1e6:>10.4f} µs"
        elif t < 1:
            formatted = f"{t * 1e3:>10.4f} ms"
        else:
            formatted = f"{t:>10.4f}  s"

        print(f"{name:<12}  {t:>18.10f}   {formatted}")

    save_results(n, results)


if __name__ == "__main__":
    main()
