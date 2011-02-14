# set coding=utf-8
from django.test import TestCase
from django.test.client import Client
#from django.auth import User
from django.db import IntegrityError
from django.core.exceptions import MultipleObjectsReturned

from oac.models import *

import geocoders_dsc as geocoders

class GeocoderTestCase(TestCase):
    def testNoAddress(self):
        address = "1000 Bogus St., BogusXXX, CA"
        g = geocoders.Google('ABQIAAAAPZhPbFDgyqqKaAJtfPgdhRQxAnOebRR8qqjlEjE1Y4ZOeQ67yxSVDP1Eq9oU2BZjw2PaheQ5prTXaw')
        place, (lat, lng) = g.geocode(address)
        self.failUnlessEqual(place, "California, USA")

    def testGoodAddress(self):
        address = "415 20th St., Oakland, CA"
        g = geocoders.Google('ABQIAAAAPZhPbFDgyqqKaAJtfPgdhRQxAnOebRR8qqjlEjE1Y4ZOeQ67yxSVDP1Eq9oU2BZjw2PaheQ5prTXaw')
        place, (lat, lng) = g.geocode(address)
        self.failUnlessEqual(place, "415 20th St, Oakland, CA 94612, USA")
        self.failUnlessAlmostEqual(float(lat), 37.808, 2)
        self.failUnlessAlmostEqual(float(lng), -122.267359, 2)

class ReadOnlyAdminTestCase(TestCase):
    """Yikes, this is going to be interesting to test
    """
    pass

class InstitutionViewsTestCase(TestCase):
    """Test the AJAX views of institution data.
    """
    fixtures = ['oac.institution.json', 'oac.institutionoldname.json', 'oac.city.json', 'oac.county.json' ]
    def setUp(self):
        """Might want to use a fixture??
        """
        City(name='Test City', county_id=1).save()
        County(name='Test County').save()
        i = Institution(ark='ark:/13030/testark',name='Test Institution',
                        city_id=1, county_id=1, latitude='37.808748',
                        longitude='-122.267359', address1='415 20th St',
                        address2='4th floor', zip4='94612')
        i.save()
        self.insts = [i]
        i = Institution(ark='ark:/13030/testark2',name='Test Institution 2',
                        city_id=1, county_id=1, latitude='37.808748',
                        longitude='-122.267359')
        i.save()
        self.insts.append(i)
        self.failUnlessEqual(264, len(Institution.objects.all()))

    def testInsitutionAddressInfoView(self):
        inst = self.insts[0]
        response = self.client.get('/djsite/institution/address_info/div/%s' % inst.name)
        self.assertContains(response, inst.address1)

    def testInstitutionAddressInfoOldNameView(self):
        duplicate_name = 'San Francisco History Center'
        try:
            response = self.client.get('/djsite/institution/address_info/div/%s' % duplicate_name)
        except MultipleObjectsReturned, e:
            print dir(e)
            self.fail('OldName lookup failed: %s' % (e.message,))

class InstitutionDataTestCase(TestCase):
    fixtures = ['oac.institution.json', 'auth.json' ]

    def testMissingParentArk(self):
        insts = Institution.objects.all()
        for inst in insts:
            if inst.parent_institution and not inst.parent_ark:
                self.fail('Missing parent ARK:%s Parent:%s' % (inst.name, inst.parent_institution.name,))

class InstitutionModelTestCase(TestCase):
    fixtures = ['oac.institution.json', 'auth.json' ]

