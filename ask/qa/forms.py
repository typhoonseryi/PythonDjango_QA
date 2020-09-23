from django import forms
from .models import *
from django.contrib.auth.models import User

class AskForm(forms.Form):
    title = forms.CharField(max_length=100)
    text = forms.CharField(widget=forms.Textarea)
    def save(self, user):
        self.cleaned_data['author'] = user
        post = Question(**self.cleaned_data)
        post.save()
        return post

class AnswerForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    def save(self, ident, user):
        self.cleaned_data['author'] = user
        self.cleaned_data['question'] = Question.objects.get(id=ident)
        post = Answer(**self.cleaned_data)
        post.save()
        return post

class SignupForm(forms.Form):
    username = forms.CharField(label='Username*', max_length=100)
    email = forms.EmailField(label='Email', required=False)
    password = forms.CharField(label='Password*', widget=forms.PasswordInput())
    def save(self):
        post = User(**self.cleaned_data)
        post.save()
        return post

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
