from django. db.models.signals import post_save,post_delete
from django.dispatch import receiver


class UserFav(object):
    pass


@receiver(post_save, Sender=UserFav)
def create_userfav(sender, instance=None, created=False, **kwargs):
    if created:  #首次创建
        answer =instance.answer
        answer.fav_num += 1
        answer.save()

@receiver(post_delete, Sender=UserFav)
def create_userfav(sender, instance=None, created=False, **kwargs):
    answer = instance.answer
    answer.fav_num -= 1
    answer.save()
