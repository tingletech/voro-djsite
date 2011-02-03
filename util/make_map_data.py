#! /usr/bin/python
'''This script generates the flat files for the map page.
'''

import os, sys
import logging, logging.handlers
import random
import math
import urllib
import lxml.etree as ET #lxml etree module
import codecs
import datetime

LOG_LEVEL = logging.INFO
LOG_BACKUP_COUNT = 10

FILE_PATH = os.path.abspath(os.path.split(__file__)[0])
DJSITE_DIR = os.path.join(FILE_PATH, '..')

URL_OAC_INSTITUTIONS = '/institutions/'
XTF_URL_BASE ="http://" + os.environ.get('J2EE_SERVER', 'content.cdlib.org:10890') + '/xtf/'

sys.path.append(DJSITE_DIR)

# set the DJANGO_SETTINGS_MODULE 
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"

#log.info( "sys.path = %s " % sys.path)

import django
#from django.utils import simplejson
# import site settings, gives access to db & models
from django.conf import settings
from oac.models import Institution, City, GroupProfile

def makeMarkerLabel(institute):
    #label is wrapped inside double quotes, so raw string & escape quotes
    label = r'<div class=\"balloon\"><strong>'
    label += r'<a href=\"' + URL_OAC_INSTITUTIONS
    label += urllib.quote_plus(institute.name_doublelist.encode('utf-8')).replace('%2F', '/')
    #label += institute.name_doublelist.encode('utf-8')
    label += r'\">'
    label += institute.name.replace('"','\\"')
    label += r'</a>'
    label += '</strong><br/>'
    label += institute.address1.replace('"','\\"')+ '<br/>'
    label += str(institute.city).replace('"','\\"') + ', CA '
    label += institute.zip4 + '<br/><br/>'
    label += 'Get directions to this place from:<br/>'
    label += r'<form onsubmit=\"loadDirectionsFromForm('
    label += str(institute.latitude) + ',' + str(institute.longitude)
    label += r',this); return false;\">'
    label += r'<table><tr valign=\"top\" >'
    label += r'<td valign=\"top\"><input type=\"text\" name=\"from\" value=\"\" size=\"25\"/></td>'
    label += r'<td valign=\"top\"><input type=\"image\" src=\"/images/buttons/go.gif\" value=\"Search\" alt=\"Go\" title=\"Go\" /></td>'
    #label += r'<td><input type=\"image\" src=\"/images/buttons/go.gif\" class=\"search-button\" value=\"Search\" alt=\"Go\" title=\"Go\" /></td>'
    label += r'</tr></table>'
    label += r'</form><br/>'
    label += r'<a href=\"' + URL_OAC_INSTITUTIONS
    label += urllib.quote_plus(institute.name_doublelist.encode('utf-8')).replace('%2F', '/')
    #label += institute.name_doublelist.encode('utf-8')
    label += r'\">'
    label += r'Browse the collections'
    label += r'</a>'
    label += '</div>'
    return label
          

def setup_logger():
    log = logging.getLogger()
    log.setLevel(LOG_LEVEL)
    h = logging.handlers.RotatingFileHandler('make_map_data.log',backupCount=LOG_BACKUP_COUNT )
    h.setLevel(LOG_LEVEL)
    format = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    h.setFormatter(format)
    h.doRollover()
    log.addHandler(h)
    h = logging.handlers.RotatingFileHandler('make_map_data.err',backupCount=LOG_BACKUP_COUNT )
    h.setLevel(logging.ERROR)
    format = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    h.setFormatter(format)
    h.doRollover()
    log.addHandler(h)
    return log


def addList(x):
    x.subinsts = []
    #    x.lat = x.latitude
    #    x.longitude = x.longitude
    return x


