from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # these URLs are for tests.py
    (r'^(?P<url>quick.*)$', 'deco.quick.view'),
    (r'^(?P<url>decorated_quick.*)$', 'deco.quick.view', {'decorator': 'decorator.html'}),
    (r'^(?P<url>context_quick.*)$', 'deco.quick.view', {'context': {'myvar': 'blah'}}),
)
