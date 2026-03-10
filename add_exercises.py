#!/usr/bin/env python3
"""
add_exercises.py  –  Append 3 DataCampExercise blocks to every .md tutorial
                     that does NOT already contain a DataCampExercise section.
Converts the file to .mdx in-place (renames + writes new content).
Idempotent: skips any file that already has 'DataCampExercise' in it.
"""

import os, re, textwrap

ROOT = "src/content/docs"

# ── depth-aware relative import path helper ──────────────────────────────────
def import_path(md_path: str) -> str:
    """Return the relative path to DataCampExercise.astro from the mdx file."""
    depth = md_path.replace("\\", "/").count("/") - ROOT.count("/") - 1
    return "../" * depth + "components/DataCampExercise.astro"

# ── exercise catalogue  (topic_key → list of 3+ exercise dicts) ──────────────
# Each dict:  title, hint, code (triple-quoted python), solution, sct, height
# ──────────────────────────────────────────────────────────────────────────────
EXERCISES: dict[str, list[dict]] = {}

# ============================================================
# PYTHON TUTORIALS – Threading
# ============================================================
EXERCISES["threading-in-python"] = [
    dict(
        title="Exercise 1 – Create a Simple Thread",
        hint="Use `threading.Thread(target=fn)` then call `.start()`.",
        code='''\
# Task: Exercise 1 – Create a Simple Thread
# Follow the steps below and fill in the blanks.
# Hint: import the threading module first.
import ___  # replace ___ with the module name

def greet():
    print("Hello from a thread!")

# Hint: create a Thread object with target=greet
t = threading.___(target=greet)  # replace ___ with Thread
# Step: start the thread
t.___()  # replace ___ with the correct method

# ── Expected Output ───────────────────────────────────────────
# Hello from a thread!
# ──────────────────────────────────────────────────────────────''',
        solution='import threading\n\ndef greet():\n    print("Hello from a thread!")\n\nt = threading.Thread(target=greet)\nt.start()',
        sct='test_output_contains("Hello from a thread!")\nsuccess_msg("Thread created and started!")',
        height=150,
    ),
    dict(
        title="Exercise 2 – Join a Thread",
        hint="Call `.join()` on the thread to wait for it to finish.",
        code='''\
# Task: Exercise 2 – Join a Thread
import threading
import time

def slow_task():
    time.sleep(0.1)
    print("Task done")

t = threading.Thread(target=slow_task)
t.start()
# Hint: use .join() so the main thread waits
t.___()  # replace ___ with the correct method
print("Main thread continues")

# ── Expected Output ───────────────────────────────────────────
# Task done
# Main thread continues
# ──────────────────────────────────────────────────────────────''',
        solution='import threading\nimport time\n\ndef slow_task():\n    time.sleep(0.1)\n    print("Task done")\n\nt = threading.Thread(target=slow_task)\nt.start()\nt.join()\nprint("Main thread continues")',
        sct='test_output_contains("Task done")\ntest_output_contains("Main thread continues")\nsuccess_msg("join() keeps things in order!")',
        height=140,
    ),
    dict(
        title="Exercise 3 – Run Multiple Threads",
        hint="Loop to create 3 threads, start each, then join each.",
        code='''\
# Task: Exercise 3 – Run Multiple Threads
import threading

def show(n):
    print(f"Thread {n} running")

threads = []
# Hint: create 3 threads for n in range(3)
for n in range(___):  # replace ___ with 3
    t = threading.Thread(target=show, args=(n,))
    threads.append(t)
    t.start()

for t in threads:
    t.___()  # replace ___ with join

# ── Expected Output (order may vary) ──────────────────────────
# Thread 0 running
# Thread 1 running
# Thread 2 running
# ──────────────────────────────────────────────────────────────''',
        solution='import threading\n\ndef show(n):\n    print(f"Thread {n} running")\n\nthreads = []\nfor n in range(3):\n    t = threading.Thread(target=show, args=(n,))\n    threads.append(t)\n    t.start()\nfor t in threads:\n    t.join()',
        sct='test_output_contains("Thread 0 running")\ntest_output_contains("Thread 2 running")\nsuccess_msg("Multiple threads launched!")',
        height=160,
    ),
]

EXERCISES["creating-and-starting-threads"] = EXERCISES["threading-in-python"]

EXERCISES["thread-synchronization-with-lock"] = [
    dict(
        title="Exercise 1 – Basic Lock Usage",
        hint="Use `lock.acquire()` before and `lock.release()` after the critical section.",
        code='''\
# Task: Exercise 1 – Basic Lock Usage
import threading

lock = threading.Lock()
counter = 0

def increment():
    global counter
    lock.___()          # replace ___ with acquire
    counter += 1
    lock.___()          # replace ___ with release

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()
print("Counter:", counter)

# ── Expected Output ───────────────────────────────────────────
# Counter: 5
# ──────────────────────────────────────────────────────────────''',
        solution='import threading\n\nlock = threading.Lock()\ncounter = 0\n\ndef increment():\n    global counter\n    lock.acquire()\n    counter += 1\n    lock.release()\n\nthreads = [threading.Thread(target=increment) for _ in range(5)]\nfor t in threads: t.start()\nfor t in threads: t.join()\nprint("Counter:", counter)',
        sct='test_output_contains("Counter: 5")\nsuccess_msg("Lock prevents race conditions!")',
        height=160,
    ),
    dict(
        title="Exercise 2 – Lock as Context Manager",
        hint="Use `with lock:` to automatically acquire and release.",
        code='''\
# Task: Exercise 2 – Lock as Context Manager
import threading

lock = threading.Lock()
total = 0

def add(n):
    global total
    # Hint: use `with lock:` instead of acquire/release
    ___ lock:           # replace ___ with with
        total += n

threads = [threading.Thread(target=add, args=(i,)) for i in range(5)]
for t in threads: t.start()
for t in threads: t.join()
print("Total:", total)

# ── Expected Output ───────────────────────────────────────────
# Total: 10
# ──────────────────────────────────────────────────────────────''',
        solution='import threading\n\nlock = threading.Lock()\ntotal = 0\n\ndef add(n):\n    global total\n    with lock:\n        total += n\n\nthreads = [threading.Thread(target=add, args=(i,)) for i in range(5)]\nfor t in threads: t.start()\nfor t in threads: t.join()\nprint("Total:", total)',
        sct='test_output_contains("Total: 10")\nsuccess_msg("with lock: is cleaner and safer!")',
        height=150,
    ),
    dict(
        title="Exercise 3 – Detect Locked State",
        hint="Use `lock.locked()` to check whether a lock is held.",
        code='''\
# Task: Exercise 3 – Detect Locked State
import threading

lock = threading.Lock()

# Before acquiring
print("Locked before acquire:", lock.___())   # replace ___ with locked

with lock:
    print("Locked inside with:", lock.___())  # replace ___ with locked

print("Locked after release:", lock.___())    # replace ___ with locked

# ── Expected Output ───────────────────────────────────────────
# Locked before acquire: False
# Locked inside with: True
# Locked after release: False
# ──────────────────────────────────────────────────────────────''',
        solution='import threading\n\nlock = threading.Lock()\nprint("Locked before acquire:", lock.locked())\nwith lock:\n    print("Locked inside with:", lock.locked())\nprint("Locked after release:", lock.locked())',
        sct='test_output_contains("False")\ntest_output_contains("True")\nsuccess_msg("locked() tells you the state!")',
        height=150,
    ),
]

EXERCISES["daemon-threads"] = [
    dict(
        title="Exercise 1 – Create a Daemon Thread",
        hint="Set `daemon=True` in `threading.Thread()`.",
        code='''\
# Task: Exercise 1 – Create a Daemon Thread
import threading, time

def background():
    while True:
        time.sleep(0.5)
        print("Daemon tick")

# Hint: pass daemon=True to make it a daemon thread
t = threading.Thread(target=background, ___=True)  # replace ___ with daemon
t.start()
print("Daemon started:", t.is_daemon())

# ── Expected Output ───────────────────────────────────────────
# Daemon started: True
# ──────────────────────────────────────────────────────────────''',
        solution='import threading, time\n\ndef background():\n    while True:\n        time.sleep(0.5)\n        print("Daemon tick")\n\nt = threading.Thread(target=background, daemon=True)\nt.start()\nprint("Daemon started:", t.is_daemon())',
        sct='test_output_contains("Daemon started: True")\nsuccess_msg("Daemon thread set correctly!")',
        height=140,
    ),
    dict(
        title="Exercise 2 – Non-Daemon vs Daemon",
        hint="Check `is_daemon()` on both a normal and a daemon thread.",
        code='''\
# Task: Exercise 2 – Non-Daemon vs Daemon
import threading

def task(): pass

normal = threading.Thread(target=task)
daemon = threading.Thread(target=task, daemon=True)

print("normal is_daemon:", normal.___())   # replace ___ with is_daemon
print("daemon is_daemon:", daemon.___())   # replace ___ with is_daemon

# ── Expected Output ───────────────────────────────────────────
# normal is_daemon: False
# daemon is_daemon: True
# ──────────────────────────────────────────────────────────────''',
        solution='import threading\n\ndef task(): pass\n\nnormal = threading.Thread(target=task)\ndaemon = threading.Thread(target=task, daemon=True)\nprint("normal is_daemon:", normal.is_daemon())\nprint("daemon is_daemon:", daemon.is_daemon())',
        sct='test_output_contains("normal is_daemon: False")\ntest_output_contains("daemon is_daemon: True")\nsuccess_msg("You know the difference!")',
        height=130,
    ),
    dict(
        title="Exercise 3 – Main Thread is Not a Daemon",
        hint="Use `threading.main_thread().daemon` to check the main thread.",
        code='''\
# Task: Exercise 3 – Main Thread is Not a Daemon
import threading

main = threading.main_thread()
# Hint: access the .daemon attribute
print("Main thread daemon:", main.___)  # replace ___ with daemon
print("Main thread name:", main.___)    # replace ___ with name

# ── Expected Output ───────────────────────────────────────────
# Main thread daemon: False
# Main thread name: MainThread
# ──────────────────────────────────────────────────────────────''',
        solution='import threading\n\nmain = threading.main_thread()\nprint("Main thread daemon:", main.daemon)\nprint("Main thread name:", main.name)',
        sct='test_output_contains("Main thread daemon: False")\ntest_output_contains("MainThread")\nsuccess_msg("Main thread is never a daemon!")',
        height=130,
    ),
]

EXERCISES["thread-communication-queue"] = [
    dict(
        title="Exercise 1 – Put and Get",
        hint="Use `q.put(item)` to enqueue and `q.get()` to dequeue.",
        code='''\
# Task: Exercise 1 – Put and Get
import queue

q = queue.Queue()
# Hint: put items into the queue
q.___("apple")    # replace ___ with put
q.___("banana")   # replace ___ with put

# Hint: get items from the queue (FIFO order)
print(q.___())    # replace ___ with get
print(q.___())    # replace ___ with get

# ── Expected Output ───────────────────────────────────────────
# apple
# banana
# ──────────────────────────────────────────────────────────────''',
        solution='import queue\n\nq = queue.Queue()\nq.put("apple")\nq.put("banana")\nprint(q.get())\nprint(q.get())',
        sct='test_output_contains("apple")\ntest_output_contains("banana")\nsuccess_msg("Queue works FIFO!")',
        height=140,
    ),
    dict(
        title="Exercise 2 – Producer-Consumer",
        hint="Producer calls `q.put(i)`, consumer calls `q.get()`.",
        code='''\
# Task: Exercise 2 – Producer-Consumer
import threading, queue

q = queue.Queue()

def producer():
    for i in range(3):
        q.___(i)              # replace ___ with put

def consumer():
    for _ in range(3):
        item = q.___()        # replace ___ with get
        print("Got:", item)

t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
t1.join(); t2.join()

# ── Expected Output ───────────────────────────────────────────
# Got: 0
# Got: 1
# Got: 2
# ──────────────────────────────────────────────────────────────''',
        solution='import threading, queue\n\nq = queue.Queue()\n\ndef producer():\n    for i in range(3):\n        q.put(i)\n\ndef consumer():\n    for _ in range(3):\n        item = q.get()\n        print("Got:", item)\n\nt1 = threading.Thread(target=producer)\nt2 = threading.Thread(target=consumer)\nt1.start(); t2.start()\nt1.join(); t2.join()',
        sct='test_output_contains("Got: 0")\ntest_output_contains("Got: 2")\nsuccess_msg("Producer-consumer pattern works!")',
        height=165,
    ),
    dict(
        title="Exercise 3 – Queue Size",
        hint="Use `q.qsize()` to check how many items are waiting.",
        code='''\
# Task: Exercise 3 – Queue Size
import queue

q = queue.Queue()
for item in ["x", "y", "z"]:
    q.put(item)

# Hint: qsize() returns the number of items in the queue
print("Size:", q.___())   # replace ___ with qsize
q.get()
print("After get:", q.___())  # replace ___ with qsize

# ── Expected Output ───────────────────────────────────────────
# Size: 3
# After get: 2
# ──────────────────────────────────────────────────────────────''',
        solution='import queue\n\nq = queue.Queue()\nfor item in ["x", "y", "z"]:\n    q.put(item)\nprint("Size:", q.qsize())\nq.get()\nprint("After get:", q.qsize())',
        sct='test_output_contains("Size: 3")\ntest_output_contains("After get: 2")\nsuccess_msg("qsize() tracks the queue!")',
        height=140,
    ),
]

