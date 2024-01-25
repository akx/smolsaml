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
        sep = "&" if "?" in self.url else "?"
        return f"{self.url}{sep}{urlencode(self.parameters)}"
