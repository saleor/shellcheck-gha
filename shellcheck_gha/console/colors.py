from typing import ClassVar


class Color:
    # List of the SGR parameters for the foreground and background colors.
    # (see https://www.man7.org/linux/man-pages/man4/console_codes.4.html)
    #
    # { <name>: <foreground-code>, ... }
    COLORS: ClassVar[dict[str, int]] = {
        "red": 31,
        "green": 32,
        "yellow": 33,
        "cyan": 36,
        "default": 39,
    }

    DEFAULT_FG_CODE = COLORS["default"]

    @classmethod
    def get_ansi_sequence(cls, attr_code: int) -> str:
        return f"\033[{attr_code}m"

    @classmethod
    def wrap(cls, text, fg_code: int):
        return (
            f"{cls.get_ansi_sequence(fg_code)}"
            f"{text}"
            f"{cls.get_ansi_sequence(cls.DEFAULT_FG_CODE)}"
        )
