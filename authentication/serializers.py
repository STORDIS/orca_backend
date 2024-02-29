from django.contrib.auth.models import User, Group
from oauth2_provider.contrib.rest_framework import TokenHasScope, TokenHasReadWriteScope
from rest_framework import serializers, generics, permissions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', "first_name", "last_name")


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name')
