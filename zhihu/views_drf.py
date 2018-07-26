from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from zhihu.models import UserProfile
from zhihu.serializer import UserProfileSerializer, UserRegisterSerializer, UserFavSerializer, \
    UserFlowQuestionSerializer

User = get_user_model()

class BasePagination(PageNumberPagination):

    """
    分页
    """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
class UserProfileViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    """
    用户
    """

    serializer_class = UserProfileSerializer
    pagination_class = BasePagination

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)

class UserRegisterViewset(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    """
    用户注册
    """

    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        re_dict = serializer.data
        payload = jwt_payload_handler(user) #
        re_dict["token"] = jwt_encode_handler(payload)
        re_dict["username"] = user.username
        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

class UserFavViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin, mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):

    """
    用户收藏回答
    """

    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication) #JSONWebTokenAuthentication-- JWT验证  SessionAuthentication --session验证
    serializer_class = UserFavSerializer
    # lookup_field = "answer"

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)

class UserFlowQuestionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                              mixins.CreateModelMixin, mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):

    """
    用户关注问题
    """

    serializer_class = UserFlowQuestionSerializer
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = "question"

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save()  #获取序列化后的数据 同时会调用create将获取的数据存储
        question = instance.question
        question.flow()

    def perform_destroy(self, instance):
        question = instance.question
        question.cancel_flow()
        question.delete()