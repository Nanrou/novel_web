# -*- coding:utf-8 -*-

import time
from functools import wraps


def time_clock(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('start {fun_name}({fun_args}{fun_kwargs})'
              .format(fun_name=func.__name__, fun_args=args or '', fun_kwargs=kwargs or ''))
        start_time = time.time()
        res = func(*args, **kwargs)
        print('--{}-- cost: {}'.format(func.__name__, my_round(time.time() - start_time)))
        return res
    return wrapper


def my_round(num):
    if num < 60:
        n = round(num, 3)
        if n < 1:
            return 'biu~'
        return '{} s'.format(n)
    elif num < 3600:
        return '{} min {} s'.format(int(num/60), round(num % 60, 2))


@time_clock
def test():
    time.sleep(3)

if __name__ == '__main__':
    test()