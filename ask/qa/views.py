from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.core.paginator import Paginator
from .models import *
from .forms import *
from vkauth.models import Session as Vksession
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST
import requests
import token

#ACCESS_TOKEN = token.access_token


def paginate(request, qs):
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404
    paginator = Paginator(qs, 10)
    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page, paginator

def do_login(login, password):
    try:
        user = User.objects.get(username=login)
    except User.DoesNotExist:
        return None
    if user.password != password:
        return None
    session = Session()
    session.key = random.random()
    session.user = user
    session.expires = datetime.now() + timedelta(hours=24)
    session.save()
    return session.key


def new_list(request):
    questions = Question.objects.new()
    page, paginator = paginate(request, questions)
    paginator.baseurl = '/?page='
    try:
        sessid = request.COOKIES.get('sessid')
        session = Session.objects.get(key=sessid)
        author = session.user.username
        auth = True
    except Session.DoesNotExist:
        author = 'Not authorized'
        auth = False
    try:
        typhoonsessid = request.COOKIES.get('typhoonsessid')
        session = Vksession.objects.get(key=typhoonsessid)
        vkauth = True
        vk_id = session.user
    except Vksession.DoesNotExist:
        vkauth = False
        vk_id = ''
    return render(request, 'base.html', {
           'posts': page.object_list,
           'paginator': paginator, 'page': page,
           'author' : author,
           'auth' : auth,
           'vkauth': vkauth,
           'vk_id': vk_id,
    })

def pop_list(request):
    questions = Question.objects.popular()
    page, paginator = paginate(request, questions)
    paginator.baseurl = '/popular/?page='
    return render(request, 'base1.html', {
           'posts': page.object_list,
           'paginator': paginator, 'page': page,
    })

def question_details(request, ident):
    error = request.GET.get('error', None)
    if error is None:
        error = ''
    try:
        sessid = request.COOKIES.get('sessid')
        session = Session.objects.get(key=sessid)
        user = session.user
        auth = True
    except Session.DoesNotExist:
        auth = False
        user = None
    try:
        question = Question.objects.get(id=ident)
    except Question.DoesNotExist:
        raise Http404
    if request.method == "POST":
        if user is not None:
            form = AnswerForm(request.POST)
            if form.is_valid():
                ans = form.save(ident, user)
                url = '/question/'+str(ident)+'/'
                return HttpResponseRedirect(url)
        else:
            error = u'Time of cookie expired!'
            url = '/question/'+str(ident)+'/?error='+error
            response = HttpResponseRedirect(url)
            return response
    else:
        form = AnswerForm()
    try:
        answers = Answer.objects.filter(question=question)
    except Question.DoesNotExist:
        answers = None
    return render(request, 'base2.html', {
           'title' : question.title,
           'text' : question.text,
           'author' : question.author,
           'user': user,
           'date' : question.added_at,
           'answers' : answers,
           'form' : form,
           'id' : ident,
           'auth' : auth,
           'error' : error,
    })


def quest_add(request):
    try:
        sessid = request.COOKIES.get('sessid')
        session = Session.objects.get(key=sessid)
        user = session.user
    except Session.DoesNotExist:
        return HttpResponseRedirect('/login/')
    if request.method == "POST":
        if user is not None:
            form = AskForm(request.POST)
            if form.is_valid():
                quest = form.save(user)
                url = '/question/'+str(quest.id)+'/'
                return HttpResponseRedirect(url)
        else:
            error = u'Time of cookie expired'
            url = '/login/?error='+error
            response = HttpResponseRedirect(url)
            return response
    else:
        form = AskForm()
    return render(request, 'ask.html', {
        'form': form,
    })


def login(request):
    error = request.GET.get('error', None)
    if error is None:
        error = ''
    if request.method == 'POST':
        login = request.POST.get('username')
        password = request.POST.get('password')
        url = request.POST.get('continue', '/')
        sessid = do_login(login, password)
        if sessid:
            response = HttpResponseRedirect(url)
            response.set_cookie('sessid', sessid, httponly=True,
            expires = datetime.now()+timedelta(hours=24)
            )
            return response
        else:
            form = LoginForm()
            error = u'Incorrect login or password'
    else:
        form = LoginForm()
    return render(request, 'login.html', {'error': error, 'form' : form })


def signup(request):
    error = ''
    if request.method == "POST":
        try:
            usn = request.POST.get('username')
            query = User.objects.get(username=usn)
            error = u'Current user already exists'
            form = SignupForm()
        except User.DoesNotExist:
            form = SignupForm(request.POST)
            if form.is_valid():
                sig = form.save()
                login = sig.username
                password = sig.password
                url = '/'
                sessid = do_login(login, password)
                response = HttpResponseRedirect(url)
                response.set_cookie('sessid', sessid, httponly=True,
                expires = datetime.now() + timedelta(hours=24)
                )
                return response
    else:
        form = SignupForm()
    return render(request, 'signup.html', {
        'form': form, 'error': error,
    })

def logout(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('typhoonsessid')
    response.delete_cookie('sessid')
    return response

@require_POST
def set_like(request):
    question_id = request.POST.get('question_id')
    user_id = request.POST.get('user_id')
    question = Question.objects.get(id=question_id)
    user = User.objects.get(id=user_id)
    question.likes.add(user)
    rating = question.likes.count()
    question.rating = rating
    question.save()
    return HttpResponse("<h2>OK</h2>")

def get_rating(request):
    if request.method == 'GET':
        ident=request.GET.get('client_response')
        question = Question.objects.get(id=ident)
        rating = question.rating
        response_data ={}
        response_data['rating'] = rating
    return JsonResponse(response_data)

def testing(request):
    response = HttpResponse()
    return response

def vk_link(request, vkid, usn):
    user = User.objects.get(username=usn)
    user.first_name = vkid
    user.save()
    return HttpResponseRedirect('/')



