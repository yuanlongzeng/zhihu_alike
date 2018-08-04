from raven import Client

client = Client('https://<key>:<secret>@sentry.io/<project>')

try:
    1 / 0
except ZeroDivisionError:
    client.captureException()  #发送给sentry服务器：包括错误栈