EXERCISES["thread-pool-with-concurrentfutures"] = [
    dict(
        title="Exercise 1 – Submit a Task",
        hint="Use `executor.submit(fn, arg)` and `.result()` to get the return value.",
        code='''\
# Task: Exercise 1 – Submit a Task
from concurrent.futures import ThreadPoolExecutor

def square(n):
    return n * n

# Hint: create an executor with max_workers=2
with ThreadPoolExecutor(max_workers=___) as ex:   # replace ___ with 2
    future = ex.___(square, 5)                     # replace ___ with submit
    print("Result:", future.___())                 # replace ___ with result

# ── Expected Output ───────────────────────────────────────────
# Result: 25
# ──────────────────────────────────────────────────────────────''',
        solution='from concurrent.futures import ThreadPoolExecutor\n\ndef square(n):\n    return n * n\n\nwith ThreadPoolExecutor(max_workers=2) as ex:\n    future = ex.submit(square, 5)\n    print("Result:", future.result())',
        sct='test_output_contains("Result: 25")\nsuccess_msg("ThreadPoolExecutor submit works!")',
        height=145,
    ),
    dict(
        title="Exercise 2 – Map Over a List",
        hint="Use `executor.map(fn, iterable)` to apply a function to each item.",
        code='''\
# Task: Exercise 2 – Map Over a List
from concurrent.futures import ThreadPoolExecutor

def double(n):
    return n * 2

with ThreadPoolExecutor(max_workers=3) as ex:
    # Hint: map applies double to each number in the list
    results = list(ex.___(double, [1, 2, 3, 4]))  # replace ___ with map
    print(results)

# ── Expected Output ───────────────────────────────────────────
# [2, 4, 6, 8]
# ──────────────────────────────────────────────────────────────''',
        solution='from concurrent.futures import ThreadPoolExecutor\n\ndef double(n):\n    return n * 2\n\nwith ThreadPoolExecutor(max_workers=3) as ex:\n    results = list(ex.map(double, [1, 2, 3, 4]))\n    print(results)',
        sct='test_output_contains("[2, 4, 6, 8]")\nsuccess_msg("map() is great for batch tasks!")',
        height=140,
    ),
    dict(
        title="Exercise 3 – Check Future Done",
        hint="Use `future.done()` to check if the task has completed.",
        code='''\
# Task: Exercise 3 – Check Future Done
from concurrent.futures import ThreadPoolExecutor

def greet(name):
    return f"Hello, {name}!"

with ThreadPoolExecutor(max_workers=1) as ex:
    f = ex.submit(greet, "World")
    # Force completion before checking
    msg = f.result()
    print("Done:", f.___())   # replace ___ with done
    print(msg)

# ── Expected Output ───────────────────────────────────────────
# Done: True
# Hello, World!
# ──────────────────────────────────────────────────────────────''',
        solution='from concurrent.futures import ThreadPoolExecutor\n\ndef greet(name):\n    return f"Hello, {name}!"\n\nwith ThreadPoolExecutor(max_workers=1) as ex:\n    f = ex.submit(greet, "World")\n    msg = f.result()\n    print("Done:", f.done())\n    print(msg)',
        sct='test_output_contains("Done: True")\ntest_output_contains("Hello, World!")\nsuccess_msg("Futures track completion!")',
        height=150,
    ),
]

# ============================================================
# PYTHON TUTORIALS – Errors and Exceptions
# ============================================================
# Slug alias for alternate filename encoding
EXERCISES["thread-pool-with-concurrent-futures"] = EXERCISES["thread-pool-with-concurrentfutures"]
EXERCISES["errors-and-exceptions"] = [
    dict(
        title="Exercise 1 – Catch a ValueError",
        hint="Wrap the int() call in a try/except ValueError block.",
        code='''\
# Task: Exercise 1 – Catch a ValueError
# Hint: use try/except to handle the error gracefully
___:                              # replace ___ with try
    num = int("not_a_number")
    print("Converted:", num)
___ ValueError:                   # replace ___ with except
    print("Caught a ValueError!")

# ── Expected Output ───────────────────────────────────────────
# Caught a ValueError!
# ──────────────────────────────────────────────────────────────''',
        solution='try:\n    num = int("not_a_number")\n    print("Converted:", num)\nexcept ValueError:\n    print("Caught a ValueError!")',
        sct='test_output_contains("Caught a ValueError!")\nsuccess_msg("ValueError caught successfully!")',
        height=130,
    ),
    dict(
        title="Exercise 2 – Multiple Except Blocks",
        hint="Add a separate `except ZeroDivisionError` clause.",
        code='''\
# Task: Exercise 2 – Multiple Except Blocks
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Cannot divide by zero"
    except ___:                 # replace ___ with TypeError
        return "Invalid types"

print(safe_divide(10, 0))
print(safe_divide(10, "x"))

# ── Expected Output ───────────────────────────────────────────
# Cannot divide by zero
# Invalid types
# ──────────────────────────────────────────────────────────────''',
        solution='def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return "Cannot divide by zero"\n    except TypeError:\n        return "Invalid types"\n\nprint(safe_divide(10, 0))\nprint(safe_divide(10, "x"))',
        sct='test_output_contains("Cannot divide by zero")\ntest_output_contains("Invalid types")\nsuccess_msg("Multiple except blocks work!")',
        height=150,
    ),
    dict(
        title="Exercise 3 – Raise a Custom Exception",
        hint="Use `raise ValueError(message)` inside an if block.",
        code='''\
# Task: Exercise 3 – Raise a Custom Exception
def check_age(age):
    if age < 0:
        # Hint: raise a ValueError with a message
        ___ ValueError("Age cannot be negative")  # replace ___ with raise
    return f"Age is {age}"

try:
    print(check_age(-5))
except ValueError as e:
    print("Error:", e)

# ── Expected Output ───────────────────────────────────────────
# Error: Age cannot be negative
# ──────────────────────────────────────────────────────────────''',
        solution='def check_age(age):\n    if age < 0:\n        raise ValueError("Age cannot be negative")\n    return f"Age is {age}"\n\ntry:\n    print(check_age(-5))\nexcept ValueError as e:\n    print("Error:", e)',
        sct='test_output_contains("Error: Age cannot be negative")\nsuccess_msg("raise creates custom errors!")',
        height=150,
    ),
]

EXERCISES["try-except"] = EXERCISES["errors-and-exceptions"]

EXERCISES["else-finally"] = [
    dict(
        title="Exercise 1 – The else Clause",
        hint="The `else` block runs only when no exception is raised.",
        code='''\
# Task: Exercise 1 – The else Clause
try:
    result = 10 / 2
except ZeroDivisionError:
    print("Division error")
___:                        # replace ___ with else
    print("Result:", result)

# ── Expected Output ───────────────────────────────────────────
# Result: 5.0
# ──────────────────────────────────────────────────────────────''',
        solution='try:\n    result = 10 / 2\nexcept ZeroDivisionError:\n    print("Division error")\nelse:\n    print("Result:", result)',
        sct='test_output_contains("Result: 5.0")\nsuccess_msg("else runs when no exception occurs!")',
        height=120,
    ),
    dict(
        title="Exercise 2 – The finally Clause",
        hint="`finally` always runs, even if an exception occurred.",
        code='''\
# Task: Exercise 2 – The finally Clause
def read_data():
    try:
        data = int("bad")
    except ValueError:
        print("Could not parse")
    ___:                     # replace ___ with finally
        print("Cleanup done")

read_data()

# ── Expected Output ───────────────────────────────────────────
# Could not parse
# Cleanup done
# ──────────────────────────────────────────────────────────────''',
        solution='def read_data():\n    try:\n        data = int("bad")\n    except ValueError:\n        print("Could not parse")\n    finally:\n        print("Cleanup done")\n\nread_data()',
        sct='test_output_contains("Could not parse")\ntest_output_contains("Cleanup done")\nsuccess_msg("finally always executes!")',
        height=140,
    ),
    dict(
        title="Exercise 3 – else + finally Together",
        hint="Use all four clauses: try / except / else / finally.",
        code='''\
# Task: Exercise 3 – else + finally Together
def process(n):
    try:
        result = 100 / n
    except ZeroDivisionError:
        print("Error: zero divisor")
    ___:                        # replace ___ with else
        print("OK:", result)
    ___:                        # replace ___ with finally
        print("Always runs")

process(4)

# ── Expected Output ───────────────────────────────────────────
# OK: 25.0
# Always runs
# ──────────────────────────────────────────────────────────────''',
        solution='def process(n):\n    try:\n        result = 100 / n\n    except ZeroDivisionError:\n        print("Error: zero divisor")\n    else:\n        print("OK:", result)\n    finally:\n        print("Always runs")\n\nprocess(4)',
        sct='test_output_contains("OK: 25.0")\ntest_output_contains("Always runs")\nsuccess_msg("All four clauses mastered!")',
        height=155,
    ),
]

EXERCISES["raise-and-custom-exceptions"] = [
    dict(
        title="Exercise 1 – Raise a Built-in Exception",
        hint="Use `raise TypeError(message)` to signal wrong input.",
        code='''\
# Task: Exercise 1 – Raise a Built-in Exception
def greet(name):
    if not isinstance(name, str):
        # Hint: raise a TypeError
        ___ TypeError("name must be a string")   # replace ___ with raise
    return f"Hello, {name}!"

try:
    print(greet(42))
except TypeError as e:
    print("TypeError:", e)

# ── Expected Output ───────────────────────────────────────────
# TypeError: name must be a string
# ──────────────────────────────────────────────────────────────''',
        solution='def greet(name):\n    if not isinstance(name, str):\n        raise TypeError("name must be a string")\n    return f"Hello, {name}!"\n\ntry:\n    print(greet(42))\nexcept TypeError as e:\n    print("TypeError:", e)',
        sct='test_output_contains("TypeError: name must be a string")\nsuccess_msg("TypeError raised correctly!")',
        height=145,
    ),
    dict(
        title="Exercise 2 – Define a Custom Exception",
        hint="Subclass `Exception` to create your own exception class.",
        code='''\
# Task: Exercise 2 – Define a Custom Exception
# Hint: inherit from Exception
class NegativeBalanceError(___):   # replace ___ with Exception
    pass

def withdraw(balance, amount):
    if amount > balance:
        raise NegativeBalanceError("Insufficient funds")
    return balance - amount

try:
    withdraw(50, 100)
except NegativeBalanceError as e:
    print("Custom error:", e)

# ── Expected Output ───────────────────────────────────────────
# Custom error: Insufficient funds
# ──────────────────────────────────────────────────────────────''',
        solution='class NegativeBalanceError(Exception):\n    pass\n\ndef withdraw(balance, amount):\n    if amount > balance:\n        raise NegativeBalanceError("Insufficient funds")\n    return balance - amount\n\ntry:\n    withdraw(50, 100)\nexcept NegativeBalanceError as e:\n    print("Custom error:", e)',
        sct='test_output_contains("Custom error: Insufficient funds")\nsuccess_msg("Custom exception created!")',
        height=155,
    ),
    dict(
        title="Exercise 3 – Re-raise an Exception",
        hint="Use bare `raise` inside an except block to re-raise the current exception.",
        code='''\
# Task: Exercise 3 – Re-raise an Exception
def parse(value):
    try:
        return int(value)
    except ValueError:
        print("Logging: could not parse", value)
        ___      # replace ___ with raise  (re-raise the same exception)

try:
    parse("abc")
except ValueError:
    print("Handled at top level")

# ── Expected Output ───────────────────────────────────────────
# Logging: could not parse abc
# Handled at top level
# ──────────────────────────────────────────────────────────────''',
        solution='def parse(value):\n    try:\n        return int(value)\n    except ValueError:\n        print("Logging: could not parse", value)\n        raise\n\ntry:\n    parse("abc")\nexcept ValueError:\n    print("Handled at top level")',
        sct='test_output_contains("Logging: could not parse abc")\ntest_output_contains("Handled at top level")\nsuccess_msg("Re-raise propagates exceptions!")',
        height=155,
    ),
]

