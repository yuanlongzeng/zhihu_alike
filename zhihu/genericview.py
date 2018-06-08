from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import generic

from zhihu.forms import AnswerForm
from zhihu.models import Question, Answer, Comment


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
        answer = Answer.objects.filter(id=int(pk)).first()
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
        answer = Answer.objects.filter(id=int(pk)).first()
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

#评论列表
class CommentsListView(generic.ListView):
    template_name = 'commentslist.html'
    model = Comment
    context_object_name = 'comments'

    def get_queryset(self):
        answer_id = self.kwargs['pk']
        answer = Answer.objects.get(pk=int(answer_id))
        # queryset = Comment.objects.all().filter(content_object=answer).order_by('-created_date')
        queryset = Comment.objects.all().filter(content_type=7,object_id=int(answer_id),status=True).order_by('-created_date')
        return queryset

class DeleteCommentView(LoginRequiredMixin, generic.DeleteView):
    model = Comment

    def get_success_url(self):
        #logger.info('评论：{} 删除成功'.format(self.object.id))
        return self.request.META.get('HTTP_REFERER', '/')

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        comment = Comment.objects.get(pk=int(pk))
        comment.status = False
        comment.save()

        return HttpResponseRedirect(self.get_success_url())


#收藏答案
@login_required
def collect(request, pk):
    data = dict(
        r=1,
    )
    if request.method == 'POST':
        user = request.user
        pk = int(pk)
        answer = Answer.objects.filter(id=int(pk)).first()
        if answer is not None:
            ret = user.collect(answer)
            if ret is True:
                data['r'] = 0
                #logger.info('{} 收藏了： {}'.format(user, answer.id))
            else:
                pass
                #logger.error('{} 收藏失败: {}'.format(user, answer.id))
    return JsonResponse(data, status=201)


@login_required
def uncollect(request, pk):
    data = dict(
        r=1,
    )
    if request.method == 'POST':
        user = request.user
        pk = int(pk)
        answer = Answer.objects.filter(id=int(pk)).first()
        if answer is not None:
            ret = user.uncollect(answer)
            if ret is True:
                data['r'] = 0
                #logger.info('{} 取消了收藏： {}'.format(user, answer.id))
            else:
                pass
                #logger.error('{} 取消收藏失败: {}'.format(user, answer.id))
    return JsonResponse(data, status=201)

#提问相关
class CreateQuestionView(LoginRequiredMixin, generic.CreateView):
    model = Question
    fields = ['title', 'topics', 'content']

    def form_valid(self, form):
        ask = form.save(commit=False)
        ask.author = self.request.user
        ask.save()
        #logger.info('{} 提了问题：{}'.format(self.request.user, ask))
        topics = self.request.POST.get('topics_list', '')
        topics = topics.split(',')
        ask.add_topics(topics)
        return redirect('asks:detail', pk=ask.id)

    def form_invalid(self, form):
        #logger.error('提问题错误')
        return redirect('index')


class QuestionDetailView(generic.FormView, generic.DetailView):
    model = Question
    form_class = AnswerForm
    template_name = 'question_detail.html'
    context_object_name = 'ask'

    def get_context_data(self, **kwargs):
        context = super(QuestionDetailView, self).get_context_data(**kwargs)
        asks = Question.objects.all().order_by('-created_date')[:5]
        vote_list = []
        collection_list = []
        answers_list = self.object.answers.order_by('-votesup', '-created_date')
        paginator = Paginator(answers_list, 5)
        topics_list = self.object.topics.all()
        if self.request.user.is_authenticated:
            for answer in answers_list:
                if self.request.user.is_voted(answer):
                    vote_list.append(answer)
                if self.request.user.is_collected(answer):
                    collection_list.append(answer)
        context['vote_list'] = vote_list
        context['collection_list'] = collection_list
        context['asks'] = asks
        context['answers'] = paginator.page(1)
        context['topics_list'] = topics_list
        return context

    def get(self, request, *args, **kwargs):
        super(QuestionDetailView, self).get(request, *args, **kwargs)
        vote_list = []
        collection_list = []
        self.object.click()
        page = request.GET.get('page', None)
        if page is None:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

        answers_list = self.object.answers.order_by('-votes', '-create_time')
        paginator = Paginator(answers_list, 5)
        try:
            answers = paginator.page(page)
        except PageNotAnInteger or EmptyPage:
            return HttpResponseNotFound
        if self.request.user.is_authenticated:
            for answer in answers_list:
                if self.request.user.is_voted(answer):
                    vote_list.append(answer)
                if self.request.user.is_collected(answer):
                    collection_list.append(answer)
        context = dict(answers=answers, vote_list=vote_list, collection_list=collection_list, is_ask_index=True)
        return render(request, 'answerslist.html', context)


class QuestionAnswerDetailView(generic.FormView, generic.DetailView):
    model = Question
    form_class = AnswerForm
    template_name = 'question_detail.html'
    context_object_name = 'ask'

    def get_context_data(self, **kwargs):
        context = super(QuestionAnswerDetailView, self).get_context_data(**kwargs)
        asks = Question.objects.all().order_by('-created_date')[:5]
        topics_list = self.object.topics.all()
        answer = self.object.question.filter(id=self.kwargs['answer_id']).first()
        vote_list = []
        collection_list = []
        if self.request.user.is_authenticated:
            if self.request.user.is_voted(answer):
                vote_list.append(answer)
            if self.request.user.is_collected(answer):
                collection_list.append(answer)
        context['vote_list'] = vote_list
        context['collection_list'] = collection_list
        context['answers'] = answer
        context['topics_list'] = topics_list
        context['asks'] = asks
        context['answer_view'] = True
        self.object.click()
        return context


@login_required
def follow_ask(request, pk):
    data = dict(
        r=1,
    )
    if request.method == 'POST':
        user = request.user
        ask = Question.objects.filter(id=int(pk)).first()
        if ask is not None:
            ret = user.follow_ask(ask)
            if ret is True:
                data['r'] = 0
                #logger.info('{} 关注了问题： {}'.format(user, ask.id))
            else:
                pass
                #logger.error('{} 关注问题失败: {}'.format(user, ask.id))
    return JsonResponse(data, status=201)


@login_required
def unfollow_ask(request, pk):
    data = dict(
        r=1,
    )
    if request.method == 'POST':
        user = request.user
        ask = Question.objects.filter(id=int(pk)).first()
        if ask is not None:
            ret = user.unfollow_ask(ask)
            if ret is True:
                data['r'] = 0
                #logger.info('{} 取消关注了问题： {}'.format(user, ask.id))
            else:
                pass
                #logger.error('{} 取消关注问题失败: {}'.format(user, ask.id))
    return JsonResponse(data, status=201)

