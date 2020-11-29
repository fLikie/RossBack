from django.http                    import HttpResponse, HttpResponseRedirect
from django.shortcuts               import render, redirect
from django.contrib.auth            import authenticate
from django.views.decorators.csrf   import csrf_exempt
from uuid                           import uuid4
from django.utils                   import timezone
from django.db.models               import Q, Count

import json

from . import models


def success_request(result):
    result['status'] = 'success'
    return HttpResponse(json.dumps(result), content_type="application/json")

def failed_request(errors):
    result = {}
    result['status'] = 'failed'
    result['errors'] = errors
    return HttpResponse(json.dumps(result), content_type = "application/json")


def get_tokens_user(request):
    if 'token' in request.headers:
        auth_token = request.headers['token']
        if models.AuthToken.objects.filter(token = auth_token, is_active = True):
            token = models.AuthToken.objects.get(token = auth_token)
            user = token.user

            return user
        else:
            return None
    else:
        return None

def create_auth_token(user):
    auth_token = models.AuthToken()
    auth_token.user = user

    token = str(uuid4())
    while models.AuthToken.objects.filter(token = token):
        token = str(uuid4())

    auth_token.token = token
    auth_token.is_active = True

    auth_token.save()

    return auth_token.token

def deactivate_user_token(auth_token):
    if models.AuthToken.objects.filter(token = auth_token, is_active = True):
        token = models.AuthToken.objects.get(token = auth_token)
        token.is_active = False
        token.save()

        return True
    else:
        return False

## Authorization views
@csrf_exempt
def login(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user_data = json.loads(request.body)
        login = None
        password = None

        if 'login' in user_data and user_data['login'] != '':
            login = user_data['login']
        else:
            errors.append('empty_login')

        if 'password' in user_data and user_data['password'] != '':
            password = user_data['password']
        else:
            errors.append('empty_password')

        if login and password:
            user = authenticate(username = login, password = password)

            if user is not None:
                token = create_auth_token(user)
                result['token'] = token
                return success_request(result)
            else:
                errors.append('cannot_login')
                return failed_request(errors)
        else:
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)

@csrf_exempt
def logout(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)

        if user:
            auth_token = request.headers['token']
            status = deactivate_user_token(auth_token)

            if status:
                return success_request(result)
            else:
                return failed_request(errors)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)


## Profie views
@csrf_exempt
def get_profile(request):
    errors = []
    result = {}

    user = get_tokens_user(request)
    if user is not None:
        if len(models.UserProfile.objects.filter(user = user)) > 0:
            profile = models.UserProfile.objects.get(user = user)
            prf = {}

            prf['id'] = user.id
            prf['surname'] = profile.surname
            prf['name'] = profile.name
            prf['patronymic'] = profile.patronymic
            prf['date_of_birth'] = profile.date_of_birth.isoformat()
            prf['date_of_employment'] = profile.date_of_employment.isoformat()

            prf['post'] = {}
            prf['post']['id'] = profile.post.id
            prf['post']['name'] = profile.post.name

            if profile.organization is not None:
                prf['organization'] = {}
                prf['organization']['id'] = profile.organization.id
                prf['organization']['name'] = profile.organization.name

            if profile.structure is not None:
                prf['structure'] = {}
                prf['structure']['id'] = profile.structure.id
                prf['structure']['name'] = profile.structure.name

            if profile.education is not None:
                prf['education'] = {}
                prf['education']['id'] = profile.education.id
                prf['education']['name'] = profile.education.name

            result['profile'] = prf
            return success_request(result)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_token')
        return failed_request(errors)

@csrf_exempt
def get_favorits(request):
    errors = []
    result = {}

    user = get_tokens_user(request)
    if user is not None:
        favorites = models.Favorite.objects.filter(user = user).order_by('-created_at')

        result['favorites'] = []
        for favorite in favorites:
            fav = {}
            fav['id'] = favorite.id
            fav['name'] = favorite.name
            fav['created_at'] = favorite.created_at
            
            result['favorites'].append(fav)

        return success_request(result)
    else:
        errors.append('wrong_token')
        return failed_request(errors)

