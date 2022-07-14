from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    key = models.TextField()
    random = models.IntegerField()


class Password(models.Model):
    user_id = models.BigIntegerField()
    title = models.TextField()
    url = models.TextField()
    username = models.TextField()
    password = models.TextField()
    remark = models.TextField()
    category = models.TextField()
