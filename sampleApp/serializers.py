from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response

from .models import *


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        read_only_fields = ['creator', 'id', 'createdDate']
        fields = '__all__'


class PostAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostAttachment
        # fields = ['attachment']
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


class PostSerializer(serializers.ModelSerializer):
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    creator = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Post
        # model = PostAttachment
        fields = '__all__'
        # with depth>=0 the return json contains creator details, with depth==0 there is only creator's id
        # depth = 1


class PostCreateSerializer(serializers.ModelSerializer):
    # attachments = PostAttachmentSerializer(many=True, read_only=False)
    # attachments = PostAttachmentSerializer(many=True, required=False, read_only=False)
    attachments = serializers.ListField(
        child=serializers.FileField(use_url=False, max_length=100000, allow_empty_file=False), write_only=True,
        required=False)
    attachments_delete_ids = serializers.ListField(
        child=serializers.IntegerField(allow_null=False), required=False, write_only=True)

    # returns urls to files -- may be useful on frontend
    # attachments_urls = serializers.SerializerMethodField(read_only=True)

    # creator = UserSerializer(many=False, read_only=True)

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
            # PostAttachment.objects.create(relatedPost=created_post, **attachment)
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

    # def get_attachments_urls(self, obj):
    #     attachments_urls = PostAttachment.objects.filter(relatedPost=obj)
    #     return [attachment.attachment.url for attachment in obj.attachments.all()]
    # return PostAttachmentSerializer(attachments_urls, many=True).data


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
