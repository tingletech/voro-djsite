import re
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType

def get_institutions_for_user(user):
    #get the profiles and then institutions user belongs to
    insts = []
    for group in user.groups.all():
        grp_prof = GroupProfile.objects.get(group=group.id)
        insts.extend(grp_prof.institutions.all())
    return insts

def valid_ark(ark):
    '''Validates arks. Right now just boolean function
    This does a very basic sanity check on arks, but doesn't completely validate
    arks as per the spec: http://www.cdlib.org/inside/diglib/ark/arkspec.html
    This should be usable throughout OAC.
    '''
    #    if not re.match(r'ark:/(\d{5}|\d{9})/[a-zA-Z0-9]+$', ark):
    if not re.match(r'ark:/(\d{5}|\d{9})/[a-zA-Z0-9=#\*+@_\$%-\./]+$', ark):
        return False
    return True

class County(models.Model):
    '''California County List
    '''
    name = models.CharField(max_length=255, unique=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        #        db_table = u'counties'

class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    county = models.ForeignKey(County)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True) 
    custom_zoom_level = models.IntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        #db_table = u'cities'

class Institution(models.Model):
    '''Contributing Institutions
    '''
    ark = models.CharField(max_length=255, unique=True, blank=True)
    parent_institution = models.ForeignKey('self', null=True, blank=True, related_name='children')
    parent_ark = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)#, blank=True)
    mainagency = models.CharField(max_length=255, null=True, blank=True)
    cdlpath = models.CharField(max_length=255, blank=True)
    address1 = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.ForeignKey(City)
    county = models.ForeignKey(County)
    zip4 = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=255, blank=True)
    phone = models.CharField(max_length=63, null=True, blank=True)
    fax = models.CharField(max_length=63, null=True, blank=True)
    email = models.CharField(max_length=63, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    custom_zoom_level = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    isa_campus = models.NullBooleanField(null=True, blank=True, default=False)
    primary_contact = models.ForeignKey(User,
                                        related_name="contact_for_institution",
                                        null=True,
                                        blank=True)
    worldcat_harvest = models.NullBooleanField(null=True, blank=True, default=False, verbose_name="WorldCat Export", help_text="Share my institution's digital object metadata with OCLC, for inclusion in WorldCat and OAIster")
    archivegrid_harvest = models.NullBooleanField(null=True, blank=True, default=False, verbose_name="ArchiveGrid Export", help_text="I'm interested in listing my OAC collection guides in ArchiveGrid and WorldCat Please have OCLC contact me.")
    show_subjects = models.NullBooleanField(null=True, blank=True, default=False, verbose_name="Show EAD Subject Terms", help_text="Show subject terms from your EADs on the institution home page.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def _get_has_collections(self):
        return self.collection_set.count()
    has_collections = property(_get_has_collections)

    def _get_stat_path(self):
        '''Rerutn the path for stats. Is just cdlpath with / replaced by
        -
        '''
        return self.cdlpath.replace('/','-')
    stat_path = property(_get_stat_path)

    def _get_name_doublelist(self):
        """Return the 'doublelist' form of the institution's name
        """
        name = ''
        if self.parent_institution:
            name += self.parent_institution.name + '::'
        name += self.name
        return name
    name_doublelist = property(_get_name_doublelist)

    @staticmethod
    def valid_name(name):
        if re.search(r'[&].+', name) != None:
            return False, 'Ampersands (&) can not be used in institution names'
        return True, 'Name OK'

    def __unicode__(self):
        name = ''
        name += self.name
        if self.parent_institution:
            name += ', Parent: ' + self.parent_institution.name
        return name

    def save(self, force_insert=False, force_update=False):
        '''Need to save any changes in url to InstituionUrl table
        '''
        # strip whitespace from arks
        self.ark = self.ark.strip()
        if not valid_ark(self.ark):
            raise ValueError('Invalid ark')
        if self.parent_institution:
            self.parent_ark = self.parent_institution.ark
        else:
            self.parent_ark = None
        #lookup self in db and compare url fields
        if not Institution.valid_name(self.name)[0]:
            raise ValueError(Institution.valid_name(self.name)[1])
        try:
            self_db = Institution.objects.get(pk=self.pk)
            if self.url != self_db.url:
                #add record to InstitutionUrl
                i_url = InstitutionUrl(institution=self_db, url=self_db.url)
                i_url.save()
            #if name has changed, create an entry in InstitutionOldName
            if self.name != self_db.name:
                i_oldname = InstitutionOldName(institution=self_db,
                                               name=self_db.name,
                                              )
                i_oldname.save()
        except Institution.DoesNotExist:
            #New institution
            pass
        return super(Institution, self).save(force_insert, force_update)

    class Meta:
        ordering = ['name']
        #db_table = u'institutions'

class InstitutionUrl(models.Model):
    '''Mapping for historic institution urls'''
    institution = models.ForeignKey(Institution, null=False)
    url = models.URLField()
    flag = models.CharField(max_length=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.institution.name + ' | ' + self.url

class InstitutionOldName(models.Model):
    '''Old names for institutions. Mainly used for interim mapping in the djsite
    view address lookup.
    '''
    institution = models.ForeignKey(Institution)
    name = models.CharField(max_length=255)#, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

class GroupProfile(models.Model):
    group = models.OneToOneField(Group) #hook into Django.auth
    #directory = models.CharField(max_length=255, null=True, blank=True)
    institutions = models.ManyToManyField(Institution, blank=True)
    #note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return unicode(self.group)

    class Meta:
        ordering = ('group__name',)
        #db_table = u'edit_groups'

class UserProfile(models.Model):
    user = models.OneToOneField(User) #hook into Django Auth
    phone = models.CharField(max_length=63, null=True, blank=True)
    #institutions = models.ManyToManyField(Institution, null=True, blank=True)
    #OAC_listserv = models.BooleanField(default=True)
    voroEAD_account = models.BooleanField(default=False)
    archon_user = models.CharField(max_length=32, null=True, blank=True)
    AT_application_user = models.CharField(max_length=32, null=True, blank=True)
    AT_database_user = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    
    def __unicode__(self):
        return self.user.__unicode__()

    class Meta:
        ordering = ['user__username']
        #db_table = u'institution_employees'

class MARCPrimaryNameDisplay(models.Model):
    campus_name = models.CharField(max_length=255)
    primary_loc = models.CharField(max_length=255)
    primary_loc_display = models.CharField(max_length=255, null=True, blank=True)
    flag = models.CharField(max_length=255, null=True, blank=True,
                           help_text='Set to r to remove entry from OAC')
    melvyl_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.primary_loc

    class Meta:
        ordering = ('campus_name', )

class Location(models.Model):
    #institutions = models.ManyToManyField(Institution, blank=True, null=True)
    mai_code_location = models.CharField(max_length=255, blank=True)
    location_type = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    suppress = models.CharField(max_length=255, null=True, blank=True,)
    campus = models.CharField(max_length=255, blank=True)
    cmp = models.CharField(max_length=255, null=True, blank=True)
    primary_name = models.CharField(max_length=255, null=True, blank=True)
    campus_name = models.CharField(max_length=255, blank=True)
    prefix = models.CharField(max_length=255, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return '%s' % (self.mai_code_location)

    class Meta:
        ordering = ['primary_name']
        #db_table = u'locations'

class LocationOverrideDisplay(models.Model):
    mai_code_location = models.CharField(max_length=255, blank=False)
    campus_name = models.CharField(max_length=255, blank=False)
    primary_loc_display = models.CharField(max_length=255, blank=True)
    prefix = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, force_insert=False, force_update=False):
        if ((len(self.mai_code_location) < 1) or (len(self.campus_name) < 1)):
            raise ValueError, 'mai_code_location and campus_name required'
        return super(LocationOverrideDisplay, self).save(force_insert, force_update)

    def __unicode__(self):
        return '%s::%s' % (self.mai_code_location, self.campus_name)

    class Meta:
        ordering = ['mai_code_location']
        #db_table = u'locations'
