from django.db import models
from django import forms
from richtext.custom_widgets import RichTextWidget

class AdminRichTextField(models.TextField):
   def __init__(self, photologue=False, *args, **kwargs):
       self.photologue = photologue
       super(AdminRichTextField, self).__init__(*args, **kwargs)
       
   def formfield(self, **kwargs):
      ff = super(AdminRichTextField, self).formfield(form_class=RichTextField,
              **kwargs)
      ff.widget = RichTextWidget()
      #return RichTextField(photologue=self.photologue)#, **kwargs)
      return ff


class RichTextField(forms.fields.Field):
    def __init__(self, photologue=False, *args, **kwargs):
      self.widget = RichTextWidget(attrs = {'photologue': photologue}) #set the default widget and attributes
      super(RichTextField, self).__init__(*args, **kwargs)
    
