#!/usr/bin/env python3
"""
scaffold_exercises.py  (v2 - idempotent, no duplicates)
For every DataCampExercise in the tutorial MDX files:
  * Reads the current code={...} prop
  * Skips it if already scaffolded (starts with "# Task:")
  * Generates a guided scaffold with hints, blanks, expected output
  * Replaces ONLY the code prop (solution/hint/sct left intact)
"""

import re
import ast
from pathlib import Path


def extract_prop(text, prop_name, start=0):
    pat = re.compile(r'\b' + re.escape(prop_name) + r'\s*=\s*\{', re.DOTALL)
    m = pat.search(text, start)
    if not m:
        return None
    brace_open = m.end() - 1
    depth = 0
    i = brace_open
    in_backtick = in_single = in_double = False
    while i < len(text):
        ch = text[i]
        esc = i > 0 and text[i - 1] == '\\'
        if ch == '`' and not in_single and not in_double and not esc:
            in_backtick = not in_backtick
        elif ch == "'" and not in_backtick and not in_double and not esc:
            in_single = not in_single
        elif ch == '"' and not in_backtick and not in_single and not esc:
            in_double = not in_double
        elif not in_backtick and not in_single and not in_double:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return text[brace_open + 1:i], m.start(), i + 1
        i += 1
    return None


def js_string_value(raw):
    v = raw.strip()
    if v.startswith('`') and v.endswith('`'):
        return v[1:-1]
    if v.startswith("'") and v.endswith("'"):
        return v[1:-1].replace("\\'", "'")
    if v.startswith('"') and v.endswith('"'):
        return v[1:-1].replace('\\"', '"')
    return v


def expected_output(code):
    results = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return results
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            fn = call.func
            name = fn.id if isinstance(fn, ast.Name) else (
                fn.attr if isinstance(fn, ast.Attribute) else '')
            if name != 'print':
                continue
            parts = []
            ok = True
            for arg in call.args:
                if isinstance(arg, ast.Constant):
                    parts.append(str(arg.value))
                else:
                    ok = False
                    break
            sep = ' '
            for kw in call.keywords:
                if kw.arg == 'sep' and isinstance(kw.value, ast.Constant):
                    sep = str(kw.value.value)
            if ok and parts:
                results.append(sep.join(parts))
    return results


