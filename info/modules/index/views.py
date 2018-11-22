from flask import render_template, current_app, session

from info import redis_store
from info.models import User
from . import index_blu


@index_blu.route('/')
def index():
    """
    显示首页
    1.如果用户已经登录,将当前登录用户的数据传到模板中,供模板显示
    :return:
    """

    # 取到用户id
    user_id = session.get("user_id",None)
    user = None
    if user_id:
        # 尝试查询用户的模型
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    data = {
        "user":user.to.dict() if user else None
    }



    return render_template('news/index.html',data = data)


# 再打开网页的时候,浏览器会默认去请求根路径+favicon.ico网站标签的小图标
# send_static_file 是flask 去查找指定的静态文件所调用的方法
@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
