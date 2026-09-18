#!/usr/bin/env python3
"""Delete all locally persisted personal training state (SRS section 7.3: "supports
deletion/reset of locally persisted personal training state").

Usage:
  python reset_state.py --state-dir <state/> [--confirm]

Without --confirm: prints every file that would be deleted and changes nothing.
With --confirm: deletes every file under --state-dir, removing now-empty
subdirectories but keeping --state-dir itself so future writes still have
somewhere to land.

This script makes no judgment about whether deletion is appropriate - that decision
belongs to the skill, which should only invoke --confirm after the user has
explicitly confirmed, in conversation, what is about to be deleted.

Exit codes:
  0 - dry-run listing printed, or deletion completed
  2 - usage/IO error (state-dir not found, not a directory)
"""
import sys
import os
import json
import argparse


def collect_files(state_dir):
    found = []
    for root, _dirs, files in os.walk(state_dir):
        for name in files:
            found.append(os.path.join(root, name))
    return sorted(found)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--confirm", action="store_true")
    try:
        args = parser.parse_args()
    except SystemExit:
        return 2

    if not os.path.isdir(args.state_dir):
        print(f"ERROR: not a directory: {args.state_dir}", file=sys.stderr)
        return 2

    try:
        files = collect_files(args.state_dir)

        if not args.confirm:
            print(json.dumps({"dry_run": True, "would_delete": files}))
            return 0

        for path in files:
            os.remove(path)

        # Remove now-empty subdirectories, deepest first, but keep state-dir itself.
        for root, dirs, _files in os.walk(args.state_dir, topdown=False):
            if root == args.state_dir:
                continue
            if not os.listdir(root):
                os.rmdir(root)

        print(json.dumps({"dry_run": False, "deleted": files}))
    except OSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