EXERCISES["debugging-tracebacks"] = [
    dict(
        title="Exercise 1 – Read a Traceback",
        hint="The last line of a traceback tells you the exception type and message.",
        code='''\
# Task: Exercise 1 – Read a Traceback
# This code raises an exception. Catch it and print its type and message.
def broken():
    return 1 / 0

try:
    broken()
except ___ as e:                   # replace ___ with ZeroDivisionError
    print("Type:", type(e).__name__)
    print("Message:", e)

# ── Expected Output ───────────────────────────────────────────
# Type: ZeroDivisionError
# Message: division by zero
# ──────────────────────────────────────────────────────────────''',
        solution='def broken():\n    return 1 / 0\n\ntry:\n    broken()\nexcept ZeroDivisionError as e:\n    print("Type:", type(e).__name__)\n    print("Message:", e)',
        sct='test_output_contains("Type: ZeroDivisionError")\ntest_output_contains("Message: division by zero")\nsuccess_msg("You can read tracebacks!")',
        height=145,
    ),
    dict(
        title="Exercise 2 – Traceback Module",
        hint="Use `traceback.print_exc()` to print a full traceback from within an except block.",
        code='''\
# Task: Exercise 2 – Traceback Module
import traceback

def risky():
    raise RuntimeError("Something broke")

try:
    risky()
except RuntimeError:
    # Hint: print the full traceback
    traceback.___()    # replace ___ with print_exc

# ── Expected Output ───────────────────────────────────────────
# Traceback (most recent call last):
#   ...
# RuntimeError: Something broke
# ──────────────────────────────────────────────────────────────''',
        solution='import traceback\n\ndef risky():\n    raise RuntimeError("Something broke")\n\ntry:\n    risky()\nexcept RuntimeError:\n    traceback.print_exc()',
        sct='test_output_contains("RuntimeError")\ntest_output_contains("Something broke")\nsuccess_msg("traceback.print_exc() shows the full stack!")',
        height=145,
    ),
    dict(
        title="Exercise 3 – Get Traceback as String",
        hint="Use `traceback.format_exc()` to capture the traceback as a string.",
        code='''\
# Task: Exercise 3 – Get Traceback as String
import traceback

try:
    x = [][0]   # IndexError
except IndexError:
    tb = traceback.___()    # replace ___ with format_exc
    print("Contains 'IndexError':", "IndexError" in tb)

# ── Expected Output ───────────────────────────────────────────
# Contains \'IndexError\': True
# ──────────────────────────────────────────────────────────────''',
        solution='import traceback\n\ntry:\n    x = [][0]\nexcept IndexError:\n    tb = traceback.format_exc()\n    print("Contains \'IndexError\':", "IndexError" in tb)',
        sct='test_output_contains("True")\nsuccess_msg("format_exc() returns the traceback as text!")',
        height=135,
    ),
]

# ============================================================
# PYTHON TUTORIALS – Asyncio
# ============================================================
EXERCISES["asyncio-in-python"] = [
    dict(
        title="Exercise 1 – Your First Coroutine",
        hint="Define an `async def` function and run it with `asyncio.run()`.",
        code='''\
# Task: Exercise 1 – Your First Coroutine
import asyncio

# Hint: use async def to define a coroutine
___ def hello():              # replace ___ with async
    print("Hello, asyncio!")

# Hint: run the coroutine with asyncio.run()
asyncio.___(hello())          # replace ___ with run

# ── Expected Output ───────────────────────────────────────────
# Hello, asyncio!
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def hello():\n    print("Hello, asyncio!")\n\nasyncio.run(hello())',
        sct='test_output_contains("Hello, asyncio!")\nsuccess_msg("First coroutine running!")',
        height=130,
    ),
    dict(
        title="Exercise 2 – await asyncio.sleep",
        hint="Use `await asyncio.sleep(seconds)` to pause without blocking.",
        code='''\
# Task: Exercise 2 – await asyncio.sleep
import asyncio

async def delayed():
    print("Before sleep")
    ___ asyncio.sleep(0)   # replace ___ with await
    print("After sleep")

asyncio.run(delayed())

# ── Expected Output ───────────────────────────────────────────
# Before sleep
# After sleep
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def delayed():\n    print("Before sleep")\n    await asyncio.sleep(0)\n    print("After sleep")\n\nasyncio.run(delayed())',
        sct='test_output_contains("Before sleep")\ntest_output_contains("After sleep")\nsuccess_msg("await pauses the coroutine!")',
        height=135,
    ),
    dict(
        title="Exercise 3 – Gather Two Coroutines",
        hint="Use `asyncio.gather(coro1(), coro2())` to run two coroutines concurrently.",
        code='''\
# Task: Exercise 3 – Gather Two Coroutines
import asyncio

async def task(name):
    await asyncio.sleep(0)
    print(f"Done: {name}")

async def main():
    # Hint: use asyncio.gather to run both tasks concurrently
    await asyncio.___(task("A"), task("B"))   # replace ___ with gather

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Done: A
# Done: B
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def task(name):\n    await asyncio.sleep(0)\n    print(f"Done: {name}")\n\nasync def main():\n    await asyncio.gather(task("A"), task("B"))\n\nasyncio.run(main())',
        sct='test_output_contains("Done: A")\ntest_output_contains("Done: B")\nsuccess_msg("gather() runs coroutines concurrently!")',
        height=150,
    ),
]

EXERCISES["coroutines-and-await"] = EXERCISES["asyncio-in-python"]

EXERCISES["tasks-create_task-and-gather"] = [
    dict(
        title="Exercise 1 – Create a Task",
        hint="Use `asyncio.create_task(coro())` to schedule a coroutine as a task.",
        code='''\
# Task: Exercise 1 – Create a Task
import asyncio

async def worker(n):
    await asyncio.sleep(0)
    print(f"Worker {n} done")

async def main():
    # Hint: create a task with asyncio.create_task()
    task = asyncio.___( worker(1) )   # replace ___ with create_task
    await task

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Worker 1 done
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def worker(n):\n    await asyncio.sleep(0)\n    print(f"Worker {n} done")\n\nasync def main():\n    task = asyncio.create_task(worker(1))\n    await task\n\nasyncio.run(main())',
        sct='test_output_contains("Worker 1 done")\nsuccess_msg("create_task schedules a coroutine!")',
        height=145,
    ),
    dict(
        title="Exercise 2 – Gather Multiple Tasks",
        hint="Pass multiple coroutine calls to `asyncio.gather()`.",
        code='''\
# Task: Exercise 2 – Gather Multiple Tasks
import asyncio

async def count(n):
    await asyncio.sleep(0)
    return n * 2

async def main():
    # Hint: gather three calls and collect results
    results = await asyncio.___(count(1), count(2), count(3))  # replace ___ with gather
    print(results)

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# [2, 4, 6]
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def count(n):\n    await asyncio.sleep(0)\n    return n * 2\n\nasync def main():\n    results = await asyncio.gather(count(1), count(2), count(3))\n    print(results)\n\nasyncio.run(main())',
        sct='test_output_contains("[2, 4, 6]")\nsuccess_msg("gather() returns a list of results!")',
        height=148,
    ),
    dict(
        title="Exercise 3 – Task Name and Done",
        hint="Use `.get_name()` and `.done()` on a task object.",
        code='''\
# Task: Exercise 3 – Task Name and Done
import asyncio

async def job():
    await asyncio.sleep(0)

async def main():
    t = asyncio.create_task(job(), name="my-task")
    await t
    print("Name:", t.___())     # replace ___ with get_name
    print("Done:", t.___())     # replace ___ with done

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Name: my-task
# Done: True
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def job():\n    await asyncio.sleep(0)\n\nasync def main():\n    t = asyncio.create_task(job(), name="my-task")\n    await t\n    print("Name:", t.get_name())\n    print("Done:", t.done())\n\nasyncio.run(main())',
        sct='test_output_contains("Name: my-task")\ntest_output_contains("Done: True")\nsuccess_msg("Tasks have names and a done() flag!")',
        height=150,
    ),
]

EXERCISES["event-loop-and-asynciorun"] = [
    dict(
        title="Exercise 1 – asyncio.run() Entry Point",
        hint="`asyncio.run()` creates the event loop and runs the given coroutine.",
        code='''\
# Task: Exercise 1 – asyncio.run() Entry Point
import asyncio

async def main():
    print("Event loop running")

# Hint: call asyncio.run() with the main coroutine
asyncio.___(main())    # replace ___ with run

# ── Expected Output ───────────────────────────────────────────
# Event loop running
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def main():\n    print("Event loop running")\n\nasyncio.run(main())',
        sct='test_output_contains("Event loop running")\nsuccess_msg("asyncio.run() is the standard entry point!")',
        height=120,
    ),
    dict(
        title="Exercise 2 – Get the Running Loop",
        hint="Inside a coroutine, use `asyncio.get_event_loop()` to access the loop.",
        code='''\
# Task: Exercise 2 – Get the Running Loop
import asyncio

async def main():
    loop = asyncio.get_event_loop()
    # Hint: check the loop is running
    print("Is running:", loop.___())   # replace ___ with is_running

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Is running: True
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def main():\n    loop = asyncio.get_event_loop()\n    print("Is running:", loop.is_running())\n\nasyncio.run(main())',
        sct='test_output_contains("Is running: True")\nsuccess_msg("The event loop is running inside a coroutine!")',
        height=130,
    ),
    dict(
        title="Exercise 3 – Schedule and Await",
        hint="Use `asyncio.ensure_future()` or `create_task()` then gather to run concurrently.",
        code='''\
# Task: Exercise 3 – Schedule and Await
import asyncio

async def ping(n):
    await asyncio.sleep(0)
    return f"pong-{n}"

async def main():
    t1 = asyncio.create_task(ping(1))
    t2 = asyncio.create_task(ping(2))
    # Hint: await both tasks using asyncio.gather
    r1, r2 = await asyncio.___(t1, t2)   # replace ___ with gather
    print(r1, r2)

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# pong-1 pong-2
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def ping(n):\n    await asyncio.sleep(0)\n    return f"pong-{n}"\n\nasync def main():\n    t1 = asyncio.create_task(ping(1))\n    t2 = asyncio.create_task(ping(2))\n    r1, r2 = await asyncio.gather(t1, t2)\n    print(r1, r2)\n\nasyncio.run(main())',
        sct='test_output_contains("pong-1 pong-2")\nsuccess_msg("Tasks gathered and awaited!")',
        height=155,
    ),
]

EXERCISES["timeouts-and-cancellation"] = [
    dict(
        title="Exercise 1 – asyncio.wait_for Timeout",
        hint="Use `asyncio.wait_for(coro, timeout=seconds)` to set a deadline.",
        code='''\
# Task: Exercise 1 – asyncio.wait_for Timeout
import asyncio

async def slow():
    await asyncio.sleep(10)

async def main():
    try:
        # Hint: set a 0.1 second timeout
        await asyncio.wait_for(slow(), timeout=___)  # replace ___ with 0.1
    except asyncio.TimeoutError:
        print("Timed out!")

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Timed out!
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def slow():\n    await asyncio.sleep(10)\n\nasync def main():\n    try:\n        await asyncio.wait_for(slow(), timeout=0.1)\n    except asyncio.TimeoutError:\n        print("Timed out!")\n\nasyncio.run(main())',
        sct='test_output_contains("Timed out!")\nsuccess_msg("wait_for cancels slow coroutines!")',
        height=148,
    ),
    dict(
        title="Exercise 2 – Cancel a Task",
        hint="Call `task.cancel()` and catch `asyncio.CancelledError`.",
        code='''\
# Task: Exercise 2 – Cancel a Task
import asyncio

async def forever():
    try:
        await asyncio.sleep(100)
    except asyncio.CancelledError:
        print("Task was cancelled")
        raise

async def main():
    t = asyncio.create_task(forever())
    await asyncio.sleep(0)
    t.___()          # replace ___ with cancel
    try:
        await t
    except asyncio.CancelledError:
        pass

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Task was cancelled
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def forever():\n    try:\n        await asyncio.sleep(100)\n    except asyncio.CancelledError:\n        print("Task was cancelled")\n        raise\n\nasync def main():\n    t = asyncio.create_task(forever())\n    await asyncio.sleep(0)\n    t.cancel()\n    try:\n        await t\n    except asyncio.CancelledError:\n        pass\n\nasyncio.run(main())',
        sct='test_output_contains("Task was cancelled")\nsuccess_msg("task.cancel() stops a running task!")',
        height=165,
    ),
    dict(
        title="Exercise 3 – Check Cancellation",
        hint="Use `task.cancelled()` after cancellation to verify.",
        code='''\
# Task: Exercise 3 – Check Cancellation
import asyncio

async def job():
    await asyncio.sleep(100)

async def main():
    t = asyncio.create_task(job())
    await asyncio.sleep(0)
    t.cancel()
    try:
        await t
    except asyncio.CancelledError:
        pass
    # Hint: check if task was cancelled
    print("Cancelled:", t.___())   # replace ___ with cancelled

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Cancelled: True
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def job():\n    await asyncio.sleep(100)\n\nasync def main():\n    t = asyncio.create_task(job())\n    await asyncio.sleep(0)\n    t.cancel()\n    try:\n        await t\n    except asyncio.CancelledError:\n        pass\n    print("Cancelled:", t.cancelled())\n\nasyncio.run(main())',
        sct='test_output_contains("Cancelled: True")\nsuccess_msg("cancelled() confirms the task was stopped!")',
        height=158,
    ),
]

