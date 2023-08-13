from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Final, Tuple

if TYPE_CHECKING:
    pass

BASE_DIR: Final = '/Users/anvacaru/Desktop/dev/nova-tehnical/audio'
SEASCAPE_SOUNDTRACK: Final = f'{BASE_DIR}/soundscape.mp3'
SEASCAPE_RECORDINGS: Final = f'{BASE_DIR}/recordings'
SEASCAPE_TIMESTAMPS: Final = [(1, 5), (2, 30), (3, 60)]


def create_scenario(soundtrack: str, recordings: str, timestamps: list[Tuple[int, int]]) -> Dict[str, Any]:
    return {'soundtrack': soundtrack, 'timestamps': timestamps, 'recordings': recordings}


SEASCAPE_SCENARIO: Final = create_scenario(SEASCAPE_SOUNDTRACK, SEASCAPE_RECORDINGS, SEASCAPE_TIMESTAMPS)


class Scenario(Enum):
    SEASCAPE = SEASCAPE_SCENARIO

    def __str__(self) -> str:
        return self.name.lower()
