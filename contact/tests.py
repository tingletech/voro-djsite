from django.test import TestCase
from django.db import IntegrityError
from django.test.client import Client
from django.utils.http import urlquote
#import xml.etree.ElementTree as ET
from BeautifulSoup import BeautifulSoup

from contact.models import *
from contact.views import ContactForm

#class ContactFormTestCase(TestCase):
#    
#    def testMinimumValidForm(self):
#        form = ContactForm()
#        print form.data
#        form.data = { 'message':"min msg", "user_agent":"Bogus User agent", }
#        print form.data
#        form.full_clean()
#        print dir(form)
#        #print form.cleaned_data
#        self.failUnless(form.is_valid())

class ContactUsMessageViewTestCase(TestCase):
    fixtures = ['contact.json', ]
    def setUp(self):
        pass

    def testContactView(self):
        response = self.client.post('/contact/')
        self.failUnless(response.status_code==200, 'Bad Status Code = %d' % response.status_code)
        self.assertTemplateUsed(response, 'contactus.html')
        self.failUnless(response.template.name=='contactus.html',
                        "Unknown template : %s" % response.template.name)
        self.failUnless(isinstance(response.context['form'], ContactForm))
        #        print "REQUEST: %s\n" % response.request
        #        print "CONTEXT: %s\n" % response.context
        #        print "CLIENT: %s\n" % response.client

    def testReferQuoteProblem(self):
        '''Need to have a test that fails if the problem with urlquoting
        the HTTP_REFERER field shows again.
        A bit tricky, need to go to page with a get and grab the url_refer
        tag to use as the url_refer to feed to an otherwise valid POST
        '''
        def replace_check_for_spam(r):
            return False, {}
        import contact.views
        contact.views.check_for_spam = replace_check_for_spam
        response = self.client.get('/contact/',
                                    HTTP_REFERER='http://oac.cdlib.org/')
        self.assertContains(response, 'url_refer')
        #grab value of url_refer with Soup?
        soup = BeautifulSoup(response.content)
        url_refer = soup.find('input',id="id_url_refer")
        url = url_refer['value']

        #make valid data except url
        post_data = {}
        post_data['user_agent'] = 'Test Client user-agent'
        post_data['message'] = 'Test Client Message!--'
        
        # This fails when buggy code in place
        post_data['url_refer'] = url
        response = self.client.post('/contact/', post_data)
        self.assertTemplateUsed(response, 'contactthanks.html')

        #now do it again with no message but an OK url_refer
        del post_data['message']
        post_data['url_refer'] = 'http://oac.cdlib.org/'
        response = self.client.post('/contact/', post_data)
        self.assertTemplateUsed(response, 'contactus.html')
        self.assertContains(response, 'url_refer')
        soup = BeautifulSoup(response.content)
        url_refer = soup.find('input',id="id_url_refer")
        url = url_refer['value']

        # This fails when buggy code in place
        post_data['message'] = 'Test Client Message!--2'
        post_data['url_refer'] = url
        response = self.client.post('/contact/', post_data)
        self.assertTemplateUsed(response, 'contactthanks.html')
        
        # this should fail on old code
        post_data['message'] = 'Test Client Message!--Broke before url_refer'
        post_data['url_refer'] = 'http://oac.cdlib.org/search?query=coolidge cabinet;institution=UC Berkeley::Bancroft Library'
        response = self.client.post('/contact/', post_data)
        self.assertTemplateUsed(response, 'contactthanks.html')

    def testWithReferURL(self):
        post_data = {}
        post_data['user_agent'] = 'Test Client user-agent'
        #NOTE: THIS REPLACES THE RECAPTCHA CALLING
        #TODO: CAN THIS BE DONE IN SETUP?
        def replace_check_for_spam(r):
            return False, {}
        import contact.views
        contact.views.check_for_spam = replace_check_for_spam

        # not yet valid, needs message
        response = self.client.post('/contact/', post_data,
                                    HTTP_REFERER='http://oac.cdlib.org/')
        #self.assertTemplateUsed(response, 'contactthanks.html')
        #self.assertContains(response, 'Thank')

        post_data['message'] = 'Test Client Message!'
        response = self.client.post('/contact/', post_data,
                                    HTTP_REFERER='http://oac.cdlib.org/')
        self.assertTemplateUsed(response, 'contactthanks.html')
        self.assertContains(response, 'Thank')
        #check the entry, how???
        entries = ContactUsMessage.objects.all().order_by('created_at')

        post_data['url_refer'] = 'http://voro-s10stg.cdlib.org/'
        response = self.client.post('/contact/', post_data)
        self.assertTemplateUsed(response, 'contactthanks.html')
        #check the entry, how???
        entries = ContactUsMessage.objects.all().order_by('created_at')

        post_data['url_refer'] = urlquote('http://voro-s10stg.cdlib.org/')
        response = self.client.post('/contact/', post_data)
        self.assertTemplateUsed(response, 'contactus.html')

        #for e in entries:
            #    print e.id, e.message, e.url_refer

    def testContactUsFormSubmission(self):
        """Submit a form with various combinations of data
        """
        post_data = {}
        response = self.client.post('/contact/', post_data)
        #response should contain 'This field is required' near textarea
        errors = response.context['form'].errors
        expected_error = { 'message': [u'This field is required.'], 'user_agent': [u'This field is required.']}
        self.failUnlessEqual(errors, expected_error)

        post_data = {'message' : 'A message only'}
        response = self.client.post('/contact/', post_data)
        errors = response.context['form'].errors
        expected_error = { 'user_agent': [u'This field is required.']}
        self.failUnlessEqual(errors, expected_error)

        post_data['user_agent'] = 'Test Client user-agent'
        response = self.client.post('/contact/', post_data)
        errors = response.context['form'].errors
        expected_error = { }
        self.failUnlessEqual(errors, expected_error)

        #need to figure out recaptcha stub?
        if not 'recaptcha' in response.context['form'].spam_errors:
            self.fail('recaptcha not in error_dict. Expecting it.')
        
        post_data['message'] = 'Test Client Message!'
        response = self.client.post('/contact/', post_data)
        
        #NOTE: THIS REPLACES THE RECAPTCHA CALLING
        #TODO: CAN THIS BE DONE IN SETUP?
        def replace_check_for_spam(r):
            return False, {}
        import contact.views
        #import sys
        #sys.modules['contact.views'].check_for_spam = replace_check_for_spam
        contact.views.check_for_spam = replace_check_for_spam


        #should now succeed
        response = self.client.post('/contact/', post_data)
        # by replacing the check spam, should pass & be template is
        # contactthanks.html
        self.assertTemplateUsed(response, 'contactthanks.html')

        post_data['HTTP_REFERER'] = 'http://oac.cdlib.org/'
        response = self.client.post('/contact/', post_data)
        self.assertTemplateUsed(response, 'contactthanks.html')

        post_data['url_refer'] = 'http://voro-s10stg.cdli.org/'
        response = self.client.post('/contact/', post_data)
        self.assertTemplateUsed(response, 'contactthanks.html')


#        print "STATUS CODE: %d\n" % response.status_code
#        print "TEMPLATE NAME: %s\n" % response.template.name
#        print "REQUEST: %s\n" % response.request
#        print "CONTEXT: %s\n" % response.context
#        #print response.content
#        # no form if submission valid. print "FORM TYPE:%s" % type(response.context['form'])
#        #        print "\n\n\n%s" % response.content

class ContactUsMessageTestCase(TestCase):
    fixtures = ['contact.json', ]

    def setUp(self):
        msgs = []
        self.msgs = msgs


    def testSchema(self):
        pass
