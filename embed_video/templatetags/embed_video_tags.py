from django.template import Library, Node, NodeList, TemplateSyntaxError
from django.utils.safestring import mark_safe

from ..base import detect_backend

register = Library()

@register.tag('video')
class VideoNode(Node):
    error_msg = ('Syntax error. Expected: ``video source as var``')

    def __init__(self, parser, token):
        bits = token.split_contents()

        if len(bits) < 4 or bits[-2] != 'as':
            raise TemplateSyntaxError(self.error_msg)

        self.url = parser.compile_filter(bits[1])
        self.as_var = bits[-1]

        self.nodelist_file = parser.parse(('endvideo',))
        parser.delete_first_token()

    def render(self, context):
        url = self.url.resolve(context)
        context.push()
        context[self.as_var] = detect_backend(url)
        output = self.nodelist_file.render(context)
        context.pop()
        return output

    def __iter__(self):
        for node in self.nodelist_file:
            yield node

    def __repr__(self):
        return '<VideoNode>'


@register.filter(is_safe=True)
def embed(backend, _size='small'):
    sizes = {
        'tiny': (560, 315),
        'small': (640, 360),
        'medium': (853, 480),
        'large': (1280, 720),
    }

    if _size in sizes:
        size = sizes[_size]
    elif 'x' in _size:
        size = _size.split('x')

    params = {
        'url': backend.url,
        'width': int(size[0]),
        'height': int(size[1]),
    }

    return mark_safe(
        '<iframe width="%(width)d" height="%(height)d" '
        'src="%(url)s" frameborder="0" allowfullscreen>'
        '</iframe>' % params
    )
