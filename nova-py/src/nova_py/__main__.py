from __future__ import annotations

import logging
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path
from typing import TYPE_CHECKING, Final

from .audio import AudacityController
from .cli.args import LOG_FORMAT, NOVACLIArgs, loglevel
from .image import Controller
from .processing import color_picker, color_picker2
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


def exec_audio(args: Namespace) -> None:
    controller = AudacityController()
    controller.start_audacity()
    controller.import_audio(args.scenario.value['soundtrack'])
    controller.import_audio_batch(args.scenario.value['recordings'])
    # controller.import_audio('/Users/anvacaru/Desktop/dev/nova-tehnical/audio/recordings/voice_0.wav')
    for track_id, timestamp in args.scenario.value['timestamps']:
        controller.move_audio_clip(track=track_id, destination_start=timestamp, destination_end=timestamp + 15)
    controller.select_all()
    controller.export_audio(output_path=args.scenario.value['output'])
    controller.select_tracks(track=0, count=controller._total_tracks)
    controller.remove_tracks()
    controller.stop_audacity()


def exec_image(args: Namespace) -> None:
    output = args.output_path  # Path('/Users/anvacaru/Desktop/dev/nova-tehnical/photos/output')
    controller = Controller()
    controller.read_files(Path(args.file_path))
    controller.process_heic_files()
    controller.run_all_photos(output)
    controller.process_video_files(output)


def exec_picker(args: Namespace) -> None:
    color_picker2(args.file_path)


def exec_trackbar(args: Namespace) -> None:
    color_picker(args.file_path)


def _create_argument_parser() -> ArgumentParser:
    def scenario_type(arg: str) -> Scenario:
        try:
            return Scenario[arg.upper()]
        except KeyError:
            raise ArgumentTypeError(f'Invalid scenario: {arg}. Expected one of: {[str(e) for e in Scenario]}')

    nova_cli_args = NOVACLIArgs()
    nova_py_args = ArgumentParser()
    nova_py_args_command = nova_py_args.add_subparsers(dest='command', required=True)

    audio_parser = nova_py_args_command.add_parser(
        'audio',
        help='Start Audio Processing.',
        parents=[nova_cli_args.logging_args],
    )

    audio_parser.add_argument(
        '--scenario',
        type=scenario_type,
        choices=list(Scenario),
        required=True,
        help='The scenario to process during startup.',
    )

    image_parser = nova_py_args_command.add_parser(
        'image',
        help='Start Image Processing.',
        parents=[nova_cli_args.logging_args],
    )

    image_parser.add_argument('file_path', help='Path to the image file.')

    image_parser.add_argument('output_path', help='Path to store the output to.')
    trackbar_parser = nova_py_args_command.add_parser(
        'trackbar',
        help='Start Color Trackbar.',
        parents=[nova_cli_args.logging_args],
    )

    trackbar_parser.add_argument('file_path', help='Path to the image file.')

    picker_parser = nova_py_args_command.add_parser(
        'picker',
        help='Start Color Picker.',
        parents=[nova_cli_args.logging_args],
    )

    picker_parser.add_argument('file_path', help='Path to the image file.')
    return nova_py_args


if __name__ == '__main__':
    main()
