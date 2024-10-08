from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'posts', api_views.PostViewSet)
router.register(r'users', api_views.UserViewSet)
router.register(r'comments', api_views.CommentViewSet)
router.register(r'profile', api_views.ProfileViewSet, basename='user_profile')

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('', views.DisplayPosts.as_view(), name='home'),
    # pk is the primary key of the current post, "int:" says that it can only contain an integer
    path('post/<int:pk>/', views.post_details, name='post-detail'),
    path('post/<int:pk>/<int:attachment_id>/', views.download_file, name='download'),
    path('post/<int:pk>/comment/', views.CreateComment.as_view(), name='comment'),
    path('post/<int:pk>/comment/<int:comment_id>/delete/', views.comment_delete, name="comment-delete"),
    path('post/new/', views.create_post, name='post-create'),
    path('post-like/<int:pk>/', views.post_like, name="post-like"),
    path('post-like/<int:pk>/<int:var>', views.post_like, name="post-like"),
    # variable must be called "pk" in this template
    path('post/<int:pk>/update/', views.UpdatePost.as_view(), name='post-update'),
    path('post/<int:pk>/update/attachment/<int:attachment_id>/delete/', views.attachment_delete,
         name='attachment-delete'),
    path('post/<int:pk>/delete/', views.PostDelete.as_view(), name='post-delete'),
    path('user/<str:username>/', views.DisplayUsersPosts.as_view(), name='user-posts'),
    path('login/', auth_views.LoginView.as_view(template_name="sampleApp/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="sampleApp/logout.html"), name='logout'),
    path('register/', views.register_user, name='register'),

    # api views
    path('api/', include(router.urls), name="api"),
    path('api/posts/<int:pk>/like/', api_views.post_like, name="post_like"),

    # authentication:
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', api_views.Logout.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
