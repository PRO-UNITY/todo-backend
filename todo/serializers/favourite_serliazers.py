from rest_framework import serializers
from todo.models import Favourite
from todo.serializers.todo_serliazers import TodoListSerializers


class FavouriteSerializers(serializers.ModelSerializer):

    class Meta:
        model = Favourite
        fields = ['id', 'todo', 'user', 'is_favorite', 'create_at', 'updated_at']


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favourite
        fields = ['id', 'todo', 'user', 'is_favorite', 'create_at', 'updated_at']

    def create(self, validated_data):
        user = self.context.get("user")
        favorites = Favourite.objects.create(**validated_data)
        favorites.user = user
        favorites.save()
        return favorites
