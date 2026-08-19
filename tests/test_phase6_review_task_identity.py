from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HARDENED = REPO_ROOT / "phase6" / "scriptops-v2-hardening.py"


def run(cmd: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)
    if result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


class ReviewTaskIdentityTests(unittest.TestCase):
    def test_two_immediate_reviews_get_distinct_task_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = os.environ.copy()
            env.update(
                GIT_AUTHOR_NAME="ScriptOps Task Identity Test",
                GIT_AUTHOR_EMAIL="task-id@example.invalid",
                GIT_COMMITTER_NAME="ScriptOps Task Identity Test",
                GIT_COMMITTER_EMAIL="task-id@example.invalid",
                PYTHONDONTWRITEBYTECODE="1",
            )

            subprocess.run(["git", "init"], cwd=root, env=env, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "ScriptOps Task Identity Test"], cwd=root, env=env, check=True)
            subprocess.run(["git", "config", "user.email", "task-id@example.invalid"], cwd=root, env=env, check=True)
            (root / "tasks").mkdir(parents=True, exist_ok=True)
            (root / "seed.txt").write_text("seed\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, env=env, check=True)
            subprocess.run(["git", "commit", "-m", "seed"], cwd=root, env=env, check=True, capture_output=True)

            first = run([sys.executable, str(HARDENED), "review", "--scene", "SCN-012"], root, env)
            second = run([sys.executable, str(HARDENED), "review", "--scene", "SCN-027"], root, env)

            first_id = re.search(r"TASK-[0-9]{14}", first.stdout)
            second_id = re.search(r"TASK-[0-9]{14}", second.stdout)
            self.assertIsNotNone(first_id, first.stdout)
            self.assertIsNotNone(second_id, second.stdout)
            self.assertNotEqual(first_id.group(0), second_id.group(0))

            packs = sorted((root / "tasks").glob("TASK-*/task-pack.yaml"))
            self.assertEqual(len(packs), 2)
            first_text = packs[0].read_text(encoding="utf-8")
            second_text = packs[1].read_text(encoding="utf-8")
            self.assertNotEqual(first_text, second_text)
            combined = first_text + second_text
            self.assertIn("scene_id: SCN-012", combined)
            self.assertIn("scene_id: SCN-027", combined)

            status = subprocess.run(
                ["git", "status", "--porcelain=v1"],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertEqual(status.stdout.strip(), "")

            print(
                "PHASE6_TASK_IDENTITY: TWO_IMMEDIATE_REVIEWS=DISTINCT; "
                "EXISTING_TASK_OVERWRITE=PREVENTED; WORKTREE=CLEAN"
            )


if __name__ == "__main__":
    unittest.main()
