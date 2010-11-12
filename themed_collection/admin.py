from django.contrib import admin
import django.forms as forms
from django.contrib.contenttypes import generic
from themed_collection.models import ThemedCollection, ThemedCollectionSidebar

class ThemedCollectionPermissionMixin(object):
    def has_change_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission(), obj)

    def has_delete_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission(), obj)


class ThemedCollectionSidebarInline(admin.TabularInline):
    model = ThemedCollectionSidebar
    extra = 1
    

class ThemedCollectionSidebarAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'id', 'themed_collection',)
    list_filter = ('themed_collection', )
    search_fields = ('title', 'content', )
    save_on_top = True
admin.site.register(ThemedCollectionSidebar, ThemedCollectionSidebarAdmin)


class ThemedCollectionAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'id', 'slug', 'title')
    search_fields = ('title', 'overview', 'questions', 'content_stds' )
    save_on_top = True
    inlines = ( ThemedCollectionSidebarInline, )

    def get_form(self, request, obj=None, **kwargs):
        f = super(ThemedCollectionAdmin, self).get_form(request, obj)
        qsu = f.base_fields['mosaic_members'].queryset
        #want to filter so only usernames with groups associated to
        # institution appear and order by.
        if obj:
            members = obj.get_members()
            pk_members = [mem.pk for mem in members]
            # replace the admin wrapper widget with the contained widget
            # this removes the 'add' button for users
            f.base_fields['mosaic_members'].widget = f.base_fields['mosaic_members'].widget.widget
            f.base_fields['mosaic_members'].queryset = qsu.filter(pk__in = pk_members)
        else:
            f.base_fields['mosaic_members'].queryset = qsu.none()
        return f

admin.site.register(ThemedCollection, ThemedCollectionAdmin)
