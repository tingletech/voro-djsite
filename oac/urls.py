from django.conf.urls.defaults import *

from oac.models import Institution
from oac.views import institution_address_info_div
from oac.views import list_archivegrid

urlpatterns = patterns('',
    # /djsite/ points to AJAX interfaces
    url(r'^institution/address_info/div/(?P<parent>.*)::(?P<inst_name>.*)', institution_address_info_div),
    url(r'^institution/address_info/div/(?P<inst_name>.*)', institution_address_info_div),
    url(r'^archivegrid_list', list_archivegrid),

)
