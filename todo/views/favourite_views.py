from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from authen.renderers import UserRenderers
from todo.models import Favourite
from todo.serializers.favourite_serliazers import (
    FavouriteSerializers,
    FavoriteSerializer
)


class FavouritesViews(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        objects_list = Favourite.objects.filter(user=request.user.id).order_by('-id')
        serializers = FavouriteSerializers(objects_list, many=True, context={"request": request})
        return Response(serializers.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=FavoriteSerializer)
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        expected_fields = set(['id', 'todo', 'user', 'is_favorite', 'create_at', 'updated_at'])
        received_fields = set(request.data.keys())
        unexpected_fields = received_fields - expected_fields
        if unexpected_fields:
            error_message = (f"Unexpected fields in request data: {', '.join(unexpected_fields)}")
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
        serializers = FavoriteSerializer(data=request.data, context={"user": request.user})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class FavouriteView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        queryset = get_object_or_404(Favourite, todo=pk, user=request.user.id)
        queryset.delete()
        return Response({"message": "Success"}, status=status.HTTP_200_OK)  