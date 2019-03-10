from django.contrib import admin

from micro_content_manager.models import MicroLearningContent

admin.site.unregister(MicroLearningContent)
admin.site.register(MicroLearningContent)