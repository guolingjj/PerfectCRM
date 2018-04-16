class F():
    def __init__(self):
        self.prev=0
        self.cur=1
    def __iter__(self):#写上他,返回自己
        return self
    def next(self):
        self.prev, self.cur=self.cur,self.cur+ self.prev
        print(self.cur)
        return self.cur
# f=F()
# for i in range(10):
#     f.next()




# def fib():
#     prev, curr = 0, 1
#     while True:
#         yield curr
#         print('sb')
#         prev, curr = curr, curr + prev
# f = fib()
# print(next(f))
# import time
# def out(func):
#     def inner(*args,**kwargs):
#         st=time.time()
#         func(*args,**kwargs)
#         et=time.time()
#         print('所用时间:',et-st)
#     return inner
# @out
# def xxx(N):
#     req=[]
#     for i in range(N):
#         req.append(i*i)
#     return req
#
# xxx(1,2)
# class Fu(object):
#     _instance=None
#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             super().__new__(cls, *args, **kwargs)
#         return cls._instance
#
# f=Fu()
# f2=Fu()
# print(f == f2)
from functools import wraps

def Out(cls):
    instance={}
    @wraps(cls)
    def inner(*args,**kwargs):
        if cls not in instance:
            instance[cls]=cls(*args,**kwargs)
        return instance[cls]
    return inner
@Out
class myc:
    a=1

m=myc()
m2=myc()
print(m == m2)