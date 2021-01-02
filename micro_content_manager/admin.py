from django.contrib import admin

from .models import MicroLearningContent, Tag, Question, Choice, Unit

admin.site.register(MicroLearningContent)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Unit)
