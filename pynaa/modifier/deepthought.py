from .modifier import modifier

class deepthought(modifier):
    def __setup__(self):
        self.name = 'testmod'
    def run(self):
        self.x = 42
    def output(self):
        print('the answer is', self.x)
        
