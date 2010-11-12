from __future__ import with_statement
import sys
import math
from os.path import abspath, dirname, join
from csv import DictWriter
# import django settings
sys.path.insert(0, abspath(join(dirname(__file__), "../")))
sys.path.insert(0, abspath(join(dirname(__file__), "../apps")))
from django.conf import settings
#os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get("DJANGO_SETTINGS_MODULE","settings")

from themed_collection.models import ThemedCollection

def main(args):
    collections = ThemedCollection.objects.all()
    coincidents = set()
    for collection in collections:
        members = collection.get_members()
        for current_mem in members:
            if not current_mem.lat:
                continue
            current_mem.collection = collection
            other_members = collection.get_members()
            other_members = [m for m in other_members if current_mem != m ]
            for other_mem in other_members:
               if not other_mem.lat:
                   continue
               other_mem.collection = collection
               dist = math.sqrt(((current_mem.lat - other_mem.lat)**2 + (current_mem.lon - other_mem.lon)**2 )) 
               if (dist == 0.0):
                   #if (dist < .001):
                   print dist, current_mem, other_mem
                   coincidents.add(current_mem)
                   coincidents.add(other_mem)
    print "NUMBER: ", len(coincidents)
    print coincidents
    fieldnames = ['ark', 'title', 'place', 'lat', 'lon', 'collection', 'exact']
    field_dict = dict([(x, x.capitalize()) for x in fieldnames])
    coincidents_sorted = sorted(coincidents, key=lambda x: str(x.collection))
    #coincidents_sorted = sorted(coincidents, key=lambda x: x.lat)
    with open('report_map_coincidents.csv','w') as f:
        csvFile = DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        csvFile.writerow(field_dict)
        for c in coincidents_sorted:
            data = { 'ark':c.object.ark.strip(),
                    'title':c.title.strip(),
                    'lat':c.lat,
                    'lon':c.lon,
                    'place':c.place,
                    'collection':str(c.collection).strip(),
                    'exact':str(c.location_exact).strip(),
                   }
            csvFile.writerow(data)

if __name__=="__main__":
    main(sys.argv)
