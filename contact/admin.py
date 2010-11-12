from django.contrib import admin
from contact.models import *

class ContactUsMessageAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('id', 'message_display', 'subject', 'url_refer',
                    'email', 'name', 'type_of_issue', 'status',
                    'release', 'created_at', 'updated_at',
                   )
    list_filter = ('open', 'assigned_group', 'release', 'type_of_issue',
                   'category', 'priority', 'status', 'source',
                  )
    search_fields = ('subject', 'message', 'name',
                    'email', 'url_refer',
                    'dependencies', 'next_steps', 'note',
                   )
    raw_id_fields = ('duplicate', )
admin.site.register(ContactUsMessage, ContactUsMessageAdmin)
