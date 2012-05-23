import settings
from django.core.urlresolvers import reverse

PRETTIFY = False
try:
    PRETTIFY = settings.PRETTIFY
except Exception:
    pass

try:
    from BeautifulSoup import BeautifulSoup
except Exception:
    PRETTIFY = False
    

class PrettifyMiddlewareBS(object):
    """HTML code prettification middleware."""
    def process_response(self, request, response):
        if request.path.startswith(reverse('admin:index')):
            return response
        if PRETTIFY and response['Content-Type'].split(';', 1)[0] == 'text/html':
            response.content = BeautifulSoup(response.content).prettify()
        return response