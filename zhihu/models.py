import hashlib
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
# Create your models here.
from django.utils import timezone


class UserProfile(AbstractUser):
    #user = models.OneToOneField(User)  #is_active  username  email   pwd  课程--课程详情可以使用OneToOneField【ForeignKey:-章--节】
    nick_name = models.CharField(max_length=50,blank=False,null=False,unique=True,verbose_name="昵称")
    # 这种不需要使用CharField  可以节省空间   但是可能直接看数据库的话就会不直观
    gender = models.CharField(max_length=2,choices=(("F","女"),("M","男")),default="M",verbose_name="性别")
    desc = models.CharField(max_length=200,verbose_name="简介")
    email = models.EmailField(max_length=64, unique=True, verbose_name='邮箱')
    mobile = models.CharField(max_length=11,unique=True,verbose_name="手机号")
    photo = models.ImageField(upload_to="media/%Y/%m/%d/",verbose_name="头像",default="media/1.jpg")  #头像路径
    user_type = models.CharField(max_length=10,choices=(("gr","个人"),("org","机构")),default="gr",verbose_name="类别")  #机构需审核
    user_status = models.CharField(max_length=10,choices=(("normal","正常"),("stop","停用"),("delete","删除")),verbose_name="用户状态",default="normal")  #用户状态
    status = models.BooleanField(default=False,verbose_name="有效标志")#用于注册激活
    #尽量正向查询，否则会做不必要的查询  所以这些关系filed应放在查询比较多的表上

   #当定义模型通过中间模型与其自身产生的多对多关系时，你必须使用参数symmetrical=False
    followings = models.ManyToManyField('self', related_name='funs', symmetrical=False,blank=True,null=True, verbose_name='关注')  #关注了--followee
    followers = models.ManyToManyField('self', related_name='follower', symmetrical=False,blank=True,null=True, verbose_name='关注者')
    vote_answers = models.ManyToManyField("Answer", related_name='vote_user', blank=True,null=True, verbose_name='点赞答案')
    unvote_answers = models.ManyToManyField("Answer", related_name='unvote_user', blank=True,null=True, verbose_name='反对答案')
    collections = models.ManyToManyField("Answer", related_name='collection_user', blank=True,null=True, verbose_name='收藏')  #不知回答-，文章等
    follow_questions = models.ManyToManyField("Question", related_name='followers', blank=True,null=True, verbose_name='关注问题')
    follow_topics = models.ManyToManyField("Topic",related_name="user",blank=True,null=True,verbose_name="关注换题")


    def __str__(self):
        return self.nick_name

    def update(self, data):
        self.nickname = data.get('nickname')
        self.gender = data.get('gender')
        self.desc = data.get('desc')
        self.photo = data.get('photo')
        self.save()

    @property
    def get_image_url(self):
        if self.photo is None or self.photo is '':
            url = 'https://cdn.v2ex.com/gravatar/{id}?default=monsterid&size=256'
            image_id = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
            return url.format(id=image_id)
        else:
            return self.photo

    def voteup(self, answer):
        if self.is_voted(answer):
            return False
        self.vote_answers.add(answer)
        answer.voteup()
        return True

    def votedown(self, answer):
        if not self.is_voted(answer):
            return False
        self.vote_answers.remove(answer)
        answer.votedown()
        return True

    def is_voted(self, answer):
        return self.vote_answers.filter(id=answer.id).exists()
    #收藏相关
    def collect(self, answer):
        if self.is_collected(answer):
            return False
        self.collections.add(answer)
        return True

    def uncollect(self, answer):
        if not self.is_collected(answer):
            return False
        self.collections.remove(answer)
        return True

    def is_collected(self, answer):
        return self.collections.filter(id=answer.id).exists()

    def follow(self, user_id):
        try:
            follow_user = UserProfile.objects.get(id=user_id)
        except User.DoesNotExist:
            return False
        if self.id != follow_user.id and not self.is_following(follow_user):
            self.followings.add(follow_user)
            return True

    def unfollow(self, user_id):
        try:
            follow_user = UserProfile.objects.get(id=user_id)
        except User.DoesNotExist:
            return False
        if self.is_following(follow_user):
            self.followings.remove(follow_user)
            return True
    def is_following(self, user):
        return self.followings.filter(id=user.id).exists()

    def follower(self, user_id):
        try:
            follow_user = UserProfile.objects.get(id=user_id)
        except User.DoesNotExist:
            return False
        if self.id != follow_user.id and not self.is_follower(follow_user):
            self.followers.add(follow_user)
            return True

    def unfollower(self, user_id):
        try:
            follow_user = UserProfile.objects.get(id=user_id)
        except User.DoesNotExist:
            return False
        if self.is_follower(follow_user):
            self.followers.remove(follow_user)
            return True
    def is_follower(self, user):
        return self.followers.filter(id=user.id).exists()

    def follow_ask(self, ask):
        if self.is_follow_ask(ask):
            return False
        self.follow_questions.add(ask)
        return True

    def unfollow_ask(self, ask):
        if not self.is_follow_ask(ask):
            return False
        self.follow_questions.remove(ask)
        return True

    def is_follow_ask(self, ask):
        return self.follow_questions.filter(id=ask.id).exists()


class Message(models.Model):
    fromid = models.ForeignKey(UserProfile,related_name="from_user",verbose_name="发送者")
    toid = models.ForeignKey(UserProfile,related_name="to_user",verbose_name="接受者")
    content = models.TextField(verbose_name="内容")
    created_date = models.DateTimeField(default=timezone.now,verbose_name="创建时间")
    status = models.BooleanField(default=True, verbose_name="有效标志")

    class Meta:
        verbose_name = "私信"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.created_date

