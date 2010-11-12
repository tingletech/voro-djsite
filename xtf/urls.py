from django.conf.urls.defaults import *
from xtf.views import view_ARKObject, view_ARKSet, view_ARKSetMember
from xtf.views import view_ARKSets, map_ARKSet
from xtf.views import edit_ARKSet, edit_ARKSetMembers, input_csv
from xtf.views import add_ARKSetMember, view_ARKSetMembers_map_json

urlpatterns = patterns('',
                       #    (r'^view_XTF_item/(?P<ark>ark:/\d+/\w+)/(.*)', view_XTF_item),
                       #    (r'^view_XTF_item/(?P<ark>ark:/\d+/\w+)$', view_XTF_item),
                       #    (r'^view_EAD_doc/(?P<ark>ark:/\d+/\w+)/(.*)', view_EAD_doc),
                       #    (r'^view_EAD_doc/(?P<ark>ark:/\d+/\w+)$', view_EAD_doc),
    url(r'^ARKObject/(?P<ark>ark:/\d+/\w+)/(.*)', view_ARKObject, name='arkobject_view'),
    url(r'^ARKObject/(?P<ark>ark:/\d+/\w+)/', view_ARKObject, name='arkobject_view'),
    url(r'^ARKSet/edit/(?P<pk>\d+)/input/', input_csv, name='inputcsv'),
    url(r'^ARKSet/edit/(?P<pk>\d+)/members/', edit_ARKSetMembers, name='arksetmembers_edit'),
    url(r'^ARKSet/(?P<pk>\d+)/edit', edit_ARKSet, name='arkset_edit'),
    url(r'^ARKSet/(?P<pk>\d+)/map/json', view_ARKSetMembers_map_json),
    url(r'^ARKSet/(?P<pk>\d+)/map', map_ARKSet, name='arkset_map'),
    url(r'^ARKSet/(?P<pk>\d+)/', view_ARKSet, name='arkset_view'),
    url(r'^ARKSet/(?P<pk>\d+)/(.*)', view_ARKSet, name='arkset_view'),
    url(r'^ARKSet/?$', view_ARKSets, name='arksets_view'),
    url(r'^ARKSetMember/(?P<pk>\d+)/(.*)', view_ARKSetMember, name='arksetmember_view'),
    url(r'^ARKSetMember/(?P<pk>\d+)/', view_ARKSetMember, name='arksetmember_view'),
                       #    url(r'^add_ARKSetMember/(?P<ark>ark:/\d+/\w+)/', add_ARKSetMember, name='arksetmember_add'),
    # how to query params get handled in URLs?
                       #    url(r'^add_ARKSetMember?(?P<ark>ark:/\d+/\w+)/', add_ARKSetMember, name='arksetmember_add'),
                       #    url(r'^add_ARKSetMember\?(?P<ark>ark:/\d+/\w+)/', add_ARKSetMember, name='arksetmember_add'),
    url(r'^ARKSetMember/add', add_ARKSetMember, name='arksetmember_add'),
)