@csrf_exempt
def change_password(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)

        if user is not None:
            user_data = json.loads(request.body)

            password = None
            password_repeat = None
            
            if 'password' in user_data and user_data['password'] != '':
                password = user_data['password']
            else:
                errors.append('empty_password')

            if 'password_repeat' in user_data and user_data['password_repeat'] != '':
                password_repeat = user_data['password_repeat']
            else:
                errors.append('empty_password_repeat')

            if password is not None and password_repeat is not None:
                if password == password_repeat:
                    user.set_password(password)
                    user.save()

                    return success_request(result)
                else:
                    errors.append('passwords_mismatch')
                    return failed_request(errors)
            else:
                return failed_request(errors)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)



## State views
@csrf_exempt
def get_states(request):
    errors = []
    result = {}

    user = get_tokens_user(request)
    if user is not None:
        result['states'] = []
        states = models.State.objects.filter(service = False)

        for state in states:
            stts = {}
            stts['name'] = state.name

            result['states'].append(stts)

        return success_request(result)
    else:
        errors.append('wrong_token')
        return failed_request(errors)


## Interests views
@csrf_exempt
def set_intrests(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)
        interests = None

        if models.Interest.objects.filter(user = user).exists():
            interests = models.Interest.objects.get(user = user)
        else:
            interests = models.Interest()
            interests.user = user
            interests.save()

        if user is not None:
            user_data = json.loads(request.body)

            interests_ids = None

            if 'interests_ids' in user_data and user_data['interests_ids'] != '':
                interests_ids = user_data['interests_ids']
            else:
                errors.append('empty_interests_ids')

            result['interests_ids'] = []
            for interest_ids in interests_ids:
                if isinstance(interest_ids, int) and models.Topic.objects.filter(id = interest_ids).exists():
                    topic = models.Topic.objects.get(id = interest_ids)
                    
                    interests.topics.add(topic)
                    interests.save()
                    
                    result['interests_ids'].append(topic.id)

            return success_request(result)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)

@csrf_exempt
def get_interests(request):
    errors = []
    result = {}

    user = get_tokens_user(request)
    
    if user is not None:
        result['topics'] = []
        
        if models.Interest.objects.filter(user = user).exists():
            interest = models.Interest.objects.get(user = user)

            for topic in interest.topics.all():
                top = {}
                top['id'] = topic.id
                top['name'] = topic.name

                result['topics'].append(top)
            return success_request(result)
        else:
            return success_request(result)
    else:
        errors.append('wrong_token')
        return failed_request(errors)


## Topic views
@csrf_exempt
def get_topics(request):
    errors = []
    result = {}

    limit = 5
    interestings = 0

    if 'limit' in request.GET and request.GET['limit'] != '':
        limit = int(request.GET['limit'])

    if 'interestings' in request.GET and request.GET['interestings'] != '':
        interestings = int(request.GET['interestings'])

    user = get_tokens_user(request)
    if user is not None:
        if interestings == 0:
            topics = models.Topic.objects.all()
        else:
            if models.Interest.objects.filter(user = user).exists():
                interests = models.Interest.objects.get(user = user)
                topics = interests.topics.all()

        result['topics'] = []
        for topic in topics:
            top = {}
            top['id'] = topic.id
            top['name'] = topic.name
            top['forums'] = []

            forums = models.Forum.objects.filter(topic = topic).order_by('-updated_at')[:limit]
            for forum in forums:
                frm = {}
                frm['id'] = forum.id

                frm['creator'] = {}
                frm['creator']['id'] = forum.creator.id
                frm['creator']['surname'] = forum.creator.profile.surname
                frm['creator']['name'] = forum.creator.profile.name
                frm['creator']['patronymic'] = forum.creator.profile.patronymic
                frm['creator']['date_of_birth'] = forum.creator.profile.date_of_birth.isoformat()
                frm['creator']['date_of_employment'] = forum.creator.profile.date_of_employment.isoformat()
                
                frm['creator']['post'] = {}
                frm['creator']['post']['id'] = forum.creator.profile.post.id
                frm['creator']['post'] = forum.creator.profile.post.name

                frm['state'] = {}
                frm['state']['id'] = forum.state.id
                frm['state']['name'] = forum.state.name

                frm['comments_count'] = forum.comments.count()
                frm['favorites_count'] = forum.favorites.count()
                frm['votes'] = 0
                for vote in forum.votes.all():
                    frm['votes'] =+ vote.score

                frm['created_at'] = forum.created_at.isoformat()
                frm['updated_at'] = forum.updated_at.isoformat()

                frm['head'] = forum.head
                frm['body'] = forum.body

                frm['favorite'] = False
                if models.Favorite.objects.filter(forum = forum, user = user, active = True).exists():
                    frm['favorite'] = True
                
                top['forums'].append(frm)

            result['topics'].append(top)

        return success_request(result)
    else:
        errors.append('wrong_token')
        return failed_request(errors)