EXERCISES["asyncio-synchronization-lock-semaphore"] = [
    dict(
        title="Exercise 1 – asyncio.Lock",
        hint="Use `async with lock:` to protect shared state in async code.",
        code='''\
# Task: Exercise 1 – asyncio.Lock
import asyncio

lock = asyncio.Lock()
counter = 0

async def increment():
    global counter
    # Hint: use async with lock:
    ___ ___ lock:       # replace blanks with: async with
        counter += 1

async def main():
    tasks = [asyncio.create_task(increment()) for _ in range(5)]
    await asyncio.gather(*tasks)
    print("Counter:", counter)

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Counter: 5
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nlock = asyncio.Lock()\ncounter = 0\n\nasync def increment():\n    global counter\n    async with lock:\n        counter += 1\n\nasync def main():\n    tasks = [asyncio.create_task(increment()) for _ in range(5)]\n    await asyncio.gather(*tasks)\n    print("Counter:", counter)\n\nasyncio.run(main())',
        sct='test_output_contains("Counter: 5")\nsuccess_msg("asyncio.Lock protects shared state!")',
        height=155,
    ),
    dict(
        title="Exercise 2 – asyncio.Semaphore",
        hint="Use `asyncio.Semaphore(n)` to limit the number of concurrent tasks.",
        code='''\
# Task: Exercise 2 – asyncio.Semaphore
import asyncio

sem = asyncio.Semaphore(___)   # replace ___ with 2

async def task(n):
    async with sem:
        await asyncio.sleep(0)
        print(f"Task {n} running")

async def main():
    await asyncio.gather(*[task(i) for i in range(4)])

asyncio.run(main())

# ── Expected Output (order may vary) ──────────────────────────
# Task 0 running
# Task 1 running
# Task 2 running
# Task 3 running
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nsem = asyncio.Semaphore(2)\n\nasync def task(n):\n    async with sem:\n        await asyncio.sleep(0)\n        print(f"Task {n} running")\n\nasync def main():\n    await asyncio.gather(*[task(i) for i in range(4)])\n\nasyncio.run(main())',
        sct='test_output_contains("Task 0 running")\ntest_output_contains("Task 3 running")\nsuccess_msg("Semaphore limits concurrency!")',
        height=153,
    ),
    dict(
        title="Exercise 3 – asyncio.Event",
        hint="Use `event.set()` to signal and `await event.wait()` to pause until signalled.",
        code='''\
# Task: Exercise 3 – asyncio.Event
import asyncio

event = asyncio.Event()

async def waiter():
    print("Waiting for event...")
    await event.___()          # replace ___ with wait
    print("Event received!")

async def setter():
    await asyncio.sleep(0)
    event.___()                # replace ___ with set

async def main():
    await asyncio.gather(waiter(), setter())

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Waiting for event...
# Event received!
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nevent = asyncio.Event()\n\nasync def waiter():\n    print("Waiting for event...")\n    await event.wait()\n    print("Event received!")\n\nasync def setter():\n    await asyncio.sleep(0)\n    event.set()\n\nasync def main():\n    await asyncio.gather(waiter(), setter())\n\nasyncio.run(main())',
        sct='test_output_contains("Waiting for event...")\ntest_output_contains("Event received!")\nsuccess_msg("asyncio.Event signals between coroutines!")',
        height=160,
    ),
]

EXERCISES["async-queues-producer-consumer"] = [
    dict(
        title="Exercise 1 – asyncio.Queue Basics",
        hint="Use `await q.put(item)` and `await q.get()` for async queues.",
        code='''\
# Task: Exercise 1 – asyncio.Queue Basics
import asyncio

async def main():
    q = asyncio.Queue()
    await q.___(42)          # replace ___ with put
    item = await q.___()     # replace ___ with get
    print("Got:", item)

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Got: 42
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def main():\n    q = asyncio.Queue()\n    await q.put(42)\n    item = await q.get()\n    print("Got:", item)\n\nasyncio.run(main())',
        sct='test_output_contains("Got: 42")\nsuccess_msg("asyncio.Queue works asynchronously!")',
        height=130,
    ),
    dict(
        title="Exercise 2 – Async Producer-Consumer",
        hint="Producer awaits `q.put()`, consumer awaits `q.get()` in separate coroutines.",
        code='''\
# Task: Exercise 2 – Async Producer-Consumer
import asyncio

async def producer(q):
    for i in range(3):
        await q.___(i)          # replace ___ with put
    await q.put(None)           # sentinel

async def consumer(q):
    while True:
        item = await q.___()    # replace ___ with get
        if item is None:
            break
        print("Consumed:", item)

async def main():
    q = asyncio.Queue()
    await asyncio.gather(producer(q), consumer(q))

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Consumed: 0
# Consumed: 1
# Consumed: 2
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def producer(q):\n    for i in range(3):\n        await q.put(i)\n    await q.put(None)\n\nasync def consumer(q):\n    while True:\n        item = await q.get()\n        if item is None:\n            break\n        print("Consumed:", item)\n\nasync def main():\n    q = asyncio.Queue()\n    await asyncio.gather(producer(q), consumer(q))\n\nasyncio.run(main())',
        sct='test_output_contains("Consumed: 0")\ntest_output_contains("Consumed: 2")\nsuccess_msg("Async producer-consumer working!")',
        height=168,
    ),
    dict(
        title="Exercise 3 – Queue Size",
        hint="Use `q.qsize()` to check how many items are in an asyncio.Queue.",
        code='''\
# Task: Exercise 3 – Queue Size
import asyncio

async def main():
    q = asyncio.Queue()
    for v in [10, 20, 30]:
        await q.put(v)
    print("Queue size:", q.___())  # replace ___ with qsize
    await q.get()
    print("After get:", q.___())   # replace ___ with qsize

asyncio.run(main())

# ── Expected Output ───────────────────────────────────────────
# Queue size: 3
# After get: 2
# ──────────────────────────────────────────────────────────────''',
        solution='import asyncio\n\nasync def main():\n    q = asyncio.Queue()\n    for v in [10, 20, 30]:\n        await q.put(v)\n    print("Queue size:", q.qsize())\n    await q.get()\n    print("After get:", q.qsize())\n\nasyncio.run(main())',
        sct='test_output_contains("Queue size: 3")\ntest_output_contains("After get: 2")\nsuccess_msg("qsize() monitors the async queue!")',
        height=148,
    ),
]

EXERCISES["structured-concurrency-with-taskgroup"] = EXERCISES["tasks-create_task-and-gather"]
EXERCISES["async-context-managers-and-async-generators"] = EXERCISES["asyncio-in-python"]
EXERCISES["async-http-with-aiohttp"] = EXERCISES["asyncio-in-python"]
EXERCISES["asyncio-mini-project-concurrent-url-checker"] = EXERCISES["asyncio-in-python"]
# Slug aliases for alternate filename encodings
EXERCISES["tasks-create-task-and-gather"] = EXERCISES["tasks-create_task-and-gather"]
EXERCISES["event-loop-and-asyncio-run"] = EXERCISES["event-loop-and-asynciorun"]

# ============================================================
# PYTHON TUTORIALS – Multiprocessing
# ============================================================
EXERCISES["multiprocessing-in-python"] = [
    dict(
        title="Exercise 1 – Start a Process",
        hint="Use `multiprocessing.Process(target=fn)` and call `.start()`.",
        code='''\
# Task: Exercise 1 – Start a Process
from multiprocessing import Process

def greet(name):
    print(f"Hello from {name}")

if __name__ == "__main__":
    # Hint: create a Process with target=greet and args=("worker",)
    p = Process(target=greet, args=(___, ))   # replace ___ with "worker"
    p.___()                                    # replace ___ with start
    p.___()                                    # replace ___ with join

# ── Expected Output ───────────────────────────────────────────
# Hello from worker
# ──────────────────────────────────────────────────────────────''',
        solution='from multiprocessing import Process\n\ndef greet(name):\n    print(f"Hello from {name}")\n\nif __name__ == "__main__":\n    p = Process(target=greet, args=("worker",))\n    p.start()\n    p.join()',
        sct='test_output_contains("Hello from worker")\nsuccess_msg("Process created and joined!")',
        height=150,
    ),
    dict(
        title="Exercise 2 – Process Pool map()",
        hint="Use `Pool.map(fn, iterable)` to apply a function across multiple processes.",
        code='''\
# Task: Exercise 2 – Process Pool map()
from multiprocessing import Pool

def square(n):
    return n * n

if __name__ == "__main__":
    # Hint: create a Pool with 2 workers
    with Pool(___) as p:            # replace ___ with 2
        results = p.___(square, [1, 2, 3, 4])  # replace ___ with map
        print(results)

# ── Expected Output ───────────────────────────────────────────
# [1, 4, 9, 16]
# ──────────────────────────────────────────────────────────────''',
        solution='from multiprocessing import Pool\n\ndef square(n):\n    return n * n\n\nif __name__ == "__main__":\n    with Pool(2) as p:\n        results = p.map(square, [1, 2, 3, 4])\n        print(results)',
        sct='test_output_contains("[1, 4, 9, 16]")\nsuccess_msg("Pool.map runs tasks in parallel!")',
        height=145,
    ),
    dict(
        title="Exercise 3 – Multiprocessing Queue",
        hint="Use `multiprocessing.Queue` with `.put()` and `.get()` to share data.",
        code='''\
# Task: Exercise 3 – Multiprocessing Queue
from multiprocessing import Process, Queue

def worker(q, value):
    q.___(value * 2)    # replace ___ with put

if __name__ == "__main__":
    q = Queue()
    p = Process(target=worker, args=(q, 21))
    p.start(); p.join()
    print("Result:", q.___())   # replace ___ with get

# ── Expected Output ───────────────────────────────────────────
# Result: 42
# ──────────────────────────────────────────────────────────────''',
        solution='from multiprocessing import Process, Queue\n\ndef worker(q, value):\n    q.put(value * 2)\n\nif __name__ == "__main__":\n    q = Queue()\n    p = Process(target=worker, args=(q, 21))\n    p.start(); p.join()\n    print("Result:", q.get())',
        sct='test_output_contains("Result: 42")\nsuccess_msg("Queue passes data between processes!")',
        height=148,
    ),
]

