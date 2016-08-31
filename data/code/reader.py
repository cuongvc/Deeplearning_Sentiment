import fastnumbers
import re
import numpy as np
from collections import defaultdict

SPEC_NUMBER = "SPEC_NUMBER"
SPEC_NONE = "SPEC_NONE"


def get_dictionary(filename):
    f = open(filename, "r")
    dict_words = []

    for line in f:
        args = line.strip().split(" ")
        word = args[0]

        if word.lower() not in dict_words:
            dict_words.append(word.lower())

    f.close()
    return dict_words


def write(dict_words, filename):
    f = open(filename, "w")
    for word in dict_words:
        f.write(word + "\n")
    f.close()


def get_dictionary_word2vec(filename):
    f = open(filename, "r")
    dict_words = []
    for line in f:
        index_of_space = get_first_index_of_char(' ', line)
        w = line[0:index_of_space].lower()

        if w not in dict_words:
            print w
            dict_words.append(w)

    f.close()
    return dict_words


def get_first_index_of_char(c, s):
    i = 0

    while i < len(s) and s[i] != c:
        i += 1

    if i == len(s):
        return -1

    return i


def export_small_w2v(dict, filename, output):
    print "Start export"

    f = open(filename, "r")
    f2 = open(output, "w")
    for line in f:
        index_of_space = get_first_index_of_char(' ', line)
        w = line[0:index_of_space].lower()
        if w in dict:
            print w
            f2.write(line)

    f.close()
    f2.close()


def standardize(filename, word_out, matrix_out):
    f = open(filename)

    f1 = open(word_out, "w")
    f2 = open(matrix_out, "w")

    for line in f:
        index_of_space = get_first_index_of_char(' ', line)
        w = line[0:index_of_space].lower()
        vec = line[index_of_space + 1: len(line)]

        f1.write(w + "\n")
        f2.write(vec)

    f1.close()
    f2.close()


def to_common_words(corpus_words, filename, word_out, matrix_out, rest_filename):
    f = open(filename)

    f1 = open(word_out, "w")
    f2 = open(matrix_out, "w")
    f3 = open(rest_filename, "w")

    # standard two set
    for w in corpus_words:
        if is_number(w):
            print "Remove {0}".format(w)
            corpus_words.remove(w)

    corpus_words.append(SPEC_NUMBER)

    for line in f:
        index_of_space = get_first_index_of_char(' ', line)
        w = line[0:index_of_space].lower()
        vec = line[index_of_space + 1: len(line)]

        # write common words to files
        if is_number(w):
            continue

        if w in corpus_words:
            f1.write(w + "\n")
            f2.write(vec)
            corpus_words.remove(w)

    for w in corpus_words:
        f3.write(w + "\n")

    f1.close()
    f2.close()
    f3.close()


def is_number(w):
    w = w.strip().replace("\n", "")
    return fastnumbers.isfloat(w) or fastnumbers.isfloat(re.sub('[^A-Za-z0-9]+', '', w))


def read_standard_dictionary(filename):
    words = []

    f = open(filename)
    for line in f:
        words.append(line.strip())

    return words


def create_random_vector(dim):
    return np.random.rand(dim)


def create_training(filename, window_size, output_matrix, output_labels):
    f = open(filename)
    f2 = open(output_matrix, "w")
    f3 = open(output_labels, "w")

    sentence = []
    for line in f:
        if line.strip() != '':
            sentence.append(line)
            continue

        # finish a sentence
        for i in range(0, len(sentence)):
            vector = []
            for index in range(i - (window_size - 1) / 2, i):
                if index < 0:
                    vector.append(SPEC_NONE)
                else:
                    vector.append(sentence[index])

            vector.append(sentence[i])
            for index in range(i + 1, i + 1 + (window_size - 1) / 2):
                if index >= len(sentence):
                    vector.append(SPEC_NONE)
                else:
                    vector.append(sentence[index])

            # finish a vector
            # write to file
            for word in vector:
                real_word = word.split(" ")[0]
                if is_number(real_word):
                    real_word = SPEC_NUMBER
                f2.write("{0} ".format(real_word))

            f2.write("\n")
            f3.write(sentence[i].strip().split(" ")[2])
            f3.write("\n")

        # reset sentence
        sentence = []

    f2.close()
    f3.close()


def create_training_postag(filename, window_size, output_matrix, output_labels):
    f = open(filename)
    f2 = open(output_matrix, "w")
    f3 = open(output_labels, "w")

    sentence = []
    for line in f:
        if line.strip() != '':
            sentence.append(line)
            continue

        # finish a sentence
        for i in range(0, len(sentence)):
            vector = []
            for index in range(i - (window_size - 1) / 2, i):
                if index < 0:
                    vector.append(SPEC_NONE)
                else:
                    vector.append(sentence[index])

            vector.append(sentence[i])
            for index in range(i + 1, i + 1 + (window_size - 1) / 2):
                if index >= len(sentence):
                    vector.append(SPEC_NONE)
                else:
                    vector.append(sentence[index])

            # finish a vector
            # write to file
            for word in vector:
                real_word = word.split(" ")[0]
                if is_number(real_word):
                    real_word = SPEC_NUMBER
                f2.write("{0} ".format(real_word))

            f2.write("\n")
            f3.write(sentence[i].strip().split(" ")[1])
            f3.write("\n")

        # reset sentence
        sentence = []

    f2.close()
    f3.close()


