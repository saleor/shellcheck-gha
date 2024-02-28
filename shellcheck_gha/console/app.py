import argparse
import logging
import sys
from pathlib import Path

from shellcheck_gha.console.result_renderer import ResultRenderer
from shellcheck_gha.extractor import Extractor, DEFAULT_SHELL


def parse_args(args: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", default=".github/workflows")
    parser.add_argument(
        "--default-shell",
        help="The default shell running in the workflow(s)",
        # 'bash' assumes GitHub workflow is running on Linux or MacOS,
        # and that 'bash' is in the PATH otherwise it will use 'sh'.
        # If it's running on Windows then it's 'cmd'.
        default=DEFAULT_SHELL,
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show more details about the execution.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Add debug information (takes precedence over --verbose).",
    )
    return parser.parse_args(args)


def main(out=sys.stdout, args: list[str] | None = None) -> None:
    ns = parse_args(args)

    if ns.debug:
        log_level = logging.DEBUG
    elif ns.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if not (directory := Path(ns.directory).absolute()).is_dir():
        sys.stderr.write(f"No such directory {directory}.\n")
        sys.exit(1)

    num_files_scanned, num_snippets_scanned, findings = Extractor(
        directory=directory,
        default_shell=ns.default_shell,
    ).run()

    print(f"=== Results: {len(findings)} file(s) have findings ===")
    print(f"Scanned {num_files_scanned} files ({num_snippets_scanned} shell scripts)")

    for part in ResultRenderer().render(findings):
        out.write(part)

    sys.exit(2 if findings else 0)
