from StringIO import StringIO
import csv
# set coding=utf-8
from django.test import TestCase
from django.test.client import Client
#from django.contrib.auth.models import User
from django.db import IntegrityError

from xtf.models import ARKObject, ARKSet, ARKSetMember
from xtf.models import DublinCoreTerm


class ARKObjectTestCase(TestCase):
    """Test basic ARKObject function
    """
    fixtures = ['auth.json', 'xtf.json']

    def testDuplicateARK(self):
        a = ARKObject(ark='ark:/13030/kt9r29q5fs')
        self.failUnlessRaises(IntegrityError, a.save)

    def testGetOrCreateARKObject(self):
        arkobj, created = ARKObject.get_or_create(ark='ark:/13030/kt9r29q5fs')
        self.failUnlessEqual(created, False)

    def testThumbnail(self):
        '''Should use a mock for the xtf call'''
        a = ARKObject(ark='ark:/13030/kt9r29q5fs')
        a = ARKObject(ark='ark:/13030/kt096nd5tt')
        #self.failUnlessEqual(a.thumbnail['src'], 'http://content.cdlib.org/ark:/13030/kt096nd5tt/thumbnail')
        self.failUnlessEqual(a.thumbnail['width'], 158)
        self.failUnlessEqual(a.thumbnail['height'], 100)

class ARKSetInputCSVTestCase(TestCase):
    '''Test the input csv view. Need to set up local csv proxy objects
    to test the view properly
    '''
    fixtures = ['auth.json', 'xtf.json', 'sites.json']

    def testCorrectView(self):
        #should be redirected to login
        response = self.client.post('/djsite/xtf/ARKSet/edit/1/input/')
        self.failUnlessEqual(302, response.status_code)
        self.assertRedirects(response, '/accounts/login/?next=/djsite/xtf/ARKSet/edit/1/input/', target_status_code=200)
        response = self.client.post('/djsite/xtf/ARKSet/edit/1/input/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/djsite/xtf/ARKSet/edit/1/input/')
        self.failUnlessEqual(200, response.status_code)
        ret = self.client.login(username='oactestuser',password='oactestuser')
        self.failUnless(ret)
        response = self.client.post('/djsite/xtf/ARKSet/edit/1/input/', follow=True)
        self.failUnlessEqual(200, response.status_code)

    def testMinimalInput(self):
        '''Test with a constructed CSV that has only ARKs and notes.
        '''
        csvfile = StringIO("""\
ark:/13030/tf6t1nb7k2/,Rosie the Riveter
ark:/13030/tf609nb1wk/,Vietnam protest
ark:/13030/tf3h4nb6hn/,Old Klamath River woman.\
""")
        csv_reader = csv.reader(csvfile)
        arkset = ARKSet.objects.get(pk=2)
        numrows, errs, set_members_added, arks_added = arkset._parse_csv(csv_reader)
        self.assertEqual(3, numrows)
        self.assertEqual(0, len(errs))
        self.assertEqual(3, len(set_members_added))
        self.assertEqual(3, len(arks_added))

class ARKObjectViewTestCase(TestCase):
    '''Test views of the arkobjects
    '''
    fixtures = ['xtf.json',]

    def testThumbnail(self):
        '''The ark had a problem with thumbnails as of 2010-11-29
        this test will pass once fixed
        '''
        a = ARKObject.objects.get(ark='ark:/13030/kt3t1nb8s2')
        c = Client()
        response = c.get(a.get_absolute_url())
        self.failUnlessEqual(200, response.status_code)
