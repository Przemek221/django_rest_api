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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    attachments = PostAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        # model = PostAttachment
        fields = '__all__'
        # with depth>=0 the return json contains creator details, with depth==0 there is only creator's id
        # depth = 1


class UserDetailsSerializer(serializers.ModelSerializer):
    # probably not needed to see comments here
    comments = CommentSerializer(many=True, read_only=True)
    userprofile = UserProfileSerializer(many=False, read_only=True)
    # mozliwe ze to aktualnie zakomentowane bedzie lepsze do tego
    user_posts = PostSerializer(many=True, read_only=True)

    # user_posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'comments', 'user_posts', 'userprofile']


class UserSerializer(serializers.ModelSerializer):
    # probably not needed to see comments here
    userprofile = UserProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'userprofile']


class PostDetailsSerializer(serializers.ModelSerializer):
    # Allows to find comments by 'related name' from models.py
    # https://stackoverflow.com/questions/46260695/django-rest-framework-get-related-objects
    comments = CommentSerializer(many=True, read_only=True)
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    creator = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Post
        # model = PostAttachment
        fields = '__all__'
        # with depth>=0 the return json contains creator details, with depth==0 there is only creator's id
        # depth = 1
