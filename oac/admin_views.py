from django.http import HttpResponse, HttpResponseServerError
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render_to_response
from django.views.generic import list_detail
#from django.contrib import admin
from oac.models import Institution, get_institutions_for_user

def adminlogout(request):
   from django.contrib.auth.views import logout
   return logout(request) #, next_page='/')


@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def institution_change_location(request, id, ark=''):
    '''Get institution & display change location page
    '''
    update = request.GET.get('update', '')
    latitude = request.GET.get('latitude', '')
    longitude = request.GET.get('longitude', '')
    try:
        if id:
            instituteQS = Institution.objects.filter(id=id)
            other_insts = Institution.objects.exclude(id=id)
        else:
            if ark:
                instituteQS = Institution.objects.filter(ark=ark)
                other_insts = Institution.objects.exclude(ark=ark)
    except Institution.DoesNotExist:
        return HttpResponseServerError('<h1>No Institution for id='
                                       + html.escape(id) + '</h1>')
    if update:
        #pdate the institution coords
        institution = instituteQS.get()
        institution.latitude = latitude
        institution.longitude = longitude
        institution.save()
        #redirect to 

    extra_context = { 'update' : update ,
                      'latitude': latitude,
                      'longitude': longitude,
                      'other_insts' : other_insts,
                    }
    return list_detail.object_detail(request,
                                     queryset = instituteQS,
                                     object_id = id,
                                     template_name = 'institution_change_location.html',
                                     extra_context = extra_context,
                                     #                                     template_object_name = 'institute',
                                    )
        
@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def institution_view_groups(request, id, ark=''):
    '''Display the related groups for a give institution. Helper for assigning
    users to appropriate group
    '''
    try:
        if id:
            inst = Institution.objects.get(pk=id)
    except Institution.DoesNotExist:
        return HttpResponseServerError('<h1>No Institution for id='
                                       + html.escape(id) + '</h1>')
    #find groups for institution
    group_profs = inst.groupprofile_set.all()
    groups = []
    for prof in group_profs:
        groups.append(prof.group)
    return render_to_response('institution_view_groups.html',
                              locals()
                             )
