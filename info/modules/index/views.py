from info import redis_store
from . import index_blu


@index_blu.route('/')
def index():
    # 向redis中保存一个值 name ning

    redis_store.set("name","ning")
    return 'index'