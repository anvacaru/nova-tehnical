from __future__ import annotations

import platform
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Final

from .utils import OSName

if TYPE_CHECKING:
    pass


BASE_DIR: Final = (
    'D:\\NOVA\\' if platform.system() == OSName.WINDOWS.value else '/Users/anvacaru/Desktop/dev/nova-tehnical/audio'
)
SEASCAPE_SOUNDTRACK: Final = f'{BASE_DIR}have_you_seen_my_body.aif'
OUTPUT: Final = f'{BASE_DIR}have_you_seen_my_body_voices.aiff'
SEASCAPE_TIMECUES: Final[dict[int, list[int]]] = {0: [198, 201, 206], 1: [332, 576], 2: [553]}


def create_scenario(timecues: dict[int, list[int]], output: str) -> Dict[str, Any]:
    return {'audio_map': timecues, 'output': output}


SEASCAPE_SCENARIO: Final = create_scenario(timecues=SEASCAPE_TIMECUES, output=OUTPUT)


class Scenario(Enum):
    SEASCAPE = SEASCAPE_SCENARIO

    def __str__(self) -> str:
        return self.name.lower()
