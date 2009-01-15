from django.test import TestCase
from django.conf import settings
from django.utils.safestring import SafeData
from django.template import Template, Context

from models import Frame
from quick import draw

class DecoTestCase(TestCase):
    def failUnlessStringContains(self, string, fragment):
        self.failUnless(string.find(fragment) > -1)
    
    def failIfStringContains(self, string, fragment):
        self.failUnless(string.find(fragment) < 0)
    
    def getPage(self, url, expected_status=200):
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, expected_status)
        return response

try:
    # if the test suite is run from the deco.testprj project, load some extra tests
    if settings.DECO_TESTPRJ:
        from deco.testprj.tests import ProjectTest
except:
    # nope; run only the tests in this file.
    pass

class RenderTest(DecoTestCase):
    def test_frame(self):
        # test rendering of text frames
        f1 = Frame.objects.create(title='Text Page', format='text', content="page <i>content</i>")
        r1 = f1.draw()
        self.failUnlessStringContains(r1, "page &lt;i&gt;content&lt;/i&gt;")
        self.failUnless(isinstance(r1, SafeData))
        
        # test rendering of html frames
        f2 = Frame(format='html', content="page <i>content</i>")
        r2 = f2.draw()
        self.failUnlessStringContains(r2, "page <i>content</i>")
        self.failUnless(isinstance(r2, SafeData))
        
        # test rendering of template frames
        f3 = Frame(format='template', content="page {% if 1 %}<i>content</i>{% else %}NO{% endif %}")
        r3 = f3.draw()
        self.failUnlessStringContains(r3, "<i>content</i>")
        self.failIfStringContains(r3, "NO")
        self.failUnless(isinstance(r3, SafeData))
        
        # test the standalone "draw" function
        r1_2 = draw("Text Page")
        self.failUnless(r1_2 == r1)
        
        
        # test rendering of non-existent frames
        def make_bad_frame():
            Frame(title="BadFormat Page", content="page <i>content</i>", format='no_such_format').draw()
        self.failUnlessRaises(TypeError, make_bad_frame)
    
    def test_formats(self):
        # test markdown
        f1 = Frame.objects.create(format='markdown', content="*blah*")
        self.failUnless(f1.draw() == '<p><em>blah</em>\n</p>')
        
        # test textile
        f2 = Frame.objects.create(format='textile', content="+blah+")
        self.failUnless(f2.draw() == '<p><ins>blah</ins></p>')
    
    def test_nonexistent_frame(self):
        self.failUnlessStringContains(draw("no_such_view"), '[view with title "no_such_view" does not exist]')
    
    def test_template_context(self):
        # insertion of context variables
        f1 = Frame.objects.create(format='template', content='{% if true %}YES{% else %}NO{% endif %}')
        r1 = f1.draw(context={'true': True})
        self.failIfStringContains(r1, 'NO')
        
        # the 'frame' context variable
        f2 = Frame.objects.create(format='template', content='{% ifequal this_frame the_frame %}YES{% else %}NO{% endifequal %}')
        r2 = f2.draw(context={'the_frame': f2})
        self.failIfStringContains(r2, 'NO')
        
        # insertion of context when using deco.quick.draw()
        f3 = Frame.objects.create(title='the_frame', format='template', content='{{ the_var }}')
        r3 = draw('the_frame', context={'the_var': 'bla!'})
        self.failUnless(r3 == 'bla!')
        
        # getting parent_context data when a frame is drawn from a templatetag
        f4 = Frame.objects.create(format='template', content='{{ the_var }}')
        r4 = Template('{% load deco_tags %}{% frame f d %}').render(Context({'d': {'the_var': 'bla'}, 'f': f4}))
        self.failUnless(r4 == 'bla')
        
        # recurrently drawing a frame
        f5 = Frame.objects.create(format='template', content=
            '{% load deco_tags %}{{ txt }}{% if items %}' +
            '[{% for item in items %}{% frame this_frame item %}{% endfor %}]' +
            '{% endif %}')
        r5 = f5.draw(context={
            'txt': 1, 'items': ({'txt': '2'}, {'items': ({'txt': 3}, {'txt': '4'})}, {'txt':'5'})})
        self.failUnless(r5 == '1[2[34]5]')

class TemplatetagsTest(DecoTestCase):
    def test_frame_tag(self):
        f1 = Frame.objects.create(title='the_frame', format='html', content='<b>my test content!</b>')
        
        # include by reference
        t1 = Template('{% load deco_tags %}{% frame f %}')
        r1 = t1.render(Context({'f': f1}))
        self.failUnless(r1 == '<b>my test content!</b>')
        
        # include by title
        t2 = Template('{% load deco_tags %}{% frame "the_frame" %}')
        r2 = t2.render(Context())
        self.failUnless(r2 == r1)
        
        # include non-existent frame by title
        t3 = Template('{% load deco_tags %}{% frame "no_such_frame" %}')
        r3 = t3.render(Context())
        self.failUnless(r3 == '[deco error: non-existent frame "no_such_frame"]')
    
    def test_frame_link_tag(self):
        f1 = Frame.objects.create(title='the_frame', format='html', content='<b>my test content!</b>', url='/the_url')
        
        # plain link, default text, pass by reference
        t1 = Template('{% load deco_tags %}{% frame_link f %}')
        r1 = t1.render(Context({'f': f1}))
        self.failUnless(r1 == '<a href="/the_url">the_frame</a>')
        
        # plain link, default text, pass by title
        t2 = Template('{% load deco_tags %}{% frame_link "the_frame" %}')
        r2 = t2.render(Context())
        self.failUnless(r2 == '<a href="/the_url">the_frame</a>')
        
        # plain link, pass by title - non-existent frame
        t3 = Template('{% load deco_tags %}{% frame_link "no_such_frame" %}')
        r3 = t3.render(Context())
        self.failUnless(r3 == '[deco error: non-existent frame "no_such_frame"]')
        
        # custom text in link
        t4 = Template('{% load deco_tags %}{% frame_link "the_frame" "my_title" %}')
        r4 = t4.render(Context())
        self.failUnless(r4 == '<a href="/the_url">my_title</a>')
