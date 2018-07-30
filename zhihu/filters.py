import django_filters

from zhihu.models import Answer


class AnswerFilter(django_filters.rest_framework.FilterSet):
    content = django_filters.CharFilter(name="content",lookup_expr="icontains")
    min_votesup = django_filters.NumberFilter(name="votesup",lookup_expr="gte")
    max_votesup = django_filters.NumberFilter(name="votesup", lookup_expr="lte")

    class Meta:
        model = Answer
        fields = ["content","min_votesup","max_votesup"]