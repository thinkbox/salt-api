# coding: utf-8
import cherrypy
import mock

from saltapi.netapi.rest_cherrypy import app

from . cptestcase import BaseCherryPyTestCase

class BaseRestCherryPyTest(BaseCherryPyTestCase):
    '''
    A base TestCase subclass for the rest_cherrypy module

    This mocks all interactions with Salt-core and sets up a dummy
    (unsubscribed) CherryPy web server.
    '''
    __opts__ = None

    @mock.patch('saltapi.APIClient', autospec=True)
    @mock.patch('salt.auth.Resolver', autospec=True)
    @mock.patch('salt.auth.LoadAuth', autospec=True)
    def setUp(self, LoadAuth, Resolver, APIClient):
        app.saltapi.APIClient = APIClient
        app.salt.auth.Resolver = Resolver
        app.salt.auth.LoadAuth = LoadAuth

        # Make local references to mocked objects so individual tests can
        # access and modify the mocked interfaces.
        self.Resolver = Resolver
        self.APIClient = APIClient

        __opts__ = self.__opts__ or {
            'external_auth': {
                'auto': {
                    'saltdev': [
                        '@wheel',
                        '@runner',
                        '.*',
                    ],
                }
            },
            'rest_cherrypy': {
                'port': 8000,
                'debug': True,
            },
        }

        root, apiopts, conf = app.get_app(__opts__)

        cherrypy.tree.mount(root, '/', conf)
        cherrypy.server.unsubscribe()
        cherrypy.engine.start()

    def tearDown(self):
        cherrypy.engine.exit()

class Root(object):
    '''
    The simplest CherryPy app needed to test individual tools
    '''
    exposed = True

    _cp_config = {}

    def GET(self):
        return {'return': ['Hello world.']}

    def POST(self, *args, **kwargs):
        return {'return': [{'args': args}, {'kwargs': kwargs}]}

class BaseToolsTest(BaseCherryPyTestCase):
    '''
    A base class so tests can selectively turn individual tools on for testing
    '''
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        },
    }

    def setUp(self):
        Root._cp_config = self._cp_config
        root = Root()

        cherrypy.tree.mount(root, '/', self.conf)
        cherrypy.server.unsubscribe()
        cherrypy.engine.start()

    def tearDown(self):
        cherrypy.engine.exit()

