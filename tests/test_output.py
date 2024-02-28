from shellcheck_gha.console.result_renderer import ResultRenderer
from shellcheck_gha.extractor import Extractor
from . import sample_workflows


def test_render_findings_human():
    scanned_file_count, scanned_snippet_count, findings = Extractor(
        directory=sample_workflows.PATH
    ).run()

    assert scanned_file_count == 1

    # The number of shell scripts within all found workflows.
    assert scanned_snippet_count == 4

    assert len(findings) == 2

    actual = "".join(ResultRenderer().render(findings))
    expected = f"""\
[\x1b[36mINFO\x1b[39m] In {sample_workflows.PATH / "with-findings.yaml"}:
    Message: Double quote to prevent globbing and word splitting.
    More information: https://www.shellcheck.net/wiki/SC2086
    Code:
        echo $BAD_JOB1
             ^^^^^^^^^^
[\x1b[36mINFO\x1b[39m] In {sample_workflows.PATH / "with-findings.yaml"}:
    Message: Double quote to prevent globbing and word splitting.
    More information: https://www.shellcheck.net/wiki/SC2086
    Code:
        echo $BAD_JOB2
             ^^^^^^^^^^
"""
    assert actual == expected
