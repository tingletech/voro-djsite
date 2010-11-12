import simplejson
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import permission_required, login_required
from django.template import RequestContext
from django.http import HttpResponse
from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
from django import forms
from xtf.models import ARKObject, ARKSet, ARKSetMember
from xtf.ARK_validator import ARKInvalid

def view_XTF_item(request, id, *args):
    xtfitem = get_object_or_404(XTFItem, item_id=id)
    # use contentype framework to get object pointed at....
    # helper function:
    # look into XTF and see if object exists,
    # create an XTFItem object if it does
    xtfdoc = xtfitem.get_associated_object()
    return render_to_response('xtf/view_XTF_item.html',
                              {'XTFItem':xtfitem, 'XTFDoc':xtfdoc },
                              context_instance = RequestContext(request)
                             )

def view_EAD_doc(request, id, *args):
    eaddoc = get_object_or_404(EADDoc, ark=id)
    return render_to_response('xtf/view_XTF_item.html',
                              {'XTFItem':None, 'XTFDoc':eaddoc },
                              context_instance = RequestContext(request)
                             )

def view_ARKObject(request, ark, *args):
    arkobject = get_object_or_404(ARKObject, ark=ark)
    return render_to_response('xtf/view_ARKObject.html',
                              locals(),#{'ARKObject':arkobject, },
                              context_instance = RequestContext(request)
                             )

def view_ARKSet(request, pk):
    '''Numeric pk access to the set
    '''
    arkset = get_object_or_404(ARKSet, pk=pk)
    return render_to_response('xtf/view_ARKSet.html',
                              locals(),#{'ARKSet':arkset, },
                              # context_instance = RequestContext(request)
                             )

def map_ARKSet(request, pk):
    arkset = get_object_or_404(ARKSet, pk=pk)
    arkset.lat = None
    arkset.lon = None
    try:
        g = arkset.geo.all()[0]
        arkset.lat = g.lat
        arkset.lon = g.lon
    except GeoPointDoesNotExist:
        pass
    #build json, will just include directly in template for now
    #should use simple json, create dict with arks as keys
    #values will be sub dict with lat, lon, thumbnail, link, ???
    json = ARKSetMembers_map_json(arkset)
    return render_to_response('xtf/map_ARKSet.html',
                              locals(),
                             )
    
def ARKSetMember_map_data(member):
    '''build the data object for an ARKSetMember'''
    return dict(note=member.annotation,
                lat=member.lat,
                lon=member.lon,
                thumbnail=member.object.thumbnail,
               )

def ARKSet_members_map_data(arkset):
    data = {}
    for member in arkset.arksetmember_set.all():
        data[member.object.ark]= ARKSetMember_map_data(member)
    return data

def ARKSetMembers_map_json(arkset):
    return simplejson.dumps(ARKSet_members_map_data(arkset))

def view_ARKSetMembers_map_json(request, pk):
    '''Return a json representation of ark set members locations for map
    '''
    arkset = get_object_or_404(ARKSet, pk=pk)
    return HttpResponse(ARKSetMembers_map_json(arkset),
                                    mimetype='application/json')
#    json += ''.join(['"', ark, '" : {region: ', str(region), ', county: "',
#                             row[4], '", city: "', row[5], '", title: "',
#                             row[2].replace('"',r'\"'), 
#                             '", themes: ', str(themes), ', notes: "',
#                             row[6].replace('"',r'\"'),
#                             '", dates: "', row[7].replace('"',r'\"'), 
#                             '", lat:', str(lat), ', lng:',
#                             str(lng), '},\n'
#                            ]
#                           )
    

@login_required
def view_ARKSets(request):
    '''View the ARK sets for a user. Include links for editing and metadata
    '''
    sets = request.user.arkset_set.all()
    return render_to_response('xtf/view_ARKsets.html',
                              locals(),
                             )


def view_ARKSetMember(request, pk):
    '''Numeric pk access to the set
    '''
    arksetmember = get_object_or_404(ARKSetMember, pk=pk)
    return render_to_response('xtf/view_ARKSetMember.html',
                              locals(),#{'ARKSetMember':arksetmember, },
                              # context_instance = RequestContext(request)
                             )