EXERCISES["process-create-start-join"] = EXERCISES["multiprocessing-in-python"]
EXERCISES["process-pool-pool-map-starmap"] = EXERCISES["multiprocessing-in-python"]
EXERCISES["sharing-data-queue-pipe-manager"] = EXERCISES["multiprocessing-in-python"]
EXERCISES["common-pitfalls-pickling-__main__"] = EXERCISES["multiprocessing-in-python"]
EXERCISES["common-pitfalls-pickling-main"] = EXERCISES["multiprocessing-in-python"]
EXERCISES["mini-project-parallel-imagenumber-processing"] = EXERCISES["multiprocessing-in-python"]
EXERCISES["mini-project-parallel-number-processing"] = EXERCISES["multiprocessing-in-python"]

# ============================================================
# PYTHON TUTORIALS – Synchronization
# ============================================================
EXERCISES["synchronization-in-python"] = EXERCISES["thread-synchronization-with-lock"]
EXERCISES["locks-lock-vs-rlock"] = EXERCISES["thread-synchronization-with-lock"]

EXERCISES["semaphores-limit-concurrency"] = [
    dict(
        title="Exercise 1 – Create a Semaphore",
        hint="Use `threading.Semaphore(n)` and call `.acquire()` / `.release()`.",
        code='''\
# Task: Exercise 1 – Create a Semaphore
import threading

# Hint: allow at most 2 concurrent acquisitions
sem = threading.Semaphore(___)   # replace ___ with 2

def task(n):
    sem.acquire()
    print(f"Task {n} running")
    sem.release()

threads = [threading.Thread(target=task, args=(i,)) for i in range(4)]
for t in threads: t.start()
for t in threads: t.join()''',
        solution='import threading\n\nsem = threading.Semaphore(2)\n\ndef task(n):\n    sem.acquire()\n    print(f"Task {n} running")\n    sem.release()\n\nthreads = [threading.Thread(target=task, args=(i,)) for i in range(4)]\nfor t in threads: t.start()\nfor t in threads: t.join()',
        sct='test_output_contains("Task 0 running")\ntest_output_contains("Task 3 running")\nsuccess_msg("Semaphore limits concurrency!")',
        height=155,
    ),
    dict(
        title="Exercise 2 – Semaphore as Context Manager",
        hint="Use `with sem:` for automatic acquire/release.",
        code='''\
# Task: Exercise 2 – Semaphore as Context Manager
import threading

sem = threading.Semaphore(2)

def worker(n):
    ___ sem:                     # replace ___ with with
        print(f"Worker {n} active")

threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
for t in threads: t.start()
for t in threads: t.join()''',
        solution='import threading\n\nsem = threading.Semaphore(2)\n\ndef worker(n):\n    with sem:\n        print(f"Worker {n} active")\n\nthreads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]\nfor t in threads: t.start()\nfor t in threads: t.join()',
        sct='test_output_contains("Worker 0 active")\nsuccess_msg("Semaphore used as context manager!")',
        height=145,
    ),
    dict(
        title="Exercise 3 – BoundedSemaphore",
        hint="Use `threading.BoundedSemaphore(n)` to prevent releasing more than the initial count.",
        code='''\
# Task: Exercise 3 – BoundedSemaphore
import threading

# Hint: use BoundedSemaphore instead of Semaphore
bsem = threading.___(2)   # replace ___ with BoundedSemaphore

bsem.acquire()
bsem.release()
print("BoundedSemaphore works:", True)

try:
    bsem.release()    # Extra release raises ValueError
    bsem.release()
except ValueError:
    print("Caught over-release!")''',
        solution='import threading\n\nbsem = threading.BoundedSemaphore(2)\nbsem.acquire()\nbsem.release()\nprint("BoundedSemaphore works:", True)\ntry:\n    bsem.release()\n    bsem.release()\nexcept ValueError:\n    print("Caught over-release!")',
        sct='test_output_contains("BoundedSemaphore works: True")\ntest_output_contains("Caught over-release!")\nsuccess_msg("BoundedSemaphore prevents bugs!")',
        height=150,
    ),
]

EXERCISES["events-signal-between-threads"] = [
    dict(
        title="Exercise 1 – threading.Event Set and Wait",
        hint="Call `event.set()` to signal; `event.wait()` blocks until set.",
        code='''\
# Task: Exercise 1 – threading.Event Set and Wait
import threading

event = threading.Event()

def worker():
    event.___()            # replace ___ with wait
    print("Worker received signal")

t = threading.Thread(target=worker)
t.start()
event.___()               # replace ___ with set
t.join()''',
        solution='import threading\n\nevent = threading.Event()\n\ndef worker():\n    event.wait()\n    print("Worker received signal")\n\nt = threading.Thread(target=worker)\nt.start()\nevent.set()\nt.join()',
        sct='test_output_contains("Worker received signal")\nsuccess_msg("Event.set() unblocks waiting threads!")',
        height=145,
    ),
    dict(
        title="Exercise 2 – Clear an Event",
        hint="Use `event.clear()` to reset the event so threads wait again.",
        code='''\
# Task: Exercise 2 – Clear an Event
import threading

event = threading.Event()
event.set()
print("Is set:", event.is_set())

event.___()              # replace ___ with clear
print("After clear:", event.is_set())''',
        solution='import threading\n\nevent = threading.Event()\nevent.set()\nprint("Is set:", event.is_set())\nevent.clear()\nprint("After clear:", event.is_set())',
        sct='test_output_contains("Is set: True")\ntest_output_contains("After clear: False")\nsuccess_msg("clear() resets the event!")',
        height=120,
    ),
    dict(
        title="Exercise 3 – Event with Timeout",
        hint="Pass a `timeout` argument to `event.wait()` to avoid blocking forever.",
        code='''\
# Task: Exercise 3 – Event with Timeout
import threading

event = threading.Event()

# Hint: wait up to 0.1 seconds
result = event.___(timeout=___)   # replace blanks: wait, 0.1
print("Signalled in time:", result)''',
        solution='import threading\n\nevent = threading.Event()\nresult = event.wait(timeout=0.1)\nprint("Signalled in time:", result)',
        sct='test_output_contains("Signalled in time: False")\nsuccess_msg("Timeout prevents infinite blocking!")',
        height=115,
    ),
]

EXERCISES["condition-variables"] = [
    dict(
        title="Exercise 1 – Condition notify and wait",
        hint="Use `with condition:` then `condition.wait()` and `condition.notify()`.",
        code='''\
# Task: Exercise 1 – Condition notify and wait
import threading

cond = threading.Condition()
items = []

def producer():
    with cond:
        items.append("data")
        cond.___()         # replace ___ with notify

def consumer():
    with cond:
        cond.___()         # replace ___ with wait
        print("Got:", items[0])

t1 = threading.Thread(target=consumer)
t2 = threading.Thread(target=producer)
t1.start(); t2.start()
t1.join(); t2.join()''',
        solution='import threading\n\ncond = threading.Condition()\nitems = []\n\ndef producer():\n    with cond:\n        items.append("data")\n        cond.notify()\n\ndef consumer():\n    with cond:\n        cond.wait()\n        print("Got:", items[0])\n\nt1 = threading.Thread(target=consumer)\nt2 = threading.Thread(target=producer)\nt1.start(); t2.start()\nt1.join(); t2.join()',
        sct='test_output_contains("Got: data")\nsuccess_msg("Condition variable used correctly!")',
        height=160,
    ),
    dict(
        title="Exercise 2 – notify_all",
        hint="Use `condition.notify_all()` to wake up all waiting threads at once.",
        code='''\
# Task: Exercise 2 – notify_all
import threading

cond = threading.Condition()
ready = []

def waiter(n):
    with cond:
        cond.wait()
        ready.append(n)

def broadcaster():
    with cond:
        cond.___()       # replace ___ with notify_all

threads = [threading.Thread(target=waiter, args=(i,)) for i in range(3)]
for t in threads: t.start()
broadcaster_t = threading.Thread(target=broadcaster)
broadcaster_t.start()
broadcaster_t.join()
for t in threads: t.join()
print("Ready count:", len(ready))''',
        solution='import threading\n\ncond = threading.Condition()\nready = []\n\ndef waiter(n):\n    with cond:\n        cond.wait()\n        ready.append(n)\n\ndef broadcaster():\n    with cond:\n        cond.notify_all()\n\nthreads = [threading.Thread(target=waiter, args=(i,)) for i in range(3)]\nfor t in threads: t.start()\nbroadcaster_t = threading.Thread(target=broadcaster)\nbroadcaster_t.start()\nbroadcaster_t.join()\nfor t in threads: t.join()\nprint("Ready count:", len(ready))',
        sct='test_output_contains("Ready count: 3")\nsuccess_msg("notify_all wakes every waiting thread!")',
        height=165,
    ),
    dict(
        title="Exercise 3 – Predicate Wait",
        hint="Use `condition.wait_for(lambda: condition_expr)` to avoid spurious wakeups.",
        code='''\
# Task: Exercise 3 – Predicate Wait
import threading

cond = threading.Condition()
flag = False

def setter():
    global flag
    with cond:
        flag = True
        cond.notify()

def checker():
    with cond:
        # Hint: wait until flag is True
        cond.wait_for(lambda: ___)  # replace ___ with flag
        print("Flag is now True!")

t1 = threading.Thread(target=checker)
t2 = threading.Thread(target=setter)
t1.start(); t2.start()
t1.join(); t2.join()''',
        solution='import threading\n\ncond = threading.Condition()\nflag = False\n\ndef setter():\n    global flag\n    with cond:\n        flag = True\n        cond.notify()\n\ndef checker():\n    with cond:\n        cond.wait_for(lambda: flag)\n        print("Flag is now True!")\n\nt1 = threading.Thread(target=checker)\nt2 = threading.Thread(target=setter)\nt1.start(); t2.start()\nt1.join(); t2.join()',
        sct='test_output_contains("Flag is now True!")\nsuccess_msg("wait_for checks the predicate!")',
        height=162,
    ),
]

EXERCISES["barrier-start-together"] = [
    dict(
        title="Exercise 1 – Basic Barrier",
        hint="Use `threading.Barrier(n)` and call `barrier.wait()` in each thread.",
        code='''\
# Task: Exercise 1 – Basic Barrier
import threading

# Hint: synchronise 3 threads
barrier = threading.Barrier(___)   # replace ___ with 3

def task(n):
    print(f"Thread {n} at barrier")
    barrier.___()                  # replace ___ with wait
    print(f"Thread {n} passed!")

threads = [threading.Thread(target=task, args=(i,)) for i in range(3)]
for t in threads: t.start()
for t in threads: t.join()''',
        solution='import threading\n\nbarrier = threading.Barrier(3)\n\ndef task(n):\n    print(f"Thread {n} at barrier")\n    barrier.wait()\n    print(f"Thread {n} passed!")\n\nthreads = [threading.Thread(target=task, args=(i,)) for i in range(3)]\nfor t in threads: t.start()\nfor t in threads: t.join()',
        sct='test_output_contains("Thread 0 at barrier")\ntest_output_contains("Thread 0 passed!")\nsuccess_msg("Barrier synchronises all threads!")',
        height=152,
    ),
    dict(
        title="Exercise 2 – Barrier Parties Count",
        hint="Use `barrier.parties` to read the number of threads it waits for.",
        code='''\
# Task: Exercise 2 – Barrier Parties Count
import threading

b = threading.Barrier(4)
print("Parties:", b.___)   # replace ___ with parties''',
        solution='import threading\n\nb = threading.Barrier(4)\nprint("Parties:", b.parties)',
        sct='test_output_contains("Parties: 4")\nsuccess_msg("parties tells you the barrier count!")',
        height=100,
    ),
    dict(
        title="Exercise 3 – Abort a Barrier",
        hint="Call `barrier.abort()` to raise `BrokenBarrierError` in waiting threads.",
        code='''\
# Task: Exercise 3 – Abort a Barrier
import threading

barrier = threading.Barrier(3)

def waiter():
    try:
        barrier.wait()
    except threading.BrokenBarrierError:
        print("Barrier was broken")

t = threading.Thread(target=waiter)
t.start()
barrier.___()    # replace ___ with abort
t.join()''',
        solution='import threading\n\nbarrier = threading.Barrier(3)\n\ndef waiter():\n    try:\n        barrier.wait()\n    except threading.BrokenBarrierError:\n        print("Barrier was broken")\n\nt = threading.Thread(target=waiter)\nt.start()\nbarrier.abort()\nt.join()',
        sct='test_output_contains("Barrier was broken")\nsuccess_msg("abort() breaks the barrier!")',
        height=148,
    ),
]

