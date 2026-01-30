from .base import IntegrationProvider, SyncResult


class AppleHealthProvider(IntegrationProvider):
    provider = "apple_health"

    def fetch(self, source) -> SyncResult:
        return SyncResult(
            status="skipped",
            message="Apple Health integration is not yet configured.",
            stats={"imported_records": 0},
        )
