import hashlib
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
# Create your models here.
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django_redis import get_redis_connection


class UserProfile(AbstractUser):
    #user = models.OneToOneField(User)  #is_active  username  email   pwd  课程--课程详情可以使用OneToOneField【ForeignKey:-章--节】
    nick_name = models.CharField(max_length=50,blank=False,null=False,unique=True,verbose_name="昵称")
    # 这种不需要使用CharField  可以节省空间   但是可能直接看数据库的话就会不直观
    gender = models.CharField(max_length=2,choices=(("F","女"),("M","男")),default="M",verbose_name="性别")
    desc = models.CharField(max_length=200,verbose_name="简介")
    email = models.EmailField(max_length=64, unique=True, verbose_name='邮箱')
    mobile = models.CharField(max_length=11,blank="",verbose_name="手机号")
    photo = models.ImageField(upload_to="media/%Y/%m/%d/",verbose_name="头像",default="media/1.jpg")  #头像路径
    user_type = models.CharField(max_length=10,choices=(("gr","个人"),("org","机构")),default="gr",verbose_name="类别")  #机构需审核
    user_status = models.CharField(max_length=10,choices=(("normal","正常"),("stop","停用"),("delete","删除")),verbose_name="用户状态",default="normal")  #用户状态
    status = models.BooleanField(default=False,verbose_name="有效标志")#用于注册激活
    #尽量正向查询，否则会做不必要的查询  所以这些关系filed应放在查询比较多的表上

   #当定义模型通过中间模型与其自身产生的多对多关系时，你必须使用参数symmetrical=False
    followings = models.ManyToManyField('self', related_name='funs', symmetrical=False,blank=True,null=True, verbose_name='关注')  #关注了--followee
    #related_name 字段名 模型中的函数名 三者不能有任何一个重名的  否则会报错
    followers = models.ManyToManyField('self', related_name='my_followers', symmetrical=False,blank=True,null=True, verbose_name='关注者')
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
    #点赞
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

    #点踩
    def un_voteup(self, answer):
        if self.un_is_voted(answer):
            return False
        self.unvote_answers.add(answer)
        answer.un_voteup()
        return True

    def un_votedown(self, answer):
        if not self.un_is_voted(answer):
            return False
        self.unvote_answers.remove(answer)
        answer.un_votedown()
        return True

    def un_is_voted(self, answer):
        return self.unvote_answers.filter(id=answer.id).exists()
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
    #话题
    def follow_topic(self, topic):
        if self.is_follow_topic(topic):
            return False
        self.follow_topics.add(topic)
        return True

    def unfollow_topic(self, topic):
        if not self.is_follow_topic(topic):
            return False
        self.follow_topics.remove(topic)
        return True

    def is_follow_topic(self, topic):
        return self.follow_topics.filter(id=topic.id).exists()
#创建用户的同时添加UserMessageCounter
@receiver(post_save,sender=UserProfile)
def createUserNotificationCounter(instance,created,**kwargs):
    if created:
        UserMessageCounter.objects.create(pk=instance.id)

class Message(models.Model):
    '''
    关注自己，回答有新评论、赞、反对等，
    有人回复自己的评论
    关注的问题有新回答
    (评论点赞、点踩)
    '''
    Message_TYPE = (
        ('F', 'follower'), #关注自己
        ('U', 'upvote'),   #赞回答
        ('UC', 'upvoteComment'), # 评论点赞 ---
        ('T', 'thanks'), # 感谢回答--
        ('C', 'comment'),  # 回答有新评论
        ('RQ', 'replyFromQuestion'),
        ('RF', 'replyFromFollowee'),
        ('UF', 'upvoteFromFollowee'),
        ('IF', 'interestFromFollowee'),  #关注问题
        ('CF', 'createdFromFollowee'),
    )
    from_user = models.ForeignKey(UserProfile,related_name="from_user",verbose_name="发送者")
    to_user = models.ForeignKey(UserProfile,related_name="to_user",verbose_name="接受者")
    content = models.TextField(verbose_name="内容")
    created_date = models.DateTimeField(default=timezone.now,verbose_name="创建时间")
    status = models.BooleanField(default=True, verbose_name="有效标志")
    has_read = models.BooleanField(default=False)
    msg_type = models.CharField(max_length=2,choices=Message_TYPE,default='F')

    #各种类型的消息
    msg_question = models.ForeignKey('Question', related_name='notify_question', blank=True, null=True,verbose_name="关注问题有新回答")
    #notify_reply = models.ForeignKey(Reply, related_name='notify_reply', blank=True, null=True)
    msg_comment = models.ForeignKey('Comment', related_name='notify_comment', blank=True, null=True,verbose_name="评论提醒")

    class Meta:
        verbose_name = "私信"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.created_date

class UserMessageCounter(models.Model):
    user_id = models.IntegerField(primary_key=True)
    unread_count = models.IntegerField(default=0)

    def __str__(self):
        return "user unread notifications count: id={0},count={1}".format(self.user_id, self.unread_count)

RK_NOTIFICATIONS_COUNTER = 'redis_pending_counter_changes'
#更新消息数量
def update_unread_count(user_id,count):
#     UserMessageCounter.objects.filter(pk=user_id).update(unread_count = F('unread_count') + count)
    con = get_redis_connection('default')
    con.zincrby(RK_NOTIFICATIONS_COUNTER, str(user_id), count)

