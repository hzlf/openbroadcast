import urllib
import cStringIO
import random

from django.http import HttpResponse
from PIL import Image


INK = "red", "blue", "green", "yellow"


def sc_proxy(request, username=None):
    
    src = request.GET.get('src')

    url = src
    
    # ... create/load image here ...
    image = Image.new("RGB", (800, 600), random.choice(INK))
    
    file = urllib.urlopen(url)
    im = cStringIO.StringIO(file.read())
    img = Image.open(im)
    
    img = img.convert('RGBA')
    
    pixdata = img.load()
    
    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y] == (239, 239, 239, 255):
                pixdata[x, y] = (255, 255, 255, 255)

    # serialize to HTTP response
    response = HttpResponse(mimetype="image/png")
    img.save(response, "PNG")
    return response