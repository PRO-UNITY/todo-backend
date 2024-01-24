from django.db import models
from django.contrib.auth.models import User


class Todo(models.Model):
    title = models.CharField(max_length=250)
    discription = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "todo_table"


class TodoCommentary(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, null=True, blank=True, related_name='comment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.CharField(max_length=250, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comment_table"


class Favourite(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, null=True, blank=True, related_name="todo")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "favourite_table"