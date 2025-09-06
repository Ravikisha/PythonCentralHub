"""
Automated Testing Framework

Features:
- Automated test discovery and execution
- Reporting
- Modular design
- CLI interface
- Error handling
"""
import sys
import os
import unittest
import importlib

class TestRunner:
    def __init__(self, test_dir):
        self.test_dir = test_dir
    def discover_and_run(self):
        loader = unittest.TestLoader()
        suite = loader.discover(self.test_dir)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 2:
            print("Usage: python automated_testing_framework.py <test_dir>")
            sys.exit(1)
        test_dir = sys.argv[1]
        runner = TestRunner(test_dir)
        runner.discover_and_run()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
