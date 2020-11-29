from django.contrib import admin
from django.contrib.auth.admin  import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation   import ugettext_lazy as _

from main.models import *


admin.site.register(AuthToken)
admin.site.register(Position)
admin.site.register(Organization)
admin.site.register(Structure)
admin.site.register(Education)
admin.site.register(UserProfile)
admin.site.register(Interest)

admin.site.register(Topic)
admin.site.register(State)
admin.site.register(Forum)
admin.site.register(Favorite)
admin.site.register(Comment)
admin.site.register(Chat)
admin.site.register(Message)