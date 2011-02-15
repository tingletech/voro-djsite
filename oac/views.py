from datetime import datetime, date
import csv
import os
import sys
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError, HttpResponseBadRequest
from django.utils import html
from django.forms import ModelForm
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.shortcuts import render_to_response
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache
from django.contrib.admin.widgets import AdminDateWidget
#from django.views.generic import list_detail
from django.views.generic.list_detail import object_list
from django.conf import settings
from oac.models import Institution, InstitutionOldName
import util.contributor_stats as stats

def getInstitutionOldName(name):
    '''See if the instituion name exists in the oldname table.
    If so, return institution esle return None
    '''
    inst = None
    try:
        oldname_list = InstitutionOldName.objects.filter(name__exact=name).order_by('expires_at', 'created_at')
        if oldname_list:
            oldname = oldname_list[0]
            if oldname.expires_at:
                oldname_list = InstitutionOldName.objects.filter(name=name).filter(expires_at__gte=datetime.now()).order_by('expires_at', 'created_at')
                oldname = oldname_list[0] if oldname_list else None
            if oldname:
                inst = oldname.institution
    except InstitutionOldName.DoesNotExist:
        pass
    return inst

def institution_address_info_div(request, **kwargs):
    '''AJAX: Returns a div filled with address info for the named institution
    Also adds whether to show subjects or not
    '''
    import re
    import urllib
    # name can be dual level with :: dividing?
    inst_name = kwargs.get('inst_name')
    inst_name = re.search('.*([A-z\+]*)', inst_name).group(0)
    inst_name = urllib.unquote_plus(inst_name)
    parent = kwargs.get('parent')
    if parent:
        parent = re.search('.*([A-z\+]*)', parent).group(0)
        parent = urllib.unquote_plus(parent)
        try:
            parent_inst = Institution.objects.get(name=parent)
        except Institution.DoesNotExist:
            # see if there is an old name that matches
            parent_inst = getInstitutionOldName(parent)
    else:
        parent_inst = None

    #raise Exception
    try:
        if parent_inst:
            institute = Institution.objects.get(name=inst_name,
                                                parent_institution=parent_inst)
        else:
            institute = Institution.objects.get(name=inst_name)
    except Institution.DoesNotExist:
        institute = getInsitutionOldName(inst_name)
        if not institute:
            return HttpResponseServerError('<h1>No Institute for name='+
                                       html.escape(inst_name) +
                                       ' -parent=' + str(parent_inst) + '</h1>')

    div = ''.join(['<div ark="',
                   html.escape((institute.ark, '')[institute.ark is None]),
                   '" latitude="',
                   html.escape(str((institute.latitude, '')[institute.latitude
                                                            is None])),
                   '" longitude="',
                   html.escape(str((institute.longitude, '')[institute.longitude
                                                             is None])),
                   '" show_subjects="',
                   html.escape(str((institute.show_subjects, 'False')[institute.show_subjects
                                                             is None])),
                   '"><div>',
                   html.escape((institute.address1,'')[institute.address1 is
                                                       None]),
                   '</div><div>',
                   html.escape((institute.address2,'')[institute.address2 is
                                                       None]),
                   '</div><div>',
                   html.escape((institute.city.name,'')[institute.city.name is
                                                        None]),
                   ', California ',
                   html.escape((institute.zip4,'')[institute.zip4 is None]),
                   '</div> <div>',
                   '<span style="font-weight:bold">Phone: </span>%s' %
                   (html.escape(institute.phone),'None')[institute.phone == ''],
                   '</div> <div>',
                   ('<span style="font-weight:bold">Fax: </span>%s' % html.escape(institute.fax), '')[institute.fax == ''],
                   '</div> <div>',
                   '<span style="font-weight:bold">Email: </span>%s' %
                   (html.escape(institute.email), 'None')[institute.email is None or institute.email == ''],
                   '</div> <div><a href="',
                   html.escape((institute.url, '')[institute.url is None]),
                   '">',
                   html.escape((institute.url, '')[institute.url is None]),
                   '</a></div>',
                   '</div>',
                  ])
    return HttpResponse(div)

