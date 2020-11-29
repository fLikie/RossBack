import os
from django.db import models
from django.contrib.auth.models import User

# User models
class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    token = models.TextField()
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return self.user.username

class Position(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

class Organization(models.Model):
    name = models.TextField()

class Structure(models.Model):
    organization = models.ForeignKey(Organization, models.CASCADE)
    name = models.TextField()

class Education(models.Model):
    name = models.TextField()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'profile')
    surname = models.TextField()
    name = models.TextField()
    patronymic = models.TextField()
    date_of_birth = models.DateField()
    post = models.ForeignKey(Position, on_delete = models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete = models.CASCADE, null = True, blank = True)
    structure = models.ForeignKey(Structure, on_delete = models.CASCADE, null = True, blank = True)
    education = models.ForeignKey(Education, on_delete = models.CASCADE, null = True, blank = True)
    date_of_employment = models.DateField()

    def __str__(self):
        return self.user.username



# Forum models
class Topic(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

class Interest(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    topics = models.ManyToManyField(Topic)

class State(models.Model):
    name = models.TextField()
    service = models.BooleanField(default = False)

    def __str__(self):
        return self.name

class Forum(models.Model):
    topic = models.ForeignKey(Topic, on_delete = models.CASCADE)
    creator = models.ForeignKey(User, on_delete = models.CASCADE)
    state = models.ForeignKey(State, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    head = models.TextField()
    body = models.TextField()

    def __str__(self):
        return self.creator.username + ' - ' + self.topic.name + ' - ' + self.head

class Favorite(models.Model):
    forum = models.ForeignKey(Forum, on_delete = models.CASCADE, related_name = 'favorites')
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.user + ' - ' + self.forum.topic

class Comment(models.Model):
    forum = models.ForeignKey(Forum, on_delete = models.CASCADE, related_name = 'comments')
    creator = models.ForeignKey(User, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    message = models.TextField()

    def __str__(self):
        return self.creator.username + ' - ' + self.forum.head + ' - ' + self.message

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    forum = models.ForeignKey(Forum, on_delete = models.CASCADE, related_name = 'votes')
    score = models.IntegerField()


# Message models
class Chat(models.Model):
    user_1 = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'user_1')
    user_2 = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'user_2')
    updated_at = models.DateTimeField(auto_now = True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete = models.CASCADE)
    sender = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
