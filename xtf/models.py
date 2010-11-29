import urllib2
import re
import lxml.etree as ET
from BeautifulSoup import BeautifulSoup
from _mysql_exceptions import IntegrityError
import _mysql_exceptions
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from xtf.ARK_validator import validate, ARKInvalid


class GeoPoint(models.Model):
    '''A holder for geo coding.
    '''
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    lat = models.FloatField(default=37.8086906)
    lon = models.FloatField(default=-122.2675416,)
    place = models.CharField(max_length=512, null=True, blank=True)
    exact = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = (("object_id", "content_type"), )

    def __unicode__(self):
        return "east="+str(self.lon)+"; north="+str(self.lat)+';'


class DublinCoreTerm(models.Model):
    ''' A Dublin Core metadata element. We support the 15 core elements with
    with unlimited qualifiers. Currently, these terms are customized for
    ARKObjects with a ForeignKey pointing to that model. If needed, could use
    the Django content-type framework to generalize the DCTerms to other models.
    '''

    DCTERMS = (\
                ('CN', 'Contributor'),
                ('CVR', 'Coverage'),
                ('CR', 'Creator'),
                ('DT', 'Date'),
                ('DSC', 'Description'),
                ('FMT', 'Format'),
                ('ID', 'Identifier'),
                ('LG', 'Language'),
                ('PBL', 'Publisher'),
                ('REL', 'Relation'),
                ('RT', 'Rights'),
                ('SRC', 'Source'),
                ('SUB', 'Subject'),
                ('T', 'Title'),
                ('TYP', 'Type'),
    )
    DCTERM_MAP = dict([(x[1].lower(), x[0]) for x in DCTERMS])
    DCTERM_LIST = [x[1].lower() for x in DCTERMS]
    
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    term = models.CharField(max_length=3, choices=DCTERMS)
    qualifier = models.CharField(max_length=255, null=True, blank=True)
    content = models.CharField(max_length=1024) # TODO: Text field?
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return ''.join([self.get_term_display(), ':', self.qualifier, ' = ', self.content, ]) if self.qualifier else ''.join([self.get_term_display(), ' = ', self.content, ])


class XTFNOTFOUND(Exception):
    pass


