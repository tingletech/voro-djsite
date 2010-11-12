import geocoders_dsc as geocoders
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from django.forms.models import BaseInlineFormSet
from django import forms
from oac.models import *
from readonlyadmin import ReadOnlyAdminFields

class OACModelAdmin(admin.ModelAdmin):
    ''' Set some default behavior for our admin site
    '''
    save_on_top = True

class InstitutionUrlAdmin(OACModelAdmin):
    list_display = ('__unicode__', 'updated_at', 'created_at' )
    #list_filter = ('institution__name',)
    search_fields = ('url', )#'institution__name', 'institution__ark', )
admin.site.register(InstitutionUrl, InstitutionUrlAdmin)

class CountyAdmin(OACModelAdmin):
    search_fields = ('name', )
admin.site.register(County, CountyAdmin)

class CityAdmin(OACModelAdmin):
    list_display = ('name', 'county')
    list_filter = ('county', )
    search_fields = ('name', 'county__name', )
admin.site.register(City, CityAdmin)

class GroupProfileAdmin(OACModelAdmin):
    list_display = ('group', )
    search_fields = ('institution__name', 'group__name', )
    #admin.site.register(GroupProfile, GroupProfileAdmin)

class GroupProfileInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(GroupProfileInlineFormSet, self).__init__(*args, **kwargs)
        self.can_delete = False

class GroupProfileStaffInline(admin.TabularInline):
    model = GroupProfile
    formset = GroupProfileInlineFormSet

class StaffGroupAdmin(GroupAdmin):
    inlines = (GroupProfileStaffInline, )

    def change_view(self, request, object_id, extra_context=None):
        '''Override change_view to add a 'users' variable for display'''
        model = self.model
        obj = model._default_manager.get(pk=object_id)
        users = obj.user_set.all()
        if extra_context:
            extra_context.update({'users':users})
        else:
            extra_context = {'users':users}
        return super(StaffGroupAdmin, self).change_view(request, object_id,
                                                 extra_context)
        
admin.site.unregister(Group)
admin.site.register(Group, StaffGroupAdmin)

class MARCPrimaryNameDisplayAdmin(OACModelAdmin):
    list_display = ('primary_loc', 'campus_name', 'primary_loc_display',
                    'melvyl_name'
                   )
    list_filter = ('campus_name', )
    search_fields = ('primary_loc', 'campus_name', 'primary_loc_display',
                    'melvyl_name'
                   )
admin.site.register(MARCPrimaryNameDisplay, MARCPrimaryNameDisplayAdmin)

class LocationAdmin(ReadOnlyAdminFields, OACModelAdmin):
    read_only = ('institutions', 'mai_code_location', 'location_type',
                 'region', 'suppress', 'campus', 'cmp',
                 'primary_name', 'campus_name', 'prefix', 'notes',
                )
    list_display = ('mai_code_location', 'primary_name', 'campus_name',
                    'campus', 'notes', )
    list_filter = ('campus', 'primary_name', )
    search_fields = ('mai_code_location', 'campus', 'primary_name',
                     'campus_name')
admin.site.register(Location, LocationAdmin)

class LocationOverrideDisplayAdmin(OACModelAdmin):
    list_display = ('mai_code_location', 'campus_name', 'primary_loc_display',
                    'notes', )
    list_filter = ('mai_code_location', 'campus_name' )
    search_fields = ('mai_code_location', 'campus_name', 'primary_loc_display')
admin.site.register(LocationOverrideDisplay, LocationOverrideDisplayAdmin)

class InstitutionOldNameAdmin(OACModelAdmin):
    list_display = ('name', 'institution', 'created_at', 'expires_at',)
    search_fields = ('name', 'institution__name', )

admin.site.register(InstitutionOldName, InstitutionOldNameAdmin)

class InstitutionAdminForm(forms.ModelForm):
    class Meta:
        model = Institution

    def clean_name(self):
        ''' Check for illegal characters in the name field'''
        #replace($Institution,'[^\i\s\.\(\),-].*','')
        data = self.cleaned_data['name']
        if not Institution.valid_name(data)[0]:
            raise forms.ValidationError(Institution.valid_name(data)[1])
        return data

    def clean_ark(self):
        if not valid_ark(self.cleaned_data['ark']):
            raise forms.ValidationError('Invalid ark')
        return self.cleaned_data['ark']

