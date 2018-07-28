from datetime import datetime,timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Answer, Question, Comment, Topic, UserProfile


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
class VerifyCode:
    pass
class UserRegisterSerializer(serializers.ModelSerializer):

    """
    用户注册序列化
    """

    mobile = serializers.CharField(
            label="手机号", required=True, allow_blank=False,
            validators=[UniqueValidator(queryset=User.objects.all(),
                                        message="手机号已注册")])

    code = serializers.CharField(required=True, write_only=True, max_length=4,
                                 min_length=4, label="验证码", error_messages={
                                    "blank": "请输入验证码",
                                    "required": "请输入验证码",
                                    "max_length": "验证码格式错误",
                                    "min_length": "验证码格式错误"
                                 })
    username = serializers.CharField(
            label="用户名", required=True, allow_blank=False,
            validators=[UniqueValidator(queryset=User.objects.all(),
                                        message="用户名已存在")])
    password = serializers.CharField(
            min_length=6, label="密码", write_only=True,
            style={'input_type': 'password'},
            error_messages={
                "min_length": "密码最少为6位"
            }
            )

    def validate_code(self, code):
        verify_records = VerifyCode.objects.filter(
                mobile=self.initial_data["mobile"]
            ).order_by("-created")
        if verify_records:
            last_record = verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5,
                                                                  seconds=0)
            if five_mintes_ago > last_record.created:
                raise serializers.ValidationError("验证码已过期")
            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")
        else:
            raise serializers.ValidationError("验证码错误")

    def validate(self, attrs):
        del attrs["code"]
        return attrs

    def create(self, validated_data):
        user = super(UserRegisterSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])  # AbstractBaseUser方法，调用的make_pasword
        user.save()
        return user

    class Meta:
        model = User
        fields = ("mobile", "code", "username", "password")

class UserFavSerializer(serializers.ModelSerializer):

    """
    User Fav Serializer
    """
    # 从其他模型取额外的必要字段 而不用depth取一些不必要的信息
    # question_id = serializers.CharField(source="answer.question.id", read_only=True)
    # question_title = serializers.CharField(source="answer.question.title", read_only=True)
    # answer_vote = serializers.CharField(source="answer.vote", read_only=True)
    # answer_text = serializers.CharField(source="answer.text", read_only=True)
    # author_name = serializers.CharField(source="answer.author", read_only=True)
    # user = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )

    class Meta:
        model = UserProfile
        fields = ("collections","id")#"__all__"
        depth = 1

class UserFlowQuestionSerializer(serializers.ModelSerializer):

    """
    User Flow Question Serializer
    """

    # user = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )  隐藏字段

    class Meta:
        model = UserProfile
        fields = ('id', 'follow_questions')
