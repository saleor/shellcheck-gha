from typing import Optional

from pydantic import BaseModel, Field, computed_field


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


class GitHubJob(BaseModel):
    steps: list[GitHubStepRun] = Field(default_factory=list)


class GitHubWorkflow(BaseModel):
    jobs: dict[str, GitHubJob]
