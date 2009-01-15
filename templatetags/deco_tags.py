from django import template
from django.utils.safestring import mark_safe

from deco.models import Frame

def frame(frame, context={}):
    """
    Renders a Deco frame
    
    To render a frame by reference::
    
        {% frame a_frame %}
    
    To render a frame by title::
    
        {% frame "the title" %}
    
    You may specify an optional dict parameter::
    
        {% frame "the title" parameter_dict }
    
    """
    if not hasattr(frame, 'draw'):
        try:
            frame = Frame.objects.filter(title=frame)[0]
        except IndexError:
            return mark_safe('[deco error: non-existent frame "%s"]' % str(frame))
    return frame.draw(context=context)
frame.is_safe = True

def frame_link(frame, text=None):
    """
    Insert a link to the given frame, pointing to the frame's URL
    
    Usage::
    
        {% frame_link a_frame %}
    
    You may specify an optional title to the link (the default title is the frame's title)::
    
        {% frame_link "Contact Page" "click here for contact page" %}
    
    """
    if not hasattr(frame, 'draw'):
        try:
            frame = Frame.objects.filter(title=frame)[0]
        except IndexError:
            return mark_safe('[deco error: non-existent frame "%s"]' % str(frame))
    if text is None:
        text = frame.title
    return mark_safe('<a href="%s">%s</a>' % (frame.url, text))
frame_link.is_safe = True

register = template.Library()
register.simple_tag(frame)
register.simple_tag(frame_link)
