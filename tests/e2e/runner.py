import os
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Sequence, Self
from .result import RunResult


@dataclass
class BinaryRunner:
    """Cross-platform runner for the gitmastery binary."""

    binary_path: str
    project_root: Path

    @classmethod
    def from_env(
        cls,
        env_var: str = "GITMASTERY_BINARY",
        project_root: Optional[Path] = None,
    ) -> Self:
        """Build a runner from an environment variable."""
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]

        raw = os.environ.get(env_var, "").strip()
        if raw:
            binary_path = raw
        else:
            system = platform.system().lower()
            if system == "windows":
                binary_path = str(project_root / "dist" / "gitmastery.exe")
            else:
                binary_path = str(project_root / "dist" / "gitmastery")

        return cls(binary_path=binary_path, project_root=project_root)

    def run(
        self,
        args: Sequence[str] = (),
        *,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        stdin_text: Optional[str] = None,
    ) -> RunResult:
        """Execute the binary with args and return a RunResult."""
        cmd = [self.binary_path] + list(args)
        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        run_env.setdefault("NO_COLOR", "1")
        run_env.setdefault("PYTHONIOENCODING", "utf-8")

        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else str(self.project_root),
            env=run_env,
            capture_output=True,
            text=True,
            timeout=timeout if timeout > 0 else None,
            input=stdin_text,
        )
        return RunResult(
            stdout=proc.stdout,
            stderr=proc.stderr,
            returncode=proc.returncode,
            command=cmd,
        )
