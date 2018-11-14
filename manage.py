from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    """项目的配置"""
    DEBUG = True

    #为Mysql添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)

# 加载配置
app.config.from_object(Config)
db = SQLAlchemy(app)


@app.route('/')
def index():
    return 'index2222'


if __name__ == '__main__':
    app.run(debug=True)
