---
title: Installation Guide
description: How to install Python and set up your development environment. This guide covers the installation process for Windows, macOS, and Linux.
sidebar: 
    order: 2
---

To get started with Python Central Hub and make the most of our tutorials and projects, you'll need to have Python installed on your machine. Follow these simple steps to install Python and set up your development environment.

## Step 1: Download Python

Visit the official Python website at [python.org](https://www.python.org/) to download the latest version of Python. We recommend downloading the latest stable release for your operating system.

- **Windows:** Download the installer executable and run it.

- **macOS:** Download the macOS installer and follow the installation instructions.

- **Linux:** Most Linux distributions come with Python pre-installed. If not, use your package manager to install Python.

## Step 2: Verify Installation

Once the installation is complete, it's essential to verify that Python has been installed correctly. Open a command prompt (or terminal) and enter the following command:

```bash title="command" showLineNumbers{1}
python --version
```

You should see the Python version number displayed, indicating a successful installation.

## Step 3: Install a Code Editor (Optional)

While Python can be written and run using a simple text editor, using a dedicated code editor can enhance your development experience. Choose a code editor that suits your preferences; popular choices include:

- [Visual Studio Code](https://code.visualstudio.com/)
- [PyCharm](https://www.jetbrains.com/pycharm/)
- [Sublime Text](https://www.sublimetext.com/)

## Step 4: Set Up a Virtual Environment (Optional but Recommended)

To manage project dependencies and ensure a clean development environment, consider setting up a virtual environment. In your project directory, run:

```bash title="command" showLineNumbers{1}
python -m venv venv
```

Activate the virtual environment:

- **On Windows:**
  ```bash title="command" showLineNumbers{1}
  .\venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```bash title="command" showLineNumbers{1}
  source venv/bin/activate
  ```

## Step 5: Ready to Code!

With Python installed and your development environment set up, you're now ready to explore the tutorials and projects on Python Central Hub. Start with our [Introduction to Python](/tutorials/introduction/) tutorial to kick off your Python journey!

If you encounter any issues during the installation process or have questions, feel free to reach out to our community forums for assistance.

Happy coding with Python Central Hub!