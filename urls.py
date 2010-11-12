from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.comments.models import Comment
from django.contrib import admin
from django.views.generic.simple import redirect_to, direct_to_template
admin.autodiscover()


from oac.views import contributor_activity
from oac.views import statistics_ingest
from oac.admin_views import institution_change_location
from oac.admin_views import institution_view_groups
from oac.admin_site import contrib_staff_site

from contact.views import contactusmessage
from request_acct.views import request_archon_at


urlpatterns = patterns('',
    #(r'^admin/', direct_to_template, {'template':'admin_site_maintenance.html'}),#admin only site shutdown notice, uncomment to display static message.
    # /admin/OAC_admin/ points to the Django default admin site
    (r'^admin/request_hosted_acct/(?P<type>.*)', request_archon_at),
    (r'^admin/request_hosted_acct/', request_archon_at),
    (r'^admin/OAC_admin/institution-activity', contributor_activity),
    (r'^admin/OAC_admin/contributor-activity', contributor_activity),
    (r'^admin/OAC_admin/ingest-statistics', statistics_ingest),
    (r'^admin/OAC_admin/oac/institution/(\d+)/viewgroups/', institution_view_groups),
    (r'^admin/oac/institution/(\d+)/viewgroups/', institution_view_groups),
    (r'^admin/OAC_admin/oac/institution/(\d+)/changelocation/', institution_change_location),
    (r'^admin/OAC_admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/OAC_admin/', include(admin.site.urls)),
    # /admin/ points to custom AdminSite in oac/admin_site.py
    (r'^admin/oac/institution/(\d+)/changelocation/', institution_change_location),
    (r'^admin/', include(contrib_staff_site.urls)),

    (r'^admin/accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^admin/accounts/logout/$', 'django.contrib.auth.views.logout', {
        'next_page':'/'} ),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {
        'next_page':'/'} ),

    (r'^contact/', contactusmessage),

    (r'djsite/xtf/', include('xtf.urls')),
    (r'djsite/themed_collection/', include('themed_collection.urls')),

    (r'djsite/', include('oac.urls')),

    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.PROJECT_PATH+'/site_media'}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.PROJECT_PATH+'/site_media/css'}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.PROJECT_PATH+'/site_media/js'}),
    (r'^yui/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.PROJECT_PATH+'/site_media/yui'}),

                       #(r'/', redirect_to, {'url':'/admin/'}),
                       #(r'', redirect_to, {'url':'/admin/'}),
)
