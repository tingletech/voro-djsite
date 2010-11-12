'''
A simple implementation for geocoding addresses. geopy imports expat which has
library problems with apache, so we crufted this up to avoid the problem.
Very basic implementation, but mimics usage of geopy Google geocoder so it could
be replaced at some point.
'''
import re
import time
import simplejson
from urllib import quote_plus, urlencode
from urllib2 import urlopen, HTTPError

GOOGLE_MAP_KEY = "ABQIAAAAPZhPbFDgyqqKaAJtfPgdhRQxAnOebRR8qqjlEjE1Y4ZOeQ67yxSVDP1Eq9oU2BZjw2PaheQ5prTXaw"

class GeoCodeException(Exception):
    pass

class Google(object):
    '''Return a place, lat, lng from Google map interface. May need to change
    this to reflect the Google service changes.

    >>> g = Google()
    >>> p, (lat, lng) = g.geocode("621 W Adams Blvd Los Angeles, CA 90007")
    >>> p
    '621 W Adams Blvd, Los Angeles, CA 90007, USA'
    >>> lat
    '34.0244050'
    >>> lng
    '-118.2791950'
    >>> p, (lat, lng) = g.geocode("Signal Hill, CA")
    >>> p
    'Signal Hill, CA, USA'
    >>> lat
    '33.8044614'
    >>> lng
    '-118.1678456'
    >>> p, (lat, lng) = g.geocode("Portsmouth Square Plaza, San Francisco")
    >>> p
    'Portsmouth Square Plaza, San Francisco, CA 94108, USA'
    >>> lat
    '37.7948051'
    >>> lng
    '-122.4051364'
    '''

    def __init__(self,
                 api_key=GOOGLE_MAP_KEY, domain='maps.google.com',
                 resource='maps/api/geocode', format_string='%s', output_format='json'):
        ''' This interface mimics the geopy one. format_string will not be used
        '''
        self.api_key = api_key
        self.domain = domain
        self.resource = resource
        self.format_string = format_string
        self.output_format = output_format
        #        self.last_request_time = None
        #        self.sleep_duration = 3 # sleep interval in seconds

    @property
    def url(self):
        domain = self.domain.strip('/')
        resource = self.resource.strip('/')
        output_format = self.output_format.strip()
        return "http://%(domain)s/%(resource)s/%(output_format)s?sensor=false&%%s" % locals()


    def _get_data(self, string):
        params = {'address': self.format_string % string,
                  }
        if self.resource.rstrip('/').endswith('geo'):
            # An API key is only required for the HTTP geocoder.
            params['key'] = self.api_key

        url = self.url % urlencode(params)
        page = urlopen(url)
        return page.read()

    def geocode(self, string, exactly_one=True):
        '''Again mimic the geopy interface
        Returns a place string and lat, lng tuple.'''
        json = self._get_data(string)
        resp_dict = simplejson.loads(json)
        attempts = 1
        while (resp_dict['status'] == 'OVER_QUERY_LIMIT' and attempts < 5):
            time.sleep(5)
            json = self._get_data(string)
            resp_dict = simplejson.loads(json)
            attempts += 1
        if resp_dict['status'] != 'OK':
            raise GeoCodeException(''.join(('Status from Google GeoCoder is ', resp_dict['status'])))
        result = resp_dict['results'][0] #take first result
        return (result['formatted_address'], (result['geometry']['location']['lat'], result['geometry']['location']['lng']))

if __name__=="__main__":
    print "SELF TEST?"
    import doctest
    doctest.testmod()
