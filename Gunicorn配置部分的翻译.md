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

#设置的参数详细说明

## 关于环境变量

如前文所讲，可以通过多种方式来设置运行参数，但是有一些参数是只能写在配置文件中，而剩下那些可以写在命令行中的参数，都是可以通过设置环境变量来设置的。

`$ GUNICORN_CMD_ARGS="--bind=127.0.0.1 --workers=3" gunicorn app:app`
##config File

### config 配置文件的地址

用法：'`-c CONFIG, --config CONFIG`'

默认值：`None`

这个参数需要在命令行中传入，或者作为应用特定配置的一部分（后面半句我也不懂）

参数要求是文件的地址，或者是python的module（我猜是类似 python:some_module.module.conf）

需要注意的是，如果参数是python的module，则参数的形式必须是python:module_name

## Server Socket 服务端口
###bind 绑定端口

用法：`-b ADDRESS, --bind ADDRESS`

默认值：`['127.0.0.1:8000']`

就是指定绑定的端口号

官方提了一个可以绑定多个地址的例子

`$ gunicorn -b 127.0.0.1:8000 -b [::1]:8000 test:app`

如上，就是将app绑到了本地的ipv4和ipv6的接口

### backlog 允许挂起的链接数

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

## Debugging 调试

### reload 重载

用法：`--reload`

默认值：`False`

更改代码的时候重启workers， 只建议在开发过程中开启。

文档推荐下载`inotify`这个包来作为重载引擎。

### reload_engine 重载的引擎

用法：`--reload-engine STRING`

默认值：`auto`

选择重载的引擎，支持的有三种，分别是`auto`，`poll`，`inotify`（需要单独安装）

### spew 显示

用法：`--spew`

默认值：`False`

启动一个能够将服务器执行过的每一条语句都打印出来的函数，然后这个选项是原子性的，就是要么全打，要么不打。

### check_config 检查配置

用法：`--check-config`

默认值：`False`

显示现在的配置。

## Server Mechanics 服务结构方面

### preload_app 预重载应用

用法：`--preload`

默认值：`False`

在worker进程被复制（派生）之前载入应用的代码。

通过预加载应用，可以节省内存资源和提高服务启动时间。当然，如果你将应用加载进worker进程这个动作延后，那么重启worker将会容易很多。

### sendfile  发送文件？

用法：`--no-sendfile`

默认值：`None`

这个值可以在环境变量设置。（文档中并没有提到这个选项是干嘛的 ）

### chdir 改变目录？

用法：`--chdir`

默认值：`/home/docs/checkouts/readthedocs.org/user_builds/gunicorn-docs/checkouts/latest/docs/source`

在载入应用之前改变目录（但是文档中没讲明白这个目录是存放什么的）

### daemon 守护进程

用法：`-D, --daemon`

默认值：`False`

以守护进程形式来运行Gunicorn进程。

其实就是将这个服务放到后台去运行。

### raw_env 设置环境变量

用法：`-e ENV, --env ENV`

默认值：`[]`

用键值对来设置环境变量。

`$ gunicorn -b 127.0.0.1:8000 --env FOO=1 test:app`

### pidfile 进程文件名

用法：`-p FILE, --pid FILE`

默认值：`None`

设置pid文件的文件名，如果不设置的话，不会创建pid文件。

### worker_tmp_dir 工作临时地址

用法：`--worker-tmp-dir DIR`

默认值：`None`

设置工作的临时文件夹的地址。

如果不设置，则会采用默认值，也就是调用`os.fchmod`来找一个地址，但是如果这个地址是disk-backed类型的文件系统，很有可能会让worker阻塞；或者如果默认的硬盘满掉了，Gunicorn也不会启动。所以文档建议我们在新挂载一个/tmpfs，然后把这个地址赋到这里来

```shell
sudo cp /etc/fstab /etc/fstab.orig
sudo mkdir /mem
echo 'tmpfs       /mem tmpfs defaults,size=64m,mode=1777,noatime,comment=for-gunicorn 0 0' | sudo tee -a /etc/fstab
sudo mount /mem
..... --worker-tmp-dir /mem
```

### user 设置用户

用法：`-u USER, --user USER`

默认值：`1005`

选择一个工作进程来作为当前用户。

这里可以输入有效的用户id或者用户名，那么在用`pwd.getpwnam(value)`的时候就可以取到这个值。如果输入`None`，则不会改变当前工作进程的用户。

###group 设置用户组

用法：`-g GROUP, --group GROUP`

默认值：`205`

与上面那个类似。

