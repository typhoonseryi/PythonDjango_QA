# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import requests
from .models import Session
from django.contrib.auth.models import User
import random
from datetime import datetime, timedelta
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from ask.settings import CLIENT_ID, CLIENT_SECRET

def check_auth(request, usn):
    try:
        sessid = request.COOKIES.get('typhoonsessid')
        session = Session.objects.get(key=sessid)
        url = '/vk_user/' + usn + '/'
        response = HttpResponseRedirect(url)
        return response
    except Session.DoesNotExist:
        url = '/vk_auth/'
        response = HttpResponseRedirect(url)
        return response

def vk_access(request):
    code = request.GET.get("code")
    if code:
        payload_access = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'code': code}
        resp_access = requests.get('https://oauth.vk.com/access_token?redirect_uri=https://typhoonseryi.pythonanywhere.com/vk_access/', params=payload_access)
        data = resp_access.json()
        access_token = data["access_token"]
        user_id = data["user_id"]
        expires_in = int(data["expires_in"])
        session = Session()
        session.key = random.random()
        session.user = user_id
        session.access_token = access_token
        session.expires = datetime.now() + timedelta(seconds=expires_in)
        session.save()
        user = User.objects.get(first_name=user_id)
        usn = user.username
        url = '/'
        response = HttpResponseRedirect(url)
        response.set_cookie('typhoonsessid', session.key, httponly=True, expires = datetime.now() + timedelta(seconds=expires_in))
        messages.success(request, 'Auth is successful')
        return response


def vk_auth(request):
    return render(request, 'button_auth.html', {'client_id': CLIENT_ID})


def vk_user(request, usn):
    user = User.objects.get(username=usn)
    user_id = user.first_name
    if user_id != '':
        sessid = request.COOKIES.get('typhoonsessid')
        session = Session.objects.get(key=sessid)
        access_token = session.access_token
        payload_user = {'user_id': user_id, 'fields': 'bdate,city', 'v': '5.52', 'access_token': access_token}
        resp = requests.get('https://api.vk.com/method/users.get', params=payload_user)
        data = resp.json()
    else:
        data={}
    try:
        first_name = data["response"][0]["first_name"]
        last_name = data["response"][0]["last_name"]
    except KeyError:
        first_name = ''
        last_name = ''
    try:
        bdate = data["response"][0]["bdate"]
    except KeyError:
        bdate = ''
    try:
        city = data["response"][0]["city"]["title"]
    except KeyError:
        city = ''
    return render(request, 'users.html', {
        'username' : usn,
        'first_name' : first_name,
        'last_name' : last_name,
        'bdate' : bdate,
        'city' : city,
    })



