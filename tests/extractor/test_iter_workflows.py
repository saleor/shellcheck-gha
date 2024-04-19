from shellcheck_gha.extractor import Extractor


def test_iter_workflows_yaml_files(tmp_path):
    child_dir = tmp_path / "child"
    child_dir.mkdir()

    expected_files = [
        # Ensure root files are matched, and matches both .yaml and .yml extensions.
        tmp_path / "file1.yaml",
        tmp_path / "file2.yml",
        # Ensure children YAML files are matched.
        child_dir / "file3.yaml",
        child_dir / "file4.yml",
    ]

    # Ensure root and children non-YAML files are not matched.
    excluded_files = [tmp_path / "invalid.json", child_dir / "invalid.json"]

    for f in expected_files + excluded_files:
        f.touch(exist_ok=False)

    path_list = list(Extractor(directory=tmp_path).iter_workflow_paths())
    assert list(sorted(path_list)) == list(sorted(expected_files))
