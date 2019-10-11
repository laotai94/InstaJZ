from annoying.decorators import ajax_request
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from Insta.models import Post, Like, Comment, InstaUser, UserConnection
from Insta.forms import CustomerUserCreationForm

# Class Views
class HelloDjango(TemplateView):
    template_name = 'home.html'

class PostListView(LoginRequiredMixin, ListView): 
    model = Post
    template_name = 'index.html'
    login_url = 'login'

    def get_queryset(self):
        current_user = self.request.user
        following = set()
        for connection in UserConnection.objects.filter(creator = current_user).select_related('following'):
            following.add(connection.following)
        return Post.objects.filter(author__in = following)
 
class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        liked = Like.objects.filter(post = self.kwargs.get('pk'), user = self.request.user).first()
        if liked:
            data['liked'] = 1
        else:
            data['liked'] = 0
        return data

class PostCreateView(CreateView):
    model = Post
    template_name = 'post_create.html'
    fields = '__all__'

class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_update.html' 
    fields = ['title', 'image']

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy("posts")
    login_url = 'login'

class SignUp(CreateView):
    form_class = CustomerUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UserDetailView(LoginRequiredMixin, DetailView):
    model = InstaUser
    template_name = 'user_detail.html'
    login_url = 'login'

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = InstaUser
    template_name = 'edit_profile.html'
    fields = ['profile_pic', 'username']
    login_url = 'login'

class ExploreView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'explore.html'
    login_url = 'login'

    def get_queryset(self):
        return Post.objects.all().order_by('-posted_on')[:20]

# Function Views
@ajax_request
def addLike(request):
    # post_pk get from index.js
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk = post_pk)
    
    # if this user did not like this post before
    try:
        # Create Like object using contructor
        like = Like(post = post, user = request.user)
        # Upload Like object to database
        like.save()
        result = 1
    # if this user liked this post before --> cancel like
    except Exception as e:
        like = Like.objects.get(post = post, user = request.user)
        like.delete()
        result = 0
    
    return {
        'result': result,
        'post_pk': post_pk
    }

@ajax_request
def addComment(request):
    # comment_text and post_pk get from index.js
    comment_text = request.POST.get('comment_text')
    post_pk = request.POST.get('post_pk')
    post = Post.objects.get(pk = post_pk)
    commenter_info = {}

    # if this user did not comment this post before
    try:
        comment = Comment(post = post, user = request.user, comment = comment_text)
        comment.save()
        username = request.user.username
        commenter_info = {
            'username' : username,
            'comment_text' : comment_text
        }

        result = 1
    except Exception as e:
        print(e)
        result = 0
    
    return {
        'result' : result,
        'post_pk' : post_pk,
        'commenter_info' : commenter_info
    }

@ajax_request
def toggleFollow(request):
    current_user = InstaUser.objects.get(pk = request.user.pk)
    follow_user_pk = request.POST.get('follow_user_pk')
    follow_user = InstaUser.objects.get(pk = follow_user_pk)

    try:
        if current_user != follow_user:
            if request.POST.get('type') == 'follow':
                connection = UserConnection(creator = current_user, following = follow_user)
                connection.save()
            elif request.POST.get('type') == 'unfollow':
                UserConnection.objects.filter(creator = current_user, following = follow_user).delete()
            result = 1
        else:
            result = 0
    except Exception as e:
        print(e)
        result = 0
    
    return {
        'result' : result,
        'type' : request.POST.get('type'),
        'follow_user_pk' : follow_user_pk
    }
