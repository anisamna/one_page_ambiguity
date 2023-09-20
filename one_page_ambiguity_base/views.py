from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic.base import TemplateView

from one_page_ambiguity_base.forms import ProfileForm, SignUpForm


@login_required(login_url=reverse_lazy("login_"))
def index(request):
    return render(request, "index.html", {
        'title': 'About QUAS Framework'
    })

@login_required(login_url=reverse_lazy("login_"))
def howtouse_view(request):
    return render(request, "how_to_use.html", {
        'title': 'How to use'
    })

@login_required(login_url=reverse_lazy("login_"))
def change_access_admin(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)
    if user_obj.is_superuser:
        user_obj.is_superuser = False
        user_obj.save()
        messages.success(request, f"Success, remove access admin {user_obj.username}")
    else:
        user_obj.is_superuser = True
        user_obj.save()
        messages.success(request, f"Success, make as admin {user_obj.username}")
    return redirect(reverse_lazy('view_list_accounts'))

# Sign Up View
class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login_")
    template_name = "registration/signup.html"


class SignedOutView(TemplateView):
    template_name = "registration/signed_out.html"

    def get(self, request):
        logout(request)
        return render(request, self.template_name)


class ToLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = "registration/login.html"

    def get_success_url(self):
        return reverse_lazy("index")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password")
        return self.render_to_response(self.get_context_data(form=form))


# Edit Profile View
class ProfileView(UpdateView):
    model = User
    form_class = ProfileForm
    success_url = reverse_lazy("index")
    template_name = "registration/profile.html"

    extra_context = {'title': 'Profile'}

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context


    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("pk", None)
        if request.user.id != user_id:
            return HttpResponseRedirect(reverse_lazy("index"))
        return super().get(request, *args, **kwargs)
