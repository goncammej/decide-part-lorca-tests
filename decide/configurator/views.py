from django.shortcuts import render
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .forms import ClassicForm, OpenQuestionForm


def configurator(request):
    return render(request, "configurator/configurator.html")


class CreateClassicView(TemplateView):
    template_name = "configurator/create_classic.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ClassicForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ClassicForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Classic voting created successfully!")
            return redirect(reverse("configurator"))
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CreateOpenQuestionView(TemplateView):
    template_name = "configurator/create_open_question.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = OpenQuestionForm()
        return context

    def post(self, request, *args, **kwargs):
        form = OpenQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Open question voting created successfully!")
            return redirect(reverse("configurator"))
        else:
            return self.render_to_response(self.get_context_data(form=form))
