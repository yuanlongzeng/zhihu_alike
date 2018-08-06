from raven import Client

client = Client('http://ead56ac79418478aacf43b261e123f7d:b31ed00258354073b1b0ea2101cf1ac2@192.168.200.129:9000//2')

try:
    1 / 0
except ZeroDivisionError:
    client.captureException()  #发送给sentry服务器：包括错误栈

client.captureMessage('Something went fundamentally wrong')