from django import template
from django.template import Context
from django.template.loader import get_template



register = template.Library()


@register.filter
def bootstrap(form):
    template = get_template("bootstrap/form.html")
    c = Context({"form": form})
    return template.render(c)


@register.filter
def bootstrap_h(form):
    template = get_template("bootstrap/form.html")
    c = Context({"form": form,'col1':'col-sm-2','col2':'col-sm-10'})
    return template.render(c)
