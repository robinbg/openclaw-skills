#!/usr/bin/env python3
"""
OpenClaw Skill Packager - 打包 skill 为 .skill 文件
"""

import json
import sys
import zipfile
from pathlib import Path

def validate_skill_structure(path):
    p = Path(path)
    if not (p / "SKILL.md").exists():
        return False, "SKILL.md missing"
    content = (p / "SKILL.md").read_text()
    if not content.startswith("---"):
        return False, "SKILL.md missing YAML frontmatter"
    return True, "Valid skill structure"


def package_skill(skill_path, output_dir=None):
    skill_path = Path(skill_path).resolve()
    
    if not skill_path.exists():
        print(f"[ERROR] Skill folder not found: {skill_path}")
        return None
    
    if not (skill_path / "SKILL.md").exists():
        print(f"[ERROR] SKILL.md not found in {skill_path}")
        return None
    
    print("Validating...")
    valid, msg = validate_skill_structure(skill_path)
    if not valid:
        print(f"[ERROR] {msg}")
        return None
    print(f"[OK] {msg}\n")
    
    output_path = Path(output_dir) if output_dir else Path.cwd()
    output_path.mkdir(parents=True, exist_ok=True)
    
    skill_file = output_path / f"{skill_path.name}.skill"
    
    print(f"Packaging to {skill_file}...")
    with zipfile.ZipFile(skill_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path.parent)
                zipf.write(file_path, arcname)
                print(f"  + {arcname}")
    
    print(f"\n✅ Packaged: {skill_file}")
    return skill_file


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_app.py <skill-folder> [output-dir]")
        print("\nExample:")
        print("  python package_app.py my-skill")
        print("  python package_app.py my-skill ./dist")
        sys.exit(1)
    
    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = package_skill(skill_path, output_dir)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()