#    def testLatin1Name(self):
#        '''want to get the inclusion of latin-1 chars (xe9,  e acute) 
#        to output in file like obj.
#        First duplicate the error
#        '''
#        import urllib
#        inst = Institution.objects.get(pk=95)
#        try:
#            x = urllib.quote_plus(inst.name_doublelist)
#        except KeyError:
#            self.fail('latin-1 encoding error')

    def testFixtureData(self):
        insts = Institution.objects.all()
        self.assertTrue(len(insts) > 235)
        inst = Institution.objects.get(id=1)
        self.failUnlessEqual(inst.ark, 'ark:/13030/tf6p3013t7')
        self.failUnlessEqual(inst.name, 'UC Davis')
        users = User.objects.all()
        self.failUnless(len(users) == 2)

    
    def testAddInst(self):
        i = Institution()
        # trying to save this should fail, min is ark & name?
        # the ark validation code in Institution raises firs exception
        self.failUnlessRaises(ValueError, i.save)
        i.ark = 'ark:/13030/bogus!Ark123'
        self.failUnlessRaises(ValueError, i.save)
        i.ark = 'ark:/13030/testArk123'
        self.failUnlessRaises(IntegrityError, i.save)
        i.city_id = 2
        self.failUnlessRaises(IntegrityError, i.save)
        i.county_id = 2
        self.failUnlessRaises(IntegrityError, i.save)
        i.cdlpath = 'boguspath'
        self.failUnlessRaises(IntegrityError, i.save)
        i.address1 = 'a test address'
        self.failUnlessRaises(IntegrityError, i.save)
        i.zip4 = '94702-2614'
        self.failUnlessRaises(IntegrityError, i.save)
        i.url = 'http://oac.cdlib.org'
        self.failUnlessRaises(IntegrityError, i.save)
        i.latitude = 37.85
        self.failUnlessRaises(IntegrityError, i.save)
        i.longitude = -122.37
        self.failUnless(i.save, 'save of institution should be ok here')
        # BAD Name
        i.name = 'A BAD & Name'
        self.failUnlessRaises(ValueError, i.save)
        i.name = 'San José State University'
        self.failUnless(i.save, 'save of institution should be ok here')


    def testAddInstPage(self):
        response = self.client.get('/admin/OAC_admin/')
        self.assertContains(response, 'Contributor Dashboard')
        self.client.login(username='oactestuser', password='oactestuser')
        from django.contrib.auth.models import User
        user = User.objects.get(username='oactestuser')
        self.failIfEqual(user, None)
        from django.test.client import Client
        c = Client()
        c.login(username='oactestuser', password='oactestuser')
        response = c.get('/admin/OAC_admin/')
        '''
        print response.content
        self.assertContains(response, 'Institutions')

        response = self.client.get('/admin/OAC_admin/')
        #print response.content
        self.assertContains(response, 'Institutions')
        response = self.client.get('/admin/OAC_admin/oac/institution/add/')
        self.assertContains(response, 'Add Institution')
        '''

class DashboardTestCase(TestCase):
    '''Test the user dashboard view'''
    fixtures = ['oac.institution.json', 'auth.json', 'oac.groupprofile.json',]

    def testDashboardAtRoot(self):
        response = self.client.get('/admin/')
        self.assertContains(response, 'Contributor Dashboard')
        logged_in = self.client.login(username='oactestuser', password='oactestuser')
        response = self.client.get('/admin/')
        self.assertTemplateUsed(response, 'admin/user_dashboard.html')
        self.assertContains(response, 'Contributor Dashboard')
        self.assertContains(response, 'My Account')
        self.assertContains(response, 'oactestuser')
        oactest_insts = get_institutions_for_user(User.objects.get(username='oactestuser'))
        self.assertEqual(str(oactest_insts),
                "[<Institution: California State Library>, <Institution: Bancroft Library, Parent: UC Berkeley>, <Institution: UC Berkeley>, <Institution: University Archives, Parent: UC Berkeley>]"
                                )

    def testArchiveGridHarvest(self):
        '''Test the archivegrid harvest option'''
        logged_in = self.client.login(username='oactestuser', password='oactestuser')
        response = self.client.get('/admin/')
        self.assertTemplateUsed(response, 'admin/user_dashboard.html')
        self.assertContains(response, 'ArchiveGrid')

class InstitutionAdminTestCase(TestCase):
    ''' Test the changes made to the admin pages for institutions.
    Currently, only the generation of search widget code is tested.
    Developing this in a TDD style.
    '''
    fixtures = ['oac.institution.json', 'auth.json', 'oac.groupprofile.json', ]

    def testSearchWidget(self):
        ''' Test that the institution's search widget is available
        '''
        x = self.client.login(username='oactestuser', password='oactestuser')
        response = self.client.get('/admin/oac/institution/34/')
        #print response
        self.assertContains(response, 'Bancroft Library')
        self.assertContains(response, '<form action="http://www.oac.cdlib.org/search">')
        self.assertContains(response, '<input value="UC Berkeley::Bancroft Library" name="institution" type="hidden">')
