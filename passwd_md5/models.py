from django.db.models import signals
#from django.dispatch.dispatcher import dispatcher
from django.contrib.auth import models as auth_app
import new, crypt, random, string

try:
    import hashlib
except ImportError:
    import md5 as hashlib    

try:
        from mod_python import apache
        def wrap_apache_log(message):
            apache.log_error(message, apache.APLOG_NOTICE )
        err_stream = wrap_apache_log
except ImportError:
        import sys
        err_stream = sys.stderr.write
    
from django.utils.encoding import smart_str
from django.conf import settings
from django.contrib.auth.models import User
import sys

def write_digest_file(filename):
    f = open(filename,'w')
    for user in User.objects.all():
        try:
            (algo, salt, hash) = user.password.split('$')
            if algo == 'md5':
                f.write(salt+hash+'\n')
        except ValueError:
            err_stream("Django User:%s has bad password.\n" % user.username)
    f.close()
    
def add_write_digest_file(instance=None, **kwargs):
    '''Currently save digest on any change to User. Couldn't hook into the
    set_password because the current User was not yet saved when it is called,
    so previous password was put in file
    '''
    filename = settings.MD5_SHELF
    write_digest_file(filename)

def set_password_crypt(self, raw_password):
    algo = 'crypt'
    saltchars = string.ascii_letters + string.digits + './'
    salt = ''.join(random.choice(saltchars) for i in range(2))
    hsh = crypt.crypt(smart_str(raw_password), salt)
    self.password = '%s$%s$%s' % (algo, salt, hsh)

def set_password_htdigest(self, raw_password):
    algo = 'md5'
    if settings.MD5_REALM:
        salt = ''.join([self.username, ':', settings.MD5_REALM, ':'])
    else:
        salt = ''.join([self.username, ':', 'oac', ':'])
    hsh = hashlib.md5(salt + smart_str(raw_password)).hexdigest()
    self.password = '%s$%s$%s' % (algo, salt, hsh)

def replace_set_password(instance=None, **kwargs):
    instance.set_password = new.instancemethod(
        set_password_htdigest, instance, instance.__class__)

signals.post_init.connect(replace_set_password,
                   sender=auth_app.User,
                         )

#signals.post_save.connect(add_write_digest_file,
#                          sender=auth_app.User,
#                         )
