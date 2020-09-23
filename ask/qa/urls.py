from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from qa.views import *

urlpatterns = [
    url(r'^$', new_list),
    url(r'^popular/', pop_list),
    url(r'^question/(\d+)/', question_details),
    url(r'^ask/', quest_add),
    url(r'^signup/', signup),
    url(r'^login/', login),
    url(r'^logout/', logout),
    url(r'^likes/', set_like),
    url(r'^getrate/', get_rating),
    url(r'^test/', testing),
    url(r'^vk_link/(\d+)/(\w+)/', vk_link),
 ]
