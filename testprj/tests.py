# from django.test import TestCase

from deco.tests import DecoTestCase

from deco.models import Frame
from deco.quick import draw

class ProjectTest(DecoTestCase):
    """
    These tests can only be run with a specially configured project, beacuse they
    need some templates to exist, and some urls to be configured; therefore they
    have been moved from "deco.tests" to "deco.testprj.tests".
    """
    def test_decorator(self):
        # basic decorator rendering
        f1 = Frame(format='html', content='[frame content]', title='frame title', url='/frame_url')
        r1 = f1.draw(decorator='decorator.html')
        self.failUnless(r1 == '[decorator begin [frame title][/frame_url]] [frame content] [decorator end]')
        
        # standalone "draw" function with decorator
        f2 = Frame.objects.create(title='Text Page', format='text', content="page <i>content</i>")
        r2 = draw("Text Page", decorator='decorator.html')
        self.failUnless(r2 == f2.draw(decorator='decorator.html'))
    
    def test_quick_view(self):
        # a simple quick.view
        f1 = Frame.objects.create(url='/quick_page_url', title='page_title', format='html', content='some content')
        self.failUnless(draw('page_title') == self.getPage('/quick_page_url').content)
        
        # a decorated quick.view
        f1.url = '/decorated_quick_page_url'
        f1.save()
        self.failUnless(draw('page_title', decorator='decorator.html') ==
            self.getPage('/decorated_quick_page_url').content)
        
        # a quick.view with a template context
        f2 = Frame.objects.create(url='/context_quick_page', title='page_title', format='template', content='{{ myvar }}')
        self.failUnless('blah' == self.getPage('/context_quick_page').content)
        
        # request for a url that doesn't match any page
        self.failUnless(self.getPage('/no_such_page', expected_status=404).content == "FILE NOT FOUND")
