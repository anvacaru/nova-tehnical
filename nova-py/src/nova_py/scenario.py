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


def create_scenario(timecues: dict[int, list[int]], img_names: list[str], output: Path) -> Dict[str, Any]:
    return {'audio_map': timecues, 'img_names': img_names, 'output': output}


SEASCAPE_SCENARIO: Final = create_scenario(
    timecues=SEASCAPE_TIMECUES, img_names=SEASCAPE_IMGNAMES, output=SEASCAPE_COMPOSITION_DIR
)


class Scenario(Enum):
    SEASCAPE = SEASCAPE_SCENARIO

    def __str__(self) -> str:
        return self.name.lower()
