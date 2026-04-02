#!/usr/bin/env python3
"""
Autoresearch Engine — continuous round-robin experiment runner.
Runs 24/7, discovers projects, cycles through them, never stalls.
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.resolve()
PROJ_DIR   = BASE_DIR / "projects"
LOGS_DIR   = BASE_DIR / "logs"
STATE_DIR  = BASE_DIR / "state"
ENGINE_LOG = LOGS_DIR / "engine.jsonl"
BUDGET_FILE = STATE_DIR / "budget.json"
GEN_PID    = STATE_DIR / "generator.pid"
STOPPED_FILE = STATE_DIR / "engine_stopped.txt"

MIN_INTERVAL_S = 120   # 2 minutes between runs per project
RUN_TIMEOUT_S  = 2400  # 40-minute subprocess timeout (rate-limited free models need time)
BUDGET_SLEEP_S = 3600  # 1 hour when budget exhausted

# ── Shutdown flag ──────────────────────────────────────────────────────────────
_shutdown = False

def _handle_signal(signum, frame):
    global _shutdown
    _shutdown = True

signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT,  _handle_signal)

# ── Helpers ────────────────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def log_event(event: str, project: str = "", **extra):
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    record = {"ts": now_iso(), "event": event, "project": project, **extra}
    with ENGINE_LOG.open("a") as f:
        f.write(json.dumps(record) + "\n")
    print(f"[{record['ts']}] {event} {project} {extra}", flush=True)

def read_score(project_path: Path) -> float:
    score_file = project_path / "best" / "score.txt"
    try:
        return float(score_file.read_text().strip())
    except Exception:
        return 0.0

def read_exp_count(project_path: Path) -> int:
    exp_file = project_path / "experiments.jsonl"
    try:
        with exp_file.open() as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def last_run_file(project_name: str) -> Path:
    return STATE_DIR / f"last_run_{project_name}.txt"

def seconds_since_last_run(project_name: str) -> float:
    lrf = last_run_file(project_name)
    try:
        ts = float(lrf.read_text().strip())
        return time.time() - ts
    except Exception:
        return float("inf")

def mark_last_run(project_name: str):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    last_run_file(project_name).write_text(str(time.time()))

def budget_ok() -> bool:
    try:
        data = json.loads(BUDGET_FILE.read_text())
        return bool(data.get("ok", True))
    except Exception:
        return True  # assume ok if file missing

def discover_projects() -> list[tuple[str, Path]]:
    """Return [(name, path)] for runnable projects."""
    projects = []
    if not PROJ_DIR.exists():
        return projects
    for entry in sorted(PROJ_DIR.iterdir()):
        if not entry.is_dir():
            continue
        # Support both formats:
        # 1. Full engine mode: agent-codex.py + test-set.json (free LLM router)
        # 2. Simple loop mode: program.md + evaluate.sh (ACP/manual)
        has_engine = (entry / "agent-codex.py").exists() and (entry / "test-set.json").exists()
        has_simple = (entry / "program.md").exists() and (entry / "evaluate.sh").exists()
        if has_engine or has_simple:
            projects.append((entry.name, entry))
    return projects

# ── Budget guard ───────────────────────────────────────────────────────────────
def wait_for_budget():
    while not budget_ok():
        log_event("budget_wait", project="", reason="budget ok=false, sleeping 1h")
        for _ in range(BUDGET_SLEEP_S):
            if _shutdown:
                return
            time.sleep(1)

# ── Generator spawn ────────────────────────────────────────────────────────────
def maybe_spawn_generator():
    gen_script = BASE_DIR / "generator.py"
    if not gen_script.exists():
        return

    # Check existing PID
    if GEN_PID.exists():
        try:
            pid = int(GEN_PID.read_text().strip())
            os.kill(pid, 0)  # raises if not running
            return  # already running
        except (ProcessLookupError, ValueError):
            GEN_PID.unlink(missing_ok=True)

    proc = subprocess.Popen(
        [sys.executable, str(gen_script)],
        cwd=str(BASE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    GEN_PID.write_text(str(proc.pid))
    log_event("generator_spawn", project="", pid=proc.pid)

# ── Run a single project ───────────────────────────────────────────────────────
def run_project(name: str, proj_path: Path):
    if _shutdown:
        return

    elapsed = seconds_since_last_run(name)
    if elapsed < MIN_INTERVAL_S:
        log_event("skip", project=name, reason=f"last_run {int(elapsed)}s ago")
        return

    wait_for_budget()
    if _shutdown:
        return

    score_before = read_score(proj_path)
    ts_label = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = LOGS_DIR / f"{name}-{ts_label}.log"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    log_event("run_start", project=name, score_before=score_before,
              experiments=read_exp_count(proj_path))

    t0 = time.time()
    try:
        # Pass --resume if a baseline already exists (avoids re-running 20-30Q baseline every cycle)
        has_baseline = any(
            '"status": "baseline"' in line
            for line in (proj_path / "experiments.jsonl").open()
        ) if (proj_path / "experiments.jsonl").exists() else False
        cmd = [sys.executable, "agent-codex.py", "--max", "10"]
        if has_baseline:
            cmd.append("--resume")
        with log_path.open("w") as log_fh:
            result = subprocess.run(
                cmd,
                cwd=str(proj_path),
                stdout=log_fh,
                stderr=subprocess.STDOUT,
                timeout=RUN_TIMEOUT_S,
            )
        duration = round(time.time() - t0, 1)
        score_after = read_score(proj_path)
        mark_last_run(name)
        log_event("run_done", project=name,
                  score_before=score_before, score_after=score_after,
                  duration_s=duration, returncode=result.returncode)
    except subprocess.TimeoutExpired:
        duration = round(time.time() - t0, 1)
        log_event("run_error", project=name, reason="timeout",
                  score_before=score_before, score_after=score_before,
                  duration_s=duration)
        mark_last_run(name)
    except Exception as exc:
        duration = round(time.time() - t0, 1)
        log_event("run_error", project=name, reason=str(exc),
                  score_before=score_before, score_after=score_before,
                  duration_s=duration)
        mark_last_run(name)

# ── Main loop ──────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Autoresearch Engine")
    parser.add_argument("--once",    action="store_true", help="Run one full cycle then exit")
    parser.add_argument("--project", metavar="NAME",      help="Only run this project")
    parser.add_argument("--dry-run", action="store_true", help="Discover and print projects only")
    args = parser.parse_args()

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    projects = discover_projects()

    if not projects:
        print("No runnable projects found in", PROJ_DIR)
        sys.exit(0)

    if args.project:
        projects = [(n, p) for n, p in projects if n == args.project]
        if not projects:
            print(f"Project '{args.project}' not found or not runnable.")
            sys.exit(1)

    if args.dry_run:
        print(f"Discovered {len(projects)} runnable project(s):")
        for name, path in projects:
            score = read_score(path)
            exps  = read_exp_count(path)
            print(f"  {name:30s}  score={score:.3f}  experiments={exps}  path={path}")
        sys.exit(0)

    log_event("engine_start", project="",
              projects=[n for n, _ in projects], pid=os.getpid())

    cycle = 0
    try:
        while not _shutdown:
            cycle += 1
            log_event("cycle_start", project="", cycle=cycle)

            for name, proj_path in projects:
                if _shutdown:
                    break
                run_project(name, proj_path)

            if not _shutdown:
                maybe_spawn_generator()

            if args.once:
                break

            # Brief pause between cycles to avoid busy-spin when all projects
            # are within their cooldown window
            if not _shutdown:
                time.sleep(30)

    finally:
        STOPPED_FILE.write_text(now_iso())
        log_event("engine_stop", project="", cycle=cycle)
        print("Engine stopped cleanly.", flush=True)

if __name__ == "__main__":
    main()
