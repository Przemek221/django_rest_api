from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirectBase
from django.shortcuts import redirect
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import PostSerializer, UserDetailsSerializer, CommentSerializer, PostDetailsSerializer, \
    UserSerializer, PostCreateSerializer
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
            elif self.action == 'create':
                return PostCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # queryset = User.objects.get(pk=self.request.user.id)
    serializer_class = UserSerializer
    displayProfile = False

    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action == 'retrieve':
            return UserDetailsSerializer
        return super().get_serializer_class()
    # def __init__(self):
    #     x = False
    #     return super().__init__(self)

    # def list(self, request, *args, **kwargs):
    #     self.displayProfile = True
    #     return self.retrieve(request, *args, **kwargs)
    #
    # def get_object(self):
    #     if self.displayProfile:
    #         self.displayProfile = False
    #         return self.request.user
    #     return super().get_object()

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset
    # def get_queryset(self):
    #     return User.objects.get(id=self.request.user.id)
    # def filter_queryset(self, queryset):
    #     return queryset.filter(pk=self.request.query_params.get(''))

    # def get_object(self):
    # pk = self.kwargs.get('pk')
    #
    # if pk == "current":
    # return self.request.user

    # return super().get_object()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    # https://stackoverflow.com/questions/67962024/how-to-query-related-object-in-drf-viewsets-modelviewset
    serializer_class = CommentSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    # better than LoggedInUserView cause the POST requests can be done here
    # queryset = User.objects.all()
    serializer_class = UserDetailsSerializer

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def get_object(self):
        # if self.request.user.is_authenticated:
        return self.request.user
        # else:
        #     return Response({'message': 'you are not logged in'}, status=401)
        # return self.request.user.is_authenticated()


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


class LoggedInUserView(APIView):
    def get(self, request):
        serializer = UserDetailsSerializer(self.request.user)
        return Response(serializer.data)


# class PostLikeView(APIView):
#     def post(self, request):


# class PostLikeViewSet(viewsets.ModelViewSet):
#     serializer_class = PostSerializer

class HttpResponseTemporaryRedirect(HttpResponseRedirectBase):
    status_code = 307


# To-do - zrobic aby post like zwracal redirect do glownej strony api lub do post details
@login_required
def post_like(request, pk):
    # in this case it's the post id, so it can be replaced with function 'pk' argument, which is primary key
    post = get_object_or_404(Post, id=pk)

    x = Response()
    x['abc'] = 3

    return x
    # if post.likes.filter(id=request.user.id).exists():
    #     post.likes.remove(request.user)
    # else:
    #     post.likes.add(request.user)

    # if request.POST.get('next') is not None:
    # return HttpResponseRedirect(request.POST.get('next'), status_code=307)
    # return HttpResponseTemporaryRedirect(request.POST.get('next'))
    # return redirect('api')
    # serializer = PostSerializer()
    # return Response(serializer.data)
    # else:
    #     serializer = PostSerializer()
    #     return Response(serializer.data)
    # return PostViewSet()
    # return redirect('api')
    # return
    # return redirect(request.user.user_posts)
    # return redirect('api_views/profile')


@api_view(
    # ['POST']
)
@login_required
def apiLike(request, pk):
    post = get_object_or_404(Post, id=pk)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    if request.POST.get('next') is not None:

        # to zaimplementowc tutaj!!!
        # if kwargs:
        #     if kwargs['var'] == 3:
        #         return HttpResponseRedirect('http://localhost:8000/api/posts')

        # if user posts -> usr posts
        # if home -> home
        # if post details -> post details
        return redirect(request.POST.get('next'))
        # return redirect('home')
        # return redirect('api/posts')
    else:
        return redirect('/api/posts/')
        # return redirect(request.user.user_posts)
        # return redirect('api_views/profile')

# nie dziala !!!!
# return redirect('api')
# dziala !!!!!!
#     return redirect('/api/')
