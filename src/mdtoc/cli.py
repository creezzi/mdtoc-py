import argparse
import sys

from . import build_toc, update


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="mdtoc", description="Generate a Markdown table of contents.")
    parser.add_argument("path")
    parser.add_argument("--write", action="store_true", help="update the file between toc markers")
    parser.add_argument("--max-level", type=int, default=3)
    args = parser.parse_args(argv)
    with open(args.path, encoding="utf-8") as f:
        text = f.read()
    if args.write:
        try:
            result = update(text, args.max_level)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        with open(args.path, "w", encoding="utf-8") as f:
            f.write(result)
    else:
        print(build_toc(text, args.max_level))
    return 0


if __name__ == "__main__":
    sys.exit(main())
