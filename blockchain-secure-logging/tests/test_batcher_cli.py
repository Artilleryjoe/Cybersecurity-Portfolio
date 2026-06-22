import subprocess
import sys
from pathlib import Path


def test_batcher_script_help_runs_when_executed_by_path():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "blockchain-secure-logging" / "offchain" / "batcher.py"

    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--config" in result.stdout
    assert "--batch-id" in result.stdout


def test_batcher_script_resolves_sources_relative_to_config(tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    project_root = repo_root / "blockchain-secure-logging"
    script = project_root / "offchain" / "batcher.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--config",
            "offchain/config.yaml",
            "--batch-id",
            "demo",
            "--manifest-dir",
            str(tmp_path),
        ],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "demo.manifest.json").exists()