class ARKObject(models.Model):
    '''A Django placeholder for non-DB data. Using the Django content-type
    abstraction?
    '''
    ark = models.CharField(max_length=255, unique=True) #mysql length limit
    geo = generic.GenericRelation(GeoPoint)
    #DCTerms = generic.GenericRelation(DublinCoreTerm)
    #content_type = models.ForeignKey(ContentType)
    #content_object = generic.GenericForeignKey('content_type', 'ark')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(ARKObject, self).__init__(*args, **kwargs)
        self._url_content_root = 'http://content.cdlib.org/'
        

    @staticmethod
    def _ARK_normalize(ark):
        ark = ark.strip()
        ark, NAAN, name, qualifier = validate(ark)
        return ark

    @staticmethod
    def get_or_create(ark):
        '''Returns an ARKObj and whether it is a newly created one.
        Raises XTFNOTFOUND if string ark not found in OAC
        Can raise other db & model errors
        '''
        created = False
        ark = ARKObject._ARK_normalize(ark)
        try:
            arkobj = ARKObject.objects.get(ark=ark)
        except ARKObject.DoesNotExist:
            #try to create a new one, should throw if ark not in OAC
            arkobj = ARKObject(ark=ark)
            arkobj.save()
            created = True
        return arkobj, created

    def _get_lat_lon(self):
        geo = self.geo.all()
        if geo:
            self._lat = geo[0].lat
            self._lon = geo[0].lon
        else:
            self._lat = self._lon = None
        return self._lat, self._lon

    @property
    def lat(self):
        '''Return lat if stored in GeoPoint object, else None
        This may have a caching problem? as these objs are created each request
        shouldn't matter much
        '''
        return self._lat if getattr(self, "_lat", None) else self._get_lat_lon()[0]

    @property
    def lon(self):
        '''Return lat if stored in GeoPoint object, else None
        '''
        return self._lon if getattr(self, "_lon", None) else self._get_lat_lon()[1]

    @property
    def has_geopoint(self):
        '''Return True if has a related GeoPoint
        '''
        return True if self.geo.all() else False

    @property
    def url_dc_root(self):
        '''Return the URL to the OAC dublin core document
        '''
        return 'http://www.oac.cdlib.org/dc/' #''.join(('http://www.oac.cdlib.org/dc/', self.ark.strip(),))# '/?layout=metadata'))

    @property
    def url_metadata(self):
        '''Return the URL to the xtf content metadata display.
        '''
        return ''.join((url_content_root, self.ark, '/?layout=metadata'))

    @property
    def url_content_root(self):
        return self._url_content_root

    @property
    def url_content(self):
        '''Return the URL to the xtf content object.
        '''
        return ''.join((self.url_content_root, self.ark.strip('/'), '/'))

    @property
    def thumbnail(self):
        '''A javascript like image placeholder to the objects thumbnail on content.cdlib.org
        '''
        #return self.url_content+'thumbnail'
        if not getattr(self, '_thumbnail', None):
            self._thumbnail = self._get_XTF_thumbnail()
        return self._thumbnail

    @property
    def image(self):
        '''Return link to the image used on calisphere.
        Requires scraping the layout=printable page for anchor with
        id="zoomMe" then grabbing the child <img> tag href
        '''
        #url = self.url_content+'?layout=printable'
        url = self.url_content
        req = urllib2.Request(url=url)
        try:
            u = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            #the dc interface should play nice
            if e.code == 404:
                return "XTFNOTFOUND"
                raise XTFNOTFOUND('ARK not found in OAC')
            raise e
        html_str = u.read()
        if (html_str.find('Document Not Found') > 0 or html_str.find('Invalid Document') > 0):
            #TODO: SHOULD NEVER GET THIS
            return "XTFNOTFOUND"
            raise XTFNOTFOUND('ARK not found in OAC')
        soup = BeautifulSoup(html_str)
        anchor_zoom = soup.find('a', attrs={"id": "zoomMe"})
        if not anchor_zoom:
            # try the first a with href substr = ark
            pat = ''.join(['/',self.ark,'.*'])
            pat = self.ark
            href_pat = re.compile(pat)
            anchor_zoom = soup.findAll('a', href=href_pat)[0]
        # BeautifulSoup behaves strangely here, can't get at child img tag
        #through the parser. Need to rip string...
        #should be better way of doing this whole process
        #regex = r'src="(\S+)"'
        #prog = re.compile(regex)
        #src = prog.search(anchor_zoom.renderContents())
        #image_link = src.group(1)
        arkimg = anchor_zoom.find('img')
        image_link = arkimg['src']
        if not image_link: #complex object?
            #find a different link: img with src left substr = /ark:/xxxxx/xx
            def arkimg(tag):
                if tag.name == 'img':
                    if tag['src'].find('ark:') > -1:
                        return True
                return False
            arkimg = soup.findAll(arkimg)[0]
            image_link = arkimg['src']
        return self.url_content_root+image_link.lstrip('/')
        '''
        return src.group(1)
        return anchor_zoom.renderContents()
        return anchor_zoom.findChild(name='img')
        return dir(anchor_zoom)
        img = anchor_zoom.contents
        img = anchor_zoom.find('img')
        #return img['src']
        return type(img)
        return dir(img)
        '''

    def save(self, force_insert=False, force_update=False):
        '''On save (esp initial, how to make ark read only after init)
        need to check with XTF if the ark is valid
        Also, if someone is trying to change the ARK, don't let them
        '''
        self.ark = ARKObject._ARK_normalize(self.ark)
        if self.pk:# existing object
            try:
                db_self = ARKObject.objects.get(pk=self.pk)
                if self.ark != db_self.ark:
                    #what to return?
                    #NOTE: this only works if I have a hidden numeric pk
                    raise ValueError('Can not change ARK for an object')
            except ARKObject.DoesNotExist:
                pass
        #Before saving the ark, make sure it's in OAC XTF
        #the _get_XTF_page will raise XTFNOTFOUND if ARK not found
        html = self._get_XTF_page()
        return super(ARKObject, self).save(force_insert, force_update)

    #How to access XTF objects? Need to fill in blank values for dcterms
    #need to map from XTF meta tags to dcterms for EAD & Digital Objects
    #content-type might still be easiest solution
    #also, do I need custom widgets for the DCterms for editing

    # make accessor functions to create lists of the various dublin core
    # element values (contents), so that <ARKObject instance>.creator(s)
    # returns list of creator DCTerms
    # Need to change the Inline to get the underlying XTF data if possible.

    def _get_XTF_search_page(self, url_base='http://content.cdlib.org/'):
        url = ''.join(( url_base, 'search?query=', self.ark.rstrip('/'), ';group=Items;raw=1'))
        # When Mod_security was added, it required an Accept header
        # so need to use urllib2 Request object, rather than urllib.urlopen()
        req = urllib2.Request(url=url)
        req.add_header("accept", "text/*")
        try:
            u = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            #the dc interface should play nice
            if e.code == 404:
                raise XTFNOTFOUND('ARK not found in OAC')
        resp_str = u.read()
        return resp_str

    def _get_XTF_page(self, url_base='http://content.cdlib.org/', query=None):
        '''Send a request to the dynaXML engine with an id?
        return string of xml.
        Can raise any urllib2.urlopen errors and 404?
        '''
        # the /dc/ interface is picky about the trailing slash, one & only one
        url = ''.join(( url_base, self.ark.rstrip('/'), '/'))
        if (query):
            url = ''.join((url, '?', query,))
        # When Mod_security was added, it required an Accept header
        # so need to use urllib2 Request object, rather than urllib.urlopen()
        req = urllib2.Request(url=url)
        req.add_header("accept", "text/*")
        try:
            u = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            #the dc interface should play nice
            if e.code == 404:
                raise XTFNOTFOUND('ARK not found in OAC')
        resp_str = u.read()
        if (resp_str.find('Document Not Found') > 0 or resp_str.find('Invalid Document') > 0):
            #TODO: SHOULD NEVER GET THIS
            raise XTFNOTFOUND('ARK not found in OAC')
        return resp_str

    def _etree_to_dcterm(self, element):
        '''Takes an etree element for the OAC QDC xml representation and 
        stuffs it into a DCTerm django object
        '''
        termval = DublinCoreTerm.DCTERM_MAP.get(element.tag, None) 
        q = element.attrib.get('q', None)
        return DublinCoreTerm(object_id = self.id,
                              content_type = ContentType.objects.get_for_model(self),
                              term = termval,
                              qualifier = q,
                              content = element.text
                             )

    def _parse_thumbnail_from_xml(self, xml):
        root = ET.fromstring(xml)
        return self._parse_thumbnail_data(root)

    def _parse_thumbnail_data(self, etree_root):
        thumbnode = etree_root.xpath('//thumbnail')[0]
        # there appear to be some thumbnode with blank X, Y -- these return ''
        # need to handle that possibility
        X = int(thumbnode.attrib.get('X', 185)) if thumbnode.attrib.get('X', 185) != '' else 185
        Y = int(thumbnode.attrib.get('Y', 140)) if thumbnode.attrib.get('Y', 140) != '' else 140
        thumbnail = {'src': self.url_content_root + self.ark.strip('/') + '/thumbnail', #A HACK HERE
                     'width': X,
                     'height': Y,
                    }
        return thumbnail

    def _parse_metadata_xml_page(self, xml):
        '''Parse the dc.xml file. Very nice concise representation of the
        DC data for OAC stuff.
        Convert the etree Elements into DublinCoreTerms
        '''
        root = ET.fromstring(xml)
        terms = {}
        for term in DublinCoreTerm.DCTERM_LIST:
            terms[term] = [self._etree_to_dcterm(elem) for elem in root.xpath('//'+term)]
        metas = root.xpath('//meta')[0].getchildren()
        terms['thumbnail'] = self._parse_thumbnail_data(root)
        return terms

    def _parse_metadata_html(self, html):
        '''Parse the page from XTF, filling in lists for the DC metadata
        Returns a dictionary of lists of ??. Dictionary is indexed by the
        Dublin Core Element Term name. Also returns a "META" list that contains
        ALL meta elements in the html.
        '''
        #xml = xml.replace('<ead>', '<ead xmlns:xtf="http://cdlib.org/xtf" xmlns:cdlpath="http://cdlib.org/cdlpath">')
        soup = BeautifulSoup(html)
        terms ={} 
        for term in DublinCoreTerm.DCTERM_LIST:
            term_dc = "DC."+term
            terms[term] = soup.findAll(attrs={"name": term_dc})
        def thumbimg(tag):
            if tag.name == 'img':
                if tag['src'].find('ark:') > -1:
                    return True
            return False
        thumbnail = soup.findAll(thumbimg)[0]
        if not thumbnail['src'].strip('/')[-9:] == 'thumbnail':
            #HACK: complex object, hard code
            thumbnail['src'] = self.url_content_root + self.ark.strip('/') + '/thumbnail' #A HACK HERE, complex objs don't have a good thumb link in metadata
            thumbnail['width'] = 185
            thumbnail['height'] = 140
        else:
            thumbnail['src'] = self.url_content_root + thumbnail['src'].strip('/')
        terms['thumbnail']=thumbnail
        return terms

    def _parse_metadata_dcxml_page(self, xml):
        '''Parse the dc.xml file. Very nice concise representation of the
        DC data for OAC stuff.
        Convert the etree Elements into DublinCoreTerms
        '''
        root = ET.fromstring(xml)
        terms = {}
        for term in DublinCoreTerm.DCTERM_LIST:
            terms[term] = [self._etree_to_dcterm(elem) for elem in root.findall(term)]
        return terms

    def _get_XTF_thumbnail(self):
        if not getattr(self, '_thumbnail', None):
            xml = self._get_XTF_search_page(url_base=self.url_content_root)
            thumbnail = self._parse_thumbnail_from_xml(xml)
            self._thumbnail = thumbnail
        return self._thumbnail

    def _get_XTF_metadata(self):
        '''Return dictionary of meta tags, index by name? This is different
        then the DC metadata'''
        if not getattr(self, '_meta_dict', None):
            xml = self._get_XTF_search_page(url_base=self.url_content_root)
            self._meta_dict = self._parse_metadata_xml_page(xml)
        return self._meta_dict


    def _get_XTF_DC_metadata(self):
        # first check to see if self data set...
        if not getattr(self, '_dc_dict', None):
            xml = self._get_XTF_page(url_base=self.url_dc_root)
            self._dc_dict = self._parse_metadata_dcxml_page(xml)
        return self._dc_dict

    def _get_dc_property(self, propname):
        '''Return list of dc elements for a give dc term.
        '''
        # verify propname in DC list
        internal_prop = "_"+propname
        if hasattr(self, internal_prop):
            prop_list = getattr(self, internal_prop)
        else:
            prop_list = self._get_XTF_DC_metadata()[propname]
        if len(prop_list) == 0:
            prop_list = None
        return prop_list

    @property
    def DCTerms(self):
        '''Returns a list of DublinCoreTerm objects that were extracted
        from the dc.xml
        '''
        dc_dict = self._get_XTF_DC_metadata()
        dc_list=[]
        [ map(dc_list.append, vlist) for vlist in dc_dict.values()]
        return dc_list

    @property
    def contributors(self):
        return self._get_dc_property("contributor")

    @property
    def coverages(self):
        return self._get_dc_property("coverage")

    @property
    def creators(self):
        return self._get_dc_property("creator")

    @property
    def dates(self):
        return self._get_dc_property("date")

    @property
    def descriptions(self):
        return self._get_dc_property("description")

    @property
    def formats(self):
        return self._get_dc_property("format")

    @property
    def identifiers(self):
        return self._get_dc_property("identifier")

    @property
    def languages(self):
        return self._get_dc_property("language")

    @property
    def publishers(self):
        return self._get_dc_property("publisher")

    @property
    def relations(self):
        return self._get_dc_property("relation")

    @property
    def rights(self):
        return self._get_dc_property("rights")

    @property
    def sources(self):
        return self._get_dc_property("source")

    @property
    def subjects(self):
        return self._get_dc_property("subject")

    @property
    def titles(self):
        return self._get_dc_property("title")

    @property
    def types(self):
        return self._get_dc_property("type")

    def __unicode__(self):
        return unicode(self.ark)

    @models.permalink
    def get_absolute_url(self):
        return ('arkobject_view', (), {'ark': self.ark, })


