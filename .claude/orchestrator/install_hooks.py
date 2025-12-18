#!/usr/bin/env python3
"""
Install Git Hooks for Orchestrator
Copies hook files to .git/hooks/
"""
import shutil
from pathlib import Path


def install_hooks():
    """Install git hooks"""
    project_root = Path(__file__).parent.parent.parent
    hooks_source = Path(__file__).parent / "hooks"
    hooks_dest = project_root / ".git" / "hooks"

    if not hooks_dest.exists():
        print("Error: .git/hooks directory not found")
        print("Make sure you're in a git repository")
        return False

    installed = []
    failed = []

    for hook_file in hooks_source.glob("*"):
        if hook_file.name.startswith("."):
            continue

        dest_file = hooks_dest / hook_file.name

        try:
            shutil.copy2(hook_file, dest_file)

            # Make executable (Unix/Mac)
            if hasattr(os, 'chmod'):
                import stat
                dest_file.chmod(dest_file.stat().st_mode | stat.S_IEXEC)

            installed.append(hook_file.name)
            print(f"[OK] Installed: {hook_file.name}")

        except Exception as e:
            failed.append((hook_file.name, str(e)))
            print(f"[FAIL] Failed: {hook_file.name} - {e}")

    print(f"\nSummary:")
    print(f"   Installed: {len(installed)}")
    print(f"   Failed: {len(failed)}")

    if installed:
        print(f"\n[SUCCESS] Git hooks installed successfully!")
        print(f"   The orchestrator will now run automatically on commits.")

    return len(failed) == 0


if __name__ == "__main__":
    import os
    success = install_hooks()
    exit(0 if success else 1)
