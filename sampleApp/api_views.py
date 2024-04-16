from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.response import Response

from .serializers import PostSerializer, UserSerializer, CommentSerializer
from .models import Post, Comment
from rest_framework.pagination import PageNumberPagination


class PostPaginationClass(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 2


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPaginationClass

    # retrieve is used when returning single item
    def retrieve(self, request, *args, **kwargs):
        queryset = super().retrieve(request, *args, **kwargs)
        queryset.data['test_data'] = 0
        return queryset

    # list is used when returning multiple objects
    # def list(self, request, *args, **kwargs):
    #     return {'a': 2}


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    # https://stackoverflow.com/questions/67962024/how-to-query-related-object-in-drf-viewsets-modelviewset
    serializer_class = CommentSerializer

