from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import PostSerializer, UserDetailsSerializer, CommentSerializer, PostDetailsSerializer, \
    UserSerializer, PostCreateSerializer, UserUpdateSerializer
from .models import Post, Comment
from rest_framework.pagination import PageNumberPagination


class PostPaginationClass(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 15


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPaginationClass
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'retrieve':
                return PostDetailsSerializer
            elif self.action == 'create' or self.action == 'update' or self.action == 'partial_update':
                return PostCreateSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        queryset = super(PostViewSet, self).filter_queryset(queryset)
        return queryset.order_by('-createdDate')

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.creator != request.user:
            return Response({'message': 'You are not the post creator'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.creator != request.user:
            return Response({'message': 'You are not the post creator'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class UserViewSet(
    # viewsets.ModelViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    # mixins.UpdateModelMixin, # User can update only self => handled in ProfileViewSet
    # mixins.DestroyModelMixin, # User cannot delete itself. If so, it will be handled in ProfileViewSet
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    displayProfile = False

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'retrieve':
            return UserDetailsSerializer
        return super().get_serializer_class()


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    # mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.creator != request.user:
            return Response({'message': 'You are not the comment creator'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class ProfileViewSet(
    # mixins.CreateModelMixin, # handled in UserViewSet
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    # mixins.DestroyModelMixin, # As for now, User cannot delete account by itself
    mixins.ListModelMixin,
    GenericViewSet
):
    # better than LoggedInUserView cause the POST requests can be done here
    serializer_class = UserDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if hasattr(self, 'action'):
            if self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
                return UserUpdateSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        # doesn't matter which id will be passed in url, it will always return current user
        return self.request.user


class Logout(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response(status=status.HTTP_200_OK, data={'message': 'Success'})
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': f'{e}'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_like(request, pk):
    post = get_object_or_404(Post, id=pk)
    # user = get_object_or_404(User, id=request.user.id)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        post.likes.add(request.user)
        return Response(status=status.HTTP_201_CREATED)
