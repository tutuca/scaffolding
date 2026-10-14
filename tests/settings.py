"""What every test runs under - the layer no test can opt out of.

These were autouse fixtures in conftest.py until 2026-09-20, when autouse was
banned (test_conventions.py): a settings module holds the same suite-wide
invariants without hiding setup from test signatures. A test wanting another
value overrides it explicitly via the `settings` fixture.
"""

from pathlib import Path

from cryptography.fernet import Fernet

from scaffolding.conf.settings import *
from scaffolding.conf.settings import ARCA

# No test touches ARCA, whatever the operator's .env says. Adapters that would
# are selected explicitly.
ARCA = {**ARCA, "AUTHORIZER": "dry_run", "RATE_PROVIDER": "manual"}

# A throwaway key: no test reads the operator's SECRETS_ENCRYPTION_KEY.
SECRETS_ENCRYPTION_KEY = Fernet.generate_key().decode()

# `scaffolding valuation --write` must land in the writing test's tmp_path. This
# default cannot be written, so a test that forgot the redirect fails at the
# write instead of leaving a report in var/.
VALUATION_REPORT = str(Path("/nonexistent") / "valuation.md")
