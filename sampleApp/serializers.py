from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response

from .models import *


class PostAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostAttachment
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(many=False, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'userprofile']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(username=validated_data['username'], password=validated_data['password'])

class CommentSerializer(serializers.ModelSerializer):
    requestUserIsOwner = serializers.SerializerMethodField(read_only=True)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        read_only_fields = ['creator', 'id', 'createdDate']
        fields = ['creator', 'id', 'createdDate', 'content', 'relatedPost', 'requestUserIsOwner']

    def get_request_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    def get_requestUserIsOwner(self, instance):
        user = self.get_request_user()
        return user == instance.creator
    
class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    creator = UserSerializer(many=False, read_only=True)
    requestUserIsOwner = serializers.SerializerMethodField(read_only=True)
    requestUserLiked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        # model = PostAttachment
        fields = '__all__'
        # with depth>=0 the return json contains creator details, with depth==0 there is only creator's id
        # depth = 1

    def get_request_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    def get_requestUserIsOwner(self, instance):
        user = self.get_request_user()
        return user == instance.creator

    def get_requestUserLiked(self, instance):
        user = self.get_request_user()
        return instance.likes.filter(id=user.pk).exists()


class PostCreateSerializer(serializers.ModelSerializer):
    attachments = serializers.ListField(
        child=serializers.FileField(use_url=False, max_length=100000, allow_empty_file=False), write_only=True,
        required=False)
    attachments_delete_ids = serializers.ListField(
        child=serializers.IntegerField(allow_null=False), required=False, write_only=True)

    class Meta:
        model = Post
        read_only_fields = ['id']
        fields = ['id', 'content', 'attachments', 'attachments_delete_ids']

        # this ensures that the return value will be only post id.
        extra_kwargs = {
            'content': {'write_only': True},
        }

    def validate_attachments_delete_ids(self, attachments_delete_ids):
        for item_id in attachments_delete_ids:
            attachment = get_object_or_404(PostAttachment, id=item_id)
            if attachment.relatedPost != self.instance:
                raise serializers.ValidationError("Given attachment is not related to the post")
        return attachments_delete_ids

    def create(self, validated_data):
        # attachments = self.initial_data.pop('attachments')
        attachments = []
        if 'attachments' in validated_data:
            attachments = validated_data.pop('attachments')
        # validated_data['attachments'] = []
        created_post = Post.objects.create(**validated_data)
        for attachment in attachments:
            PostAttachment.objects.create(relatedPost=created_post, attachment=attachment)
        return created_post

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()

        # deleting old attachments
        if 'attachments_delete_ids' in validated_data:
            id_list = validated_data.get('attachments_delete_ids')
            for item_id in id_list:
                PostAttachment.objects.get(id=item_id).delete()

        # adding new attachments
        if 'attachments' in validated_data:
            attachments = validated_data.get('attachments')
            for attachment in attachments:
                PostAttachment.objects.create(relatedPost=instance, attachment=attachment)

        return instance


class UserDetailsSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(many=False, read_only=True)
    user_posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_posts', 'userprofile']





class PostDetailsSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    creator = UserSerializer(many=False, read_only=True)
    requestUserIsOwner = serializers.SerializerMethodField(read_only=True)
    requestUserLiked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
        # with depth>=0 the return json contains creator details, with depth==0 there is only creator's id
        # depth = 1

    def get_request_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    def get_requestUserIsOwner(self, instance):
        user = self.get_request_user()
        return user == instance.creator

    def get_requestUserLiked(self, instance):
        user = self.get_request_user()
        return instance.likes.filter(id=user.pk).exists()
