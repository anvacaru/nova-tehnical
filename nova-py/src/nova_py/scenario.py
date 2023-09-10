from __future__ import annotations

import platform
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Final, Tuple

from .utils import OSName

if TYPE_CHECKING:
    pass


BASE_DIR: Final = (
    'D:/NOVA/nova-tehnical/audio'
    if platform.system() == OSName.WINDOWS.value
    else '/Users/anvacaru/Desktop/dev/nova-tehnical/audio'
)
SEASCAPE_SOUNDTRACK: Final = f'{BASE_DIR}/seascape.wav'
SEASCAPE_RECORDINGS: Final = f'{BASE_DIR}/recordings'
OUTPUT: Final = f'{BASE_DIR}/seascape_final_1.mp3'
SEASCAPE_TIMESTAMPS: Final = [(1, 198), (2, 332), (3, 553), (2, 576)]


def create_scenario(soundtrack: str, recordings: str, timestamps: list[Tuple[int, int]], output: str) -> Dict[str, Any]:
    return {'soundtrack': soundtrack, 'timestamps': timestamps, 'recordings': recordings, 'output': output}


SEASCAPE_SCENARIO: Final = create_scenario(SEASCAPE_SOUNDTRACK, SEASCAPE_RECORDINGS, SEASCAPE_TIMESTAMPS, OUTPUT)


class Scenario(Enum):
    SEASCAPE = SEASCAPE_SCENARIO

    def __str__(self) -> str:
        return self.name.lower()
