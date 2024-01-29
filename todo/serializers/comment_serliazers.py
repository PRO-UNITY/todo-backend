from rest_framework import serializers
from todo.models import TodoCommentary
from todo.serializers.todo_serliazers import TodoListSerializers


class BaseCommentSerializer(serializers.ModelSerializer):
    todo = TodoListSerializers(read_only=True)

    class Meta:
        model = TodoCommentary
        fields = ['id', 'todo', 'user', 'comment', 'create_at']


class CommentsSerializers(BaseCommentSerializer):
    
    class Meta(BaseCommentSerializer.Meta):
        fields= BaseCommentSerializer.Meta.fields


class CommentSerializer(BaseCommentSerializer):

    class Meta(BaseCommentSerializer.Meta):
        fields= BaseCommentSerializer.Meta.fields
    
    def create(self, validated_data):
        comment = TodoCommentary.objects.create(**validated_data)
        comment.user = self.context.get('user')
        comment.save()
        return comment

    def update(self, instance, validated_data):
        instance.comment = validated_data.get("comment", instance.title)
        instance.save()
        return instance