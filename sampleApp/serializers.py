from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    # Allows to find comments by 'related name' from models.py
    # https://stackoverflow.com/questions/46260695/django-rest-framework-get-related-objects
    comments = CommentSerializer(many=True, read_only=True)


    class Meta:
        model = Post
        # model = PostAttachment
        fields = '__all__'
        # with depth>=0 the return json contains creator details, with depth==0 there is only creator's id
        # depth = 1
