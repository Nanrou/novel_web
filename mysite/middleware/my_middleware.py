# -*- coding:utf-8 -*-

from django.shortcuts import redirect


MOBILE_UA = ("Mobile", "PlayStation", "Wii")


class MobileMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        先判断请求是从主域名还是从二级域名进来的，然后再判断客户端UA和目标模版是否一致
        :param request:
        :return:
        """
        host = request.META.get('HTTP_HOST')
        if 'www.' in host:
            host = host.replace('www.', '')

        if host.startswith('m'):
            if any(ua for ua in MOBILE_UA if ua in request.META['HTTP_USER_AGENT']):
                return self.get_response(request)
            else:
                # new_path = host[2:] + request.path
                new_path = 'http://www.superxiaoshuo.com' + request.path
                return redirect(new_path)

        else:
            if any(ua for ua in MOBILE_UA if ua in request.META['HTTP_USER_AGENT']):
                # new_path = 'm.' + host + request.path
                new_path = 'http://m.superxiaoshuo.com' + request.path
                return redirect(new_path)
            else:
                return self.get_response(request)