@csrf_exempt
def get_topic(request):
    errors = []
    result = {}

    topic_id = None
    offset = 0
    limit = 20

    if 'topic_id' in request.GET and request.GET['topic_id'] != '':
        topic_id = int(request.GET['topic_id'])
    else:
        errors.append('empty_topic_id')
        return failed_request(errors)

    if 'offset' in request.GET and request.GET['offset'] != '':
        offset = int(request.GET['offset'])

    if 'limit' in request.GET and request.GET['limit'] != '':
        limit = int(request.GET['limit'])

    user = get_tokens_user(request)
    if user is not None:
        if models.Topic.objects.filter(id = topic_id).exists():
            topic = models.Topic.objects.get(id = topic_id)

            result['forums'] = []
            forums = models.Forum.objects.filter(topic = topic).order_by('-updated_at')[offset : offset + limit]
            for forum in forums:
                frm = {}
                frm['id'] = forum.id

                frm['creator'] = {}
                frm['creator']['id'] = forum.creator.id
                frm['creator']['surname'] = forum.creator.profile.surname
                frm['creator']['name'] = forum.creator.profile.name
                frm['creator']['patronymic'] = forum.creator.profile.patronymic
                frm['creator']['date_of_birth'] = forum.creator.profile.date_of_birth.isoformat()
                frm['creator']['date_of_employment'] = forum.creator.profile.date_of_employment.isoformat()
                
                frm['creator']['post'] = {}
                frm['creator']['post']['id'] = forum.creator.profile.post.id
                frm['creator']['post']['name'] = forum.creator.profile.post.name

                frm['state'] = {}
                frm['state']['id'] = forum.state.id
                frm['state']['name'] = forum.state.name

                frm['comments_count'] = forum.comments.count()
                frm['favorites_count'] = forum.favorites.count()
                frm['votes'] = 0
                for vote in forum.votes.all():
                    frm['votes'] =+ vote.score

                frm['created_at'] = forum.created_at.isoformat()
                frm['updated_at'] = forum.updated_at.isoformat()

                frm['head'] = forum.head
                frm['body'] = forum.body

                frm['favorite'] = False
                if models.Favorite.objects.filter(forum = forum, user = user, active = True).exists():
                    frm['favorite'] = True
                
                result['forums'].append(frm)

            return success_request(result)
        else:
            errors.append('wrong_topic_id')
            return failed_request(errors)
    else:
        errors.append('wrong_token')
        return failed_request(errors)

        
