from __future__ import annotations

import logging
from argparse import ArgumentParser, ArgumentTypeError
from typing import TYPE_CHECKING, Final

from .audio import AudacityController
from .cli.args import LOG_FORMAT, NOVACLIArgs, loglevel
from .scenario import Scenario

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
        controller.import_audio(args.scenario.value['soundtrack'])
        controller.import_audio_batch(args.scenario.value['recordings'])
        controller.import_audio('/Users/anvacaru/Desktop/dev/nova-tehnical/audio/recordings/voice_0.wav')
        for track_id, timestamp in args.scenario.value['timestamps']:
            controller.move_audio_clip(track=track_id, destination_start=timestamp, destination_end=timestamp + 15)
        controller.select_all()
        controller.export_audio(output_path='/Users/anvacaru/Desktop/dev/nova-tehnical/audio/seascape_final_1.mp3')
        controller.select_tracks(track=0, count=controller._total_tracks)
        controller.remove_tracks()
        controller.stop_audacity()


def _create_argument_parser() -> ArgumentParser:
    def scenario_type(arg: str) -> Scenario:
        try:
            return Scenario[arg.upper()]
        except KeyError:
            raise ArgumentTypeError(f'Invalid scenario: {arg}. Expected one of: {[str(e) for e in Scenario]}')

    nova_cli_args = NOVACLIArgs()
    nova_py_args = ArgumentParser()
    nova_py_args_command = nova_py_args.add_subparsers(dest='command', required=True)

    start_parser = nova_py_args_command.add_parser(
        'start',
        help='Start Processing.',
        parents=[nova_cli_args.logging_args],
    )

    start_parser.add_argument(
        '--scenario',
        type=scenario_type,
        choices=list(Scenario),
        required=True,
        help='The scenario to process during startup.',
    )

    return nova_py_args


if __name__ == '__main__':
    main()