# 信号
@receiver(post_save, sender=Message,dispatch_uid="uid")
def incr_notifications_counter(instance, created, **kwargs):
    print('CREATE: ', instance.from_user, instance.to_user, instance.msg_type)
    if created and not instance.has_read:
        update_unread_count(instance.to_user.id, 1)
    else:
        return

@receiver(post_delete, sender=Message)
def decr_notifications_counter(instance, **kwargs):
    print('DELETE: ', instance.from_user, instance.to_user, instance.msg_type)
    if not instance.has_read:
        update_unread_count(instance.to_user.id, -1)
    else:
        return

#创建消息
def createMessages(from_user,to_user,notify_type,topic=None,question=None,reply=None,comment=None):
    '''
    创建的时候就会触发信号--更新redis中的数据--执行命令同步到数据库UserMessageCount中
    :param from_user:
    :param to_user:
    :param notify_type:
    :param topic:
    :param question:
    :param reply:
    :param comment:
    :return:
    '''
    if from_user == to_user:
        return
    if notify_type == 'F':
        Message.objects.get_or_create(
                            from_user=from_user,
                            to_user=to_user,
                            msg_type=notify_type,
                            )
    elif notify_type == 'U' or notify_type == 'T':
        Message.objects.get_or_create(
                            from_user=from_user,
                            to_user=to_user,
                            msg_type=notify_type,
                            msg_question=question,

                            )

    elif notify_type == 'UC' or notify_type == 'C':
        Message.objects.get_or_create(
                            from_user=from_user,
                            to_user=to_user,
                            msg_type=notify_type,
                            msg_question=question,
                            msg_comment=comment,
                            )
    elif notify_type == 'RQ' or notify_type == 'RF' \
      or notify_type == 'UF':
        for user in to_user:
            if from_user == to_user:
                continue
            Message.objects.get_or_create(
                            from_user=from_user,
                            to_user=user,
                            msg_type=notify_type,
                            msg_question=question,

                            )
    elif notify_type == 'CF' or notify_type == 'IF':
        for user in to_user:
            if from_user == to_user:
                continue
            Message.objects.get_or_create(
                            from_user=from_user,
                            to_user=user,
                            msg_type=notify_type,
                            msg_question=question,
                            )

def deleteMessages(from_user,to_user,notify_type,topic=None,question=None,reply=None,comment=None):
    if notify_type == 'F':
        notification = Message.objects.get(
                            from_user=from_user,
                            to_user=to_user,
                            msg_type=notify_type,
                                            )
        notification.delete()
    elif notify_type == 'U' or notify_type == 'T':
        notification = Message.objects.get(
                            from_user=from_user,
                            to_user=to_user,
                            msg_type=notify_type,
                            msg_question=question,

                                            )
        notification.delete()
    elif notify_type == 'UC' or notify_type == 'C':
        notification = Message.objects.get(
                            from_user=from_user,
                            to_user=to_user,
                            msg_type=notify_type,
                            msg_question=question,

                            msg_comment=comment,
                            )
        notification.delete()
    elif notify_type == 'RQ' or notify_type == 'RF' \
      or notify_type == 'UF':
        for user in to_user:
            notification = Message.objects.get(
                                from_user=from_user,
                                to_user=user,
                                msg_type=notify_type,
                                msg_question=question,

                                )
            notification.delete()
    elif notify_type == 'CF' or notify_type == 'IF':
        for user in to_user:
            notification = Message.objects.get(
                                from_user=from_user,
                                to_user=user,
                                msg_type=notify_type,
                                msg_question=question,
                                                )
            notification.delete()

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
    follower = models.ManyToManyField(UserProfile,blank=True,null=True,related_name="my_follow_question",verbose_name="问题关注者")
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

    def un_voteup(self):
        self.unvotes += 1
        self.save()

    def un_votedown(self):
        self.unvotes -= 1
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


# django的模型类管理器:重写或自定义一些操作模型的方法，如重写all方法只取有效数据或者自定义批量插入对重复数据进行过滤：
#示例：
# class MessageManager(models.Manager):
#
#     def bulk_insert_ignore(self,fields,value_list,print_sql=False):
#         """主要解决mysql重复数据过滤的问题 加入了 ignore 关键词"""
#         db_table = self.model._meta.db_table
#         values_sql="(%s)" %(','.join([" %s " for _ in range(len(fields))]))
#         base_sql = "INSERT IGNORE INTO %s (%s) VALUES " % (db_table, ",".join(fields))
#         sql = """%s %s""" % (base_sql, values_sql)
#         from django.db import connection,transaction
#         cursor = connection.cursor()
#         try:
#             f=cursor.executemany(sql, value_list)
#             k=transaction.commit()
#             #import pdb;pdb.set_trace()
#             return True
#         except Exception as e:
#             print (e)
#             return False
#
# class Message(models.Model):
#     op_type=(("add_answer",0),("follow_question",1),("evaluate_answer",2),("reply_answer",3),("reply_comment",4),("follow_user",5),)
#     status=models.IntegerField()
#     addtime=models.DateTimeField(auto_now_add=True)
#     message_type=models.IntegerField()
#     contentid=models.IntegerField()
#     content=models.TextField()
#     from_user=models.ForeignKey(User,related_name='mfuser')
#     to_user=models.ForeignKey(User,related_name='mtuser')
#     objects=models.Manager()
#     messageobjects=MessageManager()  #使用：Message.messageobjects.bulk_insert_ignore(fields,Message_list)
#
#     class Meta:
#         unique_together = ('contentid', 'message_type','to_user')
#         ordering=["-addtime"]