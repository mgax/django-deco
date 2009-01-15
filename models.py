from django.utils.html import escape, linebreaks
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_str, force_unicode
from django.template import Template, Context
from django.template.loader import render_to_string
from django.conf import settings
from django.db import models

# list of formats in which frames can be written
plainContentFormatList = {
    'text': 'Plain Text',
    'markdown': 'Markdown',
    'textile': 'Textile',
    'html': 'HTML',
    'template': 'Django template',
}

class Frame(models.Model):
    """
    A Frame is the basic unit of content for the Deco framework.
    
    You can configure the frame to be served as a standalone web
    page, or you can embed it in a Django template, or just render
    it as a string.
    
    Frame content may be entered in a variety of formats - Plain
    text, HTML, Markdown, Textile; you can even ask Deco to parse
    the frame's content as a Django template.
    
    If a frame is configured to render as a template, you can pass
    a "context" dictionary to the "draw" method. Among other things,
    this allows you to recursively embed a frame within a frame, to
    construct a tree/menu.
    """
    title = models.CharField(max_length=1000, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    
    url = models.CharField('URL', max_length=1000, blank=True)
    
    format = models.TextField(choices=plainContentFormatList.items(), default='text')
    content = models.TextField(blank=True)
    
    """
    Renders the Frame and returns the result as a "safe" string. Django
    will not attempt to escape the string when embedding it in a template.
    
    "decorator" is an optional parameter - it should be the name of a template
    which will be rendered after the frame is rendered. The decorator template
    receives one context variable named "deco" - it's a dict with 3 items:
    content (the rendered frame), "title" (the frame's title) and "url" (the
    frame's URL, if it has one). The decorator template is rendered and
    returned instead of the frame.
    """
    def draw(self, decorator=None, context={}):
        if decorator:
            return render_to_string(decorator, {
                'deco': {
                    'content': self.draw(),
                    'title': self.title,
                    'url': self.url,
                },
            })
        
        if self.format == 'text':
            return mark_safe(linebreaks(escape(self.content)))
        
        if self.format == 'markdown':
            try:
                import markdown
            except ImportError:
                raise TypeError, "Deco error: The Python markdown library isn't installed."
            return mark_safe(force_unicode(markdown.markdown(smart_str(self.content))))
        
        if self.format == 'textile':
            try:
                import textile
            except ImportError:
                raise TypeError, "Deco error: The Python textile library isn't installed."
            return mark_safe(force_unicode(textile.textile(smart_str(self.content), encoding='utf-8', output='utf-8')))
        
        if self.format == 'html':
            return mark_safe(self.content)
        
        if self.format == 'template':
            render_context = Context({'this_frame': self})
            render_context.update(context)
            return Template(self.content).render(render_context)
        
        raise TypeError("frame format is invalid: \"" + self.format + "\"")
    
    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return "[no title; id=%d]" % int(self.id)
    
    def __str__(self):
        return self.__unicode__()
    
    class Admin:
        list_display = ('title', 'url')
