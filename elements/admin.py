from django.contrib import admin

# Register your models here.
from elements.models import List, Element

admin.site.register(List)
admin.site.register(Element)