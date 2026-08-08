# -*- coding: utf-8 -*-
"""scripts/analyse_projects.py — extract an ACCURATE call graph from each project source.

Feeds scripts/gen-project-diagrams.mjs, which decides which pages can carry a
derived mermaid diagram.

PRECISION OVER COVERAGE
-----------------------
An earlier version resolved any `obj.method()` whose name matched a method on any
class in the file. That produced false edges immediately: in
`projects/advance/data_encryption_tool.py` it read `self.fernet.encrypt(...)` --
the cryptography library's method -- as the class calling its own `encrypt`, and
drew a self-loop. A diagram with invented edges is worse than no diagram, so the
resolver now only claims an edge it can actually justify:

  1. `name(...)`            where `name` is a module-level function in this file
  2. `self.name(...)`       where `name` is a method of the ENCLOSING class
  3. `var.name(...)`        where `var` was assigned from `ClassName(...)` in the
                            same scope, and `name` is a method of that class

Anything else -- a library call, an attribute chain, a call on a parameter -- is
left out. Self-loops are dropped: they are almost always case 3 misfiring on a
wrapped library object, and a real recursive call is not worth a diagram edge.

Output: scratch/project-analysis.json
"""
import ast
import json
import os

PROJECT_ROOT = "projects"
OUT = "scratch/project-analysis.json"


class Analyser(ast.NodeVisitor):
    def __init__(self, tree):
        self.functions = {}
        self.classes = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.functions[node.name] = node
            elif isinstance(node, ast.ClassDef):
                self.classes[node.name] = {
                    n.name: n
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
        self.edges = set()

    def _local_instances(self, scope):
        """var -> ClassName, for `var = ClassName(...)` inside this scope."""
        out = {}
        for node in ast.walk(scope):
            if not isinstance(node, ast.Assign):
                continue
            val = node.value
            if isinstance(val, ast.Call) and isinstance(val.func, ast.Name):
                cls = val.func.id
                if cls in self.classes:
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Name):
                            out[tgt.id] = cls
        return out

    def scan(self, owner, scope, enclosing_class=None):
        instances = self._local_instances(scope)
        for node in ast.walk(scope):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func

            # 1. plain module-level function
            if isinstance(fn, ast.Name):
                if fn.id in self.functions:
                    self.edges.add((owner, fn.id))
                continue

            if not isinstance(fn, ast.Attribute):
                continue
            recv = fn.value

            # 2. self.method() inside a class
            if (
                isinstance(recv, ast.Name)
                and recv.id == "self"
                and enclosing_class
                and fn.attr in self.classes.get(enclosing_class, {})
            ):
                self.edges.add((owner, f"{enclosing_class}.{fn.attr}"))
                continue

            # 3. var.method() where var = ClassName(...)
            if isinstance(recv, ast.Name) and recv.id in instances:
                cls = instances[recv.id]
                if fn.attr in self.classes[cls]:
                    self.edges.add((owner, f"{cls}.{fn.attr}"))

    def run(self, tree):
        for name, node in self.functions.items():
            self.scan(name, node)
        for cls, methods in self.classes.items():
            for mname, mnode in methods.items():
                self.scan(f"{cls}.{mname}", mnode, enclosing_class=cls)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            self.scan("__main__", node)
        # drop self-loops -- see the module docstring
        self.edges = {(a, b) for a, b in self.edges if a != b}
        return self


def analyse(path):
    src = open(path, encoding="utf8", errors="ignore").read()
    tree = ast.parse(src)
    a = Analyser(tree).run(tree)
    defs = len(a.functions) + sum(len(m) for m in a.classes.values())
    return {
        "src": path.replace("\\", "/"),
        "defs": defs,
        "functions": sorted(a.functions),
        "classes": {c: sorted(m) for c, m in a.classes.items()},
        "edges": sorted(a.edges),
        "lines": len(src.splitlines()),
    }


def main():
    rows = []
    failed = []
    for root, _, files in os.walk(PROJECT_ROOT):
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            p = os.path.join(root, f)
            try:
                rows.append(analyse(p))
            except SyntaxError as e:
                failed.append((p, str(e)))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf8") as fh:
        json.dump(rows, fh, indent=1)
    print(f"analysed {len(rows)} sources -> {OUT}")
    if failed:
        print(f"{len(failed)} failed to parse:")
        for p, e in failed[:5]:
            print(f"  {p}: {e}")


if __name__ == "__main__":
    main()
