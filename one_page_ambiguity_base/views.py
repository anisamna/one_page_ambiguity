from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic.base import TemplateView

from one_page_ambiguity_base.forms import ProfileForm, SignUpForm


@login_required(login_url=reverse_lazy("login_"))
def index(request):
    return render(request, "index.html")


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

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("pk", None)
        if request.user.id != user_id:
            print(args)
            print(kwargs)
            return HttpResponseRedirect(reverse_lazy("index"))
        return super().get(request, *args, **kwargs)
