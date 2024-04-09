import dataclasses
from pathlib import Path
from typing import Optional, Generator

from pydantic import BaseModel, Field, computed_field


class UnknownYAMLFileException(Exception):
    """
    An exception raised when the parsed YAML file does not appear to be either
    a GitHub Workflow, or a GitHub Composite Action.
    """


@dataclasses.dataclass
class ShellSnippet:
    yaml_path: Path
    step_specs: "GitHubStepRun"


class GitHubStepRun(BaseModel):
    id: Optional[str] = None

    # Note: only 'run' or 'uses' can be passed, not both.
    # But that rule is omitted for simplicity.
    uses: Optional[str] = None
    run: Optional[str] = None

    # - 'bash' is the default on Linux and MacOS platform,
    #   unless 'bash' isn't in the PATH, then it's 'sh'.
    # - 'cmd' is the default on Windows.
    shell: Optional[str] = None

    @computed_field
    def code_lines(self) -> list[str]:
        if self.run is None:
            return []
        return self.run.splitlines(keepends=False)


class GitHubSteps(BaseModel):
    steps: list[GitHubStepRun] = Field(default_factory=list)

    def iter_shell_scripts(
        self, yaml_path: Path
    ) -> Generator[ShellSnippet, None, None]:
        for step in self.steps:
            # Skip if 'run' is not defined as it means it is not a shell script
            # but rather an action reference (e.g., 'actions/checkout' step).
            if not step.run:
                continue

            yield ShellSnippet(
                yaml_path=yaml_path,
                step_specs=step,
            )


class GitHubYAML(BaseModel):
    """Pydantic model for both a GitHub Workflow, and a Composite GitHub Action."""

    jobs: Optional[dict[str, GitHubSteps]] = None
    runs: Optional[GitHubSteps] = None

    def iter_shell_scripts(
        self, yaml_path: Path
    ) -> Generator[ShellSnippet, None, None]:
        if self.jobs:
            for job in self.jobs.values():
                for snippet in job.iter_shell_scripts(yaml_path):
                    yield snippet
        elif self.runs:
            for snippet in self.runs.iter_shell_scripts(yaml_path):
                yield snippet
        else:
            # This code should never be reached unless a non-GitHub workflow or action
            # YAML file was provided to the CLI.
            raise UnknownYAMLFileException(
                "The YAML file should contain either 'jobs' or 'runs'.",
                yaml_path,
            )
