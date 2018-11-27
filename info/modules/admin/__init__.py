# 新闻详情模块的蓝图

from flask import Blueprint, session, redirect, request, url_for

# 创建蓝图对象
admin_blu = Blueprint("admin",__name__)


from . import views

@admin_blu.before_request
def check_admin():
    # if 不是管理员就跳转到主页
    is_admin = session.get("is_admin",False)
    if not is_admin and not request.url.endswith(url_for('admin.login')):
        return redirect('/')