### umask 权限掩码

用法：`-m INT, --umask INT`

默认值：`0`

Gunicorn对写文件的权限。

### initgroups 设置新组

用法：`--initgroups`

默认值：`False`

设置为真的时候，会将所有worker进程加到一个指定名字的新组中。

### tmp_upload_dir 上传文件的临时存放地址

默认值：`None`

保存那些临时的请求内容。

文档讲这个选型未来可能会被移除。

如果设置了路径，要确保worker进程有权限去写。如果不设置，则会选择/tmp来存放。

### secure_scheme_headers 

默认值：`    {'X-FORWARDED-PROTOCOL': 'ssl', 'X-FORWARDED-PROTO': 'https', 'X-FORWARDED-SSL': 'on'}`

这个字典指明了哪些请求头是HTTPS请求。

### forwarded_allow_ips 

用法：`--forwarded-allow-ips STRING`

默认值：`127.0.0.1`

（这个看不懂，感觉是将那些HTTPS请求头转发到某个地址）

## Logging 日志设置

### accesslog 设置访问日志存放的地方

用法：`--access-logfile FILE`

默认值：`None`

设置为`-`就是记录到标准输出。

### access_log_format 访问日志的格式

用法：`--access-logformat STRING`

默认值：`%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"`

| Identifier  | Description                         |
| :---------- | :---------------------------------- |
| h           | remote address                      |
| l           | '-'                                 |
| u           | user name                           |
| t           | date of the request                 |
| r           | status line (e.g. GET / HTTP/1.1)   |
| m           | request method                      |
| U           | URL path without query string       |
| q           | query string                        |
| H           | protocol                            |
| s           | status                              |
| B           | response length                     |
| b           | response length or '-' (CLF format) |
| f           | referer                             |
| a           | user agent                          |
| T           | request time in seconds             |
| D           | request time in microseconds        |
| L           | request time in decimal seconds     |
| p           | process ID                          |
| {Header}i   | request header                      |
| {Header}o   | response header                     |
| {Variable}e | environment variable                |

### errorlog 设置错误日志的存放地址

用法：`--error-logfile FILE, --log-file FILE`

默认值：`-`

设置为`-`就是记录到标准输出。

### loglevel 设置日志等级

用法：`--log-level LEVEL`

默认值：`info`

debug，info，warning，error，critical

### capture_output 捕捉标准输出

用法：`--capture-output`

默认值：`False`

重定向标准输出和标准错误信息到错误日志。

### logger_class 选择处理日志的方法

用法：`--logger-class STRING`

默认值：`gunicorn.glogging.Logger`

### logconfig 日志的配置

用法：`--log-config FILE`

默认值：`None`

默认使用python标准库logging的配置文件形式。

### syslog_addr 系统日志的地址

用法：`--log-syslog-to SYSLOG_ADDR`

默认值：`udp://localhost:514`

设置发送系统日志信息的地址。

**可传递的方式**

* `unix://PATH#TYPE`对于unix的socket来讲，可以用stream或者gram形式。
* `udp://HOST:PORT`
* `tcp://HOST:PORT`

### syslog  启用系统日志来记载

用法：`--log-syslog`

默认值：`False`

把Gunicorn的日志发送到系统日志。

### syslog_prefix 系统日志的前缀 

用法：`--log-syslog-prefix SYSLOG_RREFIX`

默认值：`None`

设置每条系统日志的前缀，默认是进程的名字。

### syslog_facility 系统日志的别名

用法：`--log-syslog-facility SYSLOG_FACILITY`

默认值：`user`

### enable_stdio_inheritance  标准输入输出的继承

用法：`-R, --enable-stdio-inhertitance`

默认值：`False`

允许标准输入输出的继承，允许标准输入输出文件描述符在守护进程模式下的继承。

可以设置环境变量`PYHTONUNBUFFERED`来取消python标准输出的缓存（？）

### statsd_host

网上查到statsd的意思是单机搭建，暂时没理解是什么意思。

### statsd_prefix

不懂不懂

## Process Naming  进程命名

### proc_name 设置进程名字

用法：`-n STRING, --name STRING`

默认值：`None`

用`setproctitle`这个模块（需要额外安装）去给进程命名，方便我们在`ps`或者`top`的时候分辨出哪个是我们想要的。

不设置的时候，会用`default_proc_name`

### default_proc_name 默认的进程名

`gunicorn`

## Server Mechanics  服务架构

### pythonpath

用法：`--pythonpath STRING`

默认值：`None`

将这些路径加到python path去

