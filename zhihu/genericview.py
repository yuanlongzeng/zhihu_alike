from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import generic, View

from zhihu.forms import AnswerForm
from zhihu.models import Question, Answer, Comment, UserProfile


# 首页功能：推（活跃用户）--拉模式、推荐
class IndexView(LoginRequiredMixin, generic.DetailView):
    template_name = 'index.html'

    def get_object(self, queryset=None):
        union_list = []
        paginator = ''
        if self.request.user.is_active:
            for follower in self.request.user.followings.all():
                union_list.append(follower.answer_set.all())
            #关注问题的所有回答  话题
            for ask in self.request.user.follow_questions.all():
                union_list.append(ask.answers.all())
            answers_list = self.request.user.answer_set.all().union(*union_list).order_by('-created_date') #合并不重复qs
            paginator = Paginator(answers_list, 10)
        else:
            #拉模式：sql查询
            for follower in self.request.user.followings.all():
                union_list.append(follower.answers.all())
            for ask in self.request.user.follow_questions.all():
                union_list.append(ask.answers.all())
            answers_list = self.request.user.answer_set.all().union(*union_list).order_by('-created_date') #合并不重复qs
            paginator = Paginator(answers_list, 10)
        return paginator

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        asks = Question.objects.all().order_by('-created_date')[:5]
        vote_list = []
        collection_list = []
        context['asks'] = asks
        context['answers'] = self.object.page(1)
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
            for answer in answers:
                if self.request.user.is_voted(answer):
                    vote_list.append(answer)
                if self.request.user.is_collected(answer):
                    collection_list.append(answer)
        context = dict(answers=answers, vote_list=vote_list, collection_list=collection_list)
        return render(request, 'answerslist.html', context)

    def handle_no_permission(self):
        return redirect('explore')
class FollowUserView(LoginRequiredMixin,View):
    def get(self,request,userid):
        data = dict(r=0)
        user = UserProfile.objects.get(id=int(userid))
        if request.user.is_following(user):
            request.user.unfollow(user.id)
        else:
            request.user.follow(user.id)
            data['r'] = 1
        return JsonResponse(data)



class ExploreView(generic.DetailView):
    template_name = 'index.html'

    def get_object(self, queryset=None):
        answers_list = Answer.objects.filter(status=True).order_by('-created_date')
        paginator = Paginator(answers_list, 10)
        return paginator

    def get_context_data(self, **kwargs):
        context = super(ExploreView, self).get_context_data(**kwargs)
        asks = Question.objects.all().order_by('-created_date')[:5]
        vote_list = []
        collection_list = []
        #用户感兴趣的
        context['asks'] = asks
        context['answers'] = self.object.page(1)  #调用get_object回去数据
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
        super(ExploreView, self).get(request, *args, **kwargs)
        page = request.GET.get('page', None)
        if page is None:  #首次访问，取第一页的数据
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)
        page = int(page)
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
        #返回此页渲染的答案html
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

class CommentCreateView(LoginRequiredMixin,generic.CreateView):
    model = Comment
    fields = ['content']
    def form_valid(self, form):
        try:
            answer = Answer.objects.filter(id=self.kwargs['pk']).first()
        except Answer.DoesNotExist:
            #logger.error('评论错误: 答案 {} 不存在'.format(self.kwargs['pk']))
            return redirect(self.request.META.get('HTTP_REFERER', '/'))
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.content_object = answer
        reply_id = self.request.POST.get('reply_id', 0)
        if reply_id =='':
            reply_id = 0
        try:
            reply = Comment.objects.filter(id=reply_id).first()
        except ValueError:
            #logger.error('回复评论错误： reply_id = {}'.format(reply_id))
            return redirect(self.request.META.get('HTTP_REFERER', '/'))
        comment.reply_to = reply
        comment.save()
        #logger.info('{} 评论了 {} 的回答'.format(comment.author, answer.author))
        return redirect(self.request.META.get('HTTP_REFERER', '/'))

    def form_invalid(self, form):
        #logger.error('comment error')
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


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
        ask.user = self.request.user
        ask.save()
        #logger.info('{} 提了问题：{}'.format(self.request.user, ask))
        topics = self.request.POST.get('topics_list', '')
        topics = topics.split(',')
        ask.add_topics(topics)
        return redirect('question_detail', pk=ask.id)

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
        answers_list = self.object.answers.filter(status=True).order_by('-votesup', '-created_date')
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
            return self.render_to_response(context) #首次进入

        answers_list = self.object.answers.order_by('-votesup', '-created_date')
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
        context = dict(answers=answers, vote_list=vote_list, collection_list=collection_list, is_ask_index=True,user=request.user)
        return render(request, 'answerslist.html', context)  #自定义渲染--下一页的答案


class QuestionAnswerDetailView(generic.FormView, generic.DetailView):
    model = Question
    form_class = AnswerForm
    template_name = 'question_detail.html'
    context_object_name = 'ask'

    def get_context_data(self, **kwargs):
        context = super(QuestionAnswerDetailView, self).get_context_data(**kwargs)
        asks = Question.objects.all().order_by('-created_date')[:5]
        topics_list = self.object.topics.all()
        answer = self.object.answers.filter(id=int(self.kwargs['answer_id'])).first()
        vote_list = []
        collection_list = []
        if self.request.user.is_authenticated:
            if self.request.user.is_voted(answer):
                vote_list.append(answer)
            if self.request.user.is_collected(answer):
                collection_list.append(answer)
        context['vote_list'] = vote_list
        context['collection_list'] = collection_list
        context['answer'] = answer
        context['topics_list'] = topics_list
        context['asks'] = asks
        context['answer_view'] = True
        #context['user'] = self.request.user
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

#回答
class CreateAnswerView(LoginRequiredMixin, generic.CreateView):
    model = Answer
    fields = ['content', 'content_text']

    def form_valid(self, form):
        ask_id = self.kwargs['pk']
        ask = Question.objects.filter(id=int(ask_id)).first()
        user = self.request.user
        if ask is not None:
            answer = form.save(commit=False)
            answer.question = ask
            answer.user = user
            answer.save()
            #logger.info('{} 回答了问题 : {}'.format(self.request.user, answer))
        return redirect(self.request.META.get('HTTP_REFERER', '/'))

    def form_invalid(self, form):
        #logger.error('answer error')
        return redirect(self.request.META.get('HTTP_REFERER', '/'))

class DeleteAnswerView(LoginRequiredMixin, generic.DeleteView):
    model = Answer

    def get_success_url(self):
        #logger.info('答案：{} 删除成功'.format(self.object.id))
        return self.request.META.get('HTTP_REFERER', '/')

    def delete(self, request, *args, **kwargs):

        success_url = self.get_success_url()
        pk = kwargs.get('pk')
        answer = Answer.objects.get(pk=int(pk))
        answer.status = False
        answer.save()
        return HttpResponseRedirect(success_url)


