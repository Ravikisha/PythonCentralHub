---
title: Built-in and Online Modules
description: Learn about the built-in and online modules in Python. How to use them and how to install them. Using the Python Package Index (PyPI).
sidebar: 
    order: 47
---

## Built-in Modules

Python has a lot of built-in modules that you can use. You can find the list of all the built-in modules in the [Python Standard Library](https://docs.python.org/3/library/index.html). You can use these modules without installing them. You can import them and use them in your code.

### Table of Built-in Modules

| S.No. | Module Name | Description |
| :---: | :--- | :--- |
| 1 | [math](https://docs.python.org/3/library/math.html) | This module provides access to the mathematical functions defined by the C standard. |
| 2 | [random](https://docs.python.org/3/library/random.html) | This module implements pseudo-random number generators for various distributions. |
| 3 | [datetime](https://docs.python.org/3/library/datetime.html) | This module supplies classes for manipulating dates and times. |
| 4 | [calendar](https://docs.python.org/3/library/calendar.html) | This module allows you to output calendars like the Unix cal program, and provides additional useful functions related to the calendar. |
| 5 | [os](https://docs.python.org/3/library/os.html) | This module provides a portable way of using operating system dependent functionality. |
| 6 | [sys](https://docs.python.org/3/library/sys.html) | This module provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter. |
| 7 | [json](https://docs.python.org/3/library/json.html) | This module implements a subset of the corresponding CPython module, as described below. For more information, refer to the original CPython documentation: json. |
| 8 | [re](https://docs.python.org/3/library/re.html) | This module provides regular expression matching operations similar to those found in Perl. |
| 9 | [time](https://docs.python.org/3/library/time.html) | This module provides various time-related functions. |
| 10 | [urllib](https://docs.python.org/3/library/urllib.html) | This module provides a high-level interface for fetching data across the World Wide Web. |
| 11 | [xml](https://docs.python.org/3/library/xml.html) | This package contains four sub-packages: dom, parsers, sax and etree. |
| 12 | [pickle](https://docs.python.org/3/library/pickle.html) | This module implements binary protocols for serializing and de-serializing a Python object structure. |
| 13 | [sqlite3](https://docs.python.org/3/library/sqlite3.html) | This module provides a DB-API 2.0 interface for SQLite databases. |
| 14 | [csv](https://docs.python.org/3/library/csv.html) | This module implements classes to read and write tabular data in CSV format. |
| 15 | [string](https://docs.python.org/3/library/string.html) | This module contains common string operations. |
| 16 | [statistics](https://docs.python.org/3/library/statistics.html) | This module provides functions for calculating mathematical statistics of numeric (Real-valued) data. |
| 17 | [collections](https://docs.python.org/3/library/collections.html) | This module implements specialized container datatypes providing alternatives to Python’s general purpose built-in containers, dict, list, set, and tuple. |
| 18 | [itertools](https://docs.python.org/3/library/itertools.html) | This module implements a number of iterator building blocks inspired by constructs from APL, Haskell, and SML. |
| 19 | [functools](https://docs.python.org/3/library/functools.html) | This module provides tools for adapting or extending functions and other callable objects, without completely rewriting them. |
| 20 | [operator](https://docs.python.org/3/library/operator.html) | This module exports a set of efficient functions corresponding to the intrinsic operators of Python. |
| 21 | [pathlib](https://docs.python.org/3/library/pathlib.html) | This module offers classes representing filesystem paths with semantics appropriate for different operating systems. |
| 22 | [argparse](https://docs.python.org/3/library/argparse.html) | This module makes it easy to write user-friendly command-line interfaces. |
| 23 | [logging](https://docs.python.org/3/library/logging.html) | This module defines functions and classes which implement a flexible event logging system for applications and libraries. |
| 24 | [unittest](https://docs.python.org/3/library/unittest.html) | This module provides a rich set of tools for constructing and running tests. |
| 25 | [pdb](https://docs.python.org/3/library/pdb.html) | The module defines an interactive source code debugger for Python programs. |
| 26 | [timeit](https://docs.python.org/3/library/timeit.html) | This module provides a simple way to time small bits of Python code. |
| 27 | [doctest](https://docs.python.org/3/library/doctest.html) | This module provides a tool for scanning a module and validating tests embedded in a program’s docstrings. |
| 28 | [typing](https://docs.python.org/3/library/typing.html) | This module provides runtime support for type hints. |
| 29 | [sysconfig](https://docs.python.org/3/library/sysconfig.html) | This module provides access to Python’s configuration information. |
| 30 | [traceback](https://docs.python.org/3/library/traceback.html) | This module provides a standard interface to extract, format and print stack traces of Python programs. |
| 31 | [gc](https://docs.python.org/3/library/gc.html) | This module provides an interface to the optional garbage collector. |
| 32 | [inspect](https://docs.python.org/3/library/inspect.html) | This module provides several useful functions to help get information about live objects. |
| 33 | [warnings](https://docs.python.org/3/library/warnings.html) | This module defines a standard warning category class. |
| 34 | [pickle](https://docs.python.org/3/library/pickle.html) | This module implements binary protocols for serializing and de-serializing a Python object structure. |
| 35 | [copy](https://docs.python.org/3/library/copy.html) | This module provides generic shallow and deep copy operations. |
| 36 | [pprint](https://docs.python.org/3/library/pprint.html) | This module provides a capability to “pretty-print” arbitrary Python data structures in a form which can be used as input to the interpreter. |
| 37 | [reprlib](https://docs.python.org/3/library/reprlib.html) | This module provides a version of repr() customized for abbreviated displays of large or deeply nested containers. |
| 38 | [enum](https://docs.python.org/3/library/enum.html) | This module defines four enumeration classes that can be used to define unique sets of names and values: Enum, IntEnum, Flag, and IntFlag. |
| 39 | [socket](https://docs.python.org/3/library/socket.html) | This module provides access to the BSD socket interface. |
| 40 | [threading](https://docs.python.org/3/library/threading.html) | This module constructs higher-level threading interfaces on top of the lower level thread module. |
| 41 | [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) | This module allows the programmer to fully leverage multiple processors on a given machine. |
| 42 | [asyncio](https://docs.python.org/3/library/asyncio.html) | This module provides infrastructure for writing single-threaded concurrent code using coroutines. |
| 43 | [subprocess](https://docs.python.org/3/library/subprocess.html) | This module allows you to spawn new processes, connect to their input/output/error pipes, and obtain their return codes. |
| 44 | [venv](https://docs.python.org/3/library/venv.html) | This module provides support for creating lightweight “virtual environments” with their own site directories, optionally isolated from system site directories. |
| 45 | [pkgutil](https://docs.python.org/3/library/pkgutil.html) | This module provides utilities for the import system. |
| 46 | [platform](https://docs.python.org/3/library/platform.html) | This module provides a portable way of using operating system dependent functionality. |
| 47 | [getpass](https://docs.python.org/3/library/getpass.html) | This module provides a portable way to handle such password prompts securely. |
| 48 | [shutil](https://docs.python.org/3/library/shutil.html) | This module offers a number of high-level operations on files and collections of files. |
| 49 | [tempfile](https://docs.python.org/3/library/tempfile.html) | This module generates temporary files and directories. |
| 50 | [gzip](https://docs.python.org/3/library/gzip.html) | This module provides a simple interface to compress and decompress files just like the GNU programs gzip and gunzip would. |