## Forum views
@csrf_exempt
def get_forum(request):
    errors = []
    result = {}

    forum_id = None
    offset = 0
    limit = 20

    if 'forum_id' in request.GET and request.GET['forum_id'] != '':
        forum_id = int(request.GET['forum_id'])
    else:
        errors.append('empty_forum_id')
        return failed_request(errors)

    if 'offset' in request.GET and request.GET['offset'] != '':
        offset = int(request.GET['offset'])

    if 'limit' in request.GET and request.GET['limit'] != '':
        limit = int(request.GET['limit'])

    user = get_tokens_user(request)
    if user is not None:
        if models.Forum.objects.filter(id = forum_id).exists():
            forum = models.Forum.objects.get(id = forum_id)

            result['topic'] = {}
            result['topic']['id'] = forum.topic.id
            result['topic']['name'] = forum.topic.name

            result['creator'] = {}
            result['creator']['id'] = forum.creator.id
            result['creator']['surname'] = forum.creator.profile.surname
            result['creator']['name'] = forum.creator.profile.name
            result['creator']['patronymic'] = forum.creator.profile.patronymic
            result['creator']['date_of_birth'] = forum.creator.profile.date_of_birth.isoformat()
            result['creator']['date_of_employment'] = forum.creator.profile.date_of_employment.isoformat()

            result['creator']['post'] = {}
            result['creator']['post']['id'] = forum.creator.profile.post.id
            result['creator']['post']['name'] = forum.creator.profile.post.name

            result['state'] = {}
            result['state']['id'] = forum.state.id
            result['state']['name'] = forum.state.name

            result['head'] = forum.head
            result['body'] = forum.body

            result['comments_count'] = forum.comments.count()
            result['favorites_count'] = forum.favorites.count()
            result['votes'] = 0
            for vote in forum.votes.all():
                result['votes'] =+ vote.score

            result['created_at'] = forum.created_at.isoformat()
            result['updated_at'] = forum.updated_at.isoformat()

            result['comments'] = []
            comments = models.Comment.objects.filter(forum = forum).order_by('created_at')
            for comment in comments:
                cmnt = {}
                cmnt['id'] = comment.id

                cmnt['creator'] = {}
                cmnt['creator']['id'] = comment.creator.id
                cmnt['creator']['surname'] = comment.creator.profile.surname
                cmnt['creator']['name'] = comment.creator.profile.name
                cmnt['creator']['patronymic'] = comment.creator.profile.patronymic
                cmnt['creator']['date_of_birth'] = comment.creator.profile.date_of_birth.isoformat()
                cmnt['creator']['date_of_employment'] = comment.creator.profile.date_of_employment.isoformat()

                cmnt['created_at'] = comment.created_at.isoformat()
                cmnt['message'] = comment.message

                result['comments'].append(cmnt)

            return success_request(result)
        else:
            errors.append('wrong_forum_id')
            return failed_request(errors)
    else:
        errors.append('wrong_token')
        return failed_request(errors)


@csrf_exempt
def create_forum(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)

        if user is not None:
            user_data = json.loads(request.body)

            topic = None
            state = None
            head = None
            body = None

            if 'topic_id' in user_data and user_data['topic_id'] != '':
                if models.Topic.objects.filter(id = user_data['topic_id']).exists():
                    topic = models.Topic.objects.get(id = user_data['topic_id'])
                else:
                    errors.append('worng_topic_id')
            else:
                errors.append('empty_topic_id')

            if 'state_id' in user_data and user_data['state_id'] != '':
                if models.State.objects.filter(id = user_data['state_id']).exists():
                    state = models.State.objects.get(id = user_data['state_id'])
                else:
                    errors.append('wrong_state_id')
            else:
                errors.append('empty_state_id')

            if 'head' in user_data and user_data['head'] != '':
                head = user_data['head']
            else:
                errors.append('empty_head')

            if 'body' in user_data and user_data['body'] != '':
                body = user_data['body']
            else:
                errors.append('empty_body')

            if topic is not None and state is not None and head is not None and body is not None:
                forum = models.Forum()

                forum.creator = user
                forum.topic = topic
                forum.state = state
                forum.head = head
                forum.body = body

                forum.save()
                result['forum_id'] = forum.id

                return success_request(result)
            else:
                return failed_request(errors)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)

@csrf_exempt
def favorite_forum(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)

        if user is not None:
            user_data = json.loads(request.body)

            forum = None

            if 'forum_id' in user_data and user_data['forum_id']:
                if models.Forum.objects.filter(id = user_data['forum_id']).exists():
                    forum = models.Forum.objects.get(id = user_data['forum_id'])
                else:
                    errors.append('wrong_forum_id')
                    return failed_request(errors)
            else:
                errors.append('empty_forum_id')
                return failed_request(errors)

            if forum is not None:
                if models.Favorite.objects.filter(user = user, forum = forum).exists():
                    favorite = models.Favorite.objects.filter(user = user, forum = forum)

                    if favorite.active:
                        errors.append('forum_already_favorite')
                        return failed_request(errors)
                    else:
                        favorite.active = True
                        favorite.save()

                        result['favorite_id'] = favorite.id
                        return success_request(result)
                else:
                    favorite = models.Favorite()
                    favorite.forum = forum
                    favorite.user = user_data
                    favorite.save()

                    result['favorite_id'] = favorite.id
                    return success_request(result)
            else:
                return failed_request(errors)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)

