from django import forms
from django.contrib import admin
from django.utils.encoding import force_unicode

class SelectAsTextInput(forms.TextInput):
    def __init__(self, attrs=None, choices=None):
        super(SelectAsTextInput, self).__init__(attrs)
        self.choices = list(choices) # force collapse

    def render(self, name, value, attrs=None, choices=()):
        text_value = ''
        options = self.choices
        if len(choices) > 0:
            options.append(choices)
        selected_choices = set([force_unicode(v) for v in [value]])
        for opt_value, opt_label in options:
            if str(opt_value) in selected_choices:
                text_value += opt_label
        return super(SelectAsTextInput, self).render(name, text_value,
                                                     attrs=attrs)

class SelectAsHiddenWithTextDisplay(forms.Select):
    def __init__(self, attrs=None, choices=None):
        super(SelectAsHiddenWithTextDisplay, self).__init__(attrs)
        self.attrs.update({ 'style':'display:none', 'class':'hidden' })
        self.choices = list(choices) # force collapse

    def render(self, name, value, attrs=None, choices=()):
        text_widget_attrs = dict(self.attrs)
        self.attrs.update({ 'style':'display:none', 'class':'hidden' })
        if attrs:
            self.attrs.update(attrs)
            #return '<h1>%s</h1>' % self.attrs
        hidden_select = super(SelectAsHiddenWithTextDisplay, self).render(
                                                                    name,
                                                                    value,
                                                                    self.attrs,
                                                                    choices
                                                                   )
        text_widget_name = name + 'for_display'
        text_widget_id = attrs.get('id')
        if text_widget_id:
            attrs['id'] = text_widget_id+'_for_display'
        text_widget_attrs.update({'class':'vTextField', 'readonly':'True', })
        text_widget = SelectAsTextInput(attrs=text_widget_attrs, choices=self.choices)
        rendering = hidden_select + text_widget.render(text_widget_name, value, attrs, choices)
        return rendering

class ReadOnlyAdminFields(object):
    ''' Not tested for File Inputs, radio inputs & ???
    Tested for select and TextInputs
    '''
    def get_form(self, request, obj=None):
        form = super(ReadOnlyAdminFields, self).get_form(request, obj)

        if hasattr(self, 'read_only'):
            for field_name in self.read_only:
                if field_name in form.base_fields:
                    widget = None
                    try:
                        # if widget is a "wrapper" type, it will contain an
                        # inner widget, else not
                        widget = form.base_fields[field_name].widget.widget
                        form.base_fields[field_name].widget = widget
                    except AttributeError:
                        pass
                    widget = form.base_fields[field_name].widget
                    if isinstance(widget, forms.widgets.Select):
                        #change to text input widget
                        widget = form.base_fields[field_name].widget = SelectAsHiddenWithTextDisplay(attrs=widget.attrs, choices=widget.choices) 
                    #set attrs to read only & no focus (for select)
                    widget.attrs.update({'readonly':'readonly',
                                    'style':'background-color:silver',
                                    #'onFocus':'this.blur();return false;',
                                   })
                    form.base_fields[field_name].required = False

        return form

    def save_form(self, request, form, change):
        '''returns an unsaved but changed obj of proper type
        '''
        import pdb
        # for read_only fields, replace value with
        # initial form value
        if hasattr(self, 'read_only'):
            for field_name in self.read_only:
                if field_name in form.base_fields:
                    if form.initial[field_name]:
                        form.data[field_name] = unicode(form.initial[field_name])
                    else:
                        form.data[field_name] = unicode('')
                        #form.fields[field_name].clean(form.data[field_name])
        form.full_clean()
        #because this is used as a mixin, need to get funky when calling
        # save model on super classes
        for base in self.__class__.__bases__:
            if issubclass(base, admin.ModelAdmin):
                obj = base.save_form(self, request, form, change)
                break # only do first one found, rely on it calling super
        return obj
