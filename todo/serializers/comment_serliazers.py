from rest_framework import serializers
from todo.models import TodoCommentary
from todo.serializers.todo_serliazers import TodoListSerializers


class CommentsSerializers(serializers.ModelSerializer):
    todo = TodoListSerializers(read_only=True)

    class Meta:
        model = TodoCommentary
        fields= ['id', 'todo', 'user', 'comment', 'create_at']


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TodoCommentary
        fields= ['id', 'todo', 'user', 'comment', 'create_at']
    
    def create(self, validated_data):
        comment = TodoCommentary.objects.create(**validated_data)
        comment.user = self.context.get('user')
        comment.save()
        return comment

    def update(self, instance, validated_data):
        instance.comment = validated_data.get("comment", instance.title)
        instance.save()
        return instance