@csrf_exempt
def unfavorite_forum(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)

        if user is not None:
            user_data = json.loads(request.body)

            forum = None

            if 'forum_id' in user_data and user_data['forum_id']:
                if models.Forum.objects.filter(id = user_data['forum_id']).exists():
                    forum = models.Forum.objects.get(id = user_data['forum_id'])
                else:
                    errors.append('wrong_forum_id')
            else:
                errors.append('empty_forum_id')

            if forum is not None:
                if models.Favorite.objects.filter(user = user, forum = forum).exists():
                    favorite = models.Favorite.objects.get(user = user, forum = forum)
                    favorite.active = False
                    favorite.save()

                    result['favorite_id'] = favorite.id
                    return success_request(result)
                else:
                    errors.append('forum_not_favorite')
                    return failed_request(errors)
            else:
                return failed_request(errors)

        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)


@csrf_exempt
def upvote_forum(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)

        if user is not None:
            user_data = json.loads(request.body)

            forum = None

            if 'forum_id' in user_data and user_data['forum_id']:
                if models.Forum.objects.filter(id = user_data['forum_id']).exists():
                    forum = models.Forum.objects.get(id = user_data['forum_id'])
                else:
                    errors.append('wrong_forum_id')
            else:
                errors.append('empty_forum_id')

            if forum is not None:
                if models.Vote.objects.filter(user = user, forum = forum).exists():
                    vote = models.Vote.objects.get(user = user, forum = forum)

                    if vote.score == 1:
                        errors.append('forum_already_upvoted')
                        return failed_request(errors)
                    else:
                        vote.score = 1
                        vote.save()

                        result['vote_id'] = vote.id
                        return success_request(result)
                else:
                    vote = models.Vote()
                    vote.user = user
                    vote.forum = forum
                    vote.score = 1

                    vote.save()
                    result['vote_id'] = vote.id
                    return success_request(result)
            else:
                return failed_request(errors)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)

@csrf_exempt
def downvote_forum(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)

        if user is not None:
            user_data = json.loads(request.body)

            forum = None

            if 'forum_id' in user_data and user_data['forum_id']:
                if models.Forum.objects.filter(id = user_data['forum_id']).exists():
                    forum = models.Forum.objects.get(id = user_data['forum_id'])
                else:
                    errors.append('wrong_forum_id')
            else:
                errors.append('empty_forum_id')

            if forum is not None:
                if models.Vote.objects.filter(user = user, forum = forum).exists():
                    vote = models.Vote.objects.get(user = user, forum = forum)

                    if vote.score == -1:
                        errors.append('forum_already_downvoted')
                        return failed_request(errors)
                    else:
                        vote.score = -1
                        vote.save()

                        result['vote_id'] = vote.id
                        return success_request(result)
                else:
                    vote = models.Vote()
                    vote.user = user
                    vote.forum = forum
                    vote.score = -1

                    vote.save()
                    result['vote_id'] = vote.id
                    return success_request(result)
            else:
                return failed_request(errors)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)


@csrf_exempt
def unvote_forum(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)

        if user is not None:
            user_data = json.loads(request.body)

            forum = None

            if 'forum_id' in user_data and user_data['forum_id']:
                if models.Forum.objects.filter(id = user_data['forum_id']).exists():
                    forum = models.Forum.objects.get(id = user_data['forum_id'])
                else:
                    errors.append('wrong_forum_id')
            else:
                errors.append('empty_forum_id')

            if forum is not None:
                if models.Vote.objects.filter(user = user, forum = forum).exists():
                    vote = models.Vote.objects.get(user = user, forum = forum)

                    if vote.score == 0:
                        errors.append('forum_already_unvoted')
                        return failed_request(errors)
                    else:
                        vote.score = 0
                        vote.save()

                        result['vote_id'] = vote.id
                        return success_request(result)
                else:
                    vote = models.Vote()
                    vote.user = user
                    vote.forum = forum
                    vote.score = 0

                    vote.save()
                    result['vote_id'] = vote.id
                    return success_request(result)
            else:
                return failed_request(errors)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)





