import csv
import simplejson
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import permission_required, login_required
from django.template import RequestContext
from django.http import HttpResponse
from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
from django import forms
from django.conf import settings
from geocoders_dsc import Google, GeoCodeException
from themed_collection.models import ThemedCollection
from xtf.models import ARKSet, ARKSetMember, ARKObject, GeoPoint, XTFNOTFOUND #should get urls from ARKSet!
from xtf.models import DublinCoreTerm
from xtf.ARK_validator import validate, extract


def ARKSetMember_map_data(member):
    '''build the data object for an ARKSetMember'''
    if member.object.titles:
        #titles = ' '.join([ d['value'] for d in member.object.titles]) # Used when BeautifulSoup is parser, should probably wrap the elem...
        titles = ' '.join([ d.content for d in member.object.titles if d.content]) #-- used whne ElementTree is parser 
    else:
        titles = member.title
    if member.object.dates:
        #dates = ' '.join([ d['value'] for d in member.object.dates if d])
        dates = ' '.join([ d.content for d in member.object.dates if d.content])
    else:
        dates = ''
    return dict(title=titles,
                date=dates,
                note=member.annotation,
                lat=member.lat,
                lon=member.lon,
                place=member.place,
                thumbnail=member.object.thumbnail,
                url_content=member.object.url_content,
                image=member.object.image,
                exact=member.location_exact,
               )

def collection_members_map_data(member_list):
    data = {}
    for member in member_list:
        data[member.object.ark]= ARKSetMember_map_data(member)
    return data

def collection_members_map_json(member_list):
    return simplejson.dumps(collection_members_map_data(member_list))

def view_json(request, pk=None, slug=None):
    '''Return a simple almost static view
    '''
    if slug:
        themed_collection = get_object_or_404(ThemedCollection, slug=slug)
    elif pk:
        themed_collection = get_object_or_404(ThemedCollection, pk=pk)
    else:
        raise Http404

    collection_members = themed_collection.get_members()
    #compile map data
    json = collection_members_map_json(collection_members)
    return HttpResponse(json, mimetype='application/json')

def view_themed_collection(request, pk=None, slug=None):
    '''Return a simple almost static view
    '''
    if slug:
        themed_collection = get_object_or_404(ThemedCollection, slug=slug)
    elif pk:
        themed_collection = get_object_or_404(ThemedCollection, pk=pk)
    else:
        raise Http404

    collections = ThemedCollection.objects.all()
    collection_members = themed_collection.get_members()
    google_map_key = settings.GOOGLE_MAP_KEY
    return render_to_response('themed_collection/view_collection.html',
                              locals()
                             )

def _parse_csv_row(csv_row):
    '''Wants a csv row list. Parses into a dict suitable for creating an
    arksetmember object
    '''
    if len(csv_row) < 2:
        raise ValueError('Must have ARK, annotation in csv row')
    ark = csv_row[1]
    ark = ark[ark.index('ark:'):]
    #validate ark
    ark, NAAN, name, qual = extract(ark)
    title = csv_row[2]
    region = csv_row[0]
    city = csv_row[4]
    geo_place = csv_row[5]
    geo_place_notes = csv_row[9]
    dates = csv_row[6]
    theme_type = csv_row[7]
    notes = csv_row[9]
    mosaic = False if csv_row[10] == '' else True
    exact = True if csv_row[11] == '' else False
    ret_dict = locals()
    del ret_dict['csv_row']
    return ret_dict

def _parse_csv(csv_reader, arkset, themed_collection):
    errors = []
    arks_added = []
    members_added = []
    num_add = 0
    not_geocoded = []
    numrows = 0
    g = Google('ABQIAAAAPZhPbFDgyqqKaAJtfPgdhRQxAnOebRR8qqjlEjE1Y4ZOeQ67yxSVDP1Eq9oU2BZjw2PaheQ5prTXaw')
    for row in csv_reader:
        numrows+=1
        try:
            data = _parse_csv_row(row)
            #print data
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
        member = ARKSetMember(object=arkobj, set=arkset, annotation=data['notes'])
        try:
            member.save()
            members_added.append(member)
            # is there a title? if so create a DCTerm for title
            if (data['title']):
                try:
                    dcterm = DublinCoreTerm(content_object=member, term='T', content=data['title'])
                    dcterm.save()
                except:
                    pass
            #attempt geocode
            place = lat = lng = None
            try:
                if not data['geo_place']:
                    location = ' '.join((data['city'], 'CA'))
                    not_geocoded.append((member, "Only to city level", location))
                else:
                    location = data['geo_place']
                place, (lat, lng) = g.geocode(location)
                gpt = GeoPoint(content_object=member, lat=lat, lon=lng, place=place, exact=data['exact'])
                gpt.save()
            except GeoCodeException, e:
                not_geocoded.append((member,e.message, location))
            #except IntegrityError, e:
                #except _mysql_exceptions.IntegrityError, e:
                    #except _mysql_exceptions.MySQLError, e
            #is in mosaic?
            if data['mosaic']:
                themed_collection.mosaic_members.add(member)
        except:
            import sys
            e = sys.exc_info()
            if e[1].message.find("IntegrityError(1062"):
                errors.append(("Duplicate Member entry for row, an ARK can only have one entry in a set.", row))
            else:
                errors.append((e[1], row))
    return numrows, errors, members_added, arks_added, not_geocoded

#Decorator won't work, need to check object level perm...
#@permission_required('xtf.change_arkset')
@login_required
def input_csv(request, pk):
    '''Input a csv of ARKSetMembers into a given arkset
    '''
    themed_collection = get_object_or_404(ThemedCollection, pk=pk)
    #    if not request.user.has_perm('xtf.change_themedcollection', themed_collection):
        #    return  HttpResponseForbidden('<h1>Permission Denied</h1>')
    arkset_choices = [(arkset.pk, arkset.title) for arkset in themed_collection.arksets.all()]
    class UploadFileForm(forms.Form):
        set = forms.ChoiceField(choices=arkset_choices)
        file = forms.FileField()


    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if not request.FILES:
                form.errors['file'] = ('NO FILE INPUT',)
            else:
                #THIS SUCKS, LOOKS LIKE THE DJANGO UPLOAD FILE doesn't use universal newlines, can i fix by reading into one that does?
                #TODO: fix this problem with newlines here, how?
                # the UploadFile object bombs right away...
                # may need to read into file, then do a universal newline read
                csv_reader = csv.reader(form.cleaned_data['file'])
                arkset = ARKSet.objects.get(id=form.cleaned_data['set'])
                numrows, errs, set_members_added, arks_added, not_geocoded = _parse_csv(csv_reader, arkset, themed_collection)
                num = len(set_members_added)
                return render_to_response('themed_collection/input_csv_result.html',
                                         locals(),
                                         )
    else:
        form = UploadFileForm()
    return render_to_response('themed_collection/input_csv.html',
                              locals(),
                             )
