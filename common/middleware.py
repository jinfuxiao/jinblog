# coding: utf-8
import time
from django.utils.deprecation import MiddlewareMixin

# 限制访问频次
# 访问频率每秒2次，[每次收到请求的时间 间隔<=0.5s,错误] 正确的是一秒之内接收到3次访问，time.sleep(1)
# 如果是5次，第6次请求的时间戳减去第1次的时间戳,如果在1s之内说明接收超过了5次
# 收到request之后，执行view之前进行判断

# 定义全局变量，作为一个配置
MAX_REQUSET_PER_SECOND = 2

class RequestBlockingMiddleware(MiddlewareMixin):
    # def process_view(self,request):
    def process_request(self, request):
        # 记录每次接收request的时间，并且和发送请求的用户绑定
        # 保存位置？->缓存,同时为了区分用户-->*session*(db:耗时；全局变量：无法分布式运算；日志文件：无法分布式运算，文件分开保存；)
        # 保存形式？进行计算的是最新接收request时间戳和前面第n个请求的时间戳（3-1）；需要维持的时间个数，限制n次即保存n个时间戳->列表

        # 取出当下请求的时间
        now = time.time()
        # 获取历史时间队列
        request_queue = request.session.get('request_queue', [])
        # 判断长度
        if len(request_queue) < MAX_REQUSET_PER_SECOND:
            # 小于额定队列长度，放行
            request_queue.append(now)
            # 用session保存这个队列
            request.session['request_queue'] = request_queue
        else:
            # 达到额定队列长度,进行判断时间间隔
            time0 = request_queue[0]
            if (now - time0) < 1:
                time.sleep(10)

            # 无论睡不睡都要操作以下代码
            # 同时把此次请求加进队列，删除队列中的第一个元素，实现滚动更新，保证队列的额定长度
            # 加入的是睡过10秒之后的时间，不是请求的时间now
            request_queue.append(time.time())
            request.session['request_queue'] = request_queue[1:]
