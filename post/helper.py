# -*- coding:utf-8 -*-

from django.core.cache import cache

# 页面缓存粒度比较粗，为了添加过期时间->带参数的装饰器

# ll
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

