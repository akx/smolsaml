from __future__ import annotations

import subprocess
from typing import Iterable


class XMLSecError(Exception):
    def __init__(self, message, results: list[subprocess.CompletedProcess]):
        super().__init__(message)
        self.results = results

    @property
    def xmlsec_outputs(self) -> Iterable[str]:
        return (result.stdout for result in self.results)
