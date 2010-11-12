from django.contrib import admin
import django.forms as forms
from django.contrib.contenttypes import generic
from xtf.models import ARKObject, ARKSet, ARKSetMember
from xtf.models import DublinCoreTerm, GeoPoint
import xtf.ARK_validator as ARKValidator 


#class XTFItemAdmin(admin.ModelAdmin):
#    save_on_top = True
#    inlines = (ContributorInline, CoverageInline, CreatorInline,
#              DateInline, FormatInline, IdentifierInline,
#              LanguageInline, PublisherInline, RelationInline,
#              RightsInline, SourceInline, SubjectInline, 
#              TitleInline, TypeInline, )
#
#admin.site.register(XTFItem, XTFItemAdmin)
#admin.site.register(XTFItem)

class XTFObjectPermissionMixin(object):
    def has_change_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission(), obj)

    def has_delete_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission(), obj)


class DCTermInline(generic.GenericTabularInline):
    model = DublinCoreTerm


class GeoPointInline(generic.GenericTabularInline):
    model = GeoPoint
    extra = 0
    max_num = 1

def arksetmember_change(request, id, ark=''):
    '''Override std admin view to add other member info to 
    page.
    '''


class ARKObjectAdminForm(forms.ModelForm):

    class Meta:
        model = ARKObject

    def clean_ark(self):
        '''Validate ARK. First check structure of ARK, then query XTF to 
        verify ARK existence.
        '''
        ark_data = self.cleaned_data["ark"].strip()
        try:
            (ark, naan, name, qual) = ARKValidator.validate(ark_data)
        except ARKValidator.ARKInvalid, e:
            raise forms.ValidationError(e)
        ark_data = ark
        # ark is ok, is it in XTF?
        obj = ARKObject()
        obj.ark = ark_data
        html = obj._get_XTF_page()
        if not html:
            raise forms.ValidationError("ARK does not exist in OAC database")
        return ark_data


class ARKObjectAdmin(admin.ModelAdmin):
    readonly_fields = ('ark', )
    search_fields = ('ark', )
    inlines = (GeoPointInline, )
    save_on_top = True
    form = ARKObjectAdminForm
    #inlines = (DCTermInline, )

admin.site.register(ARKObject, ARKObjectAdmin)

class ARKSetMemberInline(admin.TabularInline):
    model = ARKSetMember
    extra = 1

class ARKSetAdmin(XTFObjectPermissionMixin, admin.ModelAdmin):
    list_display = ('__unicode__', 'id')
    search_fields = ('title',)
    save_on_top = True
    inlines = (ARKSetMemberInline, GeoPointInline, )

    def queryset(self, request):
        qs = super(ARKSetAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(creator=request.user)

admin.site.register(ARKSet, ARKSetAdmin)

class ARKSetMemberAdmin(XTFObjectPermissionMixin,admin.ModelAdmin):
    list_display = ('__unicode__', 'id', 'set', 'has_geopoint', )
    search_fields = ('object__ark', 'set__title', 'annotation' )
    list_filter = ('set', )
    save_on_top = True
    inlines = (DCTermInline, GeoPointInline, )

    def has_geopoint(self, obj):
        return str(obj.has_geopoint)
    has_geopoint.short_description = 'Has Geocoding'

    def change_view(self, request, object_id, extra_context=None):
        '''Override change_view to add a 'users' variable for display'''
        member = ARKSetMember.objects.get(pk=object_id)
        other_members = member.set.arksetmember_set.exclude(pk=member.pk)
        if extra_context:
            extra_context.update({'others':other_members})
        else:
            extra_context = {'others':other_members}
        return super(ARKSetMemberAdmin, self).change_view(request, object_id,
                                                 extra_context)
admin.site.register(ARKSetMember, ARKSetMemberAdmin)