EXERCISES["deadlocks-and-how-to-avoid-them"] = EXERCISES["thread-synchronization-with-lock"]

# ============================================================
# PYTHON TUTORIALS – Networking
# ============================================================
EXERCISES["networking-in-python"] = [
    dict(
        title="Exercise 1 – HTTP GET with urllib",
        hint="Use `urllib.request.urlopen(url)` and `.read().decode()` to fetch a page.",
        code='''\
# Task: Exercise 1 – HTTP GET with urllib
import urllib.request

url = "https://httpbin.org/get"
# Hint: open the URL and read the response
with urllib.request.___(url) as response:   # replace ___ with urlopen
    data = response.___().decode()          # replace ___ with read
    print("Status:", response.status)

# ── Expected Output ───────────────────────────────────────────
# Status: 200
# ──────────────────────────────────────────────────────────────''',
        solution='import urllib.request\n\nurl = "https://httpbin.org/get"\nwith urllib.request.urlopen(url) as response:\n    data = response.read().decode()\n    print("Status:", response.status)',
        sct='test_output_contains("Status: 200")\nsuccess_msg("urllib fetches HTTP data!")',
        height=130,
    ),
    dict(
        title="Exercise 2 – Socket Connection",
        hint="Use `socket.create_connection((host, port))` to open a TCP connection.",
        code='''\
# Task: Exercise 2 – Socket Connection
import socket

# Hint: connect to google.com on port 80
with socket.create_connection(("www.google.com", ___)) as s:  # replace ___ with 80
    print("Connected:", s.___())   # replace ___ with getpeername

# ── Expected Output ───────────────────────────────────────────
# Connected: ('x.x.x.x', 80)
# ──────────────────────────────────────────────────────────────''',
        solution='import socket\n\nwith socket.create_connection(("www.google.com", 80)) as s:\n    print("Connected:", s.getpeername())',
        sct='test_output_contains("80")\nsuccess_msg("Socket connected!")',
        height=120,
    ),
    dict(
        title="Exercise 3 – Resolve a Hostname",
        hint="Use `socket.gethostbyname(hostname)` to get the IP address.",
        code='''\
# Task: Exercise 3 – Resolve a Hostname
import socket

# Hint: resolve "localhost" to an IP
ip = socket.___(  "localhost"  )   # replace ___ with gethostbyname
print("IP:", ip)

# ── Expected Output ───────────────────────────────────────────
# IP: 127.0.0.1
# ──────────────────────────────────────────────────────────────''',
        solution='import socket\n\nip = socket.gethostbyname("localhost")\nprint("IP:", ip)',
        sct='test_output_contains("IP: 127.0.0.1")\nsuccess_msg("gethostbyname resolves hostnames!")',
        height=110,
    ),
]

EXERCISES["http-requests-with-requests"] = [
    dict(
        title="Exercise 1 – GET Request",
        hint="Use `requests.get(url)` and check `.status_code`.",
        code='''\
# Task: Exercise 1 – GET Request
import requests

# Hint: make a GET request
r = requests.___(  "https://httpbin.org/get"  )   # replace ___ with get
print("Status:", r.___)                            # replace ___ with status_code

# ── Expected Output ───────────────────────────────────────────
# Status: 200
# ──────────────────────────────────────────────────────────────''',
        solution='import requests\n\nr = requests.get("https://httpbin.org/get")\nprint("Status:", r.status_code)',
        sct='test_output_contains("Status: 200")\nsuccess_msg("GET request succeeded!")',
        height=120,
    ),
    dict(
        title="Exercise 2 – POST with JSON",
        hint="Use `requests.post(url, json=data)` and `.json()` to read the response.",
        code='''\
# Task: Exercise 2 – POST with JSON
import requests

payload = {"name": "Alice", "score": 99}
# Hint: POST with json= keyword
r = requests.___("https://httpbin.org/post", ___=payload)  # replace blanks: post, json
print("Sent name:", r.___()["json"]["name"])                # replace ___ with json

# ── Expected Output ───────────────────────────────────────────
# Sent name: Alice
# ──────────────────────────────────────────────────────────────''',
        solution='import requests\n\npayload = {"name": "Alice", "score": 99}\nr = requests.post("https://httpbin.org/post", json=payload)\nprint("Sent name:", r.json()["json"]["name"])',
        sct='test_output_contains("Sent name: Alice")\nsuccess_msg("POST with JSON works!")',
        height=130,
    ),
    dict(
        title="Exercise 3 – Handle Timeout",
        hint="Pass `timeout=seconds` to `requests.get()` to avoid hanging indefinitely.",
        code='''\
# Task: Exercise 3 – Handle Timeout
import requests

try:
    # Hint: set timeout=0.001 to force a timeout
    r = requests.get("https://httpbin.org/delay/5", ___=0.001)  # replace ___ with timeout
except requests.exceptions.Timeout:
    print("Request timed out!")

# ── Expected Output ───────────────────────────────────────────
# Request timed out!
# ──────────────────────────────────────────────────────────────''',
        solution='import requests\n\ntry:\n    r = requests.get("https://httpbin.org/delay/5", timeout=0.001)\nexcept requests.exceptions.Timeout:\n    print("Request timed out!")',
        sct='test_output_contains("Request timed out!")\nsuccess_msg("Timeout prevents hanging!")',
        height=130,
    ),
]

EXERCISES["working-with-json-apis"] = [
    dict(
        title="Exercise 1 – Parse JSON Response",
        hint="Use `.json()` on a requests response to get a Python dict.",
        code='''\
# Task: Exercise 1 – Parse JSON Response
import requests

r = requests.get("https://httpbin.org/json")
# Hint: call .json() to parse the body
data = r.___()     # replace ___ with json
print(type(data))  # should be <class 'dict'>

# ── Expected Output ───────────────────────────────────────────
# <class 'dict'>
# ──────────────────────────────────────────────────────────────''',
        solution='import requests\n\nr = requests.get("https://httpbin.org/json")\ndata = r.json()\nprint(type(data))',
        sct='test_output_contains("<class \'dict\'>")\nsuccess_msg(".json() parses the response body!")',
        height=120,
    ),
    dict(
        title="Exercise 2 – Serialize Python to JSON",
        hint="Use `json.dumps(obj)` to convert a dict to a JSON string.",
        code='''\
# Task: Exercise 2 – Serialize Python to JSON
import json

data = {"language": "Python", "version": 3}
# Hint: use json.dumps() to serialize
text = json.___( data )   # replace ___ with dumps
print(type(text))
print(text)

# ── Expected Output ───────────────────────────────────────────
# <class 'str'>
# {"language": "Python", "version": 3}
# ──────────────────────────────────────────────────────────────''',
        solution='import json\n\ndata = {"language": "Python", "version": 3}\ntext = json.dumps(data)\nprint(type(text))\nprint(text)',
        sct='test_output_contains("<class \'str\'>")\ntest_output_contains("Python")\nsuccess_msg("json.dumps() serializes data!")',
        height=130,
    ),
    dict(
        title="Exercise 3 – Parse JSON String",
        hint="Use `json.loads(text)` to convert a JSON string back to a Python object.",
        code='''\
# Task: Exercise 3 – Parse JSON String
import json

text = \'{"city": "Berlin", "pop": 3800000}\'
# Hint: use json.loads() to parse
obj = json.___(text)    # replace ___ with loads
print(obj["city"])
print(obj["pop"])

# ── Expected Output ───────────────────────────────────────────
# Berlin
# 3800000
# ──────────────────────────────────────────────────────────────''',
        solution='import json\n\ntext = \'{"city": "Berlin", "pop": 3800000}\'\nobj = json.loads(text)\nprint(obj["city"])\nprint(obj["pop"])',
        sct='test_output_contains("Berlin")\ntest_output_contains("3800000")\nsuccess_msg("json.loads() parses JSON strings!")',
        height=130,
    ),
]

EXERCISES["sockets-tcp-client-and-server"] = EXERCISES["networking-in-python"]
EXERCISES["building-a-simple-http-server"] = EXERCISES["networking-in-python"]
EXERCISES["networking-errors-and-timeouts"] = EXERCISES["http-requests-with-requests"]

# ============================================================
# DATA ANALYTICS
# ============================================================
_NUMPY_EXERCISES = [
    dict(
        title="Exercise 1 – Create a NumPy Array",
        hint="Use `np.array([...])` to create a 1-D array from a list.",
        code='''\
# Task: Exercise 1 – Create a NumPy Array
import numpy as np

# Hint: pass a Python list to np.array()
arr = np.___(  [10, 20, 30, 40]  )   # replace ___ with array
print(arr)
print("dtype:", arr.___)              # replace ___ with dtype

# ── Expected Output ───────────────────────────────────────────
# [10 20 30 40]
# dtype: int64
# ──────────────────────────────────────────────────────────────''',
        solution='import numpy as np\n\narr = np.array([10, 20, 30, 40])\nprint(arr)\nprint("dtype:", arr.dtype)',
        sct='test_output_contains("[10 20 30 40]")\ntest_output_contains("dtype:")\nsuccess_msg("NumPy array created!")',
        height=130,
    ),
    dict(
        title="Exercise 2 – Array Shape and Reshape",
        hint="Use `.shape` to read dimensions and `.reshape(r, c)` to change them.",
        code='''\
# Task: Exercise 2 – Array Shape and Reshape
import numpy as np

arr = np.arange(12)
print("Shape:", arr.___)           # replace ___ with shape

# Hint: reshape into 3 rows and 4 columns
matrix = arr.___(3, ___)           # replace blanks: reshape, 4
print(matrix)

# ── Expected Output ───────────────────────────────────────────
# Shape: (12,)
# [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]
# ──────────────────────────────────────────────────────────────''',
        solution='import numpy as np\n\narr = np.arange(12)\nprint("Shape:", arr.shape)\nmatrix = arr.reshape(3, 4)\nprint(matrix)',
        sct='test_output_contains("Shape: (12,)")\ntest_output_contains("[[ 0  1  2  3]")\nsuccess_msg("reshape() works!")',
        height=148,
    ),
    dict(
        title="Exercise 3 – Array Arithmetic",
        hint="NumPy operations are element-wise: `arr * 2` doubles every value.",
        code='''\
# Task: Exercise 3 – Array Arithmetic
import numpy as np

a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

# Hint: element-wise addition
total = a ___ b       # replace ___ with +
print("Sum:", total)

# Hint: element-wise multiplication
product = a ___ b     # replace ___ with *
print("Product:", product)

# ── Expected Output ───────────────────────────────────────────
# Sum: [11 22 33 44]
# Product: [ 10  40  90 160]
# ──────────────────────────────────────────────────────────────''',
        solution='import numpy as np\n\na = np.array([1, 2, 3, 4])\nb = np.array([10, 20, 30, 40])\ntotal = a + b\nprint("Sum:", total)\nproduct = a * b\nprint("Product:", product)',
        sct='test_output_contains("Sum: [11 22 33 44]")\ntest_output_contains("Product:")\nsuccess_msg("Vectorised arithmetic is fast!")',
        height=148,
    ),
]

