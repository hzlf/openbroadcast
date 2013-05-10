from string import lowercase
from django.conf import settings

PENDING_LIMIT = getattr(settings, 'INVITE_PENDING_LIMIT', 5)
CODE_CHARS = getattr(settings, 'INVITE_CODE_CHARS', lowercase)
