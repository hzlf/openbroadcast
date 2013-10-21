from django.db.models import Q
from alibrary.models import Release, Artist, Label

class WikiRelease(object):
    
    """
    'listen' for an [[r:***]] to explicitly render
    """
    name = "r"
    
    def get_query(self, token):
        return Q(name=token) | Q(catalognumber=token)
    
    def attempt(self, token, **kwargs):
        if Release.objects.filter(self.get_query(token)).count() > 0:
            return True
        return False

    def render(self, token, trail=None, **kwargs):
        obj = Release.objects.get(self.get_query(token))
        if obj.catalognumber:
            return "<a href='%s'>[%s]&nbsp;%s</a>" % (obj.get_absolute_url(), obj.catalognumber, obj.name)
        else:
            return "<a href='%s'>%s</a>" % (obj.get_absolute_url(), obj.name)

class WikiArtist(object):
    
    """
    'listen' for an [[r:***]] to explicitly render
    """
    name = "a"
    def __init__(self):
        self.obj = None
    
    def get_query(self, token):
        return Q(name=token)
    
    def attempt(self, token, **kwargs):
        if Artist.objects.filter(self.get_query(token)).count() > 0:
            self.obj = Artist.objects.filter(self.get_query(token))[0]
            return True
        return False

    def render(self, token, trail=None, **kwargs):
        if self.obj:
            return "<a href='%s'>%s</a>" % (self.obj.get_absolute_url(), self.obj.name)
        else:
            return 'linker error'

class WikiLabel(object):

    """
    'listen' for an [[a:***]] to explicitly render
    """
    name = "l"
    def __init__(self):
        self.obj = None

    def get_query(self, token):
        return Q(name=token)

    def attempt(self, token, **kwargs):
        if Label.objects.filter(self.get_query(token)).count() > 0:
            self.obj = Label.objects.filter(self.get_query(token))[0]
            return True
        return False

    def render(self, token, trail=None, **kwargs):
        if self.obj:
            return "<a href='%s'>%s</a>" % (self.obj.get_absolute_url(), self.obj.name)
        else:
            return 'linker error'
