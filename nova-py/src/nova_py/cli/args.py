from __future__ import annotations

import logging
from argparse import ArgumentParser
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace
    from typing import Final, TypeVar

    T = TypeVar('T')

LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def loglevel(args: Namespace) -> int:
    if args.debug:
        return logging.DEBUG

    if args.verbose:
        return logging.INFO

    return logging.WARNING


class NOVACLIArgs:
    @cached_property
    def logging_args(self) -> ArgumentParser:
        args = ArgumentParser(add_help=False)
        args.add_argument('--verbose', '-v', default=False, action='store_true', help='Verbose output.')
        args.add_argument('--debug', default=False, action='store_true', help='Debug output.')
        return args
