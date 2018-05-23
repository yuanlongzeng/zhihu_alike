from django.contrib import admin

# Register your models here.
import xadmin
from xadmin import forms, views

# Register your models here.这样可以在后台进行显示、管理
# class PostAdmin(admin.ModelAdmin):
#     list_display = ['title', 'created_time', 'modified_time', 'category', 'user']
#
#
# admin.site.register(Post, PostAdmin)
# admin.site.register(Category)
# admin.site.register(Tag)

class BaseSetting:
    enable_themes = True  # 设置主题
    use_bootswatch = True


class GlobalSetting:
    site_title = "XX社交知识分享网站"  # 设置主题
    site_footer = "xx social website for knowledge"
    menu_style = "accordion"  #每个app下的model可展开-收缩



xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView,GlobalSetting)

#xadmin.site.register(UserProfile, UserProfileAdmin)
