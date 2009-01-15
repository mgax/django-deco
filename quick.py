from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404

from models import Frame

def view(request, url, decorator=None, context={}):
    """
    Basic view that serves a deco frame: you pass in the
    URL and an optional decorator and context; if the frame
    exists, it's rendered and returned; otherwise, the standard
    404 page is displayed.
    """
    try:
        return HttpResponse(Frame.objects.filter(url='/'+url)[0].draw(decorator=decorator, context=context))
    except IndexError:
        raise Http404()

def draw(title, decorator=None, context={}):
    """
    Retrieves a frame by title and attempts to render it and
    return it as a string.
    """
    try:
        return Frame.objects.get(title=title).draw(context=context, decorator=decorator)
    except ObjectDoesNotExist:
        return mark_safe('[view with title "%s" does not exist]' % str(title))
