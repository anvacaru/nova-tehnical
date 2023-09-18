from __future__ import annotations

import logging
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
from typing import TYPE_CHECKING, Final

from .audio.controller import AudacityController
from .cli.args import LOG_FORMAT, NOVACLIArgs, loglevel
from .scenario import Scenario
from .utils import get_input_path
from .visual.image import VisualController

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
    audio_processing(input_dir=input_dir, scenario=args.scenario)
    visual_processing(input_dir=input_dir, scenario=args.scenario)


def audio_processing(input_dir: Path, scenario: Scenario) -> None:
    audioController = AudacityController()
    audioController.start_audacity()
    audioController.import_audio_batch(input_dir=input_dir)
    audio_map = scenario.value['audio_map']
    for track_id in audio_map.keys():
        audioController.move_audio_clip(track=track_id, destinations=audio_map[track_id], duration=15)
    audioController.select_all()
    audioController.add_reverb_largeroom()
    audioController.select(start=0, end=600, track=0, count=audioController._total_tracks)
    audioController.export_audio()
    audioController.remove_tracks()
    audioController.stop_audacity()


def visual_processing(input_dir: Path, scenario: Scenario) -> None:
    visualController = VisualController()
    visualController.read_files(input_dir=input_dir, expected=len(scenario.value['img_names']))
    visualController.process_files(img_names=scenario.value['img_names'], output_dir=scenario.value['output'])


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

    main_parser.add_argument('--input', type=Path, help='[Optional] Path to the input files.')
    return nova_py_args


if __name__ == '__main__':
    main()
