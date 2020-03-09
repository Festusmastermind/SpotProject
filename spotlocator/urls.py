from django.conf.urls import url
from . import views



urlpatterns = [
    url(r'^create/$', views.create_menu, name='create-menu'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^menulist', views.menu_list, name='menulist'),
    url(r'^menulist/(?P<menu_id>[0-9]+)/delete/$', views.menu_delete, name='menu-delete'),
    url(r'^profile/$', views.owners_profiles, name='owners_profile'),
    url(r'^register/$', views.register, name='register'),
]