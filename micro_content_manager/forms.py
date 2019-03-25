from django import forms
from django.forms import ModelForm

from micro_content_manager.models import MicroLearningContent


class MicroContentEditForm(ModelForm):
    class Meta:
        model = MicroLearningContent
        fields = ['title',]


