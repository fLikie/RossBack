from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name = 'login'),
    path('logout', views.logout, name = 'logout'),

    path('get_profile', views.get_profile, name = 'get_profile'),
    path('get_favorits', views.get_favorits, name = 'get_favorits'),
    path('change_password', views.change_password, name = 'change_password'),

    path('get_states', views.get_states, name = 'get_states'),

    path('get_topics', views.get_topics, name = 'get_topics'),
    path('get_topic/<int:topic_id>', views.get_topic, name = 'get_topic'),

    path('get_forum', views.get_forum, name = 'get_forum'),
    path('create_forum', views.create_forum, name = 'create_forum'),
    path('favorite_forum', views.favorite_forum, name = 'favorite_forum'),
    path('unfavorite_forum', views.unfavorite_forum, name = 'unfavorite_forum'),

    path('upvote_forum', views.upvote_forum, name = 'upvote_forum'),
    path('downvote_forum', views.downvote_forum, name = 'downvote_forum'),
    path('unvote_forum', views.unvote_forum, name = 'unvote_forum'),

    path('create_comment', views.create_comment, name = 'create_comment'),

    path('set_intrests', views.set_intrests, name = 'set_intrests'),
    path('get_interests', views.get_interests, name = 'get_interests'),

    path('get_users', views.get_users, name = 'get_users'),
    path('get_chats', views.get_chats, name = 'get_chats'),
    path('send_message', views.send_message, name = 'send_message'),
]
