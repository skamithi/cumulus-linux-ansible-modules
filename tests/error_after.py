"""
From http://igorsobreira.com/2013/03/17/testing-infinite-loops.html
"""


class ErrorAfter(object):
    '''
    Callable that will raise `CallableExhausted`
    exception after `limit` calls

    '''

    def __init__(self, limit):
        self.limit = limit
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls > self.limit:
            raise CallableExhausted


class CallableExhausted(Exception):
    pass