def create_random_matrix(filename, output, size):
    f1 = open(filename)
    f2 = open(output, "w")
    for line in f1:
        vec = create_random_vector(size)
        for i in range(0, len(vec)):
            f2.write("{0} ".format(vec[i]))
        f2.write("\n")

    f1.close()
    f2.close()


def standard(word):
    if is_number(word):
        word = SPEC_NUMBER
    return word.strip().lower()


def create_window_size_training(matrix, words, sentence_file, output_matrix):
    f1 = open(matrix, "r")
    f2 = open(words, "r")

    print "Start reading vector..."
    map_vectors = defaultdict()
    word_dict = defaultdict()
    list_dict = []
    i = 0
    while True:
        vec = f1.readline().strip()
        word = f2.readline().strip()

        if vec is None or word is None or word == "" or vec == "":
            break

        word = standard(word)

        if word in word_dict.keys():
            continue

        word_dict[word] = i
        list_dict.append(word)
        map_vectors[word] = vec

        i += 1

    f1.close()
    f2.close()
    print "Finish reading vector..."

    size_dict = len(word_dict)
    print "Size of dictionary {0}".format(size_dict)

    def generate_unit_vector(dim, index):
        vector = np.zeros(dim)
        vector[index] = 1
        return vector

    def to_string(vector):
        return ' '.join(map(str, vector))

    print "Start convert vector to weight"
    f3 = open(sentence_file)
    f4 = open(output_matrix, "w")

    f = open("word_dict_index.txt", "w")
    for value in list_dict:
        f.write("{0}\n".format(value))
    f.close()

    spec_none = SPEC_NONE.lower()

    for line in f3:
        words = line.strip().split(" ")
        #        print words
        i = 0
        for w in words:
            i += 1
            w = standard(w)
            if w in map_vectors:
                f4.write("{0}".format(word_dict[w]))
            else:
                f4.write("{0}".format(word_dict[spec_none]))

            if i < len(words):
                f4.write(" ")
        f4.write("\n")
    f4.close()


classes = ["O", "B-LOC", "B-PER", "B-ORG", "B-TOUR", "I-ORG", "I-PER", "I-TOUR", "I-LOC", "B-PRO", "I-PRO"]
# classes = ['R', 'N', 'CH', 'V', 'C', 'M', 'A', 'E', 'L', 'P', 'Nc', 'Cc', 'Ny', 'Nb', 'I', 'Np', 'T', 'Z', 'X', 'Nu', 'Y', 'Ab', 'Vy', 'Vb', 'B', 'Ni']

print(len(classes))

# f = open("postag_output_label.txt")
# f2 = open("postag_output_label_number.txt", "w")
#
# for line in f:
#     w = line.strip()
#
#     if w not in classes:
#         classes.append(w)
#     index = classes.index(w)
#     f2.write(str(index))
#     f2.write("\n")
#
# f2.close()
# f.close()

# print classes

create_window_size_training(
  "train_data/total_matrix_final.txt",
  "train_data/total_words_final.txt",
  "postag_output_matrix_words.txt",
  "postag_output_matrix_number.txt"
)

# f1 = open("total_matrix.txt")
# f1w = open("train_data/total_matrix_final.txt", "w")
#
# f2 = open("total_word.txt")
# f2w = open("train_data/total_words_final.txt", "w")
#
# word_dict = defaultdict()
# while True:
#     vec = f1.readline().strip()
#     word = f2.readline().strip()
#
#     if vec is None or word is None or word == "" or vec == "":
#         break
#
#     word = standard(word)
#
#     if word in word_dict.keys():
#         continue
#
#     word_dict[word] = 1
#     f1w.write("{0} \n".format(vec))
#     f2w.write("{0} \n".format(word))


# create_training_postag("data/NER_TAG.txt", 11, "postag_output_matrix_words.txt", "postag_output_label.txt")
# create_training("data/NER_TAG.txt", 11, "output_matrix_words.txt", "output_label.txt")
# create_random_matrix("rest_words.txt", "rest_matrix.txt", 200)
# create matrix
# corpus_words = read_standard_dictionary("corpus.dict")
# to_common_words(corpus_words, "word2vec", "common_words.txt", "common_matrix.txt",
#                "rest_words.txt")  # w2v_words = read_standard_dictionary("w2v_words.txt")
# export_small_w2v(get_dictionary("data/NER_TAG.txt"), "data/vector-new-skipgram", "word2vec")
# write(get_dictionary("data/NER_TAG.txt"), "corpus.dict")
# write(get_dictionary_word2vec("data/vector-new-skipgram"), "word2vec.dict")
# standardize("word2vec", "w2v_words.txt", "w2v_matrix.txt")
