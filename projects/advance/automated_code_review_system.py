"""
Automated Code Review System

Features:
- Static analysis
- Reporting
- Modular design
- CLI interface
- Error handling
"""
import sys
import os
import re
from collections import defaultdict

class StaticAnalyzer:
    def __init__(self):
        pass
    def analyze(self, file_path):
        with open(file_path, 'r') as f:
            code = f.read()
        issues = []
        if 'import *' in code:
            issues.append('Wildcard import detected')
        if len(code.split('\n')) > 500:
            issues.append('File too long')
        return issues

class StyleChecker:
    def __init__(self):
        pass
    def check(self, file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
        issues = []
        for i, line in enumerate(lines):
            if len(line) > 80:
                issues.append(f'Line {i+1} too long')
            if '\t' in line:
                issues.append(f'Line {i+1} contains tab')
        return issues

class CodeReview:
    def __init__(self):
        self.analyzer = StaticAnalyzer()
        self.style = StyleChecker()
    def review(self, file_path):
        issues = self.analyzer.analyze(file_path)
        issues += self.style.check(file_path)
        return issues
    def report(self, file_path):
        issues = self.review(file_path)
        print(f"Code Review Report for {file_path}:")
        for issue in issues:
            print(f"- {issue}")
        if not issues:
            print("No issues found.")

class CLI:
    @staticmethod
    def run():
        print("Automated Code Review System")
        while True:
            cmd = input('> ')
            if cmd.startswith('review'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: review <file_path>")
                    continue
                file_path = parts[1]
                cr = CodeReview()
                cr.report(file_path)
            elif cmd == 'exit':
                break
            else:
                print("Unknown command")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
