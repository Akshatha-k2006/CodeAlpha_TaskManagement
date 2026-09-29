from django.contrib import admin
from .models import *
for m in (Project, Membership, Task, Comment, Notification): admin.site.register(m)
