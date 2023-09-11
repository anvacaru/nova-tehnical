from __future__ import annotations

import platform
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Final, Tuple

from .utils import OSName

if TYPE_CHECKING:
    pass


BASE_DIR: Final = (
    'D:\\NOVA\\' if platform.system() == OSName.WINDOWS.value else '/Users/anvacaru/Desktop/dev/nova-tehnical/audio'
)
SEASCAPE_SOUNDTRACK: Final = f'{BASE_DIR}have_you_seen_my_body.aif'
OUTPUT: Final = f'{BASE_DIR}have_you_seen_my_body_voices.aiff'
SEASCAPE_TIMESTAMPS: Final = [(1, 198), (2, 332), (3, 553), (2, 576)]


def create_scenario(soundtrack: str, timestamps: list[Tuple[int, int]], output: str) -> Dict[str, Any]:
    return {'soundtrack': soundtrack, 'timestamps': timestamps, 'output': output}


SEASCAPE_SCENARIO: Final = create_scenario(SEASCAPE_SOUNDTRACK, SEASCAPE_TIMESTAMPS, OUTPUT)


class Scenario(Enum):
    SEASCAPE = SEASCAPE_SCENARIO

    def __str__(self) -> str:
        return self.name.lower()
