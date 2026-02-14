#!/usr/bin/env python3
"""
OpenClaw API Reference

When invoked, displays the OpenClaw API reference documentation.
"""

import sys
from pathlib import Path

SKILL_MD = Path(__file__).parent.parent / "SKILL.md"

def main():
    if SKILL_MD.exists():
        print(SKILL_MD.read_text())
    else:
        print("OpenClaw API Reference\n\nNo reference content found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
