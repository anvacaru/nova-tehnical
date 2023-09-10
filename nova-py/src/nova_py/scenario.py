from __future__ import annotations

import platform
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Final, Tuple

from .utils import OSName

if TYPE_CHECKING:
    pass


os_name = platform.system()
if os_name == OSName.WINDOWS.value:
    BASE_DIR: str = 'D:/NOVA/nova-tehnical/audio'
    SEASCAPE_SOUNDTRACK: str = f'{BASE_DIR}/seascape.wav'
    SEASCAPE_RECORDINGS: str = f'{BASE_DIR}/recordings'
    OUTPUT: str = f'{BASE_DIR}/seascape_final_1.mp3'
else:
    BASE_DIR = '/Users/anvacaru/Desktop/dev/nova-tehnical/audio'
    SEASCAPE_SOUNDTRACK = f'{BASE_DIR}/seascape.wav'
    SEASCAPE_RECORDINGS = f'{BASE_DIR}/recordings'
    OUTPUT = f'{BASE_DIR}/seascape_final_1.mp3'


SEASCAPE_TIMESTAMPS: Final = [(1, 5), (2, 30), (3, 60)]


def create_scenario(soundtrack: str, recordings: str, timestamps: list[Tuple[int, int]], output: str) -> Dict[str, Any]:
    return {'soundtrack': soundtrack, 'timestamps': timestamps, 'recordings': recordings, 'output': output}


SEASCAPE_SCENARIO: Final = create_scenario(SEASCAPE_SOUNDTRACK, SEASCAPE_RECORDINGS, SEASCAPE_TIMESTAMPS, OUTPUT)


class Scenario(Enum):
    SEASCAPE = SEASCAPE_SCENARIO

    def __str__(self) -> str:
        return self.name.lower()
