import dataclasses
import logging
import subprocess
import sys
from pathlib import Path

import yaml

from shellcheck_gha.models.github_workflow import GitHubWorkflow, GitHubStepRun
from shellcheck_gha.models.shell_check_json1 import ShellCheckOutput

logger = logging.getLogger(__name__)

SUPPORTED_SHELLS = ["sh", "bash", "dash", "ksh"]
DEFAULT_SHELL = "bash"


@dataclasses.dataclass
class ShellSnippet:
    workflow_path: Path

    job_id: str  # The value from jobs.<job_id>.
    step_id: str  # The value from jobs.<job_id>.steps[*].id.
    step_number: int  # The nth position of the step inside the job.

    step_specs: GitHubStepRun

    def __str__(self):
        return f"{self.workflow_path}:jobs.{self.job_id}.steps[{self.step_number}]"


@dataclasses.dataclass
class Finding:
    shellcheck_data: ShellCheckOutput
    shell_snippet: ShellSnippet


@dataclasses.dataclass
class Extractor:
    directory: Path
    default_shell: str = DEFAULT_SHELL

    def iter_workflow_paths(self):
        """Yields all yaml files recursively."""
        for path in self.directory.rglob("*.y[a]ml"):
            if path.is_file() and not path.is_symlink():
                yield path

    @staticmethod
    def iter_shell_scripts(workflow_file: Path):
        """Yields all shell script steps contained within a GitHub workflow YAML file."""
        with workflow_file.open() as fp:
            contents = yaml.safe_load(fp)

        obj = GitHubWorkflow.model_validate(contents)
        for job_id, job_defs in obj.jobs.items():
            for step_num, step in enumerate(job_defs.steps):
                if not step.run:
                    continue

                yield ShellSnippet(
                    workflow_path=workflow_file,
                    job_id=job_id,
                    step_id=step.id,
                    step_number=step_num,
                    step_specs=step,
                )

    def check_snippet(self, snippet: ShellSnippet) -> Finding | None:
        """
        Analyzes a shell snippet from a GitHub workflow using shellcheck.

        Returns None if there are no findings.
        """

        # Assumes GitHub workflow is running on Linux or MacOS.
        # If it's running on Windows then this assumption is wrong as
        # it's 'cmd'.
        shell = snippet.step_specs.shell or self.default_shell

        if shell not in SUPPORTED_SHELLS:
            logger.warning("Unsupported shell '%s' for snippet %s", shell, snippet)
            return None

        proc = subprocess.Popen(
            [
                "shellcheck",
                f"--shell={shell}",
                "--format=json1",
                "-",
            ],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=sys.stderr,
        )

        logger.debug("Running: %r for snippet=%s", proc.args, snippet)
        stdout, stderr = proc.communicate(input=snippet.step_specs.run.encode())
        logger.debug("shellcheck results: stdout=%r, stderr=%r", stdout, stderr)

        if proc.returncode == 0:
            return None
        elif proc.returncode == 1:
            return Finding(
                shellcheck_data=ShellCheckOutput.model_validate_json(stdout),
                shell_snippet=snippet,
            )
        raise RuntimeError(
            f"shellcheck command failed unexpectedly with exit code {proc.returncode}",
            stderr,
        )

    def run(self) -> tuple[int, int, list[Finding]]:
        """
        Scans all GitHub workflow YAML files against shellcheck.

        Returns the number of files scanned, number of shell snippet analyzed,
        and the list of findings.
        """
        findings: list[Finding] = []
        num_files_scanned: int = 0
        num_snippets_scanned: int = 0

        logger.info("Scanning the directory: %s", self.directory)
        for workflow in self.iter_workflow_paths():
            num_files_scanned += 1
            logger.info("Checking the workflow: %s", workflow)

            for snippet in self.iter_shell_scripts(workflow):
                num_snippets_scanned += 1
                finding = self.check_snippet(snippet)

                if finding is not None:
                    findings.append(finding)

        return num_files_scanned, num_snippets_scanned, findings
