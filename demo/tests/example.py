
class BaseClass:
    def __init__(self):
        print("Start BaseClass.__init__()")
        self.x = 1
        print(f"val of x: {self.x}")
        print("End BaseClass.__init__()")

class Tokenizer(BaseClass):
    """Tokenize text"""
    def __init__(self, text):
        print('Start Tokenizer.__init__()')
        super().__init__()
        print(f"val of x: {self.x + 1}")
        self.tokens = text.split()
        print('End Tokenizer.__init__()')

class TextReader(BaseClass):
    """Read text"""
    def __init__(self, text):
        print('Start TextReader.__init__()')
        super().__init__()
        print(f"val of x: {self.x + 1}")
        self.raw_text = text
        print('End TextReader.__init__()')


class WordCounter(Tokenizer):
    """Count words in text"""
    def __init__(self, text):
        print('Start WordCounter.__init__()')
        super().__init__(text)
        print(f"val of x: {self.x + 2}")
        self.word_count = len(self.tokens)
        print('End WordCounter.__init__()')


class Vocabulary(Tokenizer):
    """Find unique words in text"""
    def __init__(self, text):
        print('Start Vocabulary.__init__()')
        super().__init__(text)
        print(f"val of x: {self.x + 2}")
        self.vocab = set(self.tokens)
        print('End Vocabulary.__init__()')


class TextDescriber(WordCounter, Vocabulary, TextReader):
    """Describe text with multiple metrics"""
    def __init__(self, text):
        print('Start TextDescriber.__init__()')
        super().__init__(text)
        print(f"val of x: {self.x + 3}")
        print('End TextDescriber.__init__()')


td = TextDescriber('row row row your boat')
print('--------')
print(TextDescriber.mro())
print("--------")
print(td.tokens)
print(td.vocab)
print(td.word_count)

# twc = WordCounter("row row row your boat")
# print("-----------")
# print(WordCounter.mro())
# print(twc.raw_text)
# print(twc.tokens)
# print(twc.word_count)