@never_cache
@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def contributor_activity(request, **kwargs):
    response = HttpResponse(mimetype='text/plain')
    #response['Content-Disposition'] = 'attachment; filename=institution_last_active.csv'

    institutions = Institution.objects.all()
    latest_file_times = {}
    for root, dirs, files in os.walk(settings.EAD_ROOT_DIR):
        # for current directory, find latest file time
        # filetimes are in secs from epoch 0
        latest = 0
        for f in files:
            cur_time = os.path.getmtime(os.path.join(root, f))
            if latest < cur_time:
                latest = cur_time
        # Convert latest to datetime and just put extra path 
        # as dict key
        if latest:
            latest_dt = datetime.fromtimestamp(latest)
        else:
            latest_dt = None
        subdir = root.replace(settings.EAD_ROOT_DIR,'')
        latest_file_times[subdir] = latest_dt

    writer = csv.writer(response)
    writer.writerow(('Institution', 'Parent Institution', 'Address1', 'Address2', 'City', 'Zip', 'Inst. email', 'Inst. phone', 'Inst. URL', 'Contact Name', 'Contact email', 'Contact phone', 'Path', 'Setup Date', 'Latest EAD Time'))
    for inst in institutions:
        if inst.children.count():
            continue
        latest = latest_file_times.get(inst.cdlpath, None)
        parent_name = inst.parent_institution.name.encode('utf-8') if inst.parent_institution else ''
        contact=''
        contact_phone=''
        contact_email=''
        if inst.primary_contact:
            contact = inst.primary_contact.get_full_name().encode('utf-8')
            contact_email = inst.primary_contact.email.encode('utf-8')
            try:
                contact_phone = inst.primary_contact.get_profile().phone.encode('utf-8')
            except:
                pass
        writer.writerow((inst.name.encode('utf-8'), parent_name, inst.address1.encode('utf-8') if inst.address1 else '', inst.address2.encode('utf-8') if inst.address2 else '', inst.city, inst.zip4.encode('utf-8') if inst.zip4 else '', inst.email.encode('utf-8') if inst.email else '', inst.phone.encode('utf-8') if inst.phone else '', inst.url.encode('utf-8'), contact, contact_email, contact_phone, inst.cdlpath, inst.created_at.strftime('%Y-%m-%d'), str(latest.strftime('%Y-%m-%d') if latest else None)))

    return response

class IngestStatsByDateForm(forms.Form):
    class Media:
        js = (settings.ADMIN_MEDIA_PREFIX + "js/calendar.js",
              settings.ADMIN_MEDIA_PREFIX + "/admin/OAC_admin/jsi18n/",
              settings.ADMIN_MEDIA_PREFIX + "js/admin/DateTimeShortcuts.js")

    start_date = forms.DateField(widget=AdminDateWidget(attrs={'class':'vDateField',}))
    end_date = forms.DateField(widget=AdminDateWidget(attrs={'class':'vDateField',}))
    type = forms.CharField(widget=forms.HiddenInput)
    csv_mime = forms.BooleanField(required=False, label="Import directly to excel")

@never_cache
@user_passes_test(lambda u: u.is_superuser, login_url='/admin/OAC_admin/')
def statistics_ingest(request, **kwargs):
    '''Dashboard view for ingest stats'''
    if not request. method == 'POST':
        dateForm = IngestStatsByDateForm()
        media = dateForm.media
    else:
        dateForm = IngestStatsByDateForm(request.POST)
        media = dateForm.media
        if dateForm.is_valid():
            start_date = dateForm.cleaned_data['start_date']
            end_date = dateForm.cleaned_data['end_date']
            type = dateForm.cleaned_data['type']
            csv_mime = dateForm.cleaned_data['csv_mime']
            EAD, METS = stats.parse_ingest_stats()
            if csv_mime:
                response = HttpResponse(mimetype='text/csv')
                fname = ''.join((type, '-report.csv'))
                response['Content-Disposition'] = ''.join(('attachment; filename=', fname))
            else:
                response = HttpResponse(mimetype='text/plain')
            if type=='METS':
                METS_time_filtered = stats.getMETSTimeSlice(METS, start_date, end_date)
                response.write(stats.csvMETSDict(METS_time_filtered, EAD))
            elif type=='EAD':
                EAD_time_filtered = stats.getEADTimeSlice(EAD, start_date, end_date)
                response.write(stats.csvEADDict(EAD_time_filtered))
            else:
                return HttpResponseBadRequest
            return response
    return render_to_response('statistics_dashboard.html', locals())

@never_cache
def list_archivegrid(request, **kwargs):
    '''List all institutions that have opted in to ArchiveGrid harvesting'''
    insts = Institution.objects.filter(archivegrid_harvest=True)
    return object_list(request, queryset=insts, extra_context={'url_ead_root':settings.EAD_ROOT_URL})
