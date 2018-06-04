from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.views import generic

from zhihu.models import Question, Answer


class IndexView(generic.DetailView):
    template_name = 'index.html'

    def get_object(self, queryset=None):
        answers_list = Answer.objects.order_by('-created_date')
        paginator = Paginator(answers_list, 10)
        return paginator

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        asks = Question.objects.all().order_by('-created_date')[:5]
        vote_list = []
        collection_list = []
        context['asks'] = asks
        context['answers'] = self.object.page(1)
        context['explore'] = True
        if self.request.user.is_authenticated:
            for answer in self.object.page(1):
                if self.request.user.is_voted(answer):
                    vote_list.append(answer)
                if self.request.user.is_collected(answer):
                    collection_list.append(answer)
        context['vote_list'] = vote_list
        context['collection_list'] = collection_list
        return context

    def get(self, request, *args, **kwargs):
        super(IndexView, self).get(request, *args, **kwargs)
        page = request.GET.get('page', None)
        if page is None:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

        vote_list = []
        collection_list = []
        try:
            answers = self.object.page(page)
        except PageNotAnInteger or EmptyPage:
            return HttpResponseNotFound
        if self.request.user.is_authenticated:
            for answer in self.object.page(page):
                if self.request.user.is_voted(answer):
                    vote_list.append(answer)
                if self.request.user.is_collected(answer):
                    collection_list.append(answer)
        context = dict(answers=answers, vote_list=vote_list, collection_list=collection_list)
        return render(request, 'answerslist.html', context)

class ShowAnswerView(generic.DetailView):
    model = Answer

    def get(self, request, *args, **kwargs):
        data = dict(r=1)
        try:
            answer = Answer.objects.get(id=kwargs['pk'])
        except Answer.DoesNotExist:
            return JsonResponse(data)
        data['r'] = 0
        data['content'] = answer.content
        data['create_time'] = answer.created_date.date()
        return JsonResponse(data)


#答案点赞、反对
@login_required
def vote_up(request, pk):
    data = dict(
        r=1,
    )
    if request.method == 'POST':
        user = request.user
        answer = Answer.objects.filter(id=pk).first()
        if answer is not None:
            ret = user.voteup(answer)
            if ret is True:
                data['r'] = 0
                data['count'] = answer.votesup
                #logger.info('{} 赞同了： {}'.format(user, answer.id))
            else:
                pass
                #logger.error('{} 赞同失败: {}'.format(user, answer.id))
    return JsonResponse(data, status=201)


@login_required
def vote_down(request, pk):
    data = dict(
        r=1,
    )
    if request.method == 'POST':
        user = request.user
        answer = Answer.objects.filter(id=pk).first()
        if answer is not None:
            ret = user.votedown(answer)
            if ret is True:
                data['r'] = 0
                data['count'] = answer.votesup
                #logger.info('{} 取消了赞： {}'.format(user, answer.id))
            else:
                #logger.error('{} 取消赞失败: {}'.format(user, answer.id))
                pass
    return JsonResponse(data, status=201)