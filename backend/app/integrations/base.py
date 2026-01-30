from dataclasses import dataclass
from typing import Optional

from ..models import DataSource


@dataclass
class SyncResult:
    status: str
    message: Optional[str] = None
    stats: Optional[dict] = None


class IntegrationProvider:
    provider: str

    def is_configured(self, source: DataSource) -> bool:
        return bool(source.access_token or source.refresh_token)

    def fetch(self, source: DataSource) -> SyncResult:
        return SyncResult(status="skipped", message="Not implemented", stats={})
