from __future__ import annotations

import dataclasses
from urllib.parse import urlencode


@dataclasses.dataclass
class Redirect:
    url: str
    parameters: dict[str, str]

    @property
    def full_url(self) -> str:
        if not self.parameters:
            return self.url
        return f"{self.url}?{urlencode(self.parameters)}"
