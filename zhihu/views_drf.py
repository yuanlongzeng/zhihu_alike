from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from zhihu.serializer import UserProfileSerializer

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