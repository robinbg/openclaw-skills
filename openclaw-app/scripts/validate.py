#!/usr/bin/env python3
"""
OpenClaw Skill Validation - 验证生成的 skill 项目
"""

import sys
from pathlib import Path

def validate_skill(path):
    p = Path(path)
    
    if not (p / "SKILL.md").exists():
        return False, "SKILL.md not found"
    
    content = (p / "SKILL.md").read_text()
    if not content.startswith("---"):
        return False, "Missing YAML frontmatter"
    
    if "name:" not in content[:1000] or "description:" not in content[:1000]:
        return False, "Missing name or description in frontmatter"
    
    for dirname in ["scripts", "references", "assets"]:
        dir_path = p / dirname
        if dir_path.exists():
            print(f"  [OK] {dirname}/ directory exists")
            if any(dir_path.iterdir()):
                print(f"      {dirname}/ contains files")
            else:
                print(f"      {dirname}/ is empty (OK)")
    
    return True, "Skill project looks good!"


def validate_plugin(path):
    p = Path(path)
    
    required = ["index.ts", "package.json"]
    for f in required:
        if not (p / f).exists():
            return False, f"Missing required file: {f}"
    
    import json
    try:
        pkg = json.loads((p / "package.json").read_text())
    except Exception as e:
        return False, f"Invalid package.json: {e}"
    
    if "openclaw" not in pkg or "extensions" not in pkg["openclaw"]:
        return False, "package.json missing openclaw.extensions"
    
    print("  [OK] Plugin structure valid")
    print("  [OK] openclaw.extensions defined")
    
    return True, "Plugin project looks good!"


def validate_web(path):
    p = Path(path)
    
    required = ["package.json", "app/page.tsx", "app/layout.tsx"]
    for f in required:
        if not (p / f).exists():
            return False, f"Missing required file: {f}"
    
    print("  [OK] Next.js structure present")
    
    if (p / ".env.local.example").exists():
        print("  [OK] .env.local.example provided")
    
    return True, "Web project looks good!"


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate.py <project-directory>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: Directory not found: {path}")
        sys.exit(1)
    
    if (path / "SKILL.md").exists():
        validator = validate_skill
        ptype = "skill"
    elif (path / "index.ts").exists() and (path / "package.json").exists():
        validator = validate_plugin
        ptype = "plugin"
    elif (path / "app" / "page.tsx").exists():
        validator = validate_web
        ptype = "web"
    else:
        print("Error: Cannot determine project type")
        sys.exit(1)
    
    print(f"Validating {ptype} project: {path}")
    valid, msg = validator(path)
    print(f"\nResult: {msg}")
    
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()