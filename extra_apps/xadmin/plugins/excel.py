import xadmin
from xadmin.views import BaseAdminPlugin,ListAdminView
from django.template import loader
#excel导入
class ListImportExcelPlugin(BaseAdminPlugin):
    import_excel=False
    #是否加载插件  在XXAdmin中设置是否在管理界面显示导入选项
    def init_request(self,*args,**kwargs):
        return bool(self.import_excel)
    def block_top_toolbar(self,context,nodes):
        nodes.append(loader.render_to_string("xadmin/excel/model_list.top_toolbar.import.html", context={"context_instance":"context"}))  #注意形式
xadmin.site.register_plugin(ListImportExcelPlugin,ListAdminView)
