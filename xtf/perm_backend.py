'''A permission backend for xtf objects. Ties user to the creator or owner field??
'''
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

class XTFObjectOwnerPermBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username, password):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_authenticated():
            return False
            user_obj = User.objects.get(pk=settings.ANONYMOUS_USER_ID)

        if obj is None:
            return False
        #look for creator or owner attr on obj
        # must equal user.
        u = getattr(obj, 'creator',None)
        if not u:
            u = getattr(obj, 'owner',None)
        if not u:
            return False
        return False if user_obj != u else True

class ARKObjectOwnerPermBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = True

    def authenticate(self, username, password):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_authenticated():
            return False
        if obj is None:
            return False
        #look for creator or owner attr on set
        # must equal user.
        set = getattr(obj,'set', None)
        if not set:
            return False
        u = set.getattr('creator',None)
        if not u:
            u = set.getattr('owner',None)
        if not u:
            return False
        return False if user_obj != u else True
