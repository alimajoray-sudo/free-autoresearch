#!/usr/bin/env python3
"""
setup-agent-project.py — Auto-generate autoresearch project for any OpenClaw agent.

Scans the agent's workspace, combines core files, generates a test set based on
file contents, and creates a ready-to-run compression project.

Usage:
  python3 scripts/setup-agent-project.py <workspace-dir> [--name agent-name]
  python3 scripts/setup-agent-project.py --all   # All agents in ~/.openclaw/workspace-*

Creates: projects/<agent-name>/ with system-prompt.md, test-set.json, agent-codex.py
"""
import json
import os
import re
import sys
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "projects" / "system-prompt-compression"
CORE_FILES = ["SOUL.md", "AGENTS.md", "HEARTBEAT.md", "USER.md", "TOOLS.md", "IDENTITY.md"]
MIN_FILE_SIZE = 50  # Skip near-empty files


def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from text for test generation."""
    keywords = set()
    
    # URLs and domains
    for m in re.finditer(r'https?://[^\s\)]+|[\w.-]+\.(org|com|ai|tr|io)', text):
        keywords.add(m.group())
    
    # Port numbers (localhost:XXXX)
    for m in re.finditer(r'(?:localhost|127\.0\.0\.1):(\d{4,5})', text):
        keywords.add(m.group(1))
    
    # Telegram group IDs
    for m in re.finditer(r'-\d{10,}', text):
        keywords.add(m.group())
    
    # Phone numbers
    for m in re.finditer(r'\+\d{10,}', text):
        keywords.add(m.group())
    
    # Quoted strings (names, labels)
    for m in re.finditer(r'"([^"]{3,40})"', text):
        keywords.add(m.group(1))
    
    # Email addresses
    for m in re.finditer(r'[\w.+-]+@[\w.-]+', text):
        keywords.add(m.group())
    
    # Capitalized proper nouns (3+ chars)
    for m in re.finditer(r'\b[A-Z][a-zA-Z]{2,}\b', text):
        w = m.group()
        if w not in {"The", "This", "That", "What", "When", "Where", "How", "You", "Your",
                      "Use", "For", "Not", "All", "Any", "Are", "Can", "Has", "May", "But",
                      "And", "With", "From", "Will", "Run", "Set", "Get", "Put", "New"}:
            keywords.add(w)
    
    # Code identifiers (snake_case, kebab-case)
    for m in re.finditer(r'\b[\w]+-[\w-]+\b|\b\w+_\w+\b', text):
        if len(m.group()) > 5:
            keywords.add(m.group())
    
    return sorted(keywords)


def generate_test_cases(files: dict[str, str]) -> list[dict]:
    """Generate test cases from agent workspace files."""
    tests = []
    test_id = 1
    
    for filename, content in files.items():
        if len(content) < MIN_FILE_SIZE:
            continue
        
        basename = filename.replace(".md", "")
        keywords = extract_keywords(content)
        
        if not keywords:
            continue
        
        # Split into chunks of ~500 chars, generate a test per chunk
        chunks = []
        lines = content.split("\n")
        chunk = []
        chunk_size = 0
        for line in lines:
            chunk.append(line)
            chunk_size += len(line)
            if chunk_size > 400:
                chunks.append("\n".join(chunk))
                chunk = []
                chunk_size = 0
        if chunk:
            chunks.append("\n".join(chunk))
        
        for i, chunk_text in enumerate(chunks[:5]):  # Max 5 tests per file
            chunk_kw = extract_keywords(chunk_text)
            if len(chunk_kw) < 2:
                continue
            
            # Pick 3-5 keywords per test
            selected_kw = chunk_kw[:5]
            
            # Generate a question based on file type
            if basename == "SOUL":
                questions = [
                    "What is this agent's personality?",
                    "How should this agent communicate?",
                    "What are this agent's core values?",
                    "What is this agent's role?",
                    "What boundaries does this agent have?",
                ]
            elif basename == "AGENTS":
                questions = [
                    "What are the agent's core rules?",
                    "How should tasks be delegated?",
                    "What services are configured?",
                    "What commands are available?",
                    "What are the key references?",
                ]
            elif basename == "HEARTBEAT":
                questions = [
                    "What should the heartbeat check?",
                    "When should alerts fire?",
                    "What monitoring tasks exist?",
                    "How often should checks run?",
                    "What are the alert rules?",
                ]
            elif basename == "USER":
                questions = [
                    "Who is the user?",
                    "What are the user's preferences?",
                    "What is the user's professional background?",
                    "What contact info is available?",
                    "What projects is the user working on?",
                ]
            elif basename == "TOOLS":
                questions = [
                    "What tools are available?",
                    "What services run on which ports?",
                    "How do I access external APIs?",
                    "What are the infrastructure endpoints?",
                    "What scripts can I use?",
                ]
            elif basename == "IDENTITY":
                questions = [
                    "What is this agent's identity?",
                ]
            else:
                questions = [f"What does {basename} contain?"]
            
            q = questions[i % len(questions)]
            tests.append({
                "id": test_id,
                "question": q,
                "expected_keywords": selected_kw,
                "category": f"{basename.lower()}-{i+1}",
                "source_file": filename,
            })
            test_id += 1
    
    return tests


def setup_project(workspace_dir: str, agent_name: str = None):
    """Create an autoresearch project for an agent."""
    workspace = Path(workspace_dir).resolve()
    
    if not workspace.exists():
        print(f"ERROR: {workspace} does not exist")
        return False
    
    if not agent_name:
        agent_name = workspace.name.replace("workspace-", "")
    
    project_dir = REPO_ROOT / "projects" / f"agent-{agent_name}"
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Read all core files
    files = {}
    combined = []
    total_chars = 0
    for fname in CORE_FILES:
        fpath = workspace / fname
        if fpath.exists() and fpath.stat().st_size > MIN_FILE_SIZE:
            content = fpath.read_text()
            files[fname] = content
            combined.append(f"# {fname}\n{content}")
            total_chars += len(content)
            print(f"  {fname}: {len(content):,} chars")
    
    if not files:
        print(f"  SKIP: No core files found in {workspace}")
        return False
    
    # Write combined system prompt
    system_prompt = "\n\n".join(combined)
    (project_dir / "system-prompt.md").write_text(system_prompt)
    
    # Generate test set
    tests = generate_test_cases(files)
    (project_dir / "test-set.json").write_text(json.dumps(tests, indent=2))
    
    # Copy agent-codex.py from template (it's generic)
    template_codex = TEMPLATE_DIR / "agent-codex.py"
    if template_codex.exists():
        shutil.copy2(template_codex, project_dir / "agent-codex.py")
    
    # Write project metadata
    meta = {
        "agent": agent_name,
        "workspace": str(workspace),
        "files": list(files.keys()),
        "total_chars": total_chars,
        "test_cases": len(tests),
        "created": __import__("datetime").datetime.now().isoformat(),
    }
    (project_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    
    print(f"  ✓ Project created: {project_dir}")
    print(f"    {total_chars:,} chars, {len(tests)} test cases")
    print(f"    Run: cd {project_dir} && python3 agent-codex.py --hours 6")
    
    return True


def setup_all():
    """Setup projects for all agents."""
    openclaw_dir = Path.home() / ".openclaw"
    workspaces = sorted(openclaw_dir.glob("workspace-*"))
    
    print(f"Found {len(workspaces)} agent workspaces\n")
    
    created = 0
    for ws in workspaces:
        name = ws.name.replace("workspace-", "")
        if "archive" in name:
            print(f"[{name}] SKIP (archive)")
            continue
        
        print(f"[{name}]")
        if setup_project(str(ws), name):
            created += 1
        print()
    
    print(f"Done! Created {created} projects")
    print(f"Run all: python3 engine.py --hours 6")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        setup_all()
    elif len(sys.argv) > 1:
        workspace = sys.argv[1]
        name = None
        if "--name" in sys.argv:
            idx = sys.argv.index("--name")
            name = sys.argv[idx + 1]
        setup_project(workspace, name)
    else:
        print(__doc__)
