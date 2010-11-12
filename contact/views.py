import sys
from django.conf import settings
from django.forms import ModelForm
from django.forms import ValidationError
from django.shortcuts import render_to_response
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
import recaptcha.client.captcha as Captcha
from contact.models import *


class ContactForm(ModelForm):
    class Meta:
        model = ContactUsMessage

def check_for_spam(request):
    is_spam = True
    error_dict = {}
    user_challenge = request.POST.get('recaptcha_challenge_field')
    user_resp = request.POST.get('recaptcha_response_field')
    ip = request.META.get('REMOTE_ADDR')
    captcha_resp = Captcha.submit(user_challenge, user_resp,
                                     settings.RECAPTCHA_PRIVATE_KEY, ip
                                    )
    if captcha_resp.is_valid:
        is_spam = False
    else:
        error_dict['recaptcha'] = 'Word verification incorrect. Try again.'

    return is_spam, error_dict

def send_email(msg):
        # build message
        mail_msg = 'Subject:%s\n\nMessage:%s\n\nName:%s\n\nEmail:%s\n\nURL_Refer:%s\n\nUSER_AGENT:%s\n' % ( msg.subject,
                                    msg.message, msg.name,
                                    msg.email, msg.url_refer,
                                    msg.user_agent)
        sub = msg.subject
        if not sub:
            sub = msg.message[0:25]
        subject = sub
        subject = "OAC feedback: " + subject
#        try:
        send_mail(subject, mail_msg, 'oaccontact@ucop.edu',
                  settings.CONTACT_US_EMAILS)
#        except socket.error:
#            import sys
#            (t, val, tb) = sys.exc_info()
#            if repr(val)=="error(61, 'Connection refused')":
#                pass #no email service
#            else:
#                raise

@never_cache
def contactusmessage(request):
    ''' Create & insert a ContactUsMessage if valid, if not ignore.
    Redirect to thank you page regardless of outcome?
    '''
    error_logger = request.environ['wsgi.errors']
    #error_logger.write("HI FROM DJANGO CONTACT APP")
    refer_page = request.META.get('HTTP_REFERER','')
    if request.method == 'POST':
        refer_page = request.POST.get('url_refer', refer_page)
        if request.POST.get('cancel'):
            cancel_redir = "/"
            if refer_page:
                cancel_redir = refer_page
            return HttpResponseRedirect(cancel_redir)
        f = ContactForm(request.POST)
        f.spam_errors = {}
        try:
            #print >> sys.stderr, f.data
            f.base_fields['url_refer'].clean(unicode(f.data.get('url_refer')))
        except ValidationError:
            # bind f to new form with replaced url_refer
            # just sub any spaces for +
            myData = f.data.copy()
            myData['url_refer'] = f.data.get('url_refer','').replace(' ', '+')
            f = ContactForm(myData)
            #print >> sys.stderr, f.data
        if f.is_valid(): #should mean that url_refer, user_agent and message OK?
            (is_spam, error_dict) = check_for_spam(request)
            if not is_spam:
                msg = f.save(commit=False)
                msg.open = True
                msg.status = 'N'
                msg.type_of_issue = 'X'
                msg.category = 'X'
                msg.priority = 'X'
                msg.assigned_group = 'X'
                msg.source = 'X'
                #msg.save()
                if settings.SEND_CONTACT_US_EMAIL:
                    send_email(msg)
                return render_to_response('contactthanks.html',
                                          { 'refer_page': refer_page}
                                         )
            else:
                f.spam_errors = error_dict
                #LOG to wsgi.error in request.environ
                msg_err = 'DJSITE: FAIL SPAM TEST for message: %s | url:%s | user-agent:%s\n' \
                         % (f.cleaned_data['message'],
                            f.cleaned_data['url_refer'],
                            f.cleaned_data['user_agent']
                           )
                error_logger.write(msg_err.encode('utf-8'))
        else:
            msg_err = 'DJSITE: CONTACT FORM INVALID: msg:%s | url:%s | user-agent:%s | ERR:%s\n' \
                         % (f.data.get('message','NOMSG'),
                            f.data.get('url_refer', 'NOREFER'),
                            f.data.get('user_agent', 'NOUSERAGENT'),
                            f.errors
                           )
            error_logger.write(msg_err.encode('utf-8'))
            #            error_logger.write('DJSITE: CONTACT FORM ERRORS: %s\n' % f.errors)
    else:
        f = ContactForm()
    return render_to_response('contactus.html', { 'form' : f, 'refer_page':
                                                 refer_page , 'META' :
                                                 request.META, } )
