from __future__ import annotations

import logging
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
from typing import TYPE_CHECKING, Final

from .audio.controller import AudacityController
from .cli.args import LOG_FORMAT, NOVACLIArgs, loglevel
from .scenario import Scenario
from .utils import get_input_path
from .visual.image import Controller

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


def exec_process(args: Namespace) -> None:
    input_dir: Path = args.input.resolve() if args.input is not None else get_input_path()
    args.output.resolve()
    scenario: Scenario = args.scenario

    audioController = AudacityController()
    audioController.start_audacity()
    audioController.import_audio(scenario.value['soundtrack'])
    audioController.import_audio_batch(input_dir=input_dir)
    for track_id, timestamp in scenario.value['timestamps']:
        audioController.move_audio_clip(track=track_id, destination_start=timestamp, destination_end=timestamp + 15)
    audioController.select_all()
    audioController.export_audio(output_path=scenario.value['output'])
    audioController.select_tracks(track=0, count=audioController._total_tracks)
    audioController.remove_tracks()
    audioController.stop_audacity()


def exec_visual(args: Namespace) -> None:
    args.output
    controller = Controller()
    controller.read_files(Path(args.input))
    controller.process_heic_files()


def _create_argument_parser() -> ArgumentParser:
    def scenario_type(arg: str) -> Scenario:
        try:
            return Scenario[arg.upper()]
        except KeyError:
            raise ArgumentTypeError(f'Invalid scenario: {arg}. Expected one of: {[str(e) for e in Scenario]}')

    nova_cli_args = NOVACLIArgs()
    nova_py_args = ArgumentParser()
    nova_py_args_command = nova_py_args.add_subparsers(dest='command', required=True)

    main_parser = nova_py_args_command.add_parser(
        'process',
        help='Start processing photos and voice recordings.',
        parents=[nova_cli_args.logging_args],
    )

    main_parser.add_argument(
        '--scenario',
        type=scenario_type,
        choices=list(Scenario),
        required=True,
        help='The scenario to process during startup.',
    )

    main_parser.add_argument('--output', type=Path, required=True, help='Path to Resolume Composition.')

    main_parser.add_argument('--input', type=Path, help='[Optional] Path to the input files.')
    return nova_py_args


if __name__ == '__main__':
    main()
