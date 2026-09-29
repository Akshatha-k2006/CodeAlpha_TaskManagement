import json
from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Project, Membership, Task, Comment
from .notify import notify

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})

def membership(user, pid):
    m = Membership.objects.filter(user=user, project_id=pid).select_related("project").first()
    if not m: raise Http404
    return m

def project_members(project): return [m.user for m in project.membership_set.select_related("user")]

@login_required
def dashboard(request):
    projects = (Project.objects.filter(membership__user=request.user)
        .annotate(total=Count("task", distinct=True), done=Count("task", filter=Q(task__status="done"), distinct=True))
        .prefetch_related("membership_set__user").order_by("-created"))
    return render(request, "dashboard.html", {"projects": projects})

@login_required
def profile(request):
    return render(request, "profile.html", {"tasks": request.user.tasks.exclude(status="done").select_related("project")})

@login_required
def project_create(request):
    if request.method == "POST" and request.POST.get("name", "").strip():
        p = Project.objects.create(name=request.POST["name"].strip(), description=request.POST.get("description", ""), created_by=request.user)
        Membership.objects.create(user=request.user, project=p, role="admin")
        return redirect("board", pid=p.id)
    return render(request, "project_form.html")

@login_required
def board(request, pid):
    m = membership(request.user, pid)
    tasks = m.project.task_set.select_related("assignee").annotate(ncomments=Count("comments"))
    cols = [(k, label, [t for t in tasks if t.status == k]) for k, label in Task.STATUSES]
    return render(request, "board.html", {"project": m.project, "cols": cols, "is_admin": m.role == "admin", "members": project_members(m.project)})

@login_required
@require_POST
def task_add(request, pid):
    m = membership(request.user, pid)
    title = request.POST.get("title", "").strip()
    status = request.POST.get("status", "todo")
    if title and status in dict(Task.STATUSES):
        Task.objects.create(project=m.project, title=title, status=status, created_by=request.user,
                            assignee=request.user if m.role == "member" else None)
    return redirect("board", pid=pid)

def can_edit(user, task, role): return role == "admin" or task.assignee_id == user.id

@login_required
@require_POST
def task_move(request, tid):
    task = get_object_or_404(Task, pk=tid)
    m = membership(request.user, task.project_id)
    status = json.loads(request.body or "{}").get("status")
    if status not in dict(Task.STATUSES): return JsonResponse({"error": "bad status"}, status=400)
    if not can_edit(request.user, task, m.role): return JsonResponse({"error": "Only admins or the assignee can move this task."}, status=403)
    if status != task.status:
        task.status = status; task.save()
        notify([task.assignee] if task.assignee else [], f"{request.user.username} moved “{task.title}” to {task.get_status_display()}", f"/tasks/{task.id}/", exclude=request.user)
    return JsonResponse({"ok": True})

@login_required
def task_detail(request, tid):
    task = get_object_or_404(Task.objects.select_related("project", "assignee"), pk=tid)
    m = membership(request.user, task.project_id)
    admin, own = m.role == "admin", task.assignee_id == request.user.id
    if request.method == "POST":
        if not (admin or own): return HttpResponseForbidden()
        task.description = request.POST.get("description", task.description)
        if request.POST.get("status") in dict(Task.STATUSES): task.status = request.POST["status"]
        if admin:
            task.title = request.POST.get("title", task.title).strip() or task.title
            task.due_date = request.POST.get("due_date") or None
            new = request.POST.get("assignee")
            new_user = User.objects.filter(pk=new, membership__project=task.project).first() if new else None
            if new_user != task.assignee:
                task.assignee = new_user
                if new_user: notify([new_user], f"{request.user.username} assigned you “{task.title}”", f"/tasks/{task.id}/", exclude=request.user)
        task.save()
        messages.success(request, "Task saved.")
        return redirect("task_detail", tid=tid)
    return render(request, "task.html", {"task": task, "project": task.project, "comments": task.comments.select_related("author"),
        "is_admin": admin, "can_edit": admin or own, "members": project_members(task.project), "statuses": Task.STATUSES})

@login_required
@require_POST
def comment_add(request, tid):
    task = get_object_or_404(Task, pk=tid)
    m = membership(request.user, task.project_id)
    text = json.loads(request.body or "{}").get("text", "").strip()
    if not text: return JsonResponse({"error": "Comment is empty."}, status=400)
    c = Comment.objects.create(task=task, author=request.user, text=text)
    admins = [x.user for x in task.project.membership_set.filter(role="admin").select_related("user")]
    notify(admins + ([task.assignee] if task.assignee else []), f"{request.user.username} commented on “{task.title}”", f"/tasks/{task.id}/", exclude=request.user)
    return JsonResponse({"id": c.id, "author": c.author.username, "text": c.text, "created": c.created.strftime("%b %d, %H:%M"), "can_delete": True})

@login_required
@require_POST
def comment_delete(request, cid):
    c = get_object_or_404(Comment.objects.select_related("task"), pk=cid)
    m = membership(request.user, c.task.project_id)
    if m.role != "admin" and c.author_id != request.user.id: return HttpResponseForbidden()
    tid = c.task_id; c.delete()
    return redirect("task_detail", tid=tid)

@login_required
def project_settings(request, pid):
    m = membership(request.user, pid)
    if m.role != "admin": return HttpResponseForbidden("Admins only.")
    p = m.project
    if request.method == "POST":
        a, uid = request.POST.get("action"), request.POST.get("user_id")
        admins = p.membership_set.filter(role="admin")
        if a == "edit":
            p.name = request.POST.get("name", p.name).strip() or p.name; p.description = request.POST.get("description", ""); p.save()
        elif a == "add":
            u = User.objects.filter(username=request.POST.get("username", "").strip()).first()
            if not u: messages.error(request, "No user with that username.")
            else:
                _, new = Membership.objects.get_or_create(user=u, project=p)
                if new: notify([u], f"{request.user.username} added you to {p.name}", f"/projects/{p.id}/", exclude=request.user)
        elif a in ("remove", "toggle") and uid:
            t = p.membership_set.filter(user_id=uid).first()
            if t and t.role == "admin" and admins.count() == 1: messages.error(request, "A project needs at least one admin.")
            elif t and a == "remove": t.delete(); Task.objects.filter(project=p, assignee_id=uid).update(assignee=None)
            elif t: t.role = "member" if t.role == "admin" else "admin"; t.save()
        return redirect("project_settings", pid=pid)
    return render(request, "settings.html", {"project": p, "memberships": p.membership_set.select_related("user"), "is_admin": True})

@login_required
def notifications(request):
    items = list(request.user.notifications.all()[:100])
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, "notifications.html", {"items": items, "unread_count": 0})
