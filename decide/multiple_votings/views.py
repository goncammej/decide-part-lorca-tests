from django.utils import timezone
from voting.models import Voting
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import BaseVotingForm, UpdateVotingForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html',
                      {'form': UserCreationForm})
    else:
        if (request.POST['password1'] == request.POST['password2']):
            try:
                user = User.objects.create_user(username=request.POST['username'],
                                                password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('list_votings')
            except IntegrityError:
                return render(request, 'signup.html',
                              {'form': UserCreationForm(),
                               "error": 'username already taken'})

        return render(request, 'signup.html',
                      {'form': UserCreationForm(),
                       "error": 'passwords did not match'})


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm(),
                'error': 'username or password is incorrect'
            })
        else:
            login(request, user)
            if user.is_superuser:
                return redirect('multiple_votings')
            return redirect('list_votings')


def multiple_votings(request):
    if request.method == 'GET':
        return render(request, 'multiple_votings.html',{
            'form': BaseVotingForm
        })
    else:
        try:
            form =BaseVotingForm(request.POST)
            new_voting = form.save(commit=False)
            new_voting.save()
            print(new_voting)
            return render(request, 'multiple_votings.html',{
                'form': BaseVotingForm
            })
        except :
            return render(request, 'multiple_votings.html',{
                'form': BaseVotingForm,
                'error': 'Bad data',
            })


@login_required
def list_votings(request):
    votings = Voting.objects.all()
    user = request.user
    return render(request, 'list_votings.html', {
        'votings': votings,
        'user': user,
    })

@login_required
def signout(request):
    logout(request)
    return redirect('home')

@login_required
def voting_details(request,voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    return render(request, 'voting_details.html',{
        'voting': voting,
    })


def voting_delete(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)

    if request.method == 'POST':
        
        if 'delete_button' in request.POST:
            
            voting.delete()
            messages.success(request, 'La votación ha sido eliminada con éxito.')
            return redirect('list_votings')  

    return render(request, 'list_votings.html', {'votings': Voting.objects.all(), 'user': request.user})


def start_voting(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    if request.method == 'POST':
        if 'start_voting_button' in request.POST:
            voting.create_pubkey()
            voting.start_date = timezone.now()
            voting.save()
            messages.success(request, 'Voting started successfully.')
            return redirect('list_votings')  
    return render(request, 'list_votings.html', {'votings': Voting.objects.all(), 'user': request.user})



def end_voting(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)
    if request.method == 'POST':
        if 'end_voting_button' in request.POST:
            voting.end_date = timezone.now()
            voting.save()
            messages.success(request, 'Voting started successfully.')
            return redirect('list_votings')  
    return render(request, 'list_votings.html', {'votings': Voting.objects.all(), 'user': request.user})


def update_voting(request, voting_id):
    voting = get_object_or_404(Voting, pk=voting_id)

    if request.method == 'POST':
        form = UpdateVotingForm(request.POST, instance=voting)
        if form.is_valid():
            form.save()
            messages.success(request, 'Voting updated successfully.')
            return redirect('list_votings')  # Replace with the desired URL or view name
    else:
        form = UpdateVotingForm(instance=voting)

    return render(request, 'update_voting.html', {'form': form, 'voting': voting})