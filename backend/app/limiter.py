from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared rate-limiter instance. Keyed on the client''s remote IP.
# Import this in main.py to wire it onto the app, and in auth.py to
# decorate the /token endpoint.
limiter = Limiter(key_func=get_remote_address)