class ARKSet(models.Model):
    creator = models.ForeignKey(User)
    public = models.BooleanField()
    title = models.CharField(max_length=1024)
    markup = models.TextField(null=True, blank=True)
    ark_objects = models.ManyToManyField(ARKObject, through='ARKSetMember')
    DCTerms = generic.GenericRelation(DublinCoreTerm)
    geo = generic.GenericRelation(GeoPoint)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.title)

    @models.permalink
    def get_absolute_url(self):
        return ('arkset_view', (), {'pk': self.pk, })

    @property
    def has_geopoint(self):
        '''Return True if has a related GeoPoint
        '''
        return True if self.geo.all() else False

    @staticmethod
    def _parse_csv_row(csv_row):
        '''Wants a csv row list. Parses into a dict suitable for creating an
        arksetmember object
        '''
        if len(csv_row) < 2:
            raise ValueError('Must have ARK, annotation in csv row')
        ark = csv_row[0]
        #validate ark
        ark, NAAN, name, qual = validate(ark)
        annotation = csv_row[1]
        return locals()

    def _parse_csv(self, csv_reader):
        errors = []
        arks_added = []
        members_added = []
        num_add = 0
        numrows = 0
        for row in csv_reader:
            numrows+=1
            try:
                data = self._parse_csv_row(row)
            except ValueError, e:
                errors.append((e, row))
                continue
            try:
                arkobj, created = ARKObject.get_or_create(ark=data['ark'])
                if created:
                    arks_added.append(arkobj)
            except XTFNOTFOUND, e:
                errors.append((e, row))
                continue
            member = ARKSetMember(object=arkobj, set=self, annotation=data['annotation'])
            try:
                member.save()
                members_added.append(member)
                #except IntegrityError, e:
                    #except _mysql_exceptions.IntegrityError, e:
                        #except _mysql_exceptions.MySQLError, e:
            except:
                import sys
                e = sys.exc_info()
                if e[1].message.find("IntegrityError(1062"):
                    errors.append(("Duplicate Member entry for row, an ARK can only have one entry in a set.", row))
                else:
                    errors.append((e[1], row))
        return numrows, errors, members_added, arks_added


