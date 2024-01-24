from rest_framework import serializers
from todo.models import Todo, Favourite, TodoCommentary
from authen.serializers import UserInformationSerializer


class TodoCommentarySerializer(serializers.ModelSerializer):
    user = UserInformationSerializer(read_only=True)

    class Meta:
        model = TodoCommentary
        fields = '__all__'


class TodoListSerializers(serializers.ModelSerializer):
    favorite_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()
    user = UserInformationSerializer(read_only=True)
    comment = TodoCommentarySerializer(many=True, read_only=True)
    class Meta:
        model = Todo
        fields = ['id', 'title', 'comment', 'comment_count', 'discription', 'user', 'favorite_count', 'favorite', 'create_at', 'updated_at']
    
    def get_favorite(self, obj):
        user = self.context.get("user")
        user_favorities = Favourite.objects.filter(user=user)
        if user_favorities.filter(todo__id=obj.id).exists():
            return True
        return False
    
    def get_favorite_count(self, obj):
        user = self.context.get("user")
        user_favorites = Favourite.objects.filter(todo=obj)
        return user_favorites.count()
    
    def get_comment_count(self, obj):
        user = self.context.get("user")
        user_favorites = TodoCommentary.objects.filter(todo=obj)
        return user_favorites.count()

class TodoCrudSerializers(serializers.ModelSerializer):

    class Meta:
        model = Todo
        fields = ['id', 'title', 'discription', 'user', 'create_at', 'updated_at']

    def create(self, validated_data):
        todo = Todo.objects.create(**validated_data)
        todo.user = self.context.get('user')
        todo.save()
        return todo

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.discription = validated_data.get("discription", instance.discription)
        instance.save()
        return instance