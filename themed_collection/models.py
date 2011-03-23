from django.db import models
from xtf.models import ARKSet, ARKSetMember
from richtext.fields import AdminRichTextField
from django.template.defaultfilters import slugify
import south.modelsinspector

south.modelsinspector.add_introspection_rules([], [r'^richtext\.fields\.AdminRichTextField'])

class ThemedCollection(models.Model):
    '''Basic themed collection. Has a set but no geo info?
    It's an ark set + extra stuff?
    or should it hold a onetoonefield on an arkset?
    '''
    title = models.CharField(max_length=512)
    slug = models.SlugField(max_length=255, unique=True, blank=False, null=False)
    questions = models.TextField() #Use the rich text edit stuff
    markup = AdminRichTextField(default='', blank=True,) #freeform markup
    arksets = models.ManyToManyField(ARKSet, null=True, blank=True)
    #mosaic_members = models.ManyToManyField(ARKSetMember, related_name='+', null=True, blank=True)#, limit_choices_to={'id__in': [m.id for m in self.get_members()]})#TODO: how to constrain to ones in get_members?
    mosaicmembers = models.ManyToManyField(ARKSetMember, null=True, blank=True, through='MosaicMember', related_name="themedcollection_set")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        #return ' : '.join((self.title, ' contains set :- ', unicode(self.arksets.all())))
        return self.title

    def save(self):
        ''' Create slug if null'''
        if str(self.slug) == '':
            self.slug =  slugify(self.heading)
        super(ThemedCollection, self).save()

    @models.permalink
    def get_absolute_url(self):
        return ('themed_collection_view', (), {'slug': self.slug, })

    def get_members(self):
        '''Returns a list of the ARKSetMembers in all the ARKSets for the 
        collection.
        '''
        collection_members = [] # a flat list of arkset members
        [map(collection_members.append, arkset.arksetmember_set.all()) for arkset in self.arksets.all()]
        return collection_members

class ThemedCollectionSidebar(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    themed_collection = models.ForeignKey(ThemedCollection)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('title', 'themed_collection'),)

    def __unicode__(self):
        return self.title

class MosaicMember(models.Model):
    '''Many to Many 'through' class, to associate an ordering term with
    the themed collection mosaic members.
    '''
    collection = models.ForeignKey(ThemedCollection)
    member = models.ForeignKey(ARKSetMember)
    order = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def thumbnail(self):
        return self.member.object.thumbnail

    class Meta:
        ordering = ( 'order',)
        #order_with_respect_to = 'collection'

    def __unicode__(self):
        return unicode(self.member)


#TODO: should create new GeoThemedCollection ? with region, theme_type included
# region is the constrained choice field, theme_type a many-to-many?
