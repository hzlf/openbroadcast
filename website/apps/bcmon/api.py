from django.contrib.auth.models import User
from django.db.models import Count

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS

from bcmon.models import *

class ChannelResource(ModelResource):
    
    #playout = fields.ToOneField('PlayoutResource', 'playout')
    
    class Meta:
        queryset = Channel.objects.all()
        resource_name = 'channel'
        excludes = ['id', 'updated',]
        # excludes = ['email', 'password', 'is_superuser', 'is_active', 'is_staff', 'id']
        filtering = {
            'name': ['exact', ],
        }

class PlayoutResource(ModelResource):
    
    #channel = fields.ForeignKey(ChannelResource, 'channel', null=True, full=True)
    channel = fields.ForeignKey(ChannelResource, 'channel', null=True, full=False)

    class Meta:
        queryset = Playout.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        resource_name = 'playout'
        excludes = ['updated',]
        authentication = BasicAuthentication()
        authorization = Authorization()
        filtering = {
            'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }
        
    """"""
    def obj_create(self, bundle, request, **kwargs):
        
        if 'channel' in bundle.data:
            channel = Channel.objects.filter(slug=bundle.data['channel'])[0]
            bundle.data['channel'] = {'pk':channel.pk}

        return super(PlayoutResource, self).obj_create(bundle, request, **kwargs)
    
    