class InstitutionAdmin(OACModelAdmin):
    '''
    This will need permission for only institution employees to access
    '''
    list_display = ('__unicode__', 'cdlpath', 'name', 'ark', 'mainagency', )
    list_filter = ('isa_campus', 'mainagency', 'archivegrid_harvest', 'worldcat_harvest', 'show_subjects')
    search_fields = ('name', 'ark', 'mainagency', 'cdlpath', 'description', )

    form = InstitutionAdminForm

    def get_user_institutions(self, request):
        '''Return institution list for user. (Class method?)'''
        user = request.user
        return get_institutions_for_user(user)

    def get_institution_users(self, request, obj):
        '''Return a list of all users that can edit this institution'''
        users = []
        if obj:
            grpProfs = obj.groupprofile_set.all()
            for prof in grpProfs:
                group = prof.group
                grpUsers = group.user_set.all()
                for u in grpUsers:
                    users.append(u)
        return users

    def queryset(self, request):
        '''Returns only Institutions user belongs to'''
        qs = self.model._default_manager.get_query_set()
        ordering = self.ordering or ()
        if ordering:
            qs.order_by(*ordering)
        if not request.user.is_superuser:
            #Filter according to user_institutions
            inst_ids = [inst.id for inst in self.get_user_institutions(request)]
            qs = qs.filter(id__in = inst_ids)
        return qs

    def fillin_lat_lng(self, request):
        # middle of SF Bay!
        # request values are all unicode so:
        lat = u'37.85'
        lng = u'-122.37'
        plat = request.POST.get('latitude')
        plng = request.POST.get('longitude')
        no_posted_values = not plat or not plng
        fake_values = plat == lat or plng == lng
        if no_posted_values or fake_values:
            #get lat & lng from address if possible
            #build the address string from available fields
            address_string = request.POST.get('address1', '') + ' ' + request.POST.get('address2', '')
            if request.POST.get( 'zip4'):
                address_string += ', ' + request.POST.get('zip4', '')
            elif request.POST.get('city'):
                try:
                    city = City.objects.get(pk=request.POST.get('city'))
                    address_string += ', ' + city.name + ', CA'
                except City.DoesNotExist:
                    pass
            #get geocoder
            g = geocoders.Google('ABQIAAAAPZhPbFDgyqqKaAJtfPgdhRQxAnOebRR8qqjlEjE1Y4ZOeQ67yxSVDP1Eq9oU2BZjw2PaheQ5prTXaw')
            try:
                place, (lat, lng) = g.geocode(address_string)
            except ValueError:
                pass
        else:
            lat = plat
            lng = plng
        return float(lat), float(lng)

    def add_view(self, request):
        '''Check for parent institution.
        If latitude and longitude not filled in, send a geocode request to
        retrieve values from the address fields.
        '''
        POST_new = request.POST.copy() #get mutable POST object
        parent_inst_id = request.POST.get('parent_institution')
        if parent_inst_id:
            parent_inst = Institution.objects.get(pk = parent_inst_id)
            #POST_new['parent_ark'] = parent_inst.ark
        POST_new['latitude'], POST_new['longitude'] = self.fillin_lat_lng(request)

                
        request.POST = POST_new
        return super(InstitutionAdmin, self).add_view(request)

    def get_form(self, request, obj=None, **kwargs):
        ''' Sort the User foreign key by username
        '''
        f = super(InstitutionAdmin, self).get_form(request, obj)
