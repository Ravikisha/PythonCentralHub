---
title: Getting Started
description: How to run Python code on your machine. This tutorial covers running Python code using the command line or terminal, creating Python files, and using essential Python commands.
sidebar: 
    order: 3
---

## Running Python on Your Computer

To start coding in Python, you need to have Python installed on your computer. Follow the installation guide on our [Installation Page](/tutorials/installation) if you haven't done so already.

Once Python is installed, you can run Python code using the command line or terminal.

### Using the Command Line or Terminal

1. **Open the Command Line (Windows) or Terminal (macOS/Linux):**
   - **Windows:** Press `Win + R`, type `cmd`, and press Enter.
   - **macOS/Linux:** Use the terminal application.

2. **Navigate to Your Python File's Directory:**
   Use the `cd` command to navigate to the directory where your Python file is located. For example:
   ```bash title="command" showLineNumbers{1}
   cd path/to/your/python/files
   ```

3. **Run Your Python Script:**
   Execute your Python script using the `python` command followed by the filename with the `.py` extension.
   ```bash title="command" showLineNumbers{1}
   python your_script.py
   ```

### Creating Your First Python File

1. **Open a Text Editor:**
   Use a text editor (e.g., Visual Studio Code, Sublime Text, or Notepad) to write your Python code.

2. **Write Your Python Code:**
   Create a simple Python script, for example, a "Hello, World!" program:
   ```python title="main.py" showLineNumbers{1}
   # hello_world.py
   print("Hello, World!")
   ```

3. **Save the File:**
   Save the file with a `.py` extension, such as `hello_world.py`.

4. **Run Your Python Script:**
   Follow the steps mentioned above to navigate to the file's directory in the command line or terminal and run the script.

## Important Python Commands

### Interactive Mode

Python comes with an interactive mode that allows you to execute Python commands line by line.

- **Open Interactive Mode:**
```cmd title="command" showLineNumbers{1} {4}
C:\Users\Your Name>python
Python 3.11.2 (tags/v3.11.2:878ead1, Feb  7 2023, 16:38:35) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> print("Hello, World!")
Hello, World!
```

:::note
You can also use the `py` command to open interactive mode:
```cmd title="command" showLineNumbers{1}
C:\Users\Your Name>py
Python 3.11.2 (tags/v3.11.2:878ead1, Feb  7 2023, 16:38:35) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> print("Hello, World!")
Hello, World!
```

:::

- **Exit Interactive Mode:**
```cmd title="command" showLineNumbers{1}
C:\Users\Your Name>python
Python 3.11.2 (tags/v3.11.2:878ead1, Feb  7 2023, 16:38:35) [MSC v.1934 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> print("Hello, World!")
Hello, World!
>>> exit()
C:\Users\Your Name>
```

### Running a Python File

- **Run a Python Script:**
  ```bash title="command" showLineNumbers{1}
  python your_script.py
  ```

### Virtual Environment

Virtual environments help manage dependencies for different projects.

- **Create a Virtual Environment:**
  ```bash title="command" showLineNumbers{1}
  python -m venv venv
  ```

- **Activate Virtual Environment:**
  - **Windows:**
    ```bash title="command" showLineNumbers{1}
    .\venv\Scripts\activate
    ```
  - **macOS/Linux:**
    ```bash title="command" showLineNumbers{1}
    source venv/bin/activate
    ```

- **Deactivate Virtual Environment:**
  ```bash title="command" showLineNumbers{1}
  deactivate
  ```

### Package Management (pip)

pip is the package installer for Python.

- **Install a Package:**
  ```bash title="command" showLineNumbers{1}
  pip install package_name
  ```

- **Install from Requirements File:**
  ```bash title="command" showLineNumbers{1}
  pip install -r requirements.txt
  ```

This should give you a solid start on running Python code, creating files, and using some essential commands. Explore more with our tutorials on Python Central Hub!
