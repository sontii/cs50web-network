from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    post = models.CharField(max_length=200)
    timest = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.id,
            "username": self.user.username,
            "post": self.post,
        }

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE)
    post = models.ForeignKey(Post, on_delete=CASCADE)
    comment = models.CharField(max_length=200)
    timest = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=CASCADE, related_name='liked_user')
    post = models.ForeignKey(Post, on_delete=CASCADE, related_name='liked_post')

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=CASCADE, related_name='follower')
    followed = models.ForeignKey(User, on_delete=CASCADE, related_name='followed')
