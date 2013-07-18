from django.conf import settings

from tastypie import fields
from tastypie.authentication import *
from tastypie.authorization import *
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from easy_thumbnails.files import get_thumbnailer

from alibrary.models import Media

from ep.API import fp


class MediaResource(ModelResource):
    release = fields.ForeignKey('alibrary.api.ReleaseResource', 'release', null=True, full=True, max_depth=2)
    artist = fields.ForeignKey('alibrary.api.ArtistResource', 'artist', null=True, full=True, max_depth=2)

    message = fields.CharField(attribute='message', null=True)

    class Meta:
        queryset = Media.objects.order_by('tracknumber').all()
        list_allowed_methods = ['get', ]
        detail_allowed_methods = ['get', ]
        resource_name = 'track'
        excludes = ['updated', 'release__media']
        include_absolute_url = True
        authentication = Authentication()
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }


    """
    Add streaming information
    """

    def dehydrate(self, bundle):

        obj = bundle.obj

        if obj.master:
            stream = {
                'rtmp_app': '%s' % settings.RTMP_APP,
                'rtmp_host': 'rtmp://%s:%s/' % (settings.RTMP_HOST, settings.RTMP_PORT),
                'file': obj.master,
                'uuid': obj.uuid,
                #'uri': obj.master.url,
                'uri': obj.get_stream_url(),
            }
        else:
            stream = None

        bundle.data['stream'] = stream
        bundle.data['waveform_image'] = None
        bundle.data['duration'] = bundle.obj.get_duration()
        try:
            waveform_image = bundle.obj.get_waveform_image()
            if waveform_image:
                bundle.data['waveform_image'] = bundle.obj.get_waveform_url()

        except:
            pass

        return bundle


    """
    Filters
    Enable querying by fingerprint
    """

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(MediaResource, self).build_filters(filters)

        if "code" in filters:

            print 'CODE FILTER!!!'

            ids = []
            code = filters['code']

            # code = "eJyFmGFyLSkIhbckoALLUYH9L2GO99XUncpUfH--JNptIxxA0xqdag9ke4CZXujxgu4XvL2w1gNC_QU-D_QmL_B4Ye4XfDxAoS9UPMCaL6zzQvID0uoFni_IfqBfgfyOYS_seuEa_iso7AHmfGH0F_S8sNoL214ofUCavSD-Qt8vlD3QmV849gCd8ULNB7jTCyYvvKNw1gPSxgtXtr9D9IFu-4WjD9DOF2K9kPUAd3nhL_XZX_iE8TdIOy9wvVDjgX4f-RUU-ULJA-zrhd1e-Dj7N_yll8kLnfwBinih2gOs9oI_ceYLtR4Q5NLv6GwvvPPomSm3uz_wF2_UC29vZD4g17Rf0Ru_cPP0F6w0tTTeOYee3dbuNRivma44vdZANtGa3HW5dRP3WTOqxprSSFDDbXuWkRl5p2nQ6mSUJCXp6TL3PNY9SudY2_dE58Zq5bK8K9fAUkzV5-hk-Mhw47mTd-fwtVkHw0rxSsfXko-c4IlHs3mklLriS21iOZwYpm5mPue4s_Q1HY0xdK1xJg3CGhHCF3b6aDGJl9FaanBFjo7V-qJhI1rvB9tvsnLHOjhq8vaavWQuZnxybCEO3nBS3zyIczTG7s2xnXl4c_bzRWLB-DH2BWxGTYNI4ELv3Sdcx7OndZKhe-vUglsHJYni7FojuOkyCMOP3jc8kzZ6Juxny8yRH7lPDPpkWjvaUZ258T0Sn7FWzX10NARm-qHTjBGKPWil11BpiwIHUh1zLzupQ4YX49Vuqej7EYgmnut6ihGBLXEmks_ERFW7cd8YLhjtkm2mbCneelSSGRJRM-ypsimsX2NjDG_OLpCW3-1xO_ibJnYMFS_fuUkJUoVooCOeAnES9LS_yOr_G_sCAT8axW3uW54Szl7ITKWoNeHPI4kNQufjtCVTMszZDEYfHgtn994p4YzDMuC14ataGp4k-AJaObmRrNdyDxf4VO9dgrmoSM-oQ4p4YHG43eAIpO5CreszHZJejBXbZnJl8xastAo-wzHKGAkB_Qy4TpCie1ENOIdtnW1YvKoRkoeWhpKTsjSsCcPWhrkN2q9CuBKKEBg00RU6fJEwmkWxQyVaYtERByyGXDDInqt3rHxu1FscKAJRNdiKiIXrmWOU8lCLsF1feLZsP8a-2Lqa_FFh94QX4OKY4lCIITu7b4e_8zZUFCFGf-O8t5uYyDT8WYRD2ph9hAfurXMgo3E3CuiTGiw7tSng0rZa0NzaG3yfeZwmp9hop_o-AR3KHGbTEzmYV8VwK-4zhA1EIAr-qXrRBt7TPhBr6ljl-nIICc0mWgiSIqS-GNcZ7OemRKjBKycnrx51rGBvxm7IzKDdkHy4JVZ2LKG3KrlVEYzZfdayWV-45V4_xr5AiBB7GOqI4RlIuOFqK9HVlZ1zK3JIy5ajbM8VeyHtAw6E-AIu6ltHDyNq1BcK2YEIba5EGR8lfmxsQy2KvkX3iGrbUYTQKRjqpp6wtoseum-jTmIaphRSvbvObR2z5megKkBCLScux-h0CcWNg0rmKBlIah0buYGGEVl5DlwDWYegiBI6C6ScTNlMkdeCM9ZE8ToOC1C0BmqOKmoRkqR91rtyGLFLdJ1z773_gg7C_mPsizaX5kLwUZ_ufQlVbG2Z7Mh37w1dYC_R7oTSgM5gyDD86pCmioTdGAR6SHUKRrF1C-y3rXXrjlhCj3MJ8u9mOT6zXQoK1PvfAmQzRGsbXff-M4Qp9qibA734dLRphEJrGqNn3YYPGfVczuNOoSPshC2EPSNm-UXd5vdj7D9wtFHDTlhR_NEiES38RPnL0zWQDkh4BMFVjDLxdb_9Db1yMpIyIJGO2ml7dB4nJuo81pqQ12dx3GZC0EB5QlUQtxREtftATZ2mECbK-XJsP-jUGeZ-fIwhFTglIKXRB7EEMmkGB3adiqdQAxJveuIYEg3dQw0JdO0hOFxT5JbRBfOhcNQKmV_4zPVz7AtEkJGSt9vJGijfiW8W4o4aMRwyO7AD7bM6zhqaSBRG6_nz2o_ZQLvVmyOMMMGOO4uQJyVO4vGdrcV1GubGZ9YQcP7MKpIoP7Mbxwt0vo3I31l4uPTe1wINAZ-6K0OIKGHor__5xucNnKJw4rzLozIe5Bf62Befvf0Y--Ify8EFSw=="
            #res = fp.best_match_for_query(code_string=code, elbow=10)
            res = fp.query_fp(code_string=code)

            print 'RREESS!!!'

            try:
                if res.match():
                    print res.match()
                    ids = [int(res.TRID), ]

                    orm_filters["pk__in"] = ids

                else:
                    orm_filters["pk__in"] = ()
            except:
                pass

        return orm_filters


