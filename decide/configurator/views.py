from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .forms import StandardForm


def configurator(request):
    return render(request, "configurator/configurator.html")


class CreateStandardView(TemplateView):
    template_name = "configurator/create_standard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = StandardForm()
        return context

    def post(self, request, *args, **kwargs):
        form = StandardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Standard voting created successfully!")
            return redirect(reverse("configurator"))
        else:
            return self.render_to_response(self.get_context_data(form=form))
