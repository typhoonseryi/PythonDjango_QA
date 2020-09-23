from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^vk_access/', vk_access),
    url(r'^vk_auth/', vk_auth),
    url(r'^vk_user/(\w+)', vk_user),
    url(r'^check_auth/(\w+)/', check_auth),
]