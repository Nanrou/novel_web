# Gunicorn配置
##概述

### 三种配置方式

**优先级如下，越后的优先级越大**

1.框架的设置（现在只有paster在用这个）

2.配置文件（推荐使用这个）

3.命令行的赋值

### 查看配置的方法

`$ gunicorn --check-config APP_MODULE`

这个命令可以检查app的配置

#设置的参数说明

## 关于环境变量

如前文所讲，可以通过多种方式来设置运行参数，但是有一些参数是只能写在配置文件中，而剩下那些可以写在命令行中的参数，都是可以通过设置环境变量来设置的。

`$ GUNICORN_CMD_ARGS="--bind=127.0.0.1 --workers=3" gunicorn app:app`

## config 配置文件的地址

用法：'`-c CONFIG, --config CONFIG`'

默认值：`None`

这个参数需要在命令行中传入，或者作为应用特定配置的一部分（后面半句我也不懂）

参数要求是文件的地址，或者是python的module（我猜是类似 python:some_module.module.conf）

需要注意的是，如果参数是python的module，则参数的形式必须是python:module_name

## Server Socket 服务端口

用法：`-b ADDRESS, --bind ADDRESS`

默认值：`['127.0.0.1:8000']`

就是指定绑定的端口号

官方提了一个可以绑定多个地址的例子

`$ gunicorn -b 127.0.0.1:8000 -b [::1]:8000 test:app`

如上，就是将app绑到了本地的ipv4和ipv6的接口

## backlog 允许挂起的链接数

用法：`--backlog INT`

默认值：`2048`

就是设置允许挂起的连接数的最大值

官方推荐这个值设在64-2048

## Worker Processes 工作进程相关

### workers 进程数量 

用法：`-w INT, --workers INT`

默认值：`1`

设置处理请求的进程数，官方推荐的值是`2-4 x $(NUM_CORES)`，就是核心数的2-4倍，而我在网上查到的，大多数是推荐设置为核心数的两倍+1

### worker_class 进程的工作方式

用法：`-k STRING, --worker-class STRING`

默认值：`sync`

设置进程的工作方式，默认是同步，如果需要设置异步，则需要下载相关的库

**可选的参数如下：**

*`eventlet`-要求eventlet版本大于0.9.7

*`gevent`-要求gevent版本大于0.13

*`tornado`-要求tornado版本大于0.2

*`gthread`-安装了futures库的python2（意思就是python3随便用？）

*`giohttp`-python3.4以上，且aiohttp版本大于0.21.5

如果要用自己的库来处理的话，就将库添加到`gunicorn.workers`，然后再选择自己的worker

### threads 线程数

用法：`--threads INT`

默认值：`1`

就是设置开启的多线程的数目，官方也是推荐设置为核心数的两至四倍。

这个设置只对进程工作方式为Gthread的产生影响。

### worker_connections 进程链接数

用法：` --workers-connections INT`

默认值：`1000`

 设置同时链接客户端的阀值。

这个设置只对进程工作方式为Eventlet和Gevent的产生影响。

### max_requests 最大请求数

用法：`--max-requests INT`

默认值：`0`

设置一个进程处理完max_requests次请求后自动重启

就是设置这个可以预防内存泄漏，如果不设置的话，则进程不会自动重启

### max_requests_jitter 最大请求数的变化值

用法：`--max-requests-jitter INT`

默认值：`0`

这个的作用与max_requests的几乎一致，只是后者设置为固定值，而这个的值是randint(0, max_requests_jitter)

###timeout 过期时间

用法：`-t INT, --timeout INT`

默认值：`30`

worker沉默（不工作?不发送response?）超过timeout秒之后就会重启

对于同步worker来讲，官方建议用default值就可以了，当然，如果你确认这个值不满足你的要求的时候，可以调高。

对于异步worker来讲，worker仍然会继续通信(发response?)，而且对于处理一个独立的请求来讲，它是与所需的时间无关。（个人理解为，对于异步来讲，这个参数是没有意义的）

### graceful_time 优雅的timeout（后置的timeout）

用法：`--graceful-timeout INT`

默认值：`30`

其实就是当worker接收到重启的信号之后，再工作这么久才真正执行重启。

### keepalive 链接存活时间

用法：`--keep-alive INT`

默认值：`2`

发送完一个response后，等待keepalive秒再关闭连接

建议设置为1-5

## Security 安全方面的设置

### limit_request_line 设置请求行的最大长度

用法：`--limit-request-line INT`

默认值：`4094`

允许设置的值为0-8190,0是不限制的意思。

文档中提到这个参数可以防止DDOS攻击，具体我还要去查一下为什么。

(网上查到的request-line其实就是请求的第一行，后面的都是键值对。因为RESTful的要求，这个第一行会包含挺多的信息)

### limit_request_fields 设置请求头的字段的范围

用法：`--limit-request-fields INT`

默认值：`100`

（这个我并不是很懂）

### limit_request_field_size 设置请求头的大小

用法：`--limit-request-field_size INT`

默认值：`8190`

