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

## Online Modules

There are a lot of modules that are not built-in. You can install them using the Python Package Index (PyPI). You can install them using the `pip` command. You can find the list of all the modules on the [Python Package Index](https://pypi.org/).

### Installing Modules

You can install modules using the `pip` command. You can install them using the following command:

```cmd title="command" showLineNumbers{1}
pip install <module-name>
```

You can also install a specific version of a module using the following command:

```cmd title="command" showLineNumbers{1}
pip install <module-name>==<version>
```

You can also install a module using a requirements file. You can create a requirements file using the following command:

```cmd title="command" showLineNumbers{1}
pip freeze > requirements.txt
```

You can install all the modules in the requirements file using the following command:

```cmd title="command" showLineNumbers{1}
pip install -r requirements.txt
```

### Table of Online Modules

These are some of the most popular modules that you can install using the `pip` command.

| S.No. | Module Name | Description |
| :---: | :--- | :--- |
| 1 | [numpy](https://pypi.org/project/numpy/) | NumPy is the fundamental package for array computing with Python. |
| 2 | [pandas](https://pypi.org/project/pandas/) | pandas is a fast, powerful, flexible and easy to use open source data analysis and manipulation tool, built on top of the Python programming language. |
| 3 | [matplotlib](https://pypi.org/project/matplotlib/) | Matplotlib is a comprehensive library for creating static, animated, and interactive visualizations in Python. |
| 4 | [scipy](https://pypi.org/project/scipy/) | SciPy (pronounced “Sigh Pie”) is a Python-based ecosystem of open-source software for mathematics, science, and engineering. |
| 5 | [scikit-learn](https://pypi.org/project/scikit-learn/) | scikit-learn is a Python module for machine learning built on top of SciPy and distributed under the 3-Clause BSD license. |
| 6 | [tensorflow](https://pypi.org/project/tensorflow/) | TensorFlow is an end-to-end open source platform for machine learning. |
| 7 | [keras](https://pypi.org/project/keras/) | Keras is a high-level neural networks API, written in Python and capable of running on top of TensorFlow, CNTK, or Theano. |
| 8 | [pytorch](https://pypi.org/project/pytorch/) | PyTorch is an open source machine learning library based on the Torch library, used for applications such as computer vision and natural language processing. |
| 9 | [opencv-python](https://pypi.org/project/opencv-python/) | OpenCV-Python is a library of Python bindings designed to solve computer vision problems. |
| 10 | [pillow](https://pypi.org/project/pillow/) | Pillow is the friendly PIL fork by Alex Clark and Contributors. PIL is the Python Imaging Library by Fredrik Lundh and Contributors. |
| 11 | [requests](https://pypi.org/project/requests/) | Requests is an elegant and simple HTTP library for Python, built for human beings. |
| 12 | [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) | Beautiful Soup is a library that makes it easy to scrape information from web pages. |
| 13 | [selenium](https://pypi.org/project/selenium/) | Selenium is a portable framework for testing web applications. |
| 14 | [flask](https://pypi.org/project/flask/) | Flask is a lightweight WSGI web application framework. |
| 15 | [django](https://pypi.org/project/django/) | Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design. |
| 16 | [pyqt5](https://pypi.org/project/PyQt5/) | PyQt5 is a comprehensive set of Python bindings for Qt v5. |
| 17 | [pyinstaller](https://pypi.org/project/pyinstaller/) | PyInstaller bundles a Python application and all its dependencies into a single package. |
| 18 | [cx-freeze](https://pypi.org/project/cx-Freeze/) | cx_Freeze is a set of scripts and modules for freezing Python scripts into executables in much the same way that py2exe and py2app do. |
| 19 | [py2exe](https://pypi.org/project/py2exe/) | py2exe is a Python Distutils extension which converts Python scripts into executable Windows programs, able to run without requiring a Python installation. |
| 20 | [py2app](https://pypi.org/project/py2app/) | py2app is a Python setuptools command which will allow you to make standalone application bundles and plugins from Python scripts. |
| 21 | [tinydb](https://pypi.org/project/tinydb/) | TinyDB is a lightweight document oriented database optimized for your happiness. |
| 22 | [thinker](https://pypi.org/project/thinker/) | Thinker is a Python library for building interactive command line interfaces. |
| 23 | [pytube](https://pypi.org/project/pytube/) | pytube is a lightweight, Pythonic, dependency-free, library (and command-line utility) for downloading YouTube Videos. |
| 24 | [pyautogui](https://pypi.org/project/PyAutoGUI/) | PyAutoGUI lets your Python scripts control the mouse and keyboard to automate interactions with other applications. |
| 25 | [MySQL Connector](https://pypi.org/project/mysql-connector-python/) | MySQL Connector/Python is a standardized database driver for Python platforms and development. |
| 26 | [psycopg2](https://pypi.org/project/psycopg2/) | psycopg2 is a PostgreSQL database adapter for the Python programming language. |
| 27 | [PyGreSQL](https://pypi.org/project/PyGreSQL/) | PyGreSQL is a Python module that interfaces to a PostgreSQL database. |
| 28 | [psycopg2](https://pypi.org/project/psycopg2/) | psycopg2 is a PostgreSQL database adapter for the Python programming language. |
| 29 | [cx_Oracle](https://pypi.org/project/cx-Oracle/) | cx_Oracle is a Python extension module that enables access to Oracle Database. |
| 30 | [pymssql](https://pypi.org/project/pymssql/) | pymssql is the Python language extension module that provides access to Microsoft SQL Servers from Python scripts. |
| 31 | [SQLAlchemy](https://pypi.org/project/SQLAlchemy/) | SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. |
| 32 | [PyMongo](https://pypi.org/project/pymongo/) | PyMongo is a Python distribution containing tools for working with MongoDB, and is the recommended way to work with MongoDB from Python. |
| 33 | [redis](https://pypi.org/project/redis/) | The Python interface to the Redis key-value store. |
| 34 | [pymemcache](https://pypi.org/project/pymemcache/) | A comprehensive, fast, pure Python memcached client. |
| 35 | [pyscreenshot](https://pypi.org/project/pyscreenshot/) | pyscreenshot is a Python module used to take screenshots. |
| 36 | [pytesseract](https://pypi.org/project/pytesseract/) | A Python wrapper for Google Tesseract. |
| 37 | [pywin32](https://pypi.org/project/pywin32/) | pywin32 is a Python extension for Windows. |
| 38 | [virtualenv](https://pypi.org/project/virtualenv/) | virtualenv is a tool to create isolated Python environments. |
| 39 | [pylint](https://pypi.org/project/pylint/) | Pylint is a tool that checks for errors in Python code, tries to enforce a coding standard and looks for code smells. |
| 40 | [autopep8](https://pypi.org/project/autopep8/) | autopep8 automatically formats Python code to conform to the PEP 8 style guide. |
| 41 | [pygame](https://pypi.org/project/pygame/) | Pygame is a set of Python modules designed for writing video games. |
| 42 | [pyglet](https://pypi.org/project/pyglet/) | pyglet is a cross-platform windowing and multimedia library for Python. |
| 43 | [vidstream](https://pypi.org/project/vidstream/) | A cross-platform python package that contains modules for streaming video from your computer to the internet for remote viewing. |
| 44 | [pyexcel](https://pypi.org/project/pyexcel/) | A wrapper library to read, manipulate and write data in different excel formats: csv, ods, xls, xlsx and xlsm. |
| 45 | [pipenv](https://pypi.org/project/pipenv/) | Pipenv is a tool that aims to bring the best of all packaging worlds (bundler, composer, npm, cargo, yarn, etc.) to the Python world. |
| 46 | [NLTK](https://pypi.org/project/nltk/) | NLTK is a leading platform for building Python programs to work with human language data. |
| 47 | [pyttsx3](https://pypi.org/project/pyttsx3/) | pyttsx3 is a text-to-speech conversion library in Python. |
| 48 | [theano](https://pypi.org/project/Theano/) | Theano is a Python library that allows you to define, optimize, and evaluate mathematical expressions involving multi-dimensional arrays efficiently. |
| 49 | [dash](https://pypi.org/project/dash/) | Dash is a Python framework for building analytical web applications. |
| 50 | [streamlit](https://pypi.org/project/streamlit/) | Streamlit is an open-source Python library that makes it easy to build beautiful custom web-apps for machine learning and data science. |

## Using Modules

You can use the built-in modules in your code. You can import them using the `import` keyword. You can import them using the following syntax:

```python title="syntax" showLineNumbers{1} 
import <module-name>
```

You can also import a module using an alias. You can import them using the following syntax:

```python title="syntax" showLineNumbers{1}
import <module-name> as <alias>
```

You can also import a specific function from a module. You can import them using the following syntax:

```python title="syntax" showLineNumbers{1}
from <module-name> import <function-name>
```

You can also import all the functions from a module. You can import them using the following syntax:

```python title="syntax" showLineNumbers{1}
from <module-name> import *
```

You can also import a specific function from a module using an alias. You can import them using the following syntax:

```python title="syntax" showLineNumbers{1}
from <module-name> import <function-name> as <alias>
```

You can also import all the functions from a module using an alias. You can import them using the following syntax:

```python title="syntax" showLineNumbers{1}
from <module-name> import * as <alias>
```

#### Example

You can use the `math` module in your code. You can import it using the following syntax:

```python title="math.py" showLineNumbers{1} {1,3}
import math

print(math.pi)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python math.py
3.141592653589793
```

You can also import a specific function from a module. You can import it using the following syntax:

```python title="math.py" showLineNumbers{1} {1,3}
from math import pi
print(pi)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python math.py
3.141592653589793
```

You can also import a specific function from a module using an alias. You can import it using the following syntax:

```python title="math.py" showLineNumbers{1} {1,3}
from math import pi as PI

print(PI)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python math.py
3.141592653589793
```

You can also import all the functions from a module. You can import it using the following syntax:

```python title="math.py" showLineNumbers{1} {1,3}
from math import *

print(pi)
```

Output:

```cmd title="command" showLineNumbers{1} {2}
C:\Users\username>python math.py
3.141592653589793
```

## Some Useful Modules
### Math Module
Math module is used to perform mathematical operations. It provides access to the mathematical functions defined by the C standard. It is always available in Python. It provides various mathematical operations like trigonometric operations, exponential operations, logarithmic operations, etc. It also provides some constants like pi, e, etc. It is used by importing the math module in the program. It is used in the following way:

```python title="math.py" showLineNumbers{1} {1,3-4}
import math

print(math.pi)
print(math.pow(2, 3))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python math.py
3.141592653589793
8.0
```

In this example, we have used the `pi` constant to print the value of pi. We have also used the `pow()` function to calculate the power of a number.

#### Some Important Functions of Math Module

|S.No.|Function Name|Description|Example|
|:---:|:---|:---|:---|
|1|ceil(x)|Returns the smallest integer greater than or equal to x.|`math.ceil(2.3)`|
|2|copysign(x, y)|Returns x with the sign of y.|`math.copysign(2, -3)`|
|3|fabs(x)|Returns the absolute value of x.|`math.fabs(-2.3)`|
|4|factorial(x)|Returns the factorial of x.|`math.factorial(4)`|
|5|floor(x)|Returns the largest integer less than or equal to x.|`math.floor(2.3)`|
|6|fmod(x, y)|Returns the remainder when x is divided by y.|`math.fmod(2, 3)`|
|7|frexp(x)|Returns the mantissa and exponent of x as the pair (m, e).|`math.frexp(2)`|
|8|fsum(iterable)|Returns an accurate floating point sum of values in the iterable.|`math.fsum([1, 2, 3, 4, 5])`|
|9|isfinite(x)|Returns True if x is neither an infinity nor a NaN (Not a Number).| `math.isfinite(2)`|
|10|isinf(x)|Returns True if x is a positive or negative infinity.|`math.isinf(2)`|
|11|isnan(x)|Returns True if x is a NaN.|`math.isnan(2)`|
|12|ldexp(x, i)|Returns x * (2**i).|`math.ldexp(2, 3)`|
|13|modf(x)|Returns the fractional and integer parts of x.|`math.modf(2.3)`|
|14|trunc(x)|Returns the truncated integer value of x.|`math.trunc(2.3)`|
|15|exp(x)|Returns e**x.| `math.exp(2)`|
|16|expm1(x)|Returns e**x - 1. | `math.expm1(2)`|
|17|log(x[, base])|Returns the logarithm of x to the base (defaults to e).| `math.log(2)`|
|18|log1p(x)|Returns the natural logarithm of 1+x. | `math.log1p(2)`|
|19|log2(x)|Returns the base-2 logarithm of x. | `math.log2(2)`|
|20|log10(x)|Returns the base-10 logarithm of x. | `math.log10(2)`|
|21|pow(x, y)|Returns x raised to the power y. | `math.pow(2, 3)`|
|22|sqrt(x)|Returns the square root of x. | `math.sqrt(2)`|
|23|acos(x)|Returns the arc cosine of x.| `math.acos(2)`|
|24|asin(x)|Returns the arc sine of x.| `math.asin(2)`|
|25|atan(x)|Returns the arc tangent of x.| `math.atan(2)`|
|26|atan2(y, x)|Returns atan(y / x).| `math.atan2(2, 3)`|
|27|cos(x)|Returns the cosine of x.| `math.cos(2)`|
|28|hypot(x, y)|Returns the Euclidean norm, sqrt(x*x + y*y).| `math.hypot(2, 3)`|
|29|sin(x)|Returns the sine of x.| `math.sin(2)`|
|30|tan(x)|Returns the tangent of x.| `math.tan(2)`|
|31|degrees(x)|Converts angle x from radians to degrees.| `math.degrees(2)`|
|32|radians(x)|Converts angle x from degrees to radians.| `math.radians(2)`|
|33|acosh(x)|Returns the inverse hyperbolic cosine of x.| `math.acosh(2)`|
|34|asinh(x)|Returns the inverse hyperbolic sine of x.| `math.asinh(2)`|
|35|atanh(x)|Returns the inverse hyperbolic tangent of x.| `math.atanh(2)`|
|36|cosh(x)|Returns the hyperbolic cosine of x.| `math.cosh(2)`|
|37|sinh(x)|Returns the hyperbolic cosine of x.| `math.sinh(2)`|
|38|tanh(x)|Returns the hyperbolic tangent of x.| `math.tanh(2)`|
|39|erf(x)|Returns the error function at x.| `math.erf(2)`|
|40|erfc(x)|Returns the complementary error function at x.| `math.erfc(2)`|
|41|gamma(x)|Returns the Gamma function at x.| `math.gamma(2)`|
|42|lgamma(x)|Returns the natural logarithm of the absolute value of the Gamma function at x.| `math.lgamma(2)`|
|43|pi|Mathematical constant, the ratio of circumference of a circle to it's diameter (3.14159...)| `math.pi`|
|44|e|mathematical constant e (2.71828...)| `math.e`|
|45|tau|mathematical constant tau (6.28318...)| `math.tau`|
|46|inf|floating-point positive infinity| `math.inf`|
|47|nan|floating-point NaN (not a number)| `math.nan`|
|48|isqrt(n)|Returns the integer square root of the nonnegative integer n.| `math.isqrt(2)`|
|49|comb(n, k)|Returns the number of ways to choose k items from n items without repetition and without order.| `math.comb(2, 3)`|
|50|perm(n, k)|Returns the number of ways to choose k items from n items without repetition and with order.| `math.perm(2, 3)`|

:::tip
More information about the math module can be found [here](https://docs.python.org/3/library/math.html).
:::

### Random Module
Random module is used to perform random operations. It provides access to the pseudo-random number generators for various distributions. It is always available in Python. It provides various random operations like generating random numbers, shuffling a list, etc. It is used by importing the random module in the program. It is used in the following way:

```python title="random.py" showLineNumbers{1} {1,3-4}
import random

print(random.random())
print(random.randint(1, 10))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python random.py
0.940667756167586
7
```

In this example, we have used the `random()` function to generate a random number between 0 and 1. We have also used the `randint()` function to generate a random integer between 1 and 10.

#### Some Important Functions of Random Module

|S.No.|Function Name|Description|Example|
|:---:|:---|:---|:---|
|1|random()|Returns a random float number between 0 and 1.|`random.random()`|
|2|randint(a, b)|Returns a random integer between a and b.|`random.randint(1, 10)`|
|3|randrange(start, stop[, step])|Returns a randomly selected element from range(start, stop, step).|`random.randrange(1, 10, 2)`|
|4|choice(seq)|Returns a random element from the non-empty sequence seq.|`random.choice([1, 2, 3, 4, 5])`|
|5|choices(population[, weights=None, *, cum_weights=None, k=1])|Returns a k sized list of elements chosen from the population with replacement.|`random.choices([1, 2, 3, 4, 5], k=3)`|
|6|shuffle(x[, random])|Shuffle the sequence x in place.|`random.shuffle([1, 2, 3, 4, 5])`|
|7|sample(population, k)|Returns a k length list of unique elements chosen from the population sequence or set.|`random.sample([1, 2, 3, 4, 5], k=3)`|
|8|seed([x])|Initialize the random number generator.|`random.seed(10)`|
|9|getstate()|Return an object capturing the current internal state of the generator.|`random.getstate()`|
|10|setstate(state)|Restore the internal state of the generator.|`random.setstate(state)`|
|11|getrandbits(k)|Returns a non-negative Python integer with k random bits.|`random.getrandbits(5)`|
|12|uniform(a, b)|Returns a random floating point number between a and b.|`random.uniform(1, 10)`|
|13|triangular(low, high, mode)|Returns a random floating point number between low and high, with the specified mode between those bounds.|`random.triangular(1, 10, 5)`|
|14|betavariate(alpha, beta)|Beta distribution.|`random.betavariate(1, 10)`|
|15|expovariate(lambd)|Exponential distribution.|`random.expovariate(1)`|
|16|gammavariate(alpha, beta)|Gamma distribution.|`random.gammavariate(1, 10)`|
|17|gauss(mu, sigma)|Gaussian distribution.|`random.gauss(1, 10)`|
|18|lognormvariate(mu, sigma)|Log normal distribution.|`random.lognormvariate(1, 10)`|
|19|normalvariate(mu, sigma)|Normal distribution.|`random.normalvariate(1, 10)`|
|20|vonmisesvariate(mu, kappa)|von Mises distribution.|`random.vonmisesvariate(1, 10)`|
|21|paretovariate(alpha)|Pareto distribution.|`random.paretovariate(1)`|
|22|weibullvariate(alpha, beta)|Weibull distribution.|`random.weibullvariate(1, 10)`|

:::tip
More information about the random module can be found [here](https://docs.python.org/3/library/random.html).
:::

### Datetime Module
Datetime module is used to perform date and time operations. It provides access to the date and time functions. It is always available in Python. It provides various date and time operations like getting the current date and time, getting the current year, getting the current month, etc. It is used by importing the datetime module in the program. It is used in the following way:

```python title="datetime.py" showLineNumbers{1} {1,3-4}
import datetime

print(datetime.datetime.now())
print(datetime.date(2021,12,11).strftime("%A"))
```

Output:

```cmd title="command" showLineNumbers{1} {2-3}
C:\Users\username>python datetime.py
2023-12-01 12:00:00.000000
Saturday
```

In this example, we have used the `now()` function to get the current date and time. We have also used the `strftime()` function to get the day of the week from a date.

#### Some Important Functions of Datetime Module

|S.No.|Function Name|Description|Example|
|:---:|:---|:---|:---|
|1|date(year, month, day)|Returns a date object with the specified year, month, and day.|`datetime.date(2021, 12, 11)`|
|2|datetime(year, month, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]])|Returns a datetime object with the specified year, month, day, hour, minute, second, microsecond, and tzinfo.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0)`|
|3|time([hour[, minute[, second[, microsecond[, tzinfo]]]]])|Returns a time object with the specified hour, minute, second, microsecond, and tzinfo.|`datetime.time(12, 0, 0, 0)`|
|4|timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])|Returns a timedelta object with the specified days, seconds, microseconds, milliseconds, minutes, hours, and weeks.|`datetime.timedelta(1)`|
|5|today()|Returns the current local date.|`datetime.datetime.today()`|
|6|now([tz])|Returns the current local date and time.|`datetime.datetime.now()`|
|7|utcnow()|Returns the current UTC date and time.|`datetime.datetime.utcnow()`|
|8|fromtimestamp(timestamp[, tz])|Returns the local date and time corresponding to the POSIX timestamp.|`datetime.datetime.fromtimestamp(1639209000)`|
|9|utcfromtimestamp(timestamp)|Returns the UTC date and time corresponding to the POSIX timestamp.|`datetime.datetime.utcfromtimestamp(1639209000)`|
|10|combine(date, time)|Returns a datetime object with the specified date and time.|`datetime.datetime.combine(datetime.date(2021, 12, 11), datetime.time(12, 0, 0, 0))`|
|11|strptime(date_string, format)|Returns a datetime corresponding to date_string, parsed according to format.|`datetime.datetime.strptime("2021-12-11", "%Y-%m-%d")`|
|12|strftime(format)|Returns a string representing the date and time, controlled by an explicit format string.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).strftime("%A")`|
|13|date()|Returns the date part.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).date()`|
|14|time()|Returns the time part.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).time()`|
|15|replace([year[, month[, day[, hour[, minute[, second[, microsecond[, tzinfo]]]]]]]])|Returns a datetime with the same attributes, except for those attributes given new values by whichever keyword arguments are specified.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).replace(2021, 12, 11)`|
|16|astimezone(tz=None)|Returns a datetime object with new tzinfo attribute tz, adjusting the date and time data so the result is the same UTC time as self, but in tz's local time.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).astimezone()`|
|17|timetuple()|Returns a time.struct_time such as returned by time.localtime().|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).timetuple()`|
|18|utctimetuple()|Returns a time.struct_time such as returned by time.gmtime().|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).utctimetuple()`|
|19|toordinal()|Returns the proleptic Gregorian ordinal of the date.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).toordinal()`|
|20|timestamp()|Returns POSIX timestamp corresponding to the datetime instance.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).timestamp()`|
|21|ctime()|Returns a string representing the date and time.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).ctime()`|
|22|isoformat([sep='T', timespec='auto'])|Returns a string representing the date and time in ISO 8601 format.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).isoformat()`|
|23|__str__()|Returns a string representing the date and time.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).__str__()`|
|24|__repr__()|Returns a string representing the date and time.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).__repr__()`|
|25|weekday()|Returns the day of the week as an integer, where Monday is 0 and Sunday is 6.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).weekday()`|
|26|isoweekday()|Returns the day of the week as an integer, where Monday is 1 and Sunday is 7.|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).isoweekday()`|
|27|isocalendar()|Returns a 3-tuple, (ISO year, ISO week number, ISO weekday).|`datetime.datetime(2021, 12, 11, 12, 0, 0, 0).isocalendar()`|
|28|fromisocalendar(year, week, day)|Returns the date corresponding to the specified ISO year, week number, and weekday.|`datetime.datetime.fromisocalendar(2021, 12, 11)`|

:::tip
More information about the datetime module can be found [here](https://docs.python.org/3/library/datetime.html).
:::
