from typing import Iterator

import jinja2

from shellcheck_gha.console.colors import Color
from shellcheck_gha.extractor import Finding
from shellcheck_gha.models.shell_check_json1 import ShellCheckComment

TTY_TEMPLATE = """\
{% for finding in findings %}\
{% for comment in finding.shellcheck_data.comments %}\
{% set color = comment.level | level_ansi_code %}\
[{{ comment.level | upper | wrap_color(color) }}] In {{finding.shell_snippet.workflow_path}}:
    Message: {{ comment.message }}
    More information: https://www.shellcheck.net/wiki/SC{{ comment.code }}
    Code:
        {{ finding | extract_code(comment) | indent(8) }}
        {{ ' ' * (comment.column - 1) }}{{ '^' * (comment.endColumn - comment.column + 1) }}
{% endfor %}\
{% endfor %}\
"""

# Maps ASCII control characters (with code points less than 32) to None.
# Used to sanitize untrusted inputs.
ASCII_CONTROL_CODE_TRANSLATION_MAPPING = dict.fromkeys(range(32))


class Safe(str):
    """Marks a string as safe/already escaped."""


class ResultRenderer:
    # Maps the level of the ShellCheck findings into a color code from the SGR
    # 4-bit color range attributes.
    #
    # For more information, refer to:
    # - https://www.man7.org/linux/man-pages/man4/console_codes.4.html
    LEVEL_TO_COLOR = {
        "ERROR": Color.COLORS["red"],
        "WARNING": Color.COLORS["yellow"],
        "INFO": Color.COLORS["cyan"],
    }
    # Fallback value when the level key doesn't exist in `LEVEL_TO_COLOR`.
    FALLBACK_LEVEL_COLOR = Color.COLORS["green"]

    def __init__(self):
        self.jinja_env = jinja2.Environment(
            # Automatic escaping needs to be disabled as Jinja2 only support
            # XML and HTML.
            autoescape=False,
            finalize=self.sanitize,
        )

        self.jinja_env.filters.update(
            **{
                "extract_code": self.extract_matched_code,
                "level_ansi_code": self.level_ansi_code,
                "wrap_color": self.wrap_fg_color,
            }
        )

        self.template = self.jinja_env.from_string(TTY_TEMPLATE)

    @staticmethod
    def strip_control_codes(s: str) -> str:
        """Strips ASCII control characters from a string"""
        return s.translate(ASCII_CONTROL_CODE_TRANSLATION_MAPPING)

    @classmethod
    def sanitize(cls, value: any):
        if isinstance(value, Safe):
            return value
        if isinstance(value, str):
            return cls.strip_control_codes(value)
        return value

    @staticmethod
    def extract_matched_code(
        finding: Finding, shellcheck_comment: ShellCheckComment
    ) -> str:
        """
        Extracts the lines that were found inside a shellcheck comment.
        """
        return "\n".join(
            finding.shell_snippet.step_specs.code_lines[
                shellcheck_comment.line - 1 : shellcheck_comment.endLine
            ]
        )

    @classmethod
    def level_ansi_code(cls, level: str) -> int:
        """Returns the ANSI color code for the given ShellCheck level"""
        return cls.LEVEL_TO_COLOR.get(level.upper(), cls.FALLBACK_LEVEL_COLOR)

    @classmethod
    def wrap_fg_color(cls, text, fg_color_code: int) -> Safe:
        """Wraps the given text with an ANSI color code."""
        return Safe(Color.wrap(text=cls.sanitize(text), fg_code=fg_color_code))

    def render(self, findings: list[Finding]) -> Iterator[str]:
        """
        Render the list of shellcheck findings into a human-readable text.
        """
        return self.template.generate(
            findings=findings,
        )