def build_scaffold(solution, hint_text, title):
    lines = solution.strip().split('\n')
    out = []

    task = title.strip() if title else "Complete the exercise"
    out.append(f"# Task: {task}")
    out.append("# Follow the steps below and fill in the blanks.")
    out.append("# Use the 'Solution' button only after you have tried! and check the hints. (Use Hint to unlock the Solution)")
    out.append("")

    has_class  = any(l.strip().startswith('class ')  for l in lines)
    has_def    = any(l.strip().startswith('def ')    for l in lines)
    has_for    = any(l.strip().startswith('for ')    for l in lines)
    has_while  = any(l.strip().startswith('while ')  for l in lines)
    has_if     = any(l.strip().startswith('if ')     for l in lines)
    has_import = any(l.strip().startswith('import ') or
                     l.strip().startswith('from ')   for l in lines)
    has_print  = any('print(' in l                   for l in lines)
    has_return = any(l.strip().startswith('return ') for l in lines)
    has_super  = any('super()' in l                  for l in lines)
    has_lambda = any('lambda' in l                   for l in lines)
    has_lcomp  = any('[' in l and ' for ' in l       for l in lines)
    has_dcomp  = any('{' in l and ' for ' in l       for l in lines)

    hints = []
    hint_clean = hint_text.strip().strip('`"\' ') if hint_text else ""

    if has_import:
        hints.append("# Hint: Add the import statement(s) at the very top of your code.")
    if has_class:
        hints.append("# Hint: Define the class using 'class ClassName:' -- remember the colon!")
    if has_def:
        hints.append("# Hint: Use 'def function_name(param1, param2):' to define a function.")
    if has_super:
        hints.append("# Hint: Call the parent constructor with super().__init__(arg1, arg2, ...).")
    if has_for:
        hints.append("# Hint: 'for item in iterable:' iterates over each element in sequence.")
    if has_while:
        hints.append("# Hint: Update the loop variable inside the while loop to avoid infinite loops!")
    if has_if:
        hints.append("# Hint: Structure: if condition: / elif condition: / else:")
    if has_lambda:
        hints.append("# Hint: Lambda syntax: lambda args: expression  (single-line function)")
    if has_lcomp:
        hints.append("# Hint: List comprehension: [expression for item in iterable if condition]")
    if has_dcomp:
        hints.append("# Hint: Dict comprehension: {key: value for item in iterable}")
    if has_return:
        hints.append("# Hint: The return statement sends a value back -- place it at the end of the function.")
    if has_print:
        hints.append("# Hint: print(value) displays output; print(a, b) prints multiple values.")
    if hint_clean:
        hints.append(f"# Hint: {hint_clean}")
    hints.append("# Hint: Run after every change -- small steps are easier to debug!")
    hints.append("# Hint: Read error messages carefully -- they point to the exact line.")

    seen_h = set()
    unique_hints = []
    for h in hints:
        if h not in seen_h:
            seen_h.add(h)
            unique_hints.append(h)
    hints = unique_hints[:6]

    code_positions = [i for i, l in enumerate(lines)
                      if l.strip() and not l.strip().startswith('#')]
    hint_at = {}
    if hints and code_positions:
        step = max(1, len(code_positions) // len(hints))
        for k in range(min(len(hints), len(code_positions))):
            idx = code_positions[k * step]
            hint_at[idx] = hints[k]

    hint_used = set()

    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip())
        ind = ' ' * indent

        if idx in hint_at and idx not in hint_used:
            out.append(ind + hint_at[idx])
            hint_used.add(idx)

        if not stripped or stripped.startswith('#'):
            out.append(raw)
            continue

        if stripped.startswith('import ') or stripped.startswith('from '):
            out.append(raw)
            out.append(ind + "# Above import is provided -- understand what it brings in.")
            continue

        if re.match(r'class\s+\w+', stripped):
            out.append(raw)
            out.append(ind + "    # Step: Define the class body (attributes, __init__, methods).")
            continue

        if re.match(r'def\s+\w+\s*\(', stripped):
            out.append(raw)
            out.append(ind + "    # Step: Write the function body here.")
            out.append(ind + "    pass  # remove 'pass' and add your code")
            continue

        if stripped.startswith('return '):
            expr = stripped[7:].strip()[:50]
            out.append(ind + "# Step: Return the computed result.")
            out.append(ind + f"# return ___  (should be something like: {expr})")
            continue

        if re.match(r'print\s*\(', stripped):
            inner_m = re.match(r'print\s*\((.*)\)\s*$', stripped, re.DOTALL)
            inner = inner_m.group(1).strip()[:60] if inner_m else '...'
            out.append(ind + "# Step: Call print() with the right argument(s).")
            out.append(ind + f"# Example structure: print({inner})")
            out.append(ind + "print(___)  # replace ___ with the correct expression")
            continue

        if re.match(r'for\s+.+\s+in\s+.+:', stripped):
            out.append(ind + "# Step: Write a for loop -- 'for <variable> in <iterable>:'")
            out.append(raw)
            continue

        if re.match(r'while\s+.+:', stripped):
            out.append(ind + "# Step: Write a while loop -- remember to update the loop variable!")
            out.append(raw)
            continue

        if re.match(r'(if|elif)\s+.+:|^else\s*:', stripped):
            out.append(raw)
            continue

        if re.match(r'super\(\)', stripped):
            out.append(ind + "# Step: Call the parent constructor via super().__init__(...).")
            out.append(ind + "# super().__init__(___)  fill in the parent's required arguments")
            continue

        assign_m = re.match(r'([\w.]+(?:\[.+?\])?)\s*=\s*(.+)', stripped)
        if assign_m and not stripped.startswith('=='):
            lhs = assign_m.group(1)
            rhs = assign_m.group(2).strip()
            type_hint = ""
            if rhs.startswith('['):
                type_hint = " (a list)"
            elif rhs.startswith('{'):
                type_hint = " (a dict or set)"
            elif rhs.startswith('('):
                type_hint = " (a tuple or function call)"
            elif rhs in ('True', 'False'):
                type_hint = " (True or False)"
            elif rhs.startswith(('"', "'")):
                type_hint = " (a string)"
            elif re.match(r'\d', rhs):
                type_hint = " (a number)"
            out.append(ind + f"# Step: Assign the correct value{type_hint} to '{lhs}'.")
            out.append(ind + f"{lhs} = ___  # replace ___ with the correct value")
            continue

        out.append(ind + "# Step: Write the required code here.")
        out.append(ind + "# " + stripped[:80])
        out.append(ind + "# replace the comment above with working code")

    unused = [h for k, h in hint_at.items() if k not in hint_used]
    if unused:
        out.append("")
        for h in unused:
            out.append(h)

    out_lines = expected_output(solution)
    out.append("")
    out.append("# ── Expected Output ──────────────────────────────────────────")
    if out_lines:
        for ol in out_lines:
            out.append(f"# {ol}")
    else:
        out.append("# (Run your completed code to check the output)")
    out.append("# ──────────────────────────────────────────────────────────────")

    return '\n'.join(out)


