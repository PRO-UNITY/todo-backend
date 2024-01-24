from django.urls import path
from todo.views.todo_views import (
    TodoViews,
    TodoView,
)
from todo.views.favourite_views import (
    FavouritesViews,
    FavouriteView
)
from todo.views.comment_views import (
    CommentsViews,
    CommentView
)

urlpatterns =  [
    path('todos', TodoViews.as_view()),
    path('todo/<int:pk>', TodoView.as_view()),
    path('favourites', FavouritesViews.as_view()),
    path('favourite/<int:pk>', FavouriteView.as_view()),
    path('comments', CommentsViews.as_view()),
    path('comment/<int:pk>', CommentView.as_view()),

]
