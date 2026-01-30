from .base import IntegrationProvider, SyncResult


class OpenBankingProvider(IntegrationProvider):
    provider = "open_banking"

    def fetch(self, source) -> SyncResult:
        return SyncResult(
            status="skipped",
            message="Open Banking integration is not yet configured.",
            stats={"imported_records": 0},
        )