HEADING_RE = re.compile(r'###\s+(.+)', re.MULTILINE)
DCE_OPEN_RE = re.compile(r'<DataCampExercise\b', re.DOTALL)


def process_file(path):
    original = path.read_text(encoding='utf-8')
    text = original
    result = []
    pos = 0
    count = 0

    while True:
        m = DCE_OPEN_RE.search(text, pos)
        if not m:
            result.append(text[pos:])
            break

        result.append(text[pos:m.start()])

        preceding = text[:m.start()]
        hms = list(HEADING_RE.finditer(preceding))
        exercise_title = hms[-1].group(1).strip() if hms else ""

        close_m = re.search(r'/>', text[m.start():], re.DOTALL)
        if not close_m:
            result.append(text[m.start():])
            break
        comp_end = m.start() + close_m.end()
        comp_text = text[m.start():comp_end]

        code_info = extract_prop(comp_text, 'code')
        if code_info is None:
            result.append(comp_text)
            pos = comp_end
            continue

        raw_code, c_start, c_end = code_info
        current_code = js_string_value(raw_code)

        if current_code.strip().startswith('# Task:'):
            result.append(comp_text)
            pos = comp_end
            continue

        hint_info = extract_prop(comp_text, 'hint')
        hint_text = js_string_value(hint_info[0]) if hint_info else ""

        scaffold = build_scaffold(current_code, hint_text, exercise_title)
        scaffold_js = scaffold.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

        new_code_prop = 'code={`' + scaffold_js + '`}'
        new_comp = comp_text[:c_start] + new_code_prop + comp_text[c_end:]

        result.append(new_comp)
        pos = comp_end
        count += 1

    new_text = ''.join(result)
    if new_text != original:
        path.write_text(new_text, encoding='utf-8')
        print(f"  checkmark  {path.relative_to(Path('/home/ravi/Desktop/PythonCentralHub'))}  ({count} exercise(s))")
    return count


if __name__ == '__main__':
    base = Path('/home/ravi/Desktop/PythonCentralHub')
    tutorials = base / 'src/content/docs/tutorials'
    mdx_files = sorted(tutorials.rglob('*.mdx'))
    print(f"Scanning {len(mdx_files)} MDX files ...\n")
    total_files = total_ex = 0
    for f in mdx_files:
        n = process_file(f)
        if n:
            total_files += 1
            total_ex += n
    print(f"\nDone -- {total_ex} exercise(s) scaffolded across {total_files} file(s).")