e.g.`'/home/djangoprojects/myproject,/home/python/mylibrary'`

### paste

PASS

## Server Hooks 服务的钩子函数

### on_starting

```python
def on_starting(sever):
	pass
```

这个函数会在主进程初始化后被调用。

函数需要接收一个服务的实例作为参数。

### on_reload

```python
def on_reload(server):
	pass
```

函数会在接收到挂起信号而重载的时候被调用。

函数需要接收一个服务的实例作为参数。

### when_ready

```python
def when_ready(sever):
	pass
```

函数会在服务启动之后就被调用。

函数需要接收一个服务的实例作为参数。

### pre_fork

```python
def post_fork(sever, worker):
	pass
```

函数在worker派生（生成）之前被调用。

函数需要接收一个服务的实例和一个新的worker。（不懂，既然函数是在生成worker之前调用，那又怎么将这个未生成的worker传到这个函数里面来呢）

### post_fork

```python
def post_fork(sever, worker):
	pass
```

函数在worker派生（生成）之后被调用。

函数需要接收一个服务的实例和一个新的worker。

### post_worker_init

```python
def post_worker_init(worker):
	pass
```

函数在worker完成应用初始化之后被调用。

函数需要接收一个完成初始化的worker。

### work_int

```python
def worker_int(worker):
	pass
```

函数会在worker退出信号流（？）或者挂起的时候调用。

函数需要接收一个完成初始化的worker。

### work_abort

```python
def worker_abort(worker):
	pass
```

函数会在worker接收到请求异常终止信号的时候被调用。

一般这个情况发生在timeout（超时）。

函数需要接收一个完成初始化的worker。

### pre_exec

```python
def pre_exec(server):
	pass
```

函数会在新的主进程生成（派生）之前被调用。

函数需要接收一个服务的实例。

### pre_request

```python
def pre_request(worker, req):
    worker.log.debug("%s %s" % (req.method, req.path))
```

函数会在worker处理请求之前被调用。

函数需要接收这个worker，和请求作为参数。

### post_request

```python
def post_request(worker, req, environ, resp):
    pass
```

函数会在worker处理请求后被调用。

函数需要接收这个worker，和请求作为参数。

### child_exit

```python
def child_ext(sever, worker):
    pass
```

函数会在worker完全退出之后，在主进程被调用。

函数需要接收这个服务的实例，和这个worker作为参数。

### worker_exit

```python
def worker_exit(server, worker):
    pass
```

函数会在worker完全退出之后，在worker进程被调用。

函数需要接收这个服务的实例，和这个worker作为参数。

###	nworkers_changed

```python
def nworkers_changed(server, new_value, old_value):
    pass
```

函数在worker数量产生变化后被调用。

函数接收的参数为，服务的实例，新的worker数量，和变化之前的数量。

第一次的时候，old_value是None

### on_exit

```python
def on_exit(server):
    pass
```

函数在退出Gunicorn的时候被调用。

函数接收服务的实例作为参数。

## Server Mechanics

### proxy_protocol 代理协议

用法：`--proxy_protocol`

默认值：`False`

使用代理模式。

文档介绍了开启这个模式后，可以让stunnel作为HTTPS的前端，然后Gunicorn作为HTTP的服务器。（并不是很懂，暂时略过）

### proxy_allow_ips

用法：`--proxy-allow-from`

默认值：`127.0.0.1`

不懂不懂

设置`*`来禁用这个功能。

## SSL

### keyfile

用法：`--keyfile FILE`

默认值：`None`

指定ssl的key文件（那是公匙还是私匙？）

### certfile

用法：`--certfile FILE`

默认值：`None`

指定ssl的证书文件

### ssl_version

用法：`--ssl-version`

默认值：`2`

指定使用的ssl版本（也要看标准库的ssl模块是否支持）

### cert_reqs

用法：`--cert-reqs`

默认值：`0`

是否需要客户端提供证书（也要看标准库的ssl模块是否支持）

### ca_certs

用法：`--ca-certs FILE`

默认值：`None`

指定CA证书文件

### suppress_ragged_eofs

用法：`--suppress-ragged-eofs`

默认值：`True`

禁止粗鲁的停止？不是很懂

### do_handshake_on_connect

用法：`--do-handshake-on-connect`

默认值：`False`

在socket连接的时候是否执行ssl握手（也要看标准库的ssl模块是否支持）

### ciphers

用法：`--ciphers`

默认值：`TLSv1`

指定使用的加密算法（也要看标准库的ssl模块是否支持）

## Server Mechanics

### raw_paste_global_conf

pass