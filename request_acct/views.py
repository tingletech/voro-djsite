#from datetime import datetime
#from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
#from django.utils import html
#from django import forms
from django.http import Http404, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.core.mail import send_mail
#from django.views.generic import list_detail
from django.conf import settings
from django.contrib.auth.models import User, Group
from oac.models import Institution, UserProfile

#class RequestForm(forms.Form):


EMAIL_REPLY_TO = 'oacops@cdlib.org'
# NOTE: using oacops@cdlib.org as the reply-to in the message to Footprints
# DOES NOT WORK!
EMAIL_REPLY_TO_FOOTPRINTS = 'Adrian.Turner@ucop.edu' #'oacops@ucop.edu'
REQUEST_ADMINS = ('oacops@cdlib.org', 'gamontoya@ucsd.edu')
#REQUEST_ADMINS = ('oacops@cdlib.org', 'mark.redar@cdlib.org',)
acct_type_map = { 'archon': 'Archon',
                 'at' : "Archivist's Toolkit",
                }

MSG_CONFIRMATION = '''This message confirms your request for an account to use the CDL Hosted
Archivists' Toolkit/Archon service.  We will be contacting you soon with
account details, so you can get started with using the service.  In the
meantime, please feel free to review the User Guide for the service,
available at http://www.cdlib.org/services/dsc/tools/at-archon.html
'''

@login_required
def request_archon_at(request, type):
    ''' Sends email to OAC ops requesting account for given user. If user is 
    in groups in multiple Institutions, create a drop down to choose
    '''
    user = request.user
    root_path = '/admin/' # to set log out path correctly
    type_code = type.strip('/').lower()
    type = acct_type_map.get(type_code)
    # if no type, bail
    if type == None:
        raise Http404

    if request.method == "POST":
        # send email and display confirm page?
        institution = Institution.objects.get(pk=request.POST['institution']).name
        # get user info from the request.user object
        phone = ''
        try:
            phone = str(user.userprofile.phone)
        except UserProfile.DoesNotExist:
            pass
        subject = "CDL AT/Archon account request"
        mail_msg = ''.join(['User ',
                            user.get_full_name(),
                            ' has requested a ',
                            type,
                            ' account for ',
                            institution,
                            '\n\nApplication: ',
                            type,
                            '\n\nName: ',
                            user.get_full_name(),
                            '\nVoro username: ',
                            user.username,
                            '\nEmail: ',
                            user.email,
                            '\nInstitution: ',
                            institution,
                            '\nPhone number: ',
                            phone,
                            #'\n\nStatus=Request\n',
                           ]
                          )
        send_mail(subject, mail_msg, EMAIL_REPLY_TO_FOOTPRINTS,
                  REQUEST_ADMINS)
        # user message
        subject_user = "Request Confirmation"
        send_mail(subject_user, MSG_CONFIRMATION, EMAIL_REPLY_TO, (user.email,),
                 fail_silently=True)
        return render_to_response('request_acct/request_sent.html', locals())

    user_institutions = []
    multiple_insts = False
    # check institution relationship for user
    for group in user.groups.all():
        insts = group.groupprofile.institutions.all()
        if insts.count() > 1:
            # we'll need a drop down
            for inst in insts:
                user_institutions.append([inst.id,inst.name]) 
        else:
            if insts.count() == 0:
                pass
            else:
                user_institutions.append([insts[0].id,insts[0].name]) 
    if len(user_institutions) == 0:
        return HttpResponseBadRequest(content='User '+user.get_full_name() +' ('+ user.username + ') is not a member of an OAC institution.')
    multiple_insts = True if len(user_institutions) > 1 else False
    return render_to_response('request_acct/request_hosted_acct.html', locals())
