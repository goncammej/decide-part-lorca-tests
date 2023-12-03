from django import forms
from django.conf import settings
from django.utils import timezone
from voting.models import Voting, Question, QuestionOption
from base.models import Auth


class ClassicForm(forms.ModelForm):
    question_desc = forms.CharField(label="Question")
    option1 = forms.CharField(label="Option 1")
    option2 = forms.CharField(label="Option 2")
    more_options = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Voting
        fields = ["name", "desc"]

    def save(self):
        # Create Question
        question_desc = self.cleaned_data["question_desc"]
        question = Question(desc=question_desc, type="C")
        question.save()

        # Create Options for the Question
        option1 = self.cleaned_data["option1"]
        option2 = self.cleaned_data["option2"]
        QuestionOption(question=question, option=option1).save()
        QuestionOption(question=question, option=option2).save()
        if self.cleaned_data["more_options"]:
            more_options = self.cleaned_data["more_options"].split("\n")
            for option in more_options:
                QuestionOption(question=question, option=option).save()

        # Create Auth
        if not Auth.objects.filter(url=settings.BASEURL).exists():
            auth = Auth(name="Auth", url=settings.BASEURL)
            auth.save()
        else:
            auth = Auth.objects.get(url=settings.BASEURL)

        # Create Voting
        voting = Voting(
            name=self.cleaned_data["name"],
            desc=self.cleaned_data["desc"],
            question=question,
            start_date=timezone.now(),
        )
        voting.save()
        voting.auths.add(auth)
        voting.create_pubkey()
        voting.save()

        return voting

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
        self.fields["desc"].widget.attrs.update({"class": "form-control", "rows": 3})
        self.fields["question_desc"].widget.attrs.update({"class": "form-control"})
        self.fields["option1"].widget.attrs.update({"class": "form-control"})
        self.fields["option2"].widget.attrs.update({"class": "form-control"})
        self.fields["more_options"].widget.attrs.update(
            {"class": "form-control", "id": "id_options"}
        )
