from rest_framework import serializers
from .models import *


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class PostAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostAttachment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    # probably not needed to see comments here
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'comments']


class PostSerializer(serializers.ModelSerializer):
    attachments = PostAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        # model = PostAttachment
        fields = '__all__'
        # with depth>=0 the return json contains creator details, with depth==0 there is only creator's id
        # depth = 1


class PostDetailsSerializer(serializers.ModelSerializer):
    # Allows to find comments by 'related name' from models.py
    # https://stackoverflow.com/questions/46260695/django-rest-framework-get-related-objects
    comments = CommentSerializer(many=True, read_only=True)
    attachments = PostAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        # model = PostAttachment
        fields = '__all__'
        # with depth>=0 the return json contains creator details, with depth==0 there is only creator's id
        # depth = 1