## Comment views
@csrf_exempt
def create_comment(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)

        if user is not None:
            user_data = json.loads(request.body)

            forum = None
            message = None

            if 'forum_id' in user_data and user_data['forum_id'] != '':
                if models.Forum.objects.filter(id = user_data['forum_id']).exists():
                    forum = models.Forum.objects.get(id = user_data['forum_id'])
                else:
                    errors.append('wrong_forum_id')
            else:
                errors.append('empty_forum_id')

            if 'message' in user_data and user_data['message'] != '':
                message = user_data['message']
            else:
                errors.append('empty_message')

            if forum is not None and message is not None:
                comment = models.Comment()
                
                forum.updated_at = timezone.now()
                forum.save()

                comment.forum = forum
                comment.creator = user
                comment.message = message

                comment.save()
                result['comment_id'] = comment.id

                return success_request(result)
            else:
                return failed_request(errors)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)


## Chat views
@csrf_exempt
def get_users(request):
    errors = []
    result = {}

    search = None

    if 'search' in request.GET and request.GET['search'] != '':
        search = request.GET['search']

    user = get_tokens_user(request)
    if user is not None:
        companions = models.User.objects.exclude(is_superuser = True).exclude(is_staff = True).exclude(id = user.id)

        if search != '':
            companions = models.User.objects.exclude(is_superuser = True).exclude(is_staff = True).exclude(id = user.id).filter(Q(profile__surname__contains = search) | Q(profile__name__contains = search) | Q(profile__name__contains = search) | Q(profile__patronymic__contains = search) | Q(profile__post__name__contains = search) | Q(profile__organization__name__contains = search) | Q(profile__structure__name__contains = search))

        result['users'] = []
        for companion in companions:
            usr = {}
            usr['id'] = companion.id
            usr['surname'] = companion.profile.surname
            usr['name'] = companion.profile.name
            usr['patronymic'] = companion.profile.patronymic
            usr['date_of_birth'] = companion.profile.date_of_birth.isoformat()
            usr['date_of_employment'] = companion.profile.date_of_employment.isoformat()

            result['users'].append(usr)

        return success_request(result)   
    else:
        errors.append('wrong_token')
        return failed_request(errors)


@csrf_exempt
def get_chats(request):
    errors = []
    result = {}

    user = get_tokens_user(request)
    if user is not None:
        chats = []
        chats.append(models.Chat.objects.filter(user_1 = user))
        chats.append(models.Chat.objects.filter(user_2 = user))

        result['chats'] = []
        for chat in chats:
            if models.Message.objects.filter(chat = chat).exists():
                if chat.user_1 == user:
                    cht['chat'] = {}
                    cht['chat']['id'] = chat.id
                    cht['chat']['updated_at'] = chat.updated_at

                    cht['companion'] = {}
                    cht['companion']['id'] = chat.user_2.id
                    cht['companion']['surname'] = chat.user_2.surname
                    cht['companion']['name'] = chat.user_2.name
                    cht['companion']['patronymic'] = chat.user_2.patronymic
                    cht['companion']['date_of_birth'] = chat.user_2.date_of_birth.isoformat()

                    cht['companion']['post'] = {}
                    cht['companion']['post']['id'] = chat.user_2.post.id
                    cht['companion']['post']['name'] = chat.user_2.post.name

                    last_message = models.Message.objects.filter(chat = chat).order_by('-created_at')[0]
                    cht['message'] = {}
                    cht['message']['sender_id'] = last_message.sender.id
                    cht['message']['created_at'] = last_message.created_at.isoformat()

                    result['chats'].append(cht)
                elif chat.user_2 == user:
                    cht['chat'] = {}
                    cht['chat']['id'] = chat.id
                    cht['chat']['updated_at'] = chat.updated_at

                    cht['companion'] = {}
                    cht['companion']['id'] = chat.user_1.id
                    cht['companion']['surname'] = chat.user_1.surname
                    cht['companion']['name'] = chat.user_1.name
                    cht['companion']['patronymic'] = chat.user_1.patronymic
                    cht['companion']['date_of_birth'] = chat.user_1.date_of_birth.isoformat()

                    cht['companion']['post'] = {}
                    cht['companion']['post']['id'] = chat.user_1.post.id
                    cht['companion']['post']['name'] = chat.user_1.post.name

                    last_message = models.Message.objects.filter(chat = chat).order_by('-created_at')[0]
                    cht['message'] = {}
                    cht['message']['sender_id'] = last_message.sender.id
                    cht['message']['created_at'] = last_message.created_at.isoformat()

                    result['chats'].append(cht)

        result['chats'] = sorted(result['chats'], key = itemgetter('updated_at'), reversed = True)
        return success_request(result)   
    else:
        errors.append('wrong_token')
        return failed_request(errors)

