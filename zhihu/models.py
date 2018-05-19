from datetime import datetime

from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
# Create your models here.

class UserProfile(AbstractUser):
    #user = models.OneToOneField(User)  #is_active  username  email   pwd
    nick_name = models.CharField(max_length=50,blank=False,null=False,unique=True,verbose_name="昵称")
    gender = models.CharField(max_length=2,choices=(("F","女"),("M","男")),default="M",verbose_name="性别")
    desc = models.CharField(max_length=200,verbose_name="简介")
    email = models.EmailField(max_length=64, unique=True, verbose_name='邮箱')
    mobile = models.CharField(max_length=11,unique=True,verbose_name="手机号")
    photo = models.CharField(max_length=100,unique=True,verbose_name="头像")  #头像路径
    user_type = models.CharField(max_length=10,choices=(("gr","个人"),("org","机构")),default="gr")  #机构需审核
    user_status = models.CharField(max_length=10,choices=(("normal","正常"),("stop","停用"),("delete","删除")))  #用户状态
    status = models.BooleanField(default=False,verbose_name="有效标志")#用于注册激活
    #尽量正向查询，否则会做不必要的查询  所以这些关系filed应放在查询比较多的表上

    followings = models.ManyToManyField('self', related_name='funs', symmetrical=False, verbose_name='关注')
    vote_answers = models.ManyToManyField("Answer", related_name='vote_user', blank=True, verbose_name='点赞答案')
    unvote_answers = models.ManyToManyField("Answer", related_name='unvote_user', blank=True, verbose_name='反对答案')
    collections = models.ManyToManyField("Answer", related_name='collection_user', blank=True, verbose_name='收藏')  #不知回答-，文章等
    follow_questions = models.ManyToManyField("Question", related_name='followers', blank=True, verbose_name='关注问题')

    def __str__(self):
        return self.nick_name


class Message(models.Model):
    fromid = models.IntegerField()
    toid = models.IntegerField()
    content = models.TextField()
    created_date = models.DateTimeField(default=datetime.now)
    status = models.BooleanField(default=False, verbose_name="有效标志")

    def __str__(self):
        return self.created_date

class Comment(models.Model):
    content = models.TextField()
    use = models.ForeignKey(UserProfile,verbose_name="作者")
    #可能是回答或者文章 ----使用contenttype
    content_type = models.ForeignKey(ContentType, verbose_name='关联的表名称')  # 7,8 表名称
    object_id = models.IntegerField(verbose_name='关联的表中的数据行的ID')  #
    # 帮助你快速实现content_type操作--查找相应id及model（表名）
    content_object = GenericForeignKey('content_type', 'object_id')  #创建时 chaunru content_obj = answer或者article实例即可自动关联

    created_date = models.DateTimeField(default=datetime.now)
    status = models.BooleanField(default=False, verbose_name="有效标志")
    #可能有回复别人的评论  没有就是为空  否则就为那个评论的id
    reply_to = models.ForeignKey('self', related_name='replies',
                                 blank=True, null=True, on_delete=models.CASCADE, verbose_name='回复')

    def __str__(self):
        return self.content[:10]


class Question(models.Model):
    #可以追溯所有的修改者
    creator = models.OneToOneField(UserProfile,related_name="creator",verbose_name="提问者")  #停用、拉黑--删除
    editor = models.ForeignKey(UserProfile,related_name="edior",verbose_name="编辑者")  #反向查询：不能同时使用默认的表名  默认名是userprofile_set
    title = models.CharField(max_length=100)
    topics = models.ManyToManyField("Topic",blank=True,related_name="topics",verbose_name="话题")
    content = models.TextField()
    clicks = models.IntegerField()
    created_date = models.DateTimeField(default=datetime.now,verbose_name="创建时间")
    recent_modify_date = models.DateTimeField(default=datetime.now,verbose_name="修改时间")
    comment = models.ManyToManyField(Comment)
    #answer = models.ForeignKey("Answer")  #应该是由问题得到答案的多---但是问题应该只存一份即可  要是放这就得每一个回答就得新建一个问题 --冗余  而放在回答中就只需要存问题的id就可以
    status = models.BooleanField(default=False, verbose_name="有效标志")

    def __str__(self):
        return self.title

    def add_topics(self, topics):
        for t_name in topics:
            try:
                topic = Topic.objects.get(name=t_name)
            except Topic.DoesNotExist:
                topic = Topic(name=t_name)
                topic.save()
            self.topics.add(topic)  #这样就可以自动添加关系

    def click(self):
        self.clicks += 1
        self.save()

class Topic(models.Model): #toppic应该可以自由拓展
    name = models.CharField(max_length=50,unique=True)
    desc = models.CharField(max_length=100)
    parent = models.ForeignKey('self', blank=True, null=True)  #自引用，一定要允许为空，第一级是没有父话题的
    status = models.BooleanField(default=False, verbose_name="有效标志")
    created_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.name



class Answer(models.Model):
    user = models.ForeignKey(UserProfile)
    content = models.TextField()
    created_date = models.DateTimeField(default=datetime.now)
    recent_modify_date = models.DateTimeField(default=datetime.now)
    votesup = models.IntegerField(verbose_name="赞同")
    unvotes = models.IntegerField(verbose_name="反对")
    question = models.ForeignKey("Question")
    status = models.BooleanField(default=False, verbose_name="有效标志")
    # 仅用于反向查找
    conmment_list = GenericRelation("Comment")

    def __str__(self):
        return self.content[:10]

    def voteup(self):
        self.votesup += 1
        self.save()

    def votedown(self):
        self.votesup -= 1
        self.save()

    def unvote(self):
        self.unvotes +=1
        self.save()

    def cancel_unvote(self):
        self.unvotes -=1
        self.save()

class Article(models.Model):
    user = models.ForeignKey(UserProfile,verbose_name="作者") #可能会有很多  暂时先只能有一个
    title = models.CharField(max_length=200)
    content = models.TextField()
    column = models.ForeignKey("Column",verbose_name="所属专栏")
    created_date = models.DateTimeField(default=datetime.now)
    recent_modify_date = models.DateTimeField(default=datetime.now)
    conmment_list = GenericRelation("Comment")

#专栏
class Column(models.Model):
    user = models.ForeignKey(UserProfile,verbose_name="作者")
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=datetime.now)
    recent_modify_date = models.DateTimeField(default=datetime.now)


#知乎live
