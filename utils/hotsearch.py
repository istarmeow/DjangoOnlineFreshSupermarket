# 使用redis来记录热搜，并根据分数进行排序

import redis  # 首先pip install redis安装好


class HotSearch(object):
    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=6, decode_responses=True)
        self.r_conn = redis.Redis(connection_pool=pool)  # 创建连接池，并进行连接
        self.name = 'keyword:hot:search'

    def save_keyword(self, keyword):
        # 如果关键字已存在，分数+1
        if self.r_conn.zscore(self.name, keyword):
            self.r_conn.zincrby(self.name, amount=1, value=keyword)
        else:
            self.r_conn.zadd(self.name, {keyword: 1})
        # print(self.r_conn.zrevrange(self.name, 0, 5, withscores=True))

    def get_hotsearch(self):
        hot_5 = self.r_conn.zrevrange(self.name, 0, 5)
        # 得到一个关键字的列表
        return hot_5