#        from django.forms.models import modelform_factory
#        if self.declared_fieldsets:
#            fields = flatten_fieldsets(self.declared_fieldsets)
#        else:
#            fields = None
#        if self.exclude is None:
#            exclude = []
#        else:
#            exclude = list(self.exclude)
#        defaults = {
#            "form": self.form,
#            "fields": fields,
#            "exclude": exclude + kwargs.get("exclude", []),
#            "formfield_callback": self.formfield_for_dbfield,
#        }
#        defaults.update(kwargs)
#        f = modelform_factory(self.model, **defaults)

        qsu = f.base_fields['primary_contact'].queryset
        #want to filter so only usernames with groups associated to
        # institution appear and order by.
        users = self.get_institution_users(request, obj)
        pk_users = [user.pk for user in users]
        # replace the admin wrapper widget with the contained widget
        # this removes the 'add' button for users
        f.base_fields['primary_contact'].widget = f.base_fields['primary_contact'].widget.widget
        f.base_fields['primary_contact'].queryset = qsu.filter(pk__in = pk_users).order_by('username')
        return f

    def change_view(self, request, object_id, extra_context=None):
        '''Override change_view to add a 'users' variable for display'''
        model = self.model
        other_insts = model._default_manager.exclude(pk=object_id)
        if extra_context:
            extra_context.update({'other_insts':other_insts})
        else:
            extra_context = {'other_insts':other_insts}
        return super(InstitutionAdmin, self).change_view(request, object_id,
                                                 extra_context)

admin.site.register(Institution, InstitutionAdmin)

class ContribInstitutionAdmin(ReadOnlyAdminFields, InstitutionAdmin):
    list_filter = []
    search_fields = []
    read_only = ('cdlpath', 'mainagency', 'parent_institution',
                'ark', 'url', )
    fieldsets = (
        ('' , {'fields' : ('name', 'ark', 'parent_institution', )}),
        ('Address', { #'classes' : ('collapsed'),
                     'fields' : ('address1', 'address2', 'city',  'county', 'zip4',)}),
        ('Phone', {'fields' : ('phone', 'fax',)}),
        ('WWW Info', {'fields' : ( 'url', 'email' )}),
#        ('Harvesting', {'fields' : ( 'worldcat_harvest', 'archivegrid_harvest' ), 
#                            'description' : "Control harvesting access to your institution's finding aids and objects", }),
#        ('Show Subjects', {'fields' : ( 'show_subjects', )}),
        ('Primary Contact', {'fields' : ( 'primary_contact', )}),
        ('Description', {'fields' : ('description', 'mainagency', 'cdlpath')}),
        ('Location', {'fields' : ( 'latitude', 'longitude',
                                  'custom_zoom_level',),
                      'description': "This geocoding information is used on the OAC institution map.",
                     }),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        '''Can only change is User is related to Institution...
        '''
        if request.user.is_superuser:
            return True
        if obj:
            # attempting to change particular instance, check if user has rights
            # to institution
            insts_for_user = super(ContribInstitutionAdmin, self).get_user_institutions(request)
            if obj not in insts_for_user:
                return False
        return super(ContribInstitutionAdmin, self).has_change_permission(request, obj)

class UserProfileInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(UserProfileInlineFormSet, self).__init__(*args, **kwargs)
        self.can_delete = False

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fields = ('phone', )
    formset = UserProfileInlineFormSet

class UserProfileAdmin(OACModelAdmin):
    list_display = ('user', )
    search_fields = ('user__username', )
    #admin.site.register(UserProfile, UserProfileAdmin)
    
class UserProfileStaffInline(admin.TabularInline):
    model = UserProfile
    formset = UserProfileInlineFormSet

class StaffUserAdmin(UserAdmin):
    inlines = (UserProfileStaffInline, )
admin.site.unregister(User)
admin.site.register(User, StaffUserAdmin)

class ContribUserAdmin(ReadOnlyAdminFields, UserAdmin):
    search_fields = []
    list_filter = []
    inlines = ( UserProfileInline, )
    fieldsets = (
        ('', {'fields': ('username', 'first_name', 'last_name', 'email',)}),
    )
    read_only = ('username', 'staff_status', 'is_active')#'superuser_status', 
    def queryset(self, request):
        qs = self.model._default_manager.get_query_set()
        if not request.user.is_superuser:
            #filter for only curent user
            qs = qs.filter(id=request.user.id)
        return qs
    
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj:
            if not request.user == obj:
                return False
        return super(ContribUserAdmin, self).has_change_permission(request, obj)
