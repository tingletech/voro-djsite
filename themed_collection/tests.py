import sys
import time
from django.test import TestCase
from django.test.client import Client
from liveTestCase import TestCaseLiveServer
from selenium import selenium

from themed_collection.models import ThemedCollection
from xtf.models import ARKSet

#__test__ = {"doctest": """
#Another way to test that 1 + 1 is equal to 2.
#
#>>> 1 + 1 == 2
#True
#"""}

class ThemedCollectionViewTestCase(TestCase):
    '''Test the view of ThemedCollections
    '''
    fixtures = ['themed_collection.json', 'xtf.json']
    def testEverydayLifeView(self):
        t = ThemedCollection.objects.get(id=5)
        c = Client()
        response = c.get(t.get_absolute_url())
        self.failUnlessEqual(200, response.status_code)

    def testEverydayLifeViewJSON(self):
        t = ThemedCollection.objects.get(id=5)
        c = Client()
        response = c.get(t.get_absolute_url()+'/json/')
        self.failUnlessEqual(200, response.status_code)

def test_map_marker_infowin_WithTestCaseInstance(testcase, selenium_obj):
    sel = selenium_obj
    #sel.set_timeout("300000")
    sel.open('djsite/themed_collection/themed_collection/disasters')
    #sel.wait_for_page_to_load("300000")
    #sel.open("/djsite/themed_collection/themed_collection/3/")
    testcase.assertEqual("Disasters", sel.get_title())
    sel.is_text_present('arkobject')
    sel.is_text_present('var arkobjects = {"ark:/13030/hb8j49p2v4')
    sel.is_text_present('thumbnail')
    sel.set_speed(1000)
    time.sleep(30) #give time for map load
    sel.click("showMap")
    time.sleep(10)
    print "MAP LOADED", sel.get_eval('window.map.isLoaded()')
    print "MAP CENTER", sel.get_eval('window.map.getCenter()')
    for i in range(10):
        try:
            if sel.is_visible("//div[@id='map_canvas']"): break
        except: pass
        time.sleep(1)
    else: testcase.fail("time out")
#        for i in range(10):
#            try:
#                if sel.is_element_present("//img[@src=contains('thumbnail')]"): break
#            except: pass
#            time.sleep(1)
#        else: testcase.fail("time out -- can't find expected thumbnail")
#        for i in range(60):
#            try:
#                if sel.is_element_present("//img[@src='http://content.cdlib.org/ark:/13030/tf9d5nb5bs/thumbnail']"): break
#            except: pass
#            time.sleep(1)
#        else: testcase.fail("time out -- can't find expected thumbnail")
    sel.click("//area[@id='mtgt_unnamed_88']")
    #sel.click("link=Old Russian Church, Fort Ross - after")
    sel.click("link=exact:Go to image page")
    sel.click("link=Close")
    sel.click("//img[@onclick=\"mapns.openContentPanel('ark:/13030/hb3j49p0kg','http://content.cdlib.org/ark:/13030/hb3j49p0kg/FID3');return false;\"]")
    sel.click("link=Close")
    sel.click("//img[contains(@src,'http://maps.gstatic.com/intl/en_us/mapfiles/iw_close.gif')]")
    sel.click("//div[@id='mapPanel']/a")

#class SafariLiveTest(TestCaseLiveServer):
#    fixtures = ['auth.json',]
#
#    def setUp(self):
#        # Start a test server and tell selenium where to find it.
#        self.start_test_server('dsc-voro-dev.cdlib.org', 8080)
#        self.selenium = selenium('cdl-mredar-1.ad.ucop.edu', 4444, \
#                                 '*safari', 'http://dsc-voro-dev.cdlib.org:8080')
#        #self.selenium.set_speed(1000)
#        self.selenium.start()
#
#    def tearDown(self):
#        # Stop server and Selenium
#        self.selenium.stop()
#        self.stop_test_server()
#        
#    def testLogin(self):
#        testLoginWithTestCaseInstance(self, self.selenium)
#
#    def test_map_marker_infowin(self):
#        test_map_marker_infowin_WithTestCaseInstance(self, self.selenium)

class FirefoxLiveTest(TestCaseLiveServer):
    fixtures = ['auth.json',]

    def setUp(self):
        # Start a test server and tell selenium where to find it.
        self.start_test_server('dsc-voro-dev.cdlib.org', 8080)
        self.selenium = selenium('cdl-mredar-1.ad.ucop.edu', 4444, \
            '*firefox', 'http://dsc-voro-dev.cdlib.org:8080')
        #self.selenium.set_speed(1000)
        #time.sleep(10000) # for debug
        self.selenium.start()

    def tearDown(self):
        # Stop server and Selenium
        self.selenium.stop()
        self.stop_test_server()

    def test_map_marker_infowin(self):
        self.selenium.set_speed(1000)
        test_map_marker_infowin_WithTestCaseInstance(self, self.selenium)

#class GoogleChromeLiveTest(TestCaseLiveServer):
#    fixtures = ['auth.json',]
#
#    def setUp(self):
#        # Start a test server and tell selenium where to find it.
#        self.start_test_server('dsc-voro-dev.cdlib.org', 8080)
#        #self.selenium = selenium('localhost', 4444, \
#                #    '*googlechrome', 'http://localhost:8000')
#        self.selenium = selenium('cdl-mredar-1.ad.ucop.edu', 4444, \
#                                 '*custom "/Applications/Google-Chrome.app/Contents/MacOS/Google-Chrome"', 'http://dsc-voro-dev.cdlib.org:8080')
#                                 #'*custom "/Applications/Google-Chrome.app"', 'http://dsc-voro-dev.cdlib.org:8080')
#                                 #'*custom "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"', 'http://localhost:8000')
#        #                '*googlechrome/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'http://localhost:8000')
#        #self.selenium.set_speed(1000)
#        self.selenium.start()
#
#    def tearDown(self):
#        # Stop server and Selenium
#        self.selenium.stop()
#        self.stop_test_server()
#        
#    def testLogin(self):
#        testLoginWithTestCaseInstance(self, self.selenium)
#
#    def test_map_marker_infowin(self):
#        test_map_marker_infowin_WithTestCaseInstance(self, self.selenium)
#
