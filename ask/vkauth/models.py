# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime, timedelta

# Create your models here.
class Session(models.Model):
    user = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    key = models.CharField(max_length=255, unique=True)
    expires = models.DateTimeField(default=datetime.now)