_PANDAS_EXERCISES = [
    dict(
        title="Exercise 1 – Create a DataFrame",
        hint="Pass a dict of lists to `pd.DataFrame()` to build a table.",
        code='''\
# Task: Exercise 1 – Create a DataFrame
import pandas as pd

data = {"name": ["Alice", "Bob", "Charlie"], "score": [90, 85, 92]}
# Hint: use pd.DataFrame()
df = pd.___( data )    # replace ___ with DataFrame
print(df)

# ── Expected Output ───────────────────────────────────────────
#       name  score
# 0    Alice     90
# 1      Bob     85
# 2  Charlie     92
# ──────────────────────────────────────────────────────────────''',
        solution='import pandas as pd\n\ndata = {"name": ["Alice", "Bob", "Charlie"], "score": [90, 85, 92]}\ndf = pd.DataFrame(data)\nprint(df)',
        sct='test_output_contains("Alice")\ntest_output_contains("score")\nsuccess_msg("DataFrame created!")',
        height=130,
    ),
    dict(
        title="Exercise 2 – Select a Column",
        hint="Use `df['column_name']` to select a Series.",
        code='''\
# Task: Exercise 2 – Select a Column
import pandas as pd

df = pd.DataFrame({"product": ["A", "B", "C"], "price": [10, 25, 15]})
# Hint: select the 'price' column
prices = df[___]         # replace ___ with 'price'
print(prices.mean())

# ── Expected Output ───────────────────────────────────────────
# 16.666666666666668
# ──────────────────────────────────────────────────────────────''',
        solution='import pandas as pd\n\ndf = pd.DataFrame({"product": ["A", "B", "C"], "price": [10, 25, 15]})\nprices = df["price"]\nprint(prices.mean())',
        sct='test_output_contains("16.6")\nsuccess_msg("Column selected and mean calculated!")',
        height=130,
    ),
    dict(
        title="Exercise 3 – Filter Rows",
        hint="Use a boolean mask `df[df['col'] > value]` to filter rows.",
        code='''\
# Task: Exercise 3 – Filter Rows
import pandas as pd

df = pd.DataFrame({"city": ["NY", "LA", "Chicago"], "pop": [8, 4, 3]})
# Hint: keep only rows where pop > 3
big = df[df[___] > ___]   # replace blanks: 'pop', 3
print(big)

# ── Expected Output ───────────────────────────────────────────
#   city  pop
# 0   NY    8
# 1   LA    4
# ──────────────────────────────────────────────────────────────''',
        solution='import pandas as pd\n\ndf = pd.DataFrame({"city": ["NY", "LA", "Chicago"], "pop": [8, 4, 3]})\nbig = df[df["pop"] > 3]\nprint(big)',
        sct='test_output_contains("NY")\ntest_output_contains("LA")\nsuccess_msg("Row filter works!")',
        height=130,
    ),
]

_ML_EXERCISES = [
    dict(
        title="Exercise 1 – Train-Test Split",
        hint="Use `train_test_split(X, y, test_size=0.2)` from scikit-learn.",
        code='''\
# Task: Exercise 1 – Train-Test Split
from sklearn.model_selection import ___   # replace ___ with train_test_split
import numpy as np

X = np.arange(20).reshape(10, 2)
y = np.arange(10)

X_train, X_test, y_train, y_test = ___(X, y, test_size=0.2, random_state=42)
print("Train size:", len(X_train))
print("Test size:", len(X_test))

# ── Expected Output ───────────────────────────────────────────
# Train size: 8
# Test size: 2
# ──────────────────────────────────────────────────────────────''',
        solution='from sklearn.model_selection import train_test_split\nimport numpy as np\n\nX = np.arange(20).reshape(10, 2)\ny = np.arange(10)\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\nprint("Train size:", len(X_train))\nprint("Test size:", len(X_test))',
        sct='test_output_contains("Train size: 8")\ntest_output_contains("Test size: 2")\nsuccess_msg("Data split correctly!")',
        height=148,
    ),
    dict(
        title="Exercise 2 – Fit a Linear Model",
        hint="Call `model.fit(X_train, y_train)` then `model.predict(X_test)`.",
        code='''\
# Task: Exercise 2 – Fit a Linear Model
from sklearn.linear_model import LinearRegression
import numpy as np

X = np.array([[1], [2], [3], [4], [5]])
y = np.array([2, 4, 6, 8, 10])

model = LinearRegression()
model.___(X, y)            # replace ___ with fit
preds = model.___(X)       # replace ___ with predict
print("Predictions:", preds.astype(int))

# ── Expected Output ───────────────────────────────────────────
# Predictions: [ 2  4  6  8 10]
# ──────────────────────────────────────────────────────────────''',
        solution='from sklearn.linear_model import LinearRegression\nimport numpy as np\n\nX = np.array([[1], [2], [3], [4], [5]])\ny = np.array([2, 4, 6, 8, 10])\nmodel = LinearRegression()\nmodel.fit(X, y)\npreds = model.predict(X)\nprint("Predictions:", preds.astype(int))',
        sct='test_output_contains("Predictions:")\nsuccess_msg("Model fitted and predictions made!")',
        height=148,
    ),
    dict(
        title="Exercise 3 – Evaluate with MSE",
        hint="Use `mean_squared_error(y_true, y_pred)` to measure prediction error.",
        code='''\
# Task: Exercise 3 – Evaluate with MSE
from sklearn.metrics import ___   # replace ___ with mean_squared_error
import numpy as np

y_true = np.array([3, 5, 7, 9])
y_pred = np.array([2.8, 5.1, 7.2, 8.9])

mse = ___(y_true, y_pred)         # replace ___ with mean_squared_error
print(f"MSE: {mse:.4f}")

# ── Expected Output ───────────────────────────────────────────
# MSE: 0.0275
# ──────────────────────────────────────────────────────────────''',
        solution='from sklearn.metrics import mean_squared_error\nimport numpy as np\n\ny_true = np.array([3, 5, 7, 9])\ny_pred = np.array([2.8, 5.1, 7.2, 8.9])\nmse = mean_squared_error(y_true, y_pred)\nprint(f"MSE: {mse:.4f}")',
        sct='test_output_contains("MSE:")\nsuccess_msg("MSE evaluated successfully!")',
        height=138,
    ),
]

_FLASK_EXERCISES = [
    dict(
        title="Exercise 1 – Create a Flask App",
        hint="Import Flask, create `app = Flask(__name__)`, then define a route.",
        code='''\
# Task: Exercise 1 – Create a Flask App
# (Simulated – we run the route function directly)
from flask import Flask

app = ___(  __name__  )   # replace ___ with Flask

@app.route("/")
def home():
    return "Hello, Flask!"

# Simulate calling the route
with app.test_client() as client:
    r = client.get("/")
    print(r.data.decode())

# ── Expected Output ───────────────────────────────────────────
# Hello, Flask!
# ──────────────────────────────────────────────────────────────''',
        solution='from flask import Flask\n\napp = Flask(__name__)\n\n@app.route("/")\ndef home():\n    return "Hello, Flask!"\n\nwith app.test_client() as client:\n    r = client.get("/")\n    print(r.data.decode())',
        sct='test_output_contains("Hello, Flask!")\nsuccess_msg("First Flask route works!")',
        height=148,
    ),
    dict(
        title="Exercise 2 – Dynamic Route",
        hint="Use `<name>` in the route path and add it as a function parameter.",
        code='''\
# Task: Exercise 2 – Dynamic Route
from flask import Flask

app = Flask(__name__)

# Hint: add a <name> variable to the route
@app.route("/greet/<___>")   # replace ___ with name
def greet(name):
    return f"Hello, {name}!"

with app.test_client() as c:
    print(c.get("/greet/Alice").data.decode())

# ── Expected Output ───────────────────────────────────────────
# Hello, Alice!
# ──────────────────────────────────────────────────────────────''',
        solution='from flask import Flask\n\napp = Flask(__name__)\n\n@app.route("/greet/<name>")\ndef greet(name):\n    return f"Hello, {name}!"\n\nwith app.test_client() as c:\n    print(c.get("/greet/Alice").data.decode())',
        sct='test_output_contains("Hello, Alice!")\nsuccess_msg("Dynamic routes work!")',
        height=140,
    ),
    dict(
        title="Exercise 3 – Return JSON",
        hint="Use `flask.jsonify(data)` to return a JSON response.",
        code='''\
# Task: Exercise 3 – Return JSON
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/status")
def status():
    # Hint: use jsonify to return a dict as JSON
    return ___({"ok": True, "code": 200})   # replace ___ with jsonify

with app.test_client() as c:
    import json
    data = json.loads(c.get("/status").data)
    print("ok:", data["ok"])
    print("code:", data["code"])

# ── Expected Output ───────────────────────────────────────────
# ok: True
# code: 200
# ──────────────────────────────────────────────────────────────''',
        solution='from flask import Flask, jsonify\nimport json\n\napp = Flask(__name__)\n\n@app.route("/status")\ndef status():\n    return jsonify({"ok": True, "code": 200})\n\nwith app.test_client() as c:\n    data = json.loads(c.get("/status").data)\n    print("ok:", data["ok"])\n    print("code:", data["code"])',
        sct='test_output_contains("ok: True")\ntest_output_contains("code: 200")\nsuccess_msg("jsonify returns JSON responses!")',
        height=152,
    ),
]

_TESTING_EXERCISES = [
    dict(
        title="Exercise 1 – Write a unittest TestCase",
        hint="Subclass `unittest.TestCase` and use `assertEqual` to assert values.",
        code='''\
# Task: Exercise 1 – Write a unittest TestCase
import unittest

def add(a, b):
    return a + b

class TestAdd(unittest.___):    # replace ___ with TestCase
    def test_positive(self):
        self.___(add(2, 3), 5)  # replace ___ with assertEqual

# Run inline
suite = unittest.TestLoader().loadTestsFromTestCase(TestAdd)
runner = unittest.TextTestRunner(verbosity=0)
result = runner.run(suite)
print("Tests run:", result.testsRun)
print("Failures:", len(result.failures))

# ── Expected Output ───────────────────────────────────────────
# Tests run: 1
# Failures: 0
# ──────────────────────────────────────────────────────────────''',
        solution='import unittest\n\ndef add(a, b):\n    return a + b\n\nclass TestAdd(unittest.TestCase):\n    def test_positive(self):\n        self.assertEqual(add(2, 3), 5)\n\nsuite = unittest.TestLoader().loadTestsFromTestCase(TestAdd)\nrunner = unittest.TextTestRunner(verbosity=0)\nresult = runner.run(suite)\nprint("Tests run:", result.testsRun)\nprint("Failures:", len(result.failures))',
        sct='test_output_contains("Tests run: 1")\ntest_output_contains("Failures: 0")\nsuccess_msg("unittest TestCase working!")',
        height=160,
    ),
    dict(
        title="Exercise 2 – assertRaises",
        hint="Use `self.assertRaises(ExceptionType)` as a context manager.",
        code='''\
# Task: Exercise 2 – assertRaises
import unittest

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class TestDivide(unittest.TestCase):
    def test_zero(self):
        # Hint: use assertRaises to expect a ValueError
        with self.___(___):          # replace blanks: assertRaises, ValueError
            divide(10, 0)

suite = unittest.TestLoader().loadTestsFromTestCase(TestDivide)
result = unittest.TextTestRunner(verbosity=0).run(suite)
print("Passed:", result.wasSuccessful())

# ── Expected Output ───────────────────────────────────────────
# Passed: True
# ──────────────────────────────────────────────────────────────''',
        solution='import unittest\n\ndef divide(a, b):\n    if b == 0:\n        raise ValueError("Cannot divide by zero")\n    return a / b\n\nclass TestDivide(unittest.TestCase):\n    def test_zero(self):\n        with self.assertRaises(ValueError):\n            divide(10, 0)\n\nsuite = unittest.TestLoader().loadTestsFromTestCase(TestDivide)\nresult = unittest.TextTestRunner(verbosity=0).run(suite)\nprint("Passed:", result.wasSuccessful())',
        sct='test_output_contains("Passed: True")\nsuccess_msg("assertRaises verifies exceptions!")',
        height=160,
    ),
    dict(
        title="Exercise 3 – setUp and tearDown",
        hint="Override `setUp` to run before each test and `tearDown` after.",
        code='''\
# Task: Exercise 3 – setUp and tearDown
import unittest

class TestLifecycle(unittest.TestCase):
    def ___(self):              # replace ___ with setUp
        self.data = [1, 2, 3]
        print("setUp called")

    def test_length(self):
        self.assertEqual(len(self.data), 3)

    def ___(self):              # replace ___ with tearDown
        print("tearDown called")

suite = unittest.TestLoader().loadTestsFromTestCase(TestLifecycle)
unittest.TextTestRunner(verbosity=0).run(suite)

# ── Expected Output includes ──────────────────────────────────
# setUp called
# tearDown called
# ──────────────────────────────────────────────────────────────''',
        solution='import unittest\n\nclass TestLifecycle(unittest.TestCase):\n    def setUp(self):\n        self.data = [1, 2, 3]\n        print("setUp called")\n\n    def test_length(self):\n        self.assertEqual(len(self.data), 3)\n\n    def tearDown(self):\n        print("tearDown called")\n\nsuite = unittest.TestLoader().loadTestsFromTestCase(TestLifecycle)\nunittest.TextTestRunner(verbosity=0).run(suite)',
        sct='test_output_contains("setUp called")\ntest_output_contains("tearDown called")\nsuccess_msg("setUp/tearDown lifecycle works!")',
        height=162,
    ),
]