class Comment(models.Model):
    content = models.TextField()
    user = models.ForeignKey(UserProfile,verbose_name="作者")
    #可能是回答或者文章 ----使用contenttype 自动关联
    content_type = models.ForeignKey(ContentType, verbose_name='关联的表名称',blank=True,null=True)  # 7,8 表名称
    object_id = models.IntegerField(verbose_name='关联的表中的数据行的ID',blank=True,null=True)  #
    # 帮助你快速实现content_type操作--查找相应id及model（表名）  不会生成该列  但是创建数据时传入一个表的实例给该变量即可  上面两个不用传值
    content_object = GenericForeignKey('content_type', 'object_id')  #创建时 chaunru content_obj = answer或者article实例即可自动关联

    created_date = models.DateTimeField(default=timezone.now,verbose_name="创建时间")
    status = models.BooleanField(default=True, verbose_name="有效标志")
    #可能有回复别人的评论  没有就是为空  否则就为那个评论的id
    reply_to = models.ForeignKey('self', related_name='replies',
                                 blank=True, null=True, on_delete=models.CASCADE, verbose_name='回复',help_text="单独回复某答案或文章则为空，表示在下面回复某人的评论")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content[:10]

    def answer(self):
        return self.content_object.filter()


class Question(models.Model):
    #可以追溯所有的修改者
    creator = models.ForeignKey(UserProfile,related_name="creator",verbose_name="提问者")  #停用、拉黑--删除
    editor = models.ForeignKey(UserProfile,related_name="edior",verbose_name="编辑者")  #反向查询：不能同时使用默认的表名  默认名是userprofile_set
    title = models.CharField(max_length=100,verbose_name="标题")
    topics = models.ManyToManyField("Topic",blank=True,related_name="questions",verbose_name="话题")
    content = models.TextField(verbose_name="内容")
    clicks = models.IntegerField(default=0,verbose_name="点击数")
    created_date = models.DateTimeField(default=timezone.now,verbose_name="创建时间")
    recent_modify_date = models.DateTimeField(default=timezone.now,verbose_name="修改时间")

    comment_list = GenericRelation("Comment", verbose_name="评论列表")
    #comment = models.ManyToManyField(Comment,blank=True,null=True,verbose_name="评论")
    #answer = models.ForeignKey("Answer")  #应该是由问题得到答案的多---但是问题应该只存一份即可  要是放这就得每一个回答就得新建一个问题 --冗余  而放在回答中就只需要存问题的id就可以
    status = models.BooleanField(default=True, verbose_name="有效标志")

    class Meta:
        verbose_name = "提问"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def add_topics(self, topics):
        for t_name in topics:
            try:
                topic = Topic.objects.get(name=t_name)
            except Topic.DoesNotExist:
                topic = Topic(name=t_name,desc=t_name)
                topic.save()
            self.topics.add(topic)  #这样就可以自动添加关系

    def click(self):
        self.clicks += 1
        self.save()

    def answer_cnt(self):
        return self.answers.filter(status=True).count()

class Topic(models.Model): #toppic应该可以自由拓展
    name = models.CharField(max_length=50,unique=True,verbose_name="话题名称")
    desc = models.CharField(max_length=100,verbose_name="描述")
    parent = models.ForeignKey('self', blank=True, null=True,verbose_name="父话题")  #自引用，一定要允许为空，第一级是没有父话题的
    status = models.BooleanField(default=True, verbose_name="有效标志")
    created_date = models.DateTimeField(default=timezone.now,verbose_name="创建时间")

    class Meta:
        verbose_name = "话题"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name



class Answer(models.Model):
    user = models.ForeignKey(UserProfile)
    content = models.TextField()
    content_text = models.TextField(default=content)
    created_date = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    recent_modify_date = models.DateTimeField(default=timezone.now, verbose_name="修改时间")
    votesup = models.IntegerField(default=0,verbose_name="赞同")
    unvotes = models.IntegerField(default=0,verbose_name="反对")
    question = models.ForeignKey("Question",verbose_name="回答",related_name="answers") #注意related_name
    status = models.BooleanField(default=True, verbose_name="有效标志")
    # 仅用于反向查找
    comment_list = GenericRelation("Comment",verbose_name="评论列表")

    class Meta:
        verbose_name = "回答"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content[:10]

    def voteup(self):
        self.votesup += 1
        self.save()

    def votedown(self):
        self.votesup -= 1
        self.save()

    def comment_cnt(self):
        return self.comment_list.filter(status=True).count()


class Article(models.Model):
    user = models.ForeignKey(UserProfile,verbose_name="作者") #可能会有很多  暂时先只能有一个
    title = models.CharField(max_length=200)
    content = models.TextField()
    column = models.ForeignKey("Column",verbose_name="所属专栏")
    created_date = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    recent_modify_date = models.DateTimeField(default=timezone.now, verbose_name="修改时间")
    comment_list = GenericRelation("Comment",blank=True,null=True,verbose_name="评论列表")
    status = models.BooleanField(default=True, verbose_name="有效标志")

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

#专栏
class Column(models.Model):
    user = models.ForeignKey(UserProfile,verbose_name="作者")
    name = models.CharField(max_length=100,verbose_name="专栏名称")
    desc = models.CharField(max_length=200,verbose_name="简介")
    created_date = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    recent_modify_date = models.DateTimeField(default=timezone.now, verbose_name="修改时间")
    status = models.BooleanField(default=True, verbose_name="有效标志")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "专栏"
        verbose_name_plural = verbose_name


#知乎live
