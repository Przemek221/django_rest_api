from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, FileResponse
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import (UpdateUserForm, UpdateProfileForm, CreatePostForm, CreatePostAttachmentForm)
from .models import Post, Comment, PostAttachment


def get_attachments(post_id):
    return PostAttachment.objects.filter(relatedPost=post_id).all()


class DisplayPosts(ListView):
    model = Post
    # by default template name is: appName/modelName_viewType
    template_name = 'sampleApp/home.html'
    context_object_name = 'posts'
    ordering = ['-createdDate']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['attachments'] = {}
        for item in data['posts']:
            attachments = get_attachments(item.id)
            data['attachments'].update({item.id: attachments})
        return data


class DisplayUsersPosts(ListView):
    model = Post
    # by default template name is: appName/modelName_viewType
    template_name = 'sampleApp/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(creator=user).order_by('-createdDate')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['attachments'] = {}
        for item in data['posts']:
            attachments = get_attachments(item.id)
            data['attachments'].update({item.id: attachments})
        return data


@login_required
def post_like(request, pk, **kwargs):
    # in this case it's the post id, so it can be replaced with function 'pk' argument, which is primary key
    post = get_object_or_404(Post, id=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    if request.POST.get('next') is not None:

        # if kwargs:
        #     if kwargs['var'] == 3:
        #         return HttpResponseRedirect('http://localhost:8000/api/posts')

        # if user posts -> usr posts
        # if home -> home
        # if post details -> post details



        # return HttpResponseRedirect('http://localhost:8000/api')
        # return HttpResponseRedirect('http://localhost:8000/api')
        # return redirect(request.POST.get('next'))
        return redirect('home')
        # return redirect('api/posts')
    else:
        return redirect('api')
        # return redirect(request.user.user_posts)
        # return redirect('api_views/profile')


def post_details(request, pk):
    arg = {
        'object': Post.objects.get(id=pk),
        'comments': Comment.objects.filter(relatedPost=pk),
        'attachments': PostAttachment.objects.filter(relatedPost=pk)
    }

    return render(request, 'sampleApp/post_detail.html', arg)


def download_file(request, pk, attachment_id):
    file = PostAttachment.objects.filter(pk=attachment_id, relatedPost=pk).first()
    return FileResponse(file.attachment, as_attachment=True)


@login_required
def create_post(request):
    if request.method == 'POST':
        post_form = CreatePostForm(request.POST)
        post_attachment_form = CreatePostAttachmentForm(request.POST, request.FILES)
        uploaded_files = request.FILES.getlist('attachment')
        if post_form.is_valid() and post_attachment_form.is_valid():
            post_form.instance.creator = request.user
            created_post = post_form.save()

            for file in uploaded_files:
                temp = PostAttachment(attachment=file, relatedPost=created_post)
                temp.save()

            messages.success(request, "Post created")
            return redirect(reverse('post-detail', args=[created_post.id]))
    else:
        post_form = CreatePostForm()
        post_attachment_form = CreatePostAttachmentForm()

    arg = {
        'form': post_form,
        'post_attachment_form': post_attachment_form
    }
    return render(request, 'sampleApp/post_form.html', arg)


class CreateComment(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']

    def get_post(self, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['pk'])
        return post

    def form_valid(self, form):
        # assigning creator before validation
        form.instance.creator = self.request.user
        form.instance.relatedPost = self.get_post()
        return super().form_valid(form)


class UpdatePost(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['content']

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']

        old_attachments = PostAttachment.objects.filter(relatedPost=pk)
        if old_attachments.first() is not None:
            data['attachments'] = old_attachments.all()
        data['post_attachment_form'] = CreatePostAttachmentForm()

        return data

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        created_post = get_object_or_404(Post, pk=pk)

        post_attachment_form = CreatePostAttachmentForm(request.POST, request.FILES)
        uploaded_files = request.FILES.getlist('attachment')
        if post_attachment_form.is_valid():
            for file in uploaded_files:
                temp = PostAttachment(attachment=file, relatedPost=created_post)
                temp.save()

        return super().post(request)

    def form_valid(self, form):
        # assigning creator before validation
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.creator


class PostDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/../'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.creator


@login_required
def comment_delete(request, pk, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    post_id = pk
    if comment.creator == request.user:
        comment.delete()
    else:
        messages.error(request, "You are not the commenter")

    return redirect(reverse('post-detail', args=[post_id]))


@login_required
def attachment_delete(request, pk, attachment_id):
    attachment = get_object_or_404(PostAttachment, pk=attachment_id)
    if attachment.relatedPost.creator == request.user:
        attachment.delete()
    else:
        messages.error(request, "You are not the owner of the post")

    return redirect(reverse('post-update', args=[pk]))


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"User {username} registered")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'sampleApp/register.html', {'form': form, 'title': 'register'})


@login_required
def profile(request):
    if request.method == 'POST':
        update_user_form = UpdateUserForm(request.POST, instance=request.user)
        update_profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if update_profile_form.is_valid() and update_user_form.is_valid():
            update_user_form.save()
            update_profile_form.save()
            messages.success(request, f"Profile updated")
            return redirect('profile')

    else:
        update_user_form = UpdateUserForm(instance=request.user)
        update_profile_form = UpdateProfileForm(instance=request.user.userprofile)

    arg = {
        'update_user_form': update_user_form,
        'update_profile_form': update_profile_form
    }
    return render(request, 'sampleApp/profile.html', arg)
