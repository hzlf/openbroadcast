from django.contrib.auth.models import User
from django.db.models import Count

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS



from tastypie.cache import SimpleCache

from django.contrib import comments

from django.contrib.comments.models import Comment

from tastypie.contrib.contenttypes.fields import GenericForeignKeyField

from alibrary.models import Release
from alibrary.api import ReleaseResource

"""
class ReleaseResource(ModelResource):
    class Meta:
        queryset = Release.objects.all()
"""
     
class CommentResource(ModelResource):
    
    # label = fields.ForeignKey('alibrary.api.LabelResource', 'label', null=True, full=True, max_depth=2)

    """
    content_object = GenericForeignKeyField({
        Note: NoteResource,
        Quote: QuoteResource
    }, 'content_object')
    """
    
    content_object = GenericForeignKeyField(to={Release: ReleaseResource}, attribute='content_object', null=True, full=False)
    
    """
    curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"comment":"sdfsdfsdf", "content_object": "/de/api/v1/release/1963/"}' http://localhost:8081/api/v1/comment/
    """
    
    class Meta:
        queryset = Comment.objects.all()
        list_allowed_methods = ['get','put','post']
        detail_allowed_methods = ['get',]
        resource_name = 'comment'
        excludes = ['ip_address', 'user_email', 'user_url', 'object_pk']
        #include_absolute_url = True
        authentication =  Authentication()
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        #cache = SimpleCache(timeout=120)
        

"""
    def dehydrate(self, bundle):
        
        if(bundle.obj.main_image):
            opt = dict(size=(70, 70), crop=True, bw=False, quality=80)
            try:
                main_image = get_thumbnailer(bundle.obj.main_image).get_thumbnail(opt)
                bundle.data['main_image'] = main_image.url
            except:
                pass

        return bundle
"""

    