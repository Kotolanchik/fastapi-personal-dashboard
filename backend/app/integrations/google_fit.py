from .base import IntegrationProvider, SyncResult


class GoogleFitProvider(IntegrationProvider):
    provider = "google_fit"

    def fetch(self, source) -> SyncResult:
        return SyncResult(
            status="skipped",
            message="Google Fit integration is not yet configured.",
            stats={"imported_records": 0},
        )