class ARKSetForm(forms.ModelForm):
    class Meta:
        model = ARKSet
        exclude = ('creator', 'ark_objects')

def edit_ARKSet(request, pk):
    arkset = get_object_or_404(ARKSet, pk=pk)
    # need to set up a Model Form
    # then handel ARKSet members interface
    form = ARKSetForm(instance=arkset)
    return render_to_response('xtf/edit_ARKSet.html',
                              locals(),
                             )

def edit_ARKSetMembers(request, pk):
    arkset = get_object_or_404(ARKSet, pk=pk)
    return render_to_response('xtf/edit_ARKSetMembers.html',
                              locals(),
                             )

class UploadFileForm(forms.Form):
    file = forms.FileField()


#Decorator won't work, need to check object level perm...
#@permission_required('xtf.change_arkset')
@login_required
def input_csv(request, pk):
    '''Input a csv of ARKSetMembers into a given arkset
    '''
    arkset = get_object_or_404(ARKSet, pk=pk)
    if not request.user.has_perm('xtf.change_arkset', arkset):
        return  HttpResponseForbidden('<h1>Permission Denied</h1>')
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid:
            if not request.FILES:
                form.errors['file'] = ('NO FILE INPUT',)
            else:
                import csv
                csv_reader = csv.reader(request.FILES['file'])
                numrows, errs, set_members_added, arks_added = arkset._parse_csv(csv_reader)
                num = len(set_members_added)
                return render_to_response('xtf/input_csv_result.html',
                                         locals(),
                                         )
    else:
        form = UploadFileForm()
    return render_to_response('xtf/input_csv.html',
                              locals(),
                             )

class ARKSetMemberForm(forms.ModelForm):
    class Meta:
        model = ARKSetMember
        
class ARKSetMemberAddForm(forms.Form):
    set = forms.ChoiceField()
    object = forms.CharField(max_length=50, widget=forms.HiddenInput)
    annotation = forms.CharField(widget=forms.Textarea)

def add_MemberToARKSet(request, set_id, ark):
    '''Add an ARKObject to the given set. Must create a ARKSetMember with
    set and ARK & annotation.
    '''
    set = ARKSet.objects.get(pk=set_id)
    if not request.user.has_perm('xtf.change_arkset', set):
        return  HttpResponseForbidden('<h1>Permission Denied</h1>')
    arkObj = ARKObject.objects.get(ark=ark)
    note = request.POST.get('annotation',None)
    member = ARKSetMember(set=set, object=arkObj, annotation=note)
    #TODO: save may throw following, how to handle?
    #Exception Type:  	IntegrityError
    #Exception Value: 	(1062, "Duplicate entry '1-12' for key 2")
    member.save()
    return render_to_response('xtf/arksetmember_added.html',
                              locals()
                             )

@login_required(redirect_field_name='next')
def add_ARKSetMember(request):
    sets = request.user.arkset_set.all()
    set_choices = [(s.id, str(s)) for s in sets]
    if request.method == 'POST':
        #on post, don't create an arkobject?
        # want to forward to the chosen 
        form = ARKSetMemberAddForm(request.POST)
        form['set'].field.choices = set_choices
        if form.is_valid():
            #send to selected set members/add page?
            return add_MemberToARKSet(request, form.cleaned_data['set'], form.cleaned_data['object'])
    else:
        #form = ARKSetMemberForm(initial={'object':arkobject.id, })
        #all this to get ark
        if request.method == 'GET':
            if request.GET.get('ark',None):
                try:
                    arkobject, newARK = ARKObject._get_or_create(request.GET['ark'])
                except ARKInvalid, e:
                    msg = ''.join(('Bad Request: ARK invalid : ', str(e)))
                    return HttpResponseBadRequest(content=msg)
            else:
                return HttpResponseBadRequest(content='Bad Request: No ARK given')
        #form = ARKSetMemberForm(initial={'object':arkobject, 'set':sets, })
        form = ARKSetMemberAddForm(initial={'object':arkobject, 'set':set_choices, })
        form['set'].field.choices = set_choices
    return render_to_response('xtf/add_ARKSetMember.html',
                              locals(),
                             )
