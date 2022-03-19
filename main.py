import os
import re
import pymorphy2
import nltk
from nltk.corpus import stopwords
from string import punctuation


def tokenize_file(path):
    russian_stopwords = stopwords.words("russian")

    with open(path, encoding='cp1251', mode='r') as f:
        text = f.read()

    file_tokens = nltk.word_tokenize(text.lower())
    file_tokens = [file_token for file_token in file_tokens
                   if file_token not in russian_stopwords and file_token not in punctuation]
    return file_tokens


if __name__ == '__main__':
    nltk.download('popular')
    directory = 'pages'
    # только слова, удовлетворяющие этому паттерну попадут в список токенов
    token_pattern = "^[а-яА-Я]+$"
    # словарь токенов: ключ - токен, значение - список страниц, на которых он встретился
    tokens_index = dict()
    analyzer = pymorphy2.MorphAnalyzer()

    # итерация по всем файлам директории
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # проверка на тип
        if os.path.isfile(file_path):
            # токены из файла
            returned_tokens = tokenize_file(file_path)
            # удаление дубликатов путем приведения к множеству
            returned_tokens = set(returned_tokens)
            # фильтрация по заданному паттерну
            filtered_tokens = [returned_token for returned_token in returned_tokens
                               if re.match(token_pattern, returned_token)]

            # выбираю из названия файла его порядковый номер
            file_number = ""
            for char in filename:
                if char.isdigit():
                    file_number = file_number + char

            # записываю каждый токен файла в словарь токенов
            for filtered_token in filtered_tokens:
                if filtered_token not in tokens_index.keys():
                    tokens_index[filtered_token] = [file_number]
                else:
                    tokens_index[filtered_token].append(file_number)

    # создание словаря лемм и соответствующих им токенов
    lemmas_dict = dict()
    for token in tokens_index.keys():
        parsed_token = analyzer.parse(token)[0]
        lemma = parsed_token.normal_form
        # добавление токена по ключу (лемме)
        if lemma not in lemmas_dict.keys():
            lemmas_dict[lemma] = [token]
        else:
            lemmas_dict[lemma].append(token)

    with open('inverted_index.txt', encoding='cp1251', mode='w+') as f_index:
        f_index.write("")

    # сохранение инвертированного индекса
    with open('inverted_index.txt', encoding='cp1251', mode='a') as f_index:
        for key, values in lemmas_dict.items():
            pages = []
            for value in values:
                pages = pages + tokens_index[value]
            f_index.write(f'{key} {" ".join(set(pages))}\n')
