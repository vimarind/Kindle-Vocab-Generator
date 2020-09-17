import re, json, requests, csv, time, os
from core.Word import Word


def __safe_list_get(l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default


def load_vocabulary(filename):
    extract_highlights = re.compile(r"<div class='noteText'>(.*)<\/h3>")
    get_words = re.compile(r'^[\s\.\,\;\:\!\?\'\’\"\“\”\—\-]*([a-zA-Z-]+)[\’s]*[\s\.\,\;\:\!\?\'\’\"\“\”\—\-]*$')
    file = open(filename, 'r')
    extracted = []
    words = {}
    others = []

    for line in file.readlines():
        result = extract_highlights.search(line)
        if result is not None:
            extracted.append(result.group(1))
    file.close()

    for highlight in extracted:
        result = get_words.search(highlight)
        if result is not None:
            word = result.group(1).lower()
            if word not in words.keys():
                words[word] = Word(word)
        else:
            others.append(highlight)

    return words, others


def populate_words(words, oxford_api, words_api=None, allow_messages=True):
    """
    Iterates the words dictionary, populating the data of each object using the OxfordAPI and with the optional
    WordsAPI to be used in the case the word is not found in the Oxford dictionary.
    :param words: The dictionary containing the words to be populated.
    :param oxford_api: The OxfordAPI object.
    :param words_api: The WordsAPI object.
    :param allow_messages: Boolean value to indicate if messages should be displayed in the console.
    :return: A list of those words that have not been found.
    """
    incomplete_words = []
    i = 0
    for word in words.values():
        if allow_messages:
            print(i, ': ', word.text)
            i = i + 1
        success = oxford_api.get_word(word)
        if not success and words_api:
            definitions = words_api.definitions(word.text)
            if definitions and definitions.get('definitions', False):
                for definition in definitions.get('definitions', list()):
                    word.definitions.append(definition.get('definition', None))
    for item in words.items():
        key = item[0]
        word = item[1]
        if len(word.definitions) == 0:
            incomplete_words.append(key)
    return incomplete_words


def write_to_tsv(words, filename):
    """
    Writes the list of words to a file in the format of a Tab Separated Values (TSV).
    :param words: The list of words to be saved.
    :param filename: The name of the file to be written.
    """
    with open(filename, 'wt') as file:
        tsv_writer = csv.writer(file, delimiter='\t')
        for word in words.values():
            row = [word.text, __safe_list_get(word.definitions, 0, ' ')]
            for example in word.examples[:5]:
                row.append(example)
            for _ in range(5 - len(word.examples)):
                row.append(' ')
            row.append(', '.join(word.synonyms))
            if word.synonyms == 0:
                row.append(' ')
            row.append(('[sound:' + word.text + '.mp3]') if word.audio_file is not '' else ' ')
            tsv_writer.writerow(row)


def write_incomplete_words(incomplete_words, filename):
    """
    Write the list of incomplete words (those that do not have definitions) to a text file.
    :param incomplete_words: The array of word strings.
    :param filename: The name of the file to be written.
    """
    with open(filename, 'w') as file:
        for word in incomplete_words:
            file.write(word + '\n')


def get_audios(words, path):
    """
    Pulls all the audios from internet and saves them to the provided path.
    :param words: The list of words already populated.
    :param path: The path where the audios will be stored.
    :return:
    """
    i = 0
    for word in words.values():
        if word.audio_file is not '':
            if not os.path.exists(path + word.text + '.mp3'):
                with open(path + word.text + '.mp3', 'wb') as file:
                    success = False
                    while not success:
                        try:
                            r = requests.get(word.audio_file, allow_redirects=True)
                        except:
                            print('Request error')
                        file.write(r.content)
                        print(i, ': ', word.text)
                        success = True
                        time.sleep(0.5)
        i = i + 1

