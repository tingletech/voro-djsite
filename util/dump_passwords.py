from django.contrib.auth.models import User
import sys

f = open('user.digests','w')
for user in User.objects.all():
    try:
        (algo, salt, hash) = user.password.split('$')
        if algo == 'md5':
            f.write(salt+hash+'\n')
    except ValueError:
        sys.stderr.write("User:%s has bad password.\n" % user.username)
f.close()
