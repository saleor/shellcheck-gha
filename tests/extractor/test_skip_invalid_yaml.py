# TODO: add test case that ensures it raises an exception if a YAML file is not YAML.
import pytest
import yaml.parser

from shellcheck_gha.extractor import Extractor
from shellcheck_gha.models.github_action import UnknownYAMLFileException


def test_skips_yaml_unsupported_files(tmp_path):
    """
    When an unknown YAML file (non-GitHub workflow and non-composite action YAML)
    is passed and ``raise_on_unsupported_yaml`` is set to ``False``
    it shouldn't raise an exception, instead it should skip the file
    and proceed to the next YAML files.
    """

    invalid_yaml_file = tmp_path / "invalid.yaml"
    invalid_yaml_file.write_text("{}")

    valid_yaml = tmp_path / "valid.yaml"
    valid_yaml.write_text(
        """\
runs:
  using: "composite"
  steps:
    - run: echo $BAD_COMPOSITE_ACTION
      shell: bash
    - run: echo "$GOOD_COMPOSITE_ACTION"
      shell: bash
"""
    )

    extractor = Extractor(
        directory=tmp_path,
        raise_on_unsupported_yaml=True,
    )

    # Should raise when ``raise_on_unsupported_yaml=True``.
    with pytest.raises(UnknownYAMLFileException):
        extractor.run()

    # Shouldn't raise when ``raise_on_unsupported_yaml=False``.
    extractor.raise_on_unsupported_yaml = False
    scanned_file_count, scanned_snippet_count, findings = extractor.run()
    assert scanned_file_count == 1, "shouldn't count invalid.yaml"
    assert scanned_snippet_count == 2
    assert len(findings) == 1


@pytest.mark.parametrize("raise_on_unsupported_yaml", [True, False])
def test_raises_on_invalid_yaml_syntax(tmp_path, raise_on_unsupported_yaml):
    """
    When an invalid YAML file syntax is passed, it should raise an exception
    even if ``raise_on_unsupported_yaml=False``.
    """

    invalid_yaml_file = tmp_path / "invalid.yaml"
    invalid_yaml_file.write_text("- a\nb: c")

    extractor = Extractor(
        directory=tmp_path,
        raise_on_unsupported_yaml=raise_on_unsupported_yaml,
    )

    with pytest.raises(yaml.parser.ParserError):
        extractor.run()
