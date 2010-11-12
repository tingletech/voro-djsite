from django.template import Node #, NodeList, Template, Context, Variable
from django.template import TemplateSyntaxError# , VariableDoesNotExist, BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END, SINGLE_BRACE_START, SINGLE_BRACE_END, COMMENT_TAG_START, COMMENT_TAG_END
from django.template import get_library, Library, InvalidTemplateLibrary
from django.conf import settings
from django.utils.encoding import smart_str, smart_unicode
from django.utils.safestring import mark_safe
import os

register = Library()

def include_is_allowed(filepath):
    for root in settings.ALLOWED_INCLUDE_ROOTS:
        if root:
            if filepath.startswith(root):
                return True
    return False

class SsiRelativeNode(Node):
    def __init__(self, root_path, relative_path, parsed):
        self.root_path, self.relative_path, self.parsed = root_path, relative_path, parsed

    def render(self, context):
        #determine absolute path to requested file
        #if root_path is not blank, use it
        #else look at settings.SSI_ROOT then os.environ.get(SSI_ROOT)
        root_path = self.root_path
        if not os.path.exists(root_path):
            root_path = context.get(root_path)
            if not root_path:
                try:
                    root_path = settings.SSI_ROOT
                except AttributeError:
                    root_path = os.environ.get('DJANGO_SSI_ROOT')
        if not root_path:
            return "[Can not determine root path for include]"
        filepath = os.path.join(root_path, self.relative_path)
        if not include_is_allowed(filepath):
            if settings.DEBUG:
                return "[Didn't have permission to include file:%s]" % filepath
            else:
                return '' # Fail silently for invalid includes.
        try:
            fp = open(filepath, 'r')
            output = fp.read()
            fp.close()
        except IOError:
            output = ''
        if self.parsed:
            try:
                t = Template(output, name=filepath)
                return t.render(context)
            except TemplateSyntaxError, e:
                if settings.DEBUG:
                    return "[Included template had syntax error: %s]" % e
                else:
                    return '' # Fail silently for invalid included templates.
        return output

def ssi_rel(parser, token):
    """
    Outputs the contents of a given file into the page.

    Like a simple "include" tag, the ``ssi_rel`` tag includes the contents
    of another file -- which is specified relative to a root dir --
    in the current page::

        {% ssi_rel '' includes/top-header.html %} -- use settings or environ
        SSI_ROOT

        {% ssi_rel ssi_root includes/top-header.html %} -- use
        context['ssi_root']

        {% ssi_rel /root/path/htdocs/ includes/top-header.html %} -- use given
        path

    If the optional "parsed" parameter is given, the contents of the included
    file are evaluated as template code, with the current context::

        {% ssi_rel '' includes/top-header.html parsed %}
    """
    bits = token.contents.split()
    parsed = False
    if len(bits) not in (3, 4):
        raise TemplateSyntaxError("'ssi' tag takes 2 argument: the root path"
                                  " and the relative path to"
                                  " the file to be included")
    if len(bits) == 4:
        if bits[3] == 'parsed':
            parsed = True
        else:
            raise TemplateSyntaxError("Third (optional) argument to %s tag"
                                      " must be 'parsed'" % bits[0])
    return SsiRelativeNode(bits[1], bits[2], parsed)
ssi_rel = register.tag(ssi_rel)