def XTF_inst_dict(URL=None):
    ''' Returns a dictionary indexed by institution doublelist name.
    doublelist name is <name of parent>::<name of inst>, if no parent it's
    just <name of inst>
    '''
    if not URL:
        institutions_query_1 = XTF_URL_BASE + "rawQuery?query=";
        institutions_query_2 = '''\
<query indexPath="index" termLimit="1000" workLimit="20000000"
	style="style/crossQuery/resultFormatter/oac4/limitFormatter.xsl"
	startDoc="1" maxDocs="0" normalizeScores="false">
  <facet field="facet-institution" select="**" sortGroupsBy="value"/>
  <and>
    <and field="oac4-tab">
      <term>Collections*</term>
    </and>
  </and>
</query>
'''
        URL = institutions_query_1 + urllib.quote(institutions_query_2)

    insts = []
    xml = urllib.urlopen(URL)
    #print xml.readlines()
    #sys.stdout.flush()
    try:
        tree = ET.parse(xml)
        root = tree.getroot()
        groups = root.findall("./facet/group")
        for g in groups:
            insts.append( dict(name=g.attrib['value'], pname=None))
            subgroups = g.findall("./group")
            for sg in subgroups:
                insts.append( dict(name=sg.attrib['value'], pname=g.attrib['value']))
    finally:
        xml.close()
    instsDoubleList = map(lambda x: x['pname']+'::'+x['name'] if x['pname'] else x['name'], insts)
    instsDoubleListDict = dict( zip(instsDoubleList, insts))
    return instsDoubleListDict

def report_inst_counts(institution_list):
    ''' Report the number of institutions
    Need to check that each inst has a valid voro ead user and
    remove parents?
    '''
    count_insts = 0
    inst_valid = []
    for inst in institution_list:
        if inst.isa_campus == 0:
            inst_valid.append(inst)
            count_insts += 1
        for subinst in inst.subinsts:
            inst_valid.append(subinst)
            count_insts +=1
    # for inst_valid see if there is a user with  a voro ead accoutn
    # this will be a bit involved, must get associated groupprofiles for inst
    # get groups for the groupprofiles, get users for the groups
    # then check user's profile for voro ead flag. Add inst only if a user has voro ead and break loop
    inst_verified = []
    for inst in inst_valid:
        verified = False
        gprofiles = inst.groupprofile_set.all()
        for prof in gprofiles:
            group = prof.group
            for user in group.user_set.all():
                if user.userprofile.voroEAD_account == 1:
                    inst_verified.append(inst)
                    verified = True
                    break
            if verified == True:
                break

    return count_insts, inst_verified

def report_new_insts(institution_list, date_since,
                     date_until=datetime.date.today()):
    ''' Report number of new institutions since given date
    First filter the list by date, then use report inst counts
    Django date fields are already date times
    '''
    recents = []
    for inst in institution_list:
        if date_until >= inst.created_at.date() >= date_since:
            recents.append(inst)
    #print recents
    return report_inst_counts(recents)

