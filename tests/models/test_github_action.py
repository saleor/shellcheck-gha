from pathlib import Path

import pytest

from models.github_action import GitHubYAML, UnknownYAMLFileException


def test_iter_shell_scripts_raises_on_unknown_file_type():
    """
    Ensure when a non-GitHub Composite Action, and a non-GitHub Workflow YAML file
    was parsed, it raises an exception when trying to iterate through the
    shell scripts.
    """

    parsed = GitHubYAML.model_validate({"foo": "bar"})

    with pytest.raises(UnknownYAMLFileException) as exc:
        list(parsed.iter_shell_scripts(Path("dummy")))

    assert exc.value.args == ("The YAML file should contain either 'jobs' or 'runs'.",)
