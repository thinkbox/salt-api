# coding: utf-8
import cgi
import json
import urllib

import cherrypy
import yaml

from tests.utils import BaseRestCherryPyTest

class TestAuth(BaseRestCherryPyTest):
    def test_get_root_noauth(self):
        '''
        GET requests to the root URL should not require auth
        '''
        request, response = self.request('/')
        self.assertEqual(response.status, '200 OK')

    def test_post_root_auth(self):
        '''
        POST requests to the root URL redirect to login
        '''
        self.assertRaisesRegexp(cherrypy.InternalRedirect, '\/login',
                self.request, '/', method='POST', data={})

    def test_login_noauth(self):
        '''
        GET requests to the login URL should not require auth
        '''
        request, response = self.request('/login')
        self.assertEqual(response.status, '200 OK')

    def test_webhook_auth(self):
        '''
        Requests to the webhook URL require auth by default
        '''
        self.assertRaisesRegexp(cherrypy.InternalRedirect, '\/login',
                self.request, '/hook', method='POST', data={})

class TestLogin(BaseRestCherryPyTest):
    auth_creds = (
            ('username', 'saltdev'),
            ('password', 'saltdev'),
            ('eauth', 'auto'))

    def test_good_login(self):
        '''
        Test logging in
        '''
        # Mock mk_token for a positive return
        self.Resolver.return_value.mk_token.return_value = {
            'token': '6d1b722e',
            'start': 1363805943.776223,
            'expire': 1363849143.776224,
            'name': 'saltdev',
            'eauth': 'auto',
        }

        body = urllib.urlencode(self.auth_creds)
        request, response = self.request('/login', method='POST', body=body,
            headers={
                'content-type': 'application/x-www-form-urlencoded'
        })
        self.assertEqual(response.status, '200 OK')

    def test_bad_login(self):
        '''
        Test logging in
        '''
        # Mock mk_token for a negative return
        self.Resolver.return_value.mk_token.return_value = {}

        body = urllib.urlencode({'totally': 'invalid_creds'})
        request, response = self.request('/login', method='POST', body=body,
            headers={
                'content-type': 'application/x-www-form-urlencoded'
        })
        self.assertEqual(response.status, '401 Unauthorized')

class TestWebhookDisableAuth(BaseRestCherryPyTest):
    __opts__ = {
        'rest_cherrypy': {
            'port': 8000,
            'debug': True,
            'webhook_disable_auth': True,
        },
    }

    def test_webhook_noauth(self):
        '''
        Auth can be disabled for requests to the webhook URL
        '''
        body = urllib.urlencode({'foo': 'Foo!'})
        request, response = self.request('/hook', method='POST', body=body,
            headers={
                'content-type': 'application/x-www-form-urlencoded'
        })
        self.assertEqual(response.status, '200 OK')
