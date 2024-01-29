from rest_framework import serializers
from todo.models import Favourite
from todo.serializers.todo_serliazers import TodoListSerializers


class BaseFavouriteSerializer(serializers.ModelSerializer):
    todo = TodoListSerializers(read_only=True)

    class Meta:
        model = Favourite
        fields = ['id', 'todo', 'user', 'is_favorite', 'create_at', 'updated_at']


class FavouriteSerializers(BaseFavouriteSerializer):

    class Meta(BaseFavouriteSerializer.Meta):
        fields= BaseFavouriteSerializer.Meta.fields


class FavoriteSerializer(BaseFavouriteSerializer):

    class Meta(BaseFavouriteSerializer.Meta):
        fields= BaseFavouriteSerializer.Meta.fields

    def create(self, validated_data):
        user = self.context.get("user")
        favorites = Favourite.objects.create(**validated_data)
        favorites.user = user
        favorites.save()
        return favorites