class ARKSetMember(models.Model):
    set = models.ForeignKey(ARKSet)
    object = models.ForeignKey(ARKObject)
    annotation = models.TextField(null=True, blank=True)
    DCTerms = generic.GenericRelation(DublinCoreTerm)
    geo = generic.GenericRelation(GeoPoint)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("set", "object"), )

    def __unicode__(self):
        return ''.join((unicode(self.object), ' in ', unicode(self.set)))

    def _get_lat_lon(self):
        geo = self.geo.all()
        if geo:
            self._lat = geo[0].lat
            self._lon = geo[0].lon
        else:
            self._lat = self.object.lat
            self._lon = self.object.lon
        return self._lat, self._lon

    @property
    def has_geopoint(self):
        '''Return True if has a related GeoPoint
        '''
        return True if self.geo.all() else False

    @property
    def title(self):
        '''Return the first of any title Dublin Core Terms. If none, return
        object unicode?
        '''
        titles = self.DCTerms.filter(term='T')
        return titles[0].content if titles else unicode(self.object)

    @property
    def lat(self):
        '''Return lat if stored in GeoPoint object, else None
        This may have a caching problem? as these objs are created each request
        shouldn't matter much
        '''
        return self._lat if getattr(self, "_lat", None) else self._get_lat_lon()[0]

    @property
    def lon(self):
        '''Return lat if stored in GeoPoint object, else None
        '''
        return self._lon if getattr(self, "_lon", None) else self._get_lat_lon()[1]
    @property
    def place(self):
        '''Reuturn GeoPoint.place else None'''
        geo = self.geo.all()
        if geo:
            return geo[0].place
        else:
            return None

    @property
    def location_exact(self):
        '''Is the stated location "exact"? (not approx)'''
        geo = self.geo.all()
        if geo:
            return geo[0].exact
        else:
            return None

    @models.permalink
    def get_absolute_url(self):
        return ('arksetmember_view', (), {'pk': self.pk, })
