from django.contrib.auth.models import User
from micro_content_manager.models import Unit, MicroLearningContent
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name']


class MicroContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MicroLearningContent
        fields = ['id', 'title']