@csrf_exempt
def get_chat(request):
    errors = []
    result = {}

    user_id = None

    if 'user_id' in request.GET and request.GET['user_id'] != '':
        user_id = int(request.GET['user_id'])
    else:
        errors.append('empty_user_id')
        return failed_request(errors)

    user = get_tokens_user(request)
    if user is not None:
        if user.id != user_id:
            if models.User.objects.filter(id = user_id).exists():
                user_2 = models.User.objects.get(id = user_id)

                chat = None
                user_is_initiator = False

                if models.Chat.objects.filter(user_1 = user, user_2 = user_2).exists():
                    chat = models.Chat.objects.get(user_1 = user, user_2 = user_2)
                    user_is_initiator = True
                elif models.Chat.objects.filter(user_1 = user_2, user_2 = user):
                    chat = models.Chat.objects.get(user_1 = user_2, user_2 = user)
                    user_is_initiator = False

                if chat is not None:
                    if user_is_initiator:
                        result['id'] = chat.id

                        result['companion'] = {}
                        result['companion']['surname'] = chat.user_2.surname
                        result['companion']['name'] = chat.user_2.name
                        result['companion']['patronymic'] = chat.user_2.patronymic
                        result['companion']['date_of_birth'] = chat.user_2.date_of_birth.isoformat()

                        result['companion']['post'] = {}
                        result['companion']['post']['id'] = chat.user_2.post.id
                        result['companion']['post']['name'] = chat.user_2.post.name

                        return success_request(result)
                    else:
                        result['id'] = chat.id

                        result['companion'] = {}
                        result['companion']['surname'] = chat.user_1.surname
                        result['companion']['name'] = chat.user_1.name
                        result['companion']['patronymic'] = chat.user_1.patronymic
                        result['companion']['date_of_birth'] = chat.user_1.date_of_birth.isoformat()

                        result['companion']['post'] = {}
                        result['companion']['post']['id'] = chat.user_1.post.id
                        result['companion']['post']['name'] = chat.user_1.post.name

                        return success_request(result)
                else:
                    chat = models.Chat()
                    chat.user_1 = user
                    chat.user_2 = user_2
                    chat.save()

                    result['id'] = chat.id

                    result['companion'] = {}
                    result['companion']['surname'] = chat.user_1.surname
                    result['companion']['name'] = chat.user_1.name
                    result['companion']['patronymic'] = chat.user_1.patronymic
                    result['companion']['date_of_birth'] = chat.user_1.date_of_birth.isoformat()

                    result['companion']['post'] = {}
                    result['companion']['post']['id'] = chat.user_1.post.id
                    result['companion']['post']['name'] = chat.user_1.post.name

                    return success_request(result)
            else:
                errors.append('wrong_user_id')
        else:
            errors.append('wrong_user_id')
    else:
        errors.append('wrong_token')
        return failed_request(errors)


@csrf_exempt
def send_message(request):
    errors = []
    result = {}

    if request.method == 'POST' and request.body:
        user = get_tokens_user(request)

        if user is not None:
            user_data = json.loads(request.body)

            chat = None
            text = None

            if 'chat_id' in user_data and user_data['chat_id'] != '':
                if models.Chat.objects.filter(chat_id = user_data['chat_id']).exists():
                    chat = models.Chat.objects.get(chat_id = user_data['chat_id'])

                    if chat.user_1 != user and chat.user_2 != user:
                        errors.append('wrong_chat_id')
                        return failed_request(errors)
                else:
                    errors.append('wrong_chat_id')
                    return failed_request(errors)
            else:
                errors.append('empty_chat_id')
                return failed_request(errors)

            if 'text' in user_data and user_data['text'] != '':
                text = user_data['text']
            else:
                errors.append('empty_text')
                return failed_request(errors)

            if chat is not None and text is not None:
                message = models.Message()
                message.chat = chat
                message.sender = user
                message.text = text
                message.save()

                result['message_id'] = message.id

                return success_request(result)
            else:
                return failed_request(errors)
        else:
            errors.append('wrong_token')
            return failed_request(errors)
    else:
        errors.append('wrong_request')
        return failed_request(errors)
    