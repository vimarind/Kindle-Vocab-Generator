import json


class Word:

    def __init__(self, text):
        self.text = text
        self.definitions = []
        self.examples = []
        self.synonyms = []
        self.audio_file = ''
        self.tags = []
        self.rank = 0

    def save_to_json(self, filename):
        with open(filename, 'w') as file:
            file.write(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__,
                           self.text)

    def __eq__(self, other):
        if isinstance(other, Word):
            return self.text == other.text
        elif isinstance(other, str):
            return self.text == other
        return False