from network.models import User
from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(Comment)