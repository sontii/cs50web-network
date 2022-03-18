
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile", views.profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("<int:post_id>", views.comment, name="comment"),
    path("edit/<int:post_id>", views.editpost, name="editpost"),
    path("likes/<int:post_id>", views.postlikes, name="postlikes"),
    path("<str:usr>", views.usr, name="usr"),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
