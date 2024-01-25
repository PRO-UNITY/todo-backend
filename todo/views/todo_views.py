from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from todo.pagination import StandardResultsSetPagination, Pagination

from authen.renderers import UserRenderers
from todo.models import Todo
from todo.serializers.todo_serliazers import (
    TodoListSerializers,
    TodoCrudSerializers
)


class TodoViews(APIView, Pagination):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    serializer_class = TodoListSerializers

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        queryset = Todo.objects.all().order_by('-id')
        page = super().paginate_queryset(queryset)
        if page is not None:
            serializer = super().get_paginated_response(self.serializer_class(page, many=True, context={"request": request}).data)
        else:
            serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=TodoCrudSerializers)
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        expected_fields = set(["title", "discription", "user", "create_at", "updated_at",])
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields
        if unexpected_fields:
            error_message = (f"Unexpected fields in request data: {', '.join(unexpected_fields)}")
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        serializers = TodoCrudSerializers(data=request.data, context={"user": request.user})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class TodoView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def get(self, request, pk):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        todo=pk
        objects_list = get_object_or_404(Todo, id=pk)
        serializers = TodoListSerializers(objects_list, context={"request": request, 'todo': todo})
        return Response(serializers.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=TodoCrudSerializers)
    def put(self, request, pk):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        expected_fields = set(["title", "discription", "user", "create_at", "updated_at",])
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields
        if unexpected_fields:
            error_message = (f"Unexpected fields in request data: {', '.join(unexpected_fields)}")
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        serializers = TodoCrudSerializers(context={"user": request.user, "request": request}, instance=Todo.objects.filter(id=pk)[0], data=request.data, partial=True,)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response({"error": "update error data"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        queryset = Todo.objects.get(id=pk)
        queryset.delete()
        return Response({"message": "Success"}, status=status.HTTP_200_OK)