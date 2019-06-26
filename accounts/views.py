from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm
from django.views.generic import CreateView, DetailView, UpdateView
from .models import User, UserRelation
from django.utils.text import slugify
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def get_latest_users(request):
    l_users = User.objects.order_by('-pk')[:5][::-1]
    l_users_data = []
    for u in l_users:
        l_users_data.append({
            "id": u.pk,
            "username": u.username,
            "url": "accounts/" + u.slug,
            "avatar": u.avatar.url
        })
    data = {
        "code": 200,
        "description": "success",
        "data": {
            "users": l_users_data
        }
    }
    return JsonResponse(data)

def logout_view(request):
    logout(request)
    return redirect('login')

def follow(request, pk):
    target = get_object_or_404(User, pk=pk)
    num_results = UserRelation.objects.filter(follower=request.user, target=target).count()
    if num_results == 0:
        ur = UserRelation(follower=request.user, target=target, accepted=True)
        ur.save()
        return JsonResponse({'code':201, 'description':'success'})
    return JsonResponse({'code':200, 'description':'already following'})

def unfollow(request, pk):
    target = get_object_or_404(User, pk=pk)
    num_results = UserRelation.objects.filter(follower=request.user, target=target).count()
    if num_results == 1:
        ur = UserRelation.objects.filter(follower=request.user, target=target)
        ur.delete()
        return JsonResponse({'code':201, 'description':'success'})
    return JsonResponse({'code':200, 'description':'not following'})

# Create your views here.
class RegisterView(CreateView):
    model = User
    slug_field = 'username'
    slug_kwargs = 'username'
    template_name = "accounts/register.html"
    fields = ['username', 'email', 'password']

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = User(username=username, password=raw_password, email=email)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

class ProfileView(UpdateView):
    model = User
    template_name = 'accounts/profile.html'
    fields = ['avatar', 'fullname', 'username', 'bio', 'bp']
    success_url = reverse_lazy('home')

    def get_queryset(self, *args, **kwargs):
        if (self.kwargs['slug'][0] == '@'):
            self.kwargs['slug'] = self.kwargs['slug'][:1]
        return super().get_queryset(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['current_user'] = self.request.user
        if self.request.user == context['object']:
            context['is_current_user'] = True
        else:
            context['is_current_user'] = False
            for r in context['object'].getFollowers():
                if r.accepted and r.follower == self.request.user:
                    context['following'] = True
                else:
                    context['following'] = False
        return context