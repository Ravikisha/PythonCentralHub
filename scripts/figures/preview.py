"""Render a figure module to PNG so a human (or Claude) can actually look at it.

The committed artefacts are SVG, which is right for the site and useless for
review — you cannot see an SVG by reading it. This renders the same ``FIGURES``
to PNG in a scratch directory instead.

    python scripts/figures/preview.py dl/phase-01-foundations/activation-functions
    python scripts/figures/preview.py ml/phase-04-classification/decision-trees --out /tmp/x

Defaults to the dark palette, since that is the site's default theme.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _style import DARK, LIGHT, _rc  # noqa: E402


def load(module_path: str):
    """Import a figure module by its ``group/slug`` path."""
    path = os.path.join(HERE, *module_path.split("/"))
    if not path.endswith(".py"):
        path += ".py"
    if not os.path.exists(path):
        raise SystemExit(f"no figure module at {path}")
    directory = os.path.dirname(path)
    sys.path.insert(0, directory)
    sys.path.insert(0, os.path.dirname(directory))
    spec = importlib.util.spec_from_file_location("pchfig_preview", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("module", help="group/slug, e.g. dl/phase-01-foundations/activation-functions")
    parser.add_argument("--out", default=os.environ.get("PCH_PREVIEW_DIR", "figure-preview"))
    parser.add_argument("--light", action="store_true", help="use the light palette")
    parser.add_argument("--dpi", type=int, default=110)
    parser.add_argument("--svg", action="store_true",
                        help="also write the committed dark/light SVG pair, so "
                             "an expensive module is only computed once")
    parser.add_argument("--report", action="store_true",
                        help="also run the module's __main__ block, so one run "
                             "yields the PNG, the SVGs and the printed numbers")
    parser.add_argument("--only", action="append", metavar="FIGURE",
                        help="render only these figures by name; repeatable. "
                             "Use after a cosmetic fix so a legend change does "
                             "not retrain the whole module.")
    args = parser.parse_args()

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    module = load(args.module)
    palette = LIGHT if args.light else DARK
    os.makedirs(args.out, exist_ok=True)

    specs = module.FIGURES
    if args.only:
        wanted = set(args.only)
        specs = [spec for spec in specs if spec.name in wanted]
        missing = wanted - {spec.name for spec in module.FIGURES}
        if missing:
            print(f"no such figure(s): {', '.join(sorted(missing))}")
            return 1

    written = []
    for spec in specs:
        with plt.rc_context(_rc(palette)):
            # Mirror _style.render exactly, so a preview cannot look different
            # from the committed SVG.
            plt.rcParams["axes.prop_cycle"] = plt.cycler(color=palette.cycle)
            fig = plt.figure(figsize=spec.size)
            ax = fig.add_subplot(111) if spec.axes else None
            spec.draw(fig, ax, palette)
            fig.tight_layout()
            target = os.path.join(args.out, f"{spec.name}-{palette.name}.png")
            fig.savefig(target, format="png", dpi=args.dpi, bbox_inches="tight")
            plt.close(fig)
        written.append(target)

    if args.svg:
        # The figure functions are lru_cached inside the module, so rendering
        # the SVGs here reuses the measurements the PNG already paid for.
        from _style import render

        group, slug = args.module.rsplit("/", 1)
        destination = os.path.join(HERE, "..", "..", "public", "images", group,
                                   slug)
        destination = os.path.abspath(destination)
        os.makedirs(destination, exist_ok=True)
        for spec in specs:
            for path in render(spec, destination):
                written.append(path)

    for target in written:
        print(target)

    if args.report:
        # Everything the module measures is lru_cached, so running its
        # __main__ block now reuses the work the figures already paid for.
        import ast as _ast

        path = os.path.join(HERE, *args.module.split("/")) + ".py"
        source = open(path, encoding="utf-8").read()
        tree = _ast.parse(source)
        body = []
        for node in tree.body:
            if (isinstance(node, _ast.If)
                    and _ast.dump(node.test).find("__main__") >= 0):
                body = node.body
        if body:
            print("\n" + "=" * 70)
            exec(compile(_ast.Module(body=body, type_ignores=[]),
                         path, "exec"), module.__dict__)
        else:
            print("no __main__ block found to report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