_AUTOMATION_EXERCISES = [
    dict(
        title="Exercise 1 – List Files with os.listdir",
        hint="Use `os.listdir(path)` to get a list of filenames in a directory.",
        code='''\
# Task: Exercise 1 – List Files with os.listdir
import os

# Hint: list the current directory
files = os.___( "." )     # replace ___ with listdir
print("Type:", type(files))
print("Found files:", len(files) > 0)

# ── Expected Output ───────────────────────────────────────────
# Type: <class 'list'>
# Found files: True
# ──────────────────────────────────────────────────────────────''',
        solution='import os\n\nfiles = os.listdir(".")\nprint("Type:", type(files))\nprint("Found files:", len(files) > 0)',
        sct='test_output_contains("Type: <class \'list\'>")\ntest_output_contains("Found files: True")\nsuccess_msg("os.listdir() works!")',
        height=125,
    ),
    dict(
        title="Exercise 2 – Join Paths with os.path.join",
        hint="Use `os.path.join(base, name)` to build a portable file path.",
        code='''\
# Task: Exercise 2 – Join Paths with os.path.join
import os

base = "/home/user"
name = "report.txt"
# Hint: join base and name into a path
path = os.path.___( base, name )   # replace ___ with join
print(path)

# ── Expected Output ───────────────────────────────────────────
# /home/user/report.txt
# ──────────────────────────────────────────────────────────────''',
        solution='import os\n\nbase = "/home/user"\nname = "report.txt"\npath = os.path.join(base, name)\nprint(path)',
        sct='test_output_contains("/home/user/report.txt")\nsuccess_msg("os.path.join builds correct paths!")',
        height=120,
    ),
    dict(
        title="Exercise 3 – Write and Read a File",
        hint="Use `open(path, 'w')` to write and `open(path, 'r')` to read.",
        code='''\
# Task: Exercise 3 – Write and Read a File
import os, tempfile

# Create a temp file path
path = os.path.join(tempfile.gettempdir(), "test_auto.txt")

# Hint: open in write mode and write a line
with open(path, "___") as f:   # replace ___ with w
    f.write("Automation works!")

# Hint: open in read mode and read it back
with open(path, "___") as f:   # replace ___ with r
    print(f.read())

# ── Expected Output ───────────────────────────────────────────
# Automation works!
# ──────────────────────────────────────────────────────────────''',
        solution='import os, tempfile\n\npath = os.path.join(tempfile.gettempdir(), "test_auto.txt")\nwith open(path, "w") as f:\n    f.write("Automation works!")\nwith open(path, "r") as f:\n    print(f.read())',
        sct='test_output_contains("Automation works!")\nsuccess_msg("File write and read done!")',
        height=148,
    ),
]

# ── map topic keys to exercises ──────────────────────────────────────────────
# Data Analytics
for _key in [
    "introduction-to-numpy", "numpy-array-creation", "numpy-arithmetic-operations",
    "indexing-and-slicing-arrays", "broadcasting-in-numpy", "shape-manipulation--reshape",
    "numpy-data-types-dtypes", "numpy-random-module", "numpy-universal-functions-ufuncs",
    "statistical-functions-in-numpy", "saving-and-loading-numpy-data",
    "staking-and-splitting-arrays", "linear-algebra-with-numpy",
]:
    EXERCISES[_key] = _NUMPY_EXERCISES

for _key in [
    "introduction-to-pandas", "series-and-dataframes", "data-inspection-head-tail-info-describe",
    "reading-and-writing-data-csv-excel-json", "indexing-and-selecting-data-loc-iloc",
    "filtering-with-conditions-and-or-isin-query", "handling-missing-data-isna-fillna-dropna",
    "grouping-and-aggregations-groupby-agg", "applying-functions-apply-map-applymap",
    "cleaning-data-astype-duplicates-string-cleaning", "merging-and-joining-data-merge-join-concat",
    "reshaping-data-pivot-pivot_table-melt", "working-with-dates-and-times-to_datetime-dt-accessor",
]:
    EXERCISES[_key] = _PANDAS_EXERCISES

for _key in [
    "what-is-machine-learning", "types-of-machine-learning-supervised-unsupervised-reinforcement",
    "the-ml-lifecycle-from-data-to-deployment", "introduction-to-regression-analysis",
    "simple-linear-regression", "multiple-linear-regression", "introduction-to-classification",
    "logistic-regression-binary-vs-multiclass", "k-nearest-neighbors-knn",
    "evaluation-metrics-confusion-matrix", "bias-vs-variance-tradeoff",
    "k-fold-cross-validation", "hyperparameter-tuning-with-gridsearchcv",
    "introduction-to-clustering", "k-means-clustering-algorithm",
    "text-preprocessing-tokenization-stemming-lemmatization",
]:
    EXERCISES[_key] = _ML_EXERCISES

for _key in [
    "first-flask-application-hello-world", "basic-routing", "variable-rules-dynamic-urls",
    "http-methods-get-vs-post", "handling-query-parameters", "url-building-url_for",
    "returning-json-data", "redirects-and-errors", "custom-error-pages-404-500",
    "introduction-to-jinja2", "rendering-templates", "passing-variables-to-templates",
    "template-inheritance-extends", "introduction-to-flask-wtf", "handling-form-data",
    "form-validation", "introduction-to-orms", "setting-up-flask-sqlalchemy",
    "creating-database-models", "crud---create-record", "crud---read-record",
    "crud---update-record", "crud---delete-record", "building-a-simple-api",
    "introduction-to-rest", "json-serialization", "token-based-authentication-jwt",
]:
    EXERCISES[_key] = _FLASK_EXERCISES

for _key in [
    "introduction-to-python-s-unittest-library", "writing-your-first-test-case",
    "using-assertequal-and-other-assertions", "the-test-lifecycle-setup-and-teardown",
    "test-discovery-and-running-tests", "skipping-tests-and-expected-failures",
    "why-choose-pytest-over-unittest", "writing-concise-tests-with-plain-assert",
    "pytest-fixtures-managing-test-dependencies", "parameterized-testing-running-tests-with-multiple-data-sets",
    "mocking-and-patching-with-unittestmock", "measuring-code-coverage-with-coveragepy",
    "api-testing-fundamentals", "testing-rest-apis-with-the-requests-library",
    "unit-testing-testing-individual-components", "integration-testing-testing-module-interactions",
    "introduction-to-code-linting", "using-flake8-for-style-checks",
    "test-driven-development-tdd-workflow",
]:
    EXERCISES[_key] = _TESTING_EXERCISES

for _key in [
    "the-os-module-navigating-directories", "the-shutil-module-copying-moving-and-deleting",
    "managing-paths-with-pathlib", "pattern-matching-with-glob",
    "searching-files-by-content-or-extension", "batch-renaming-files-script",
    "automating-file-backups", "compressing-files-zip-and-tar-archives",
    "processing-csv-data-with-the-csv-module", "working-with-excel-openpyxl-basics",
    "extracting-text-from-pdfs", "generating-automated-reports",
    "http-requests-with-the-requests-library", "parsing-html-with-beautifulsoup",
    "introduction-to-selenium-webdriver", "sending-emails-with-smtplib",
    "running-scripts-from-the-command-line", "using-arguments-with-argparse",
    "scheduling-scripts-on-linux-and-mac-cron-jobs",
    "using-the-schedule-library-for-python",
    "logging-for-automation-scripts-logging-module",
]:
    EXERCISES[_key] = _AUTOMATION_EXERCISES

# ── helpers ───────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Very simple slug: lowercase, replace spaces/special chars with -."""
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

def find_exercises(slug: str) -> list[dict] | None:
    """Return exercises for the given slug or None if no mapping found."""
    if slug in EXERCISES:
        return EXERCISES[slug]
    # Try partial match
    for key, exs in EXERCISES.items():
        if key in slug or slug in key:
            return exs
    return None

def build_exercise_mdx(exs: list[dict], import_rel: str) -> str:
    """Build the MDX block to append."""
    lines = [
        "",
        f'import DataCampExercise from "{import_rel}";',
        "",
        "## 🧪 Try It Yourself",
        "",
    ]
    for ex in exs:
        lines.append(f'### {ex["title"]}')
        lines.append("")
        lines.append("<DataCampExercise")
        lines.append('  lang="python"')
        lines.append(f'  hint={{`{ex["hint"]}`}}')
        # code: indent each line, wrap in backtick template literal
        code_lines = ex["code"].splitlines()
        code_escaped = "\n".join(code_lines)
        lines.append(f"  code={{`{code_escaped}`}}")
        sol_lines = ex["solution"].replace("`", "\\`")
        lines.append(f"  solution={{`{sol_lines}`}}")
        lines.append(f'  sct={{`{ex["sct"]}`}}')
        lines.append(f'  height={{{ex["height"]}}}')
        lines.append("/>")
        lines.append("")
    return "\n".join(lines)

# ── main processing ───────────────────────────────────────────────────────────

def process_file(md_path: str) -> tuple[str, str]:
    """
    Returns (status, message).
    status: 'skipped' | 'converted' | 'no_exercises'
    """
    with open(md_path, encoding="utf-8") as f:
        content = f.read()

    # Skip if already has exercises
    if "DataCampExercise" in content:
        return "skipped", "already has exercises"

    filename = os.path.splitext(os.path.basename(md_path))[0]
    slug = slugify(filename)
    exs = find_exercises(slug)

    if not exs:
        return "no_exercises", f"no exercise mapping for slug: {slug}"

    mdx_path = os.path.splitext(md_path)[0] + ".mdx"
    rel_import = import_path(md_path)
    block = build_exercise_mdx(exs, rel_import)
    new_content = content.rstrip() + "\n" + block + "\n"

    # Write as .mdx
    with open(mdx_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # Remove original .md if the target is different
    if mdx_path != md_path:
        os.remove(md_path)

    return "converted", mdx_path

# ── collect all target files ──────────────────────────────────────────────────

TARGET_DIRS = [
    "src/content/docs/tutorials/Python Asyncio",
    "src/content/docs/tutorials/Python Errors and Exceptions",
    "src/content/docs/tutorials/Python MultiProcessing",
    "src/content/docs/tutorials/Python Networking",
    "src/content/docs/tutorials/Python Synchronization",
    "src/content/docs/tutorials/Python Threading",
    "src/content/docs/Data Analytics",
    "src/content/docs/Flask Tutorials",
    "src/content/docs/Machine Learning",
    "src/content/docs/Python Automation and Scripting",
    "src/content/docs/Software Testing and Quality",
]

converted = skipped = no_ex = 0

for tdir in TARGET_DIRS:
    for dirpath, _dirs, filenames in os.walk(tdir):
        for fname in filenames:
            if not fname.endswith(".md"):
                continue
            full = os.path.join(dirpath, fname)
            status, msg = process_file(full)
            if status == "converted":
                print(f"  ✅  {full} → .mdx")
                converted += 1
            elif status == "skipped":
                print(f"  ⏭   {full} ({msg})")
                skipped += 1
            else:
                print(f"  ⚠️  {full} ({msg})")
                no_ex += 1

print(f"\n{'─'*60}")
print(f"Converted : {converted}")
print(f"Skipped   : {skipped}  (already had exercises)")
print(f"No mapping: {no_ex}")
print(f"Total     : {converted + skipped + no_ex}")
