from django.contrib import admin
from todo.models import Todo, TodoCommentary, Favourite

admin.site.register(Todo)
admin.site.register(TodoCommentary)
admin.site.register(Favourite)