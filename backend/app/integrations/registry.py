from typing import Optional

from .apple_health import AppleHealthProvider
from .google_fit import GoogleFitProvider
from .open_banking import OpenBankingProvider


PROVIDERS = {
    GoogleFitProvider.provider: GoogleFitProvider(),
    AppleHealthProvider.provider: AppleHealthProvider(),
    OpenBankingProvider.provider: OpenBankingProvider(),
}


def get_provider(name: str):
    return PROVIDERS.get(name)


def list_providers() -> list[str]:
    return sorted(PROVIDERS.keys())