class SimpleMediaResource(ModelResource):
    #release = fields.ForeignKey('alibrary.api.ReleaseResource', 'release', null=True, full=False, max_depth=2)
    #artist = fields.ForeignKey('alibrary.api.ArtistResource', 'artist', null=True, full=False, max_depth=2)

    #message = fields.CharField(attribute='message', null=True)

    class Meta:
        queryset = Media.objects.order_by('tracknumber').all()
        list_allowed_methods = ['get', ]
        detail_allowed_methods = ['get', ]
        resource_name = 'track'
        excludes = ['updated', 'release__media']
        include_absolute_url = True
        authentication = Authentication()
        authorization = Authorization()
        filtering = {
            #'channel': ALL_WITH_RELATIONS,
            'created': ['exact', 'range', 'gt', 'gte', 'lt', 'lte'],
        }


    """
    Add streaming information
    """

    def dehydrate(self, bundle):

        obj = bundle.obj

        if obj.master:
            stream = {
                'rtmp_app': '%s' % settings.RTMP_APP,
                'rtmp_host': 'rtmp://%s:%s/' % (settings.RTMP_HOST, settings.RTMP_PORT),
                'file': obj.master,
                'uuid': obj.uuid,
                #'uri': obj.master.url,
                'uri': obj.get_stream_url(),
            }
        else:
            stream = None

        bundle.data['stream'] = stream
        bundle.data['waveform_image'] = None
        bundle.data['duration'] = bundle.obj.get_duration()
        try:
            waveform_image = bundle.obj.get_waveform_image()
            if waveform_image:
                bundle.data['waveform_image'] = bundle.obj.get_waveform_url()

        except:
            pass

        return bundle