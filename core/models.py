from django.conf import settings
from django.db import models
U = settings.AUTH_USER_MODEL

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(U, on_delete=models.CASCADE, related_name="created_projects")
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Membership(models.Model):
    ROLES = [("admin", "Admin"), ("member", "Member")]
    user = models.ForeignKey(U, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLES, default="member")
    class Meta: unique_together = ("user", "project")

class Task(models.Model):
    STATUSES = [("todo", "To Do"), ("doing", "In Progress"), ("done", "Done")]
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default="todo")
    assignee = models.ForeignKey(U, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(U, on_delete=models.CASCADE, related_name="+")
    created = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(U, on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["created"]

class Notification(models.Model):
    recipient = models.ForeignKey(U, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created"]