def report_institution_numbers(institution_list, filename='inst_counts.txt'):
    f = open(filename, 'w')
    try:
        c, insts_valid = report_inst_counts(institution_list)
        msg = "Current active OAC institutions: " + str(c) + '\n\n\n'
        f.write(msg)
    
        # since begining of current year
        today = datetime.date.today()
        cal_year_start = datetime.date(today.year, 1, 1)
        c2, i2 = report_new_insts(institution_list, cal_year_start)
        msg = ''.join([ "INSTS since: ", str(cal_year_start), " : ", str(c2),
                       ' :\n ', str(i2), '\n\n\n'])
        f.write(msg)
    
        # rolling windows
        # last month
        delta = datetime.timedelta(days=30)
        date_since = today - delta
        c2, i2 = report_new_insts(institution_list, date_since)
        msg = ''.join(["INSTS in last 30 days: ", str(c2),
                       ' :\n ', str(i2), '\n\n\n'])
        f.write(msg)
        # last 3 months
        delta = datetime.timedelta(days=90)
        date_since = today - delta
        c2, i2 = report_new_insts(institution_list, date_since)
        msg = ''.join(["INSTS in last 90 days: ", str(c2),
                       ' :\n ', str(i2), '\n\n\n'])
        f.write(msg)
        # last 6 months
        delta = datetime.timedelta(days=180)
        date_since = today - delta
        c2, i2 = report_new_insts(institution_list, date_since)
        msg = ''.join(["INSTS in last 180 days: ", str(c2),
                       ' :\n ', str(i2), '\n\n\n'])
        f.write(msg)
        # last year
        delta = datetime.timedelta(days=365)
        date_since = today - delta
        c2, i2 = report_new_insts(institution_list, date_since)
        msg = ''.join(["INSTS in last year: ", str(c2),
                       ' :\n ', str(i2), '\n\n\n'])
        f.write(msg)

        # fiscal year
        if today.month >= 7:
            last_july = datetime.date(today.year, 7, 1)
        else:
            last_july = datetime.date(today.year-1, 7, 1)
        c2, i2 = report_new_insts(institution_list, last_july)
        msg = ''.join([ "INSTS current fiscal year since: ", str(last_july),
                       " : ", str(c2), ' :\n ',
                       str(i2), '\n\n\n'])
        f.write(msg)
    
        # previous fiscal year
        last_fiscal_year_end = last_july
        last_fiscal_year_start = datetime.date(last_july.year-1, 7, 1)
        c2, i2 = report_new_insts(institution_list, last_fiscal_year_start,
                                  last_fiscal_year_end)
        msg =  ''.join(["INSTS during previous fiscal year from: ", str(last_fiscal_year_start), " to ",
        str(last_fiscal_year_end), " : ",  str(c2), ' :\n ', str(i2), '\n\n\n' ])
        f.write(msg)

    finally:
        f.close()

