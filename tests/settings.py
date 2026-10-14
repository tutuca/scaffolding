"""What every test runs under."""

from scaffolding.conf.settings import *

# The Django test client speaks to `testserver`; accept any host in tests.
ALLOWED_HOSTS = ["*"]
