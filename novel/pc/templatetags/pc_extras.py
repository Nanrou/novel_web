from django import template

register = template.Library()


@register.filter
def insert_two_indentation(value):
    _indentation = '\u3000\u3000'
    return _indentation + value.replace('<br/>', '<br/>' + _indentation)