def main(argv):


    log = setup_logger()
    institution_list = map(addList , Institution.objects.order_by('name'))
    log.info(institution_list)
    log.info( "NUM INSTS:%d" % len(institution_list))
    
    #Remove any insts not found in XTF query
    xtf_doublelist = XTF_inst_dict()
    not_in_xtf = []
    in_xtf = []
    tmp_list = []
    for i, inst in enumerate(institution_list):
        if inst.name_doublelist not in xtf_doublelist:
            log.info("DJANGO INST NOT FOUND IN XTF:%s" % inst.name_doublelist)
            not_in_xtf.append((inst.name_doublelist, inst))
            #institution_list.remove(inst) DON'T DO THIS IN PLACE 
            # edit of iteration list. (should create a list cmprehension to 
            # loop over???? index gets screwed with in place editing
        else:
            log.info("DJANGO FOUND IN XTF:%s" % inst.name_doublelist)
            xtf_doublelist[inst.name_doublelist]['in_django'] = True
            in_xtf.append((inst.name_doublelist, inst))
            tmp_list.append(inst)
    institution_list = tmp_list

    '''
    #TODO: erase following?
    f = open('not_in_xtf','w')
    for x in not_in_xtf:
        f.write(x[0] + ' ---- ' + str(x[1]) + '\n')
    f.close()
    print not_in_xtf
    print "\n\n\n\n\n\n\n"
    f = open('in_xtf','w')
    for x in in_xtf:
        f.write(x[0] + ' ---- ' + str(x[1]) + '\n')
    f.close()
    print in_xtf
    '''
    # report institutitions in XTf but not Django
    not_in_django = []
    # Probably want to report these below as 
    # well as insts in Django but not XTF
    for doublename,x in xtf_doublelist.items():
        if not x.has_key('in_django'):
            log.info('INST IN XTF but not DJANGO:%s', doublename) 
            not_in_django.append(doublename)

    '''
    print "\n\n\n\n\n\n\n"
    print not_in_django
    f = open('not_in_django','w')
    for x in not_in_django:
        f.write(x +'\n')
    f.close()
    f = open('xtf_list','w')
    for doublename, x in xtf_doublelist.items():
        f.write(doublename + ' ---- ' + str(x) + '\n')
    f.close()
    '''

    log.info("NUMBER OF INSTS for map page:%d" % len(institution_list))
    log.info("NUMBER OF XTF INSTS:%d" % len(xtf_doublelist))

    '''
    Put any institutes that are at same lat-longitude in a 'circle' around point
    '''
    used_lat_longitude = {}
    for institute in institution_list:
        lat_longitude_key = '%s|%s' % (institute.latitude, institute.longitude)
        if lat_longitude_key in used_lat_longitude:
            used_lat_longitude[lat_longitude_key].append(institute)
        else:
            used_lat_longitude[lat_longitude_key] = [institute,]
    #    if len(institute.subinsts) > 0:
    #        for inst in institute.subinsts:
    #            lat_longitude_key = '%s|%s' % (inst.latitude, inst.longitude)
    #        if lat_longitude_key in used_lat_longitude:
    #            used_lat_longitude[lat_longitude_key].append(inst)
    #        else:
    #            used_lat_longitude[lat_longitude_key] = [inst,]
    
    
    
    for (lat_longitude, inst_list) in used_lat_longitude.items():
        num_items = len(inst_list)
        log.info("Original lat: %s, numb:%d" % (lat_longitude, num_items))
        if num_items > 1:
            #need to fudge with lat/longitudes for items in list
            radius = .0001 * num_items
            angle = random.random()*(2*math.pi)
            angle = 0
            angle_delta = (math.pi*2)/num_items
            
            for inst in inst_list:
                inst.latitude= inst.latitude + (radius * math.cos(angle))
                inst.longitude =  inst.longitude + (radius * math.sin(angle))
                log.info("Inst: %s , angle: %s, lat:%s, longitude:%s" % (inst.name,
                                                                   angle,
                                                                   inst.latitude,
                                                                   inst.longitude)
                        )
                angle += angle_delta
    

    #the institutes are now ordered by name, but we must also list parent and 
    # sub institutions in order:::
    # for each institute
    # for each institution if a child attach to parent list....
    
    institution_list_loop = list(Institution.objects.order_by('name'))
    count = 0
    for institute in institution_list_loop:
        count = count + 1
        try:
            # if inst has children, remove them from list... 
            for inst in institute.children.all():
                try:
                    inst_item = institution_list[institution_list.index(inst)]
                    institution_list[institution_list.index(institute)].subinsts.append(inst_item)
                    institution_list.remove(inst)
                except ValueError:
                    # Already removed by XTF check
                    continue
        except Institution.DoesNotExist:
            #has no parent, find out how many subinsts?
            log.info("ERROR FOR inst=%s. Parent bombs...." % institute)
    
    #log resulting 'list'
    for institute in institution_list:
        log.info("TOP:%s lat:%s longitude:%s" % (institute, institute.latitude,
                                        institute.longitude))
        try:
            if len(institute.subinsts) > 0:
                for inst in institute.subinsts:
                    log.info("\tChild:%s lat:%s longitude:%s" % (inst, inst.latitude,
                                                        inst.longitude))
        except AttributeError:
            pass
    

    #create the institutes.js file
    #json formatted institute information
    
    #also create the campus.dropdown file for 'campus' institutions
    
    campus_list = []
    campus_dropdown = ''
    city_list = []
    city_dropdown = ''
    
    institute_json = 'var institutes = {'
    first = True
    inchild = False
    count = 0
    length = len(institution_list)
    # now the institutes in list are all top level institutes
    # children are accessed through the children param!!!!
    
    for institute in institution_list:
        #build incremental html for sidebar display (a bit fragile this)
        #the first and last items have different prefix & postfix requirements
        html = ''
        
        if len(institute.subinsts) == 0:
            #if len(institute.subinsts) == 0:
            html = r'<div class=\"institutions-off\" >'
            html += r'<a href=\"javascript:zoomToMarkerWithDeselect(\'' + institute.ark + r'\')\">'
            html += institute.name + '</a></div>'
        else:
            html = r'<div class=\"institutions-off\" >'
            html += r'<a href=\"javascript:zoomToMarkerWithDeselect(\'' + institute.ark + r'\')\">'
            html += institute.name + '</a>'
            #        html += '</div>'
            
