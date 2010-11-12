from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from themed_collection.views import view_themed_collection, view_json, input_csv

urlpatterns = patterns('',
    url(r'^themed_collection/edit/(?P<pk>\d+)/input/', input_csv, name='inputcsv'),
    url(r'^themed_collection/edit/(?P<slug>\S+)/input/', input_csv, name='inputcsv'),
    url(r'^themed_collection/json/?$', view_json, {'slug': 'everydaylife'}),
    url(r'^themed_collection/(?P<pk>\d+)//?json/?$', view_json, name='json'),
    url(r'^themed_collection/(?P<slug>\S+)//?json/?$', view_json, name='json'),
    url(r'^themed_collection/(?P<pk>\d+)/.*', view_themed_collection, name='themed_collection_view'),
    url(r'^themed_collection/(?P<slug>\S+)/.*', view_themed_collection, name='themed_collection_view'),
    url(r'^themed_collection/(?P<slug>\S+)$', view_themed_collection, name='themed_collection_view'),
    url(r'^themed_collection/?$', view_themed_collection, {'slug': 'everydaylife'}),
)
