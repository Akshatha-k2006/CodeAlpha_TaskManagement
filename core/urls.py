from django.urls import path
from django.contrib.auth import views as av
from . import views as v
urlpatterns = [
    path("", v.dashboard, name="dashboard"),
    path("login/", av.LoginView.as_view(), name="login"),
    path("logout/", av.LogoutView.as_view(), name="logout"),
    path("register/", v.register, name="register"),
    path("profile/", v.profile, name="profile"),
    path("notifications/", v.notifications, name="notifications"),
    path("projects/new/", v.project_create, name="project_create"),
    path("projects/<int:pid>/", v.board, name="board"),
    path("projects/<int:pid>/settings/", v.project_settings, name="project_settings"),
    path("projects/<int:pid>/tasks/add/", v.task_add, name="task_add"),
    path("tasks/<int:tid>/", v.task_detail, name="task_detail"),
    path("tasks/<int:tid>/move/", v.task_move, name="task_move"),
    path("tasks/<int:tid>/comments/", v.comment_add, name="comment_add"),
    path("comments/<int:cid>/delete/", v.comment_delete, name="comment_delete"),
]
