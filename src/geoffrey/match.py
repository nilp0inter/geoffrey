from fnmatch import fnmatch


class Match:
    def __init__(self, expression):
        self.expression = expression

    def __call__(self, data):
        return fnmatch(data, self.expression)
