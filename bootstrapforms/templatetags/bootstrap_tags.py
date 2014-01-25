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

    if 'class' in field.field.widget.attrs:
        field.field.widget.attrs['class']+=' form-control'
    else:
        field.field.widget.attrs['class']='form-control'
    
    return field.__str__()

@register.filter
def cleanspace(value):#this is for a wierd django bug that textarea are always with a white space inside....
    return value.replace('> <','><')