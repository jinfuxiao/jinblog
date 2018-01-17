# -*- coding:utf-8 -*-

from django.core.cache import cache

from redis import Redis
from post.models import Article


# 页面缓存粒度比较粗，为了添加过期时间->带参数的装饰器

def page_cache(timeout):
    def wrap1(view_func):
        def wrap2(request, *args, **kwargs):
            # key的设置：唯一标识这个页面-资源->URL
            key = 'J_PAGES-%s' % request.get_full_path()
            # cache中获取 response
            response = cache.get(key)
            if response is not None:
                print('return from cache')
                # 如果有，直接返回response
                return response
            else:
                print('return from view')
                # 如果没有，执行view函数
                response = view_func(request, *args, **kwargs)
                # 把结果保存在cache中
                cache.set(key, response, timeout)
                return response
        return wrap2
    return wrap1

# 统计量--这是一个很广泛的使用
# 思路：这是一个排行榜，我们用到redis的SortedSet。首先1，要文章阅读一次，点击量增1。2，显示
# 实现功能1，写在阅读文章详情的view函数中，用到rds.zincrby('a_click', aid)，点击一次对应文章的点击量+1
# 实现功能2，展示写在首页，用到的数据是文章本身和点击量
# 实现功能2，排序-zrevrange()-找到aid-搜索对应的文章对象-和点击量结合-返回
# 2.1, 查看并处理zrevrange()的返回值
# 2.2, 通过aid'批量'搜到这10篇文章
# 2.3, 文章本身的点击量的结合，构造返回的数据
# 2.4, 返回
# 如果是comment的评论数量，显示评论最多的文章列表
# 增加评论数量是在comment函数中，执行一次post提交，评论一次评论量+1，所以comment函数中调用record_click()函数
# 显示是在首页，评论量top5
# 实现功能1，
# 需要改造一下record_count()函数，变成装饰器
# 问题1，装饰器怎么写？
# 问题2，多个装饰器的书写顺序

# 实现功能2，构造一个函数，get_comments_n_articles(number)，排序-通过aid找到对应的文章，和评论量结合返回
# 2.1，article_comments = rds.zrevrange('a_comment', 0, number, withscores=True)
# 2.2, ...


rds = Redis(host='10.0.112.84', port=6379, db=9)

def record_count(count=1):
    def wrap1(view_func):
        def wrap2(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            key = 'a_' + view_func.__name__
            aid = int(request.GET.get('aid', 0))
            rds.zincrby(key, aid, count)
            return response
        return wrap2
    return wrap1

#
# def record_click(aid, count=1):
#     # 设计count字段是为了以后批量修改--前瞻性
#     rds.zincrby('a_click', aid, count)



def get_top_n_articles(number):

    # 这个函数要实现功能：从[(b'aid', 点击量（浮点型)）,...]-->[[Article(aid), 点击量（int）]

    # 1.排序，倒序zrevrange()显示,，返回的是[(b'aid', 点击量浮点型)]
    # (b'aid').decode('utf8')->转换为aid或者  int（）
    article_clicks = rds.zrevrange('a_click', 0, number, withscores=True)
    article_clicks = [[int(aid), int(click)] for aid, click in article_clicks]

    # 2.取出文章的实例和对应的点击量--批量操作
    # in_bulk()取出的是字典，无序
    # bulk_create()批量创建
    # aid for aid, _ in article_clicks 等价于 d[0] for d in article_clicks
    articles = Article.objects.in_bulk(aid for aid, _ in article_clicks)
    # 返回的是{aid:<Article object(aid) ...>,...}

    # 我们现在又的是article_clicks=[aid,点击量]和articles={aid:<Article object(aid) ...>,...}
    # 我们需要构造的是
    # [
    #     [Article(aid), 点击量],
    #     ...
    # ]
    # 所以相当于把[]中每一条数据的aid换成{}中的aid对应的值
    # 虽然articles中的aid的顺序和article_clicks中aid的顺序是不一样的，但是经过取值操作，还是排序了
    for data in article_clicks:
        a_id = data[0]
        data[0] = articles[a_id]

    return article_clicks
