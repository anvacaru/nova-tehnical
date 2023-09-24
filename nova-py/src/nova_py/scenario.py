from __future__ import annotations

import platform
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Final

from .utils import OSName

if TYPE_CHECKING:
    pass


BASE_DIR: Final[Path] = (
    Path('D:\\NOVA\\') if platform.system() == OSName.WINDOWS.value else Path('/Users/dev/nova-tehnical/')
)
SEASCAPE_COMPOSITION_DIR: Final[Path] = BASE_DIR / 'Have you seen my body'
SEASCAPE_TIMECUES: Final[dict[int, list[int]]] = {0: [198], 1: [332, 576], 2: [555]}
SEASCAPE_IMGNAMES: Final[list[str]] = [
    'user_frontal.png',
    'user_hands_raised_frontal.png',
    'user_side.png',
    'user_back.png',
    'user_walking_back.png',
]

WALK_COMPOSITION_DIR: Final[Path] = BASE_DIR / 'walk' / 'walk'
WALK_IMGNAMES: Final[list[str]] = [
    'P1 full body frontal.png',
    'P1 full body side.png',
    'P1 full body walking front.png',
    'P2 full body frontal.png',
    'P2 full body side.png',
    'P2 full body walking front.png',
]


def create_scenario(
    timecues: dict[int, list[int]] | None, img_names: list[str], output: Path, has_visual: bool, has_audio: bool
) -> Dict[str, Any]:
    return {
        'audio_map': timecues,
        'img_names': img_names,
        'output': output,
        'has_visual': has_visual,
        'has_audio': has_audio,
    }


SEASCAPE_SCENARIO: Final = create_scenario(
    timecues=SEASCAPE_TIMECUES,
    img_names=SEASCAPE_IMGNAMES,
    output=SEASCAPE_COMPOSITION_DIR,
    has_visual=True,
    has_audio=True,
)

WALK_SCENARIO: Final = create_scenario(
    timecues=None, img_names=WALK_IMGNAMES, output=WALK_COMPOSITION_DIR, has_visual=True, has_audio=False
)


class Scenario(Enum):
    SEASCAPE = SEASCAPE_SCENARIO
    WALK = WALK_SCENARIO

    def __str__(self) -> str:
        return self.name.lower()
