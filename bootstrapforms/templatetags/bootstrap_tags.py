from django import template
from django.template import Context
from django.template.loader import get_template



register = template.Library()





@register.filter
def as_bootstrap(form):
    template = get_template("bootstrap/form.html")
    c = Context({"form": form})
    return template.render(c)

@register.filter
def as_bootstrap_h(form):
    template = get_template("bootstrap/form.html")
    c = Context({"form": form,'col1':'col-sm-2','col2':'col-sm-10'})
    return template.render(c)

@register.filter
def css_class(field):
	return field.field.widget.__class__.__name__.lower()

@register.filter
def formcontrol(field):
	x = field.__str__().split()
	x.insert(1,'class="form-control"')
	return " ".join(x)