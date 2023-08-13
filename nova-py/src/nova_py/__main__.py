from __future__ import annotations

import logging
from argparse import ArgumentParser
from typing import TYPE_CHECKING, Final

from .audio import AudacityController
from .cli.args import LOG_FORMAT, NOVACLIArgs, loglevel

if TYPE_CHECKING:
    from argparse import Namespace


_LOGGER: Final = logging.getLogger(__name__)


def main() -> None:
    parser = _create_argument_parser()
    args = parser.parse_args()
    logging.basicConfig(level=loglevel(args), format=LOG_FORMAT)

    executor_name = 'exec_' + args.command.lower().replace('-', '_')
    if executor_name not in globals():
        raise AssertionError(f'Unimplemented command: {args.command}')

    execute = globals()[executor_name]
    execute(args)


def exec_start(args: Namespace) -> None:
    controller = AudacityController()
    controller.start_audacity()
    with controller.opened_pipes():
        controller.stop_audacity()


def _create_argument_parser() -> ArgumentParser:
    nova_cli_args = NOVACLIArgs()
    nova_py_args = ArgumentParser()
    nova_py_args_command = nova_py_args.add_subparsers(dest='command', required=True)

    nova_py_args_command.add_parser(
        'start',
        help='Start Audacity.',
        parents=[nova_cli_args.logging_args],
    )

    return nova_py_args


if __name__ == '__main__':
    main()
