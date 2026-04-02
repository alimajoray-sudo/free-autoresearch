#!/usr/bin/env python3
"""
apply-results.py — Apply compression results back to agent workspaces.

Reads the optimized system-prompt.md from each agent project, splits it back
into individual files (SOUL.md, AGENTS.md, etc.), and writes them to the workspace.

Usage:
  python3 scripts/apply-results.py [--agent NAME] [--dry-run] [--min-compression 10]

Safety:
  - Creates timestamped backups before any write
  - Shows diff before applying (--dry-run to preview only)
  - Only applies if compression >= threshold
  - Never writes outside agent workspace directories
"""
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKUP_BASE = Path.home() / ".openclaw" / "workspace-main" / "backups"


def split_combined_prompt(combined: str) -> dict[str, str]:
    """Split a combined system-prompt.md back into individual files."""
    files = {}
    current_file = None
    current_lines = []
    
    for line in combined.split("\n"):
        # Match headers like "# SOUL.md" or "# AGENTS.md"
        m = re.match(r'^# (\w+\.md)$', line)
        if m:
            if current_file:
                files[current_file] = "\n".join(current_lines).strip() + "\n"
            current_file = m.group(1)
            current_lines = []
        else:
            current_lines.append(line)
    
    if current_file:
        files[current_file] = "\n".join(current_lines).strip() + "\n"
    
    return files


def apply_agent(agent_name: str, dry_run: bool = True, min_compression: float = 10.0):
    """Apply compression results for one agent."""
    project_dir = REPO_ROOT / "projects" / f"agent-{agent_name}"
    meta_file = project_dir / "meta.json"
    best_file = project_dir / "best" / "system-prompt.md"
    
    if not meta_file.exists():
        print(f"[{agent_name}] No project found")
        return False
    
    meta = json.loads(meta_file.read_text())
    workspace = Path(meta["workspace"])
    
    if not best_file.exists():
        print(f"[{agent_name}] No best result yet (run autoresearch first)")
        return False
    
    # Calculate compression
    original_size = meta["total_chars"]
    best_text = best_file.read_text()
    compressed_size = len(best_text)
    compression = (1 - compressed_size / original_size) * 100
    
    print(f"[{agent_name}] {original_size:,} → {compressed_size:,} chars ({compression:.1f}% compressed)")
    
    if compression < min_compression:
        print(f"  SKIP: compression {compression:.1f}% < threshold {min_compression}%")
        return False
    
    # Split back into files
    files = split_combined_prompt(best_text)
    
    if not files:
        print(f"  ERROR: Could not split result into files")
        return False
    
    print(f"  Files to update: {', '.join(files.keys())}")
    
    # Show diffs
    for fname, new_content in files.items():
        original = workspace / fname
        if original.exists():
            old_size = len(original.read_text())
            new_size = len(new_content)
            delta = old_size - new_size
            print(f"  {fname}: {old_size:,} → {new_size:,} chars ({'-' if delta > 0 else '+'}{abs(delta)})")
    
    if dry_run:
        print(f"  DRY RUN — no changes written. Use --apply to write.")
        return True
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = BACKUP_BASE / f"pre-apply-{agent_name}-{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for fname in files:
        src = workspace / fname
        if src.exists():
            shutil.copy2(src, backup_dir / fname)
    print(f"  Backup: {backup_dir}")
    
    # Apply
    for fname, new_content in files.items():
        target = workspace / fname
        # Safety: verify target is in workspace
        if not str(target.resolve()).startswith(str(workspace.resolve())):
            print(f"  SAFETY BLOCK: {target} is outside workspace!")
            continue
        target.write_text(new_content)
    
    print(f"  ✓ Applied to {workspace}")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply autoresearch compression results")
    parser.add_argument("--agent", help="Specific agent name")
    parser.add_argument("--all", action="store_true", help="All agents")
    parser.add_argument("--apply", action="store_true", help="Actually write (default: dry run)")
    parser.add_argument("--min-compression", type=float, default=10.0,
                        help="Minimum compression %% to apply (default: 10)")
    args = parser.parse_args()
    
    dry_run = not args.apply
    
    if args.agent:
        apply_agent(args.agent, dry_run=dry_run, min_compression=args.min_compression)
    elif args.all:
        projects = sorted(REPO_ROOT.glob("projects/agent-*"))
        for p in projects:
            name = p.name.replace("agent-", "")
            apply_agent(name, dry_run=dry_run, min_compression=args.min_compression)
            print()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
