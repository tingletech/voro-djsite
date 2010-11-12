from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin.sites import *
from django.utils.translation import ugettext_lazy, ugettext as _
from django.template import RequestContext
from django.conf.urls.defaults import *
from django.core import urlresolvers
from django.core.mail import send_mail
import django.forms as forms
from oac.models import Institution, get_institutions_for_user
from oac.admin import ContribInstitutionAdmin, ContribUserAdmin

class ContribStaffAdminSite(admin.AdminSite):
    index_template = 'admin/user_dashboard.html'
    def index(self, request, extra_context=None):
        return self.user_dashboard(request)

    def get_urls(self):
        urls = super(ContribStaffAdminSite, self).get_urls()
        my_urls = patterns('',
            (r'^dashboard/$', self.admin_view(self.user_dashboard))
        )
        return my_urls + urls
    
    def has_permission(self, request):
        return request.user.is_authenticated()

    def has_access_permission(self, user):
        return user.is_active

#need to decide how to deal with "admin" flag in users.....
# and how to restrict various Admin_sites....
#add another check to the basic admin site????
    def login(self, request):
        """
        Displays the login form for the given HttpRequest.
        """
        from django.contrib.auth.models import User

        # If this isn't already the login page, display it.
        if not request.POST.has_key(LOGIN_FORM_KEY):
            if request.POST:
                message = _("Please log in again, because your session has expired.")
            else:
                message = ""
            return self.display_login_form(request, message)

        # Check that the user accepts cookies.
        if not request.session.test_cookie_worked():
            message = _("Looks like your browser isn't configured to accept cookies. Please enable cookies, reload this page, and try again.")
            return self.display_login_form(request, message)
        else:
            request.session.delete_test_cookie()

        # Check the password.
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is None:
            message = ERROR_MESSAGE
            if u'@' in username:
                # Mistakenly entered e-mail address instead of username? Look it up.
                try:
                    user = User.objects.get(email=username)
                except (User.DoesNotExist, User.MultipleObjectsReturned):
                    message = _("Usernames cannot contain the '@' character.")
                else:
                    if user.check_password(password):
                        message = _("Your e-mail address is not your username."
                                    " Try '%s' instead.") % user.username
                    else:
                        message = _("Usernames cannot contain the '@' character.")
            return self.display_login_form(request, message)

        # The user data is correct; log in the user in and continue.
        else:
            if self.has_access_permission(user):
                login(request, user)
                return http.HttpResponseRedirect(request.get_full_path())
            else:
                return self.display_login_form(request, ERROR_MESSAGE)
    login = never_cache(login)

    def user_dashboard(self, request):
        '''This will set up access to the useful data for the given logged in user.
        Includes link to user profile edit, info for institution(s)....
        This is not protected by a login required, because it wants to be at the
        root of the admin app. Coule wrap it in another "start" view or something.
        '''
        title = "Dashboard"
        user = request.user
        logout_url = urlresolvers.reverse('contrib_admin:logout')
        user_change_url = urlresolvers.reverse('contrib_admin:auth_user_change', args=(user.id,))
        if request.POST:
            #deal with form data, need to look at pk field
            pk = request.POST['pk']
            inst = Institution.objects.get(pk=pk)
            orig_archivegrid_harvest = inst.archivegrid_harvest #binding form causes inst to change
            form = RecordShareInstitutionForm(request.POST, instance=inst)
            if form.is_valid():
                #check that user has rights to change the given institution
                user.institutions = get_institutions_for_user(user)
                #should we say something if not allowed?
                if inst in user.institutions:
                    # notify ArchiveGrid is grid option changed
                    if form.cleaned_data['archivegrid_harvest'] != orig_archivegrid_harvest:
                        if form.cleaned_data['archivegrid_harvest']:
                            subject = 'New ArchiveGrid sign up from OAC'
                            msg = 'A new contributor has signed up for ArchiveGrid harvesting from the OAC.'
                            msg = ''.join((msg, '\n\nUser ', user.get_full_name(), ' email: ', user.email,))  
                            msg = ''.join((msg, ' has requested ArchiveGrid harvesting of ', inst.name_doublelist, ' record\'s from ', settings.EAD_ROOT_URL, '/', inst.cdlpath))
                        else:
                            subject = 'ArchiveGrid removal from OAC'
                            msg = 'A contributor has requested removal from ArchiveGrid harvesting.'
                            msg = ''.join((msg, '\n\nUser ', user.get_full_name(), ' email: ', user.email,))  
                            msg = ''.join((msg, ' has requested the removal from ArchiveGrid harvesting of ', inst.name_doublelist, ' record\'s from ', settings.EAD_ROOT_URL, '/', inst.cdlpath))

                        send_mail(subject, msg, 'oacops@cdlib.org', settings.ARCHIVE_GRID_EMAILS) 
                    form.save()
        forms = {}
        user.institutions = get_institutions_for_user(user)
        for inst in user.institutions:
            inst.form_harvesting = RecordShareInstitutionForm(instance=inst)
            #forms[inst.id] = RecordShareInstitutionForm(instance=inst)
        return render_to_response('admin/user_dashboard.html',
                                  locals(),
                                  context_instance=RequestContext(request)
                                 )

def yesornot(val):
    if val == "True" or val == True:
        return True
    else:
        return False

class RecordShareInstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ('id', 'archivegrid_harvest')
        widgets = {
            'worldcat_harvest': forms.widgets.CheckboxInput(check_test=yesornot, attrs={'value':"True",}),
            'archivegrid_harvest': forms.widgets.CheckboxInput(check_test=yesornot, attrs={'value':"True",}),
        }
contrib_staff_site = ContribStaffAdminSite(name="contrib_admin")
contrib_staff_site.register(Institution, ContribInstitutionAdmin)
contrib_staff_site.register(User, ContribUserAdmin)
