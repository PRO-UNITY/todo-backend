from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from todo.models import Favourite
from utils.auth_views import user_permission
from utils.expected_fields import check_required_key
from utils.error_response import (
    internal_server_response,
    bad_request_response,
    success_response,
    success_created_response,
)
from todo.serializers.favourite_serliazers import (
    FavouriteSerializers,
    FavoriteSerializer
)


class FavouritesViews(APIView):

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_401_UNAUTHORIZED)
        objects_list = Favourite.objects.filter(user=request.user.id).order_by('-id')
        serializers = FavouriteSerializers(objects_list, many=True, context={"request": request})
        return success_response(serializers.data)

    @user_permission
    @swagger_auto_schema(request_body=FavoriteSerializer)
    def post(self, request, user_id=None):
        if user_id is None:
            return internal_server_response()
        
        valid_fields = {'id', 'todo', 'user', 'is_favorite', 'create_at', 'updated_at'}
        unexpected_fields = check_required_key(request, valid_fields)
        if unexpected_fields:
            return bad_request_response(f"Unexpected fields: {', '.join(unexpected_fields)}")

        serializers = FavoriteSerializer(data=request.data, context={"user": user_id})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return success_created_response(serializers.data)
        return bad_request_response(serializers.errors)


class FavouriteView(APIView):

    @user_permission
    def delete(self, request, pk, user_id=None):
        if user_id is None:
            return internal_server_response()
        queryset = get_object_or_404(Favourite, todo=pk, user=user_id)
        queryset.delete()
        return success_response("delete success")