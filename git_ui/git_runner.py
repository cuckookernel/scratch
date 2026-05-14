import subprocess
import os

class GitRunner:
    @staticmethod
    def run(args: list[str]) -> tuple[int, str, str]:
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    @staticmethod
    def get_status_groups() -> dict[str, list[str]]:
        # Using core.quotepath=false to get clean paths (no quotes for spaces)
        _, stdout, _ = GitRunner.run(["git", "-c", "core.quotepath=false", "status", "--porcelain"])

        groups = {"untracked": [], "modified": [], "added": []}
        for line in stdout.splitlines():
            if not line:
                continue
            status = line[:2]
            path = line[3:].strip()

            if status == "??":
                groups["untracked"].append(path)
            elif status[0] in "MADR" and status[1] == " ":
                groups["added"].append(path)
            elif status[1] in "MA" or status[0] == " ":
                groups["modified"].append(path)

        return groups

    @staticmethod
    def get_branch_name() -> str:
        _, stdout, _ = GitRunner.run(["git", "branch", "--show-current"])
        return stdout.strip() or "Detached HEAD"

    @staticmethod
    def get_all_branches() -> list[str]:
        # Get local branches
        _, stdout, _ = GitRunner.run(["git", "branch", "--format=%(refname:short)"])
        return [line.strip() for line in stdout.splitlines() if line.strip()]

    @staticmethod
    def get_diff(path: str | None = None, cached: bool = False) -> str:
        cmd = ["git", "diff", "--color=always"]
        if cached:
            cmd.append("--cached")
        if path:
            cmd.append(path)
        _, stdout, _ = GitRunner.run(cmd)
        return stdout

    @staticmethod
    def get_blame(path: str) -> str:
        _, stdout, _ = GitRunner.run(["git", "blame", "--color=always", path])
        return stdout
