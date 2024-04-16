import pytest
from pydantic import ValidationError

from shellcheck_gha.models.github_action import GitHubYAML


def test_deserialization_raises_on_unknown_file_type():
    """
    Ensure when a non-GitHub Composite Action, and a non-GitHub Workflow YAML file
    was parsed, it raises an exception when deserializing the input.
    """

    with pytest.raises(ValidationError) as exc:
        GitHubYAML.model_validate({"foo": "bar"})
    errors = exc.value.errors()
    assert len(errors) == 1
    assert (
        errors[0]["msg"]
        == "Assertion failed, The YAML file should contain either 'jobs' or 'runs'."
    )
