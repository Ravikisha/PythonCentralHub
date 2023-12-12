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

```cmd title="command" showLineNumbers{1} {1-2}
C:\Users\username>python math.py
3.141592653589793
8.0
```

#### Some Important Functions of Math Module

|S.No.|Function Name|Description|
|:---:|:---|:---|
|1|ceil(x)|Returns the smallest integer greater than or equal to x.|
|2|copysign(x, y)|Returns x with the sign of y.|
|3|fabs(x)|Returns the absolute value of x.|
|4|factorial(x)|Returns the factorial of x.|
|5|floor(x)|Returns the largest integer less than or equal to x.|
|6|fmod(x, y)|Returns the remainder when x is divided by y.|
|7|frexp(x)|Returns the mantissa and exponent of x as the pair (m, e).|
|8|fsum(iterable)|Returns an accurate floating point sum of values in the iterable.|
|9|isfinite(x)|Returns True if x is neither an infinity nor a NaN (Not a Number).|
|10|isinf(x)|Returns True if x is a positive or negative infinity.|
|11|isnan(x)|Returns True if x is a NaN.|
|12|ldexp(x, i)|Returns x * (2**i).|
|13|modf(x)|Returns the fractional and integer parts of x.|
|14|trunc(x)|Returns the truncated integer value of x.|
|15|exp(x)|Returns e**x.|
|16|expm1(x)|Returns e**x - 1.|
|17|log(x[, base])|Returns the logarithm of x to the base (defaults to e).|
|18|log1p(x)|Returns the natural logarithm of 1+x.|
|19|log2(x)|Returns the base-2 logarithm of x.|
|20|log10(x)|Returns the base-10 logarithm of x.|
|21|pow(x, y)|Returns x raised to the power y.|
|22|sqrt(x)|Returns the square root of x.|
|23|acos(x)|Returns the arc cosine of x.|
|24|asin(x)|Returns the arc sine of x.|
|25|atan(x)|Returns the arc tangent of x.|
|26|atan2(y, x)|Returns atan(y / x).|
|27|cos(x)|Returns the cosine of x.|
|28|hypot(x, y)|Returns the Euclidean norm, sqrt(x*x + y*y).|
|29|sin(x)|Returns the sine of x.|
|30|tan(x)|Returns the tangent of x.|
|31|degrees(x)|Converts angle x from radians to degrees.|
|32|radians(x)|Converts angle x from degrees to radians.|
|33|acosh(x)|Returns the inverse hyperbolic cosine of x.|
|34|asinh(x)|Returns the inverse hyperbolic sine of x.|
|35|atanh(x)|Returns the inverse hyperbolic tangent of x.|
|36|cosh(x)|Returns the hyperbolic cosine of x.|
|37|sinh(x)|Returns the hyperbolic cosine of x.|
|38|tanh(x)|Returns the hyperbolic tangent of x.|
|39|erf(x)|Returns the error function at x.|
|40|erfc(x)|Returns the complementary error function at x.|
|41|gamma(x)|Returns the Gamma function at x.|
|42|lgamma(x)|Returns the natural logarithm of the absolute value of the Gamma function at x.|
|43|pi|Mathematical constant, the ratio of circumference of a circle to it's diameter (3.14159...)|
|44|e|mathematical constant e (2.71828...)|
|45|tau|mathematical constant tau (6.28318...)|
|46|inf|floating-point positive infinity|
|47|nan|floating-point NaN (not a number)|
|48|isqrt(n)|Returns the integer square root of the nonnegative integer n.|
|49|comb(n, k)|Returns the number of ways to choose k items from n items without repetition and without order.|
|50|perm(n, k)|Returns the number of ways to choose k items from n items without repetition and with order.|

:::tip
More information about the math module can be found [here](https://docs.python.org/3/library/math.html).
:::

