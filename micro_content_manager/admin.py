from django.contrib import admin
from .models import MicroLearningContent, Tag, Question, Choice

admin.site.register(MicroLearningContent)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Choice)