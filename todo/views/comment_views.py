from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from todo.models import Todo, TodoCommentary
from todo.pagination import StandardResultsSetPagination, Pagination
from utils.expected_fields import check_required_key
from utils.auth_views import user_permission
from utils.error_response import (
    internal_server_response,
    bad_request_response,
    success_response,
    success_created_response,
)
from todo.serializers.comment_serliazers import (
    CommentsSerializers,
    CommentSerializer
)


class CommentsViews(APIView, Pagination):
    pagination_class = StandardResultsSetPagination
    serializer_class = CommentsSerializers

    @user_permission
    def get(self, request, user_id=None):
        if user_id is None:
            return internal_server_response()
        queryset = TodoCommentary.objects.filter(user=user_id).order_by('-id')
        page = super().paginate_queryset(queryset)
        if page is not None:
            serializer = super().get_paginated_response(self.serializer_class(page, many=True, context={"request": request}).data)
        else:
            serializer = self.serializer_class(queryset, many=True)
        return success_response(serializer.data)

    @user_permission
    @swagger_auto_schema(request_body=CommentSerializer)
    def post(self, request, user_id=None):
        if user_id is None:
            return internal_server_response("Invalid user data")
        valid_fields = {'id', 'todo', 'user', 'comment', 'create_at'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")
        serializers = CommentSerializer(data=request.data, context={"user": user_id})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_created_response(serializers.data)
        return bad_request_response(serializers.errors)


class CommentView(APIView):

    @user_permission
    def get(self, request, pk, user_id=None):
        if user_id is None:
            return internal_server_response()
        objects_list = get_object_or_404(Todo, id=pk)
        serializers = CommentsSerializers(objects_list, context={"request": request})
        return success_response(serializers.data)

    @user_permission
    @swagger_auto_schema(request_body=CommentSerializer)
    def put(self, request, pk, user_id=None):
        if user_id is None:
            return internal_server_response()
        valid_fields = {'id', 'todo', 'user', 'comment', 'create_at'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")
        serializers = CommentSerializer(context={"user": request.user, "request": request}, instance=Todo.objects.filter(id=pk)[0], data=request.data, partial=True,)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_created_response(serializers.data)
        return success_response(serializers.errors)

    @user_permission
    def delete(self, request, pk, user_id=None):
        if user_id is None:
            return internal_server_response()
        queryset = TodoCommentary.objects.get(id=pk)
        queryset.delete()
        return success_response("delete success")