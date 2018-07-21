from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers
from .models import Answer, Question, Comment, Topic


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = "__all__"
        depth = 1

class AnswerCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"
        depth = 1

class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"
        #depth = 1
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        #depth = 1

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"
        #depth = 1

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):

    #fav = serializers.StringRelatedField(many=True)
    password = serializers.CharField(
        style={'input_type': 'password'},  #用户输入时以* 显示
        label="密码",
        write_only=True, #write_only ：y用户post过来后不会序列化返回的字段 如密码 read_only:后台产生返回的字段：如订单号
    )
    #links = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = "__all__"
        #fields = ("username", "gender", "email", "password", "views", "links", "fav")

    # def get_links(self, obj):
    #     request = self.context['request']
    #     return reverse('user-detail', kwargs={'pk': obj.pk},
    #                    request=request)