#        if institute.parent_ark is None:
    #            institute.parent_ark = ''
    
        #build the label for GMap Marker popup
        label = makeMarkerLabel(institute)
    
        json_rep = ''.join(['"',institute.ark,'" : {',
                            'name:"', institute.name.replace('"','\\"'),'"',
                            ', lat:', str(institute.latitude),
                            ', lng:', str(institute.longitude),
                            ', address:"', institute.address1.replace('"','\\"'),'"',
                            ', city:"', institute.city.name,'"',
                            ', county:"', institute.county.name,'"',
                            ', zip4:"', institute.zip4,'"',
                            ', url:"', str(institute.url),'"',
                            ', region:"', str(institute.region),'"',
                            #                            ', parent_ark:"', institute.parent_ark,'"',
                            ', label:"', label, '"',
                            ', html:"', html, '"',
                            '},\n'])
        institute_json = institute_json + json_rep
    
    
        # now if institute has children----
        if len(institute.subinsts) > 0:
            #if len(institute.subinsts) > 0:
            #for inst in institute.children.all():
            for inst in institute.subinsts:
                log.info("Sub-institute:%s lat:%s longitude:%s" % (inst.name,
                                                             inst.latitude,
                                                             inst.longitude
                                                            )
                        )
                chtml = r'<div class=\"institutuions-off\" style=\"text-indent:3em;\">'
                chtml += r'<a href=\"javascript:zoomToMarker(\'' + inst.ark + r'\')\">'
                chtml += inst.name + '</a></div>'
                label = makeMarkerLabel(inst)
                json_rep = ''.join(['"',inst.ark,'" : {',
                            'name:"', inst.name.replace('"','\\"'),'"',
                            ', lat:', str(inst.latitude),
                            ', lng:', str(inst.longitude),
                            ', address:"', inst.address1.replace('"','\\"'),'"',
                            ', city:"', inst.city.name,'"',
                            ', county:"', inst.county.name,'"',
                            ', zip4:"', inst.zip4,'"',
                            ', url:"', str(inst.url),'"',
                            ', region:"', str(inst.region),'"',
                                    #                            ', parent_ark:"', inst.parent_ark,'"',
                            ', label:"', label, '"',
                            ', html:"', chtml, '"',
                            '},\n'])
                institute_json = institute_json + json_rep
    
            #last one needt to add a /div to close parent
            institute_json = institute_json[:-4] + '</div>"},\n'
    
                
        if (institute.isa_campus != 0):
            campus_list.append(institute)
    
        if (institute.city not in city_list):
            city_list.append(institute.city)
    
        count = count+1
    

    report_institution_numbers(institution_list)

    campus_list.sort(lambda x,y: cmp(x.name, y.name))
    for campus in campus_list:
        campus_dropdown += ''.join(['<option value="',
                                   campus.ark,
                                   '">',
                                   campus.name, '</option>\n'])
    
    #sort list of cities
    city_list.sort(lambda x,y: cmp(x.name, y.name))
    for city in city_list:
       city_dropdown += ''.join(['<option value="',
                                 str(city.latitude), ',',
                                 str(city.longitude), '">',
                                 city.name,
                                 '</option>\n'])
    
    institute_json = institute_json[:-2] + "\n}\n"
    inst_file = codecs.open('institutes.js','w', 'utf-8')
    inst_file.write(institute_json)
    inst_file.close()
    
    campus_file = codecs.open('campus.dropdown','w', 'utf-8')
    campus_file.write(campus_dropdown)
    campus_file.close
    log.info("Campus list contains %d entries" % len(campus_list))
    
    city_file = codecs.open('city.dropdown','w', 'utf-8')
    city_file.write(city_dropdown)
    city_file.close
    
if __name__=="__main__":
    main(sys.argv)
