import numpy as np
from collections import defaultdict
import random

matrix_file = open("train_data/output_matrix_number.txt")
label_file = open("train_data/output_label_number.txt")

label_dict = defaultdict()

classes = ["O", "B-LOC", "B-PER", "B-ORG", "B-TOUR", "I-ORG", "I-PER", "I-TOUR", "I-LOC", "B-PRO", "I-PRO"]


class Element:
    def __init__(self, vector, label):
        self.vector = vector
        self.label = label

    def get_vector(self):
        return self.vector

    def get_label(self):
        return self.label


class Elements:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def get_element(self, index):
        return self.elements[index]

    def size(self):
        return len(self.elements)


def to_label(number_label):
    return classes[int(number_label)]


def add_elements(dicts, elements):
    l = elements.get_element(0).get_label()
    if l not in dicts.keys():
        dicts[l] = []
    dicts[l].append(elements)


in_long_word = False
current_long_word = Elements()
count = 0

for line in matrix_file:
    count += 1
    line = line.strip()
    label = label_file.readline().strip()

    if line is "" or label is "" or line is None or label is None:
        break

    if label not in label_dict.keys():
        label_dict[label] = []

    element = Element(line, label)
    label = to_label(element.get_label())

    if not in_long_word:
        # current not in a long word
        if label == 'O':
            elements = Elements()
            elements.add_element(element)
            add_elements(label_dict, elements)
            in_long_word = False

        else:
            if label == 'B-LOC' or label == 'B-PER' or label == 'B-PRO' or label == 'B-TOUR' or label == 'B-ORG':
                current_long_word = Elements()
                in_long_word = True
                current_long_word.add_element(element)
        continue

    else:
        # in long words
        if label == 'O':
            # finish long word and add it
            add_elements(label_dict, current_long_word)

            # add word 'O'
            elements = Elements()
            elements.add_element(element)
            add_elements(label_dict, elements)
            in_long_word = False

        else:
            type_long_word = classes[int(current_long_word.get_element(0).get_label())]
            is_continue_word = False

            if type_long_word == 'B-LOC' and classes[int(element.get_label())] == 'I-LOC':
                is_continue_word = True

            if type_long_word == 'B-PER' and classes[int(element.get_label())] == 'I-PER':
                is_continue_word = True

            if type_long_word == 'B-ORG' and classes[int(element.get_label())] == 'I-ORG':
                is_continue_word = True

            if type_long_word == 'B-TOUR' and classes[int(element.get_label())] == 'I-TOUR':
                is_continue_word = True

            if type_long_word == 'B-PRO' and classes[int(element.get_label())] == 'I-PRO':
                is_continue_word = True

            if is_continue_word:
                # continue add word to current_long_word
                current_long_word.add_element(element)
                in_long_word = True
            else:
                # finish word
                add_elements(label_dict, current_long_word)

                # create new long word
                label = to_label(element.get_label())
                if label not in ['B-PRO', 'B-TOUR', 'B-LOC', 'B-PER', 'B-ORG']:
                    print("Fuck error {0} {1} {2}".format(to_label(current_long_word.get_element(0).get_label()), label,
                                                          count))

                current_long_word = Elements()
                current_long_word.add_element(element)
                in_long_word = True

train_distribution = {
    '0': 2000,
    '1': 2000,
    '2': 2000,
    '3': 2000,
    '4': 2000,
    '5': 2000,
    '6': 2000,
    '7': 2000,
    '8': 2000,
    '9': 2000,
    '10': 2000,
}

train_ratio = 0.8

train_mat_file = open("train_data/full_train_matrix_file.txt", "w")
test_mat_file = open("train_data/full_test_matrix_file.txt", "w")

train_label_file = open("train_data/full_train_label_file.txt", "w")
test_label_file = open("train_data/full_test_label_file.txt", "w")

train_label_file_string = open("train_data/full_train_label_file_string.txt", "w")
test_label_file_string = open("train_data/full_test_label_file_string.txt", "w")

for key in ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0']:
    num = train_distribution[key]

    # if num > len(label_dict[key]):
    num = len(label_dict[key])

    train_num = int(num * train_ratio)
    test_num = int(num - train_num)

    train_elements_index = random.sample(range(0, len(label_dict[key])), train_num)

    # create index and remove training index
    test_elements_index = list(set(range(0, len(label_dict[key]))) - set(train_elements_index))

    for i in train_elements_index:
        for j in range(0, label_dict[key][i].size()):
            train_mat_file.write(label_dict[key][i].get_element(j).get_vector())
            train_mat_file.write('\n')

            train_label_file.write(label_dict[key][i].get_element(j).get_label())
            train_label_file.write('\n')

            train_label_file_string.write(classes[int(label_dict[key][i].get_element(j).get_label())])
            train_label_file_string.write('\n')

    for i in test_elements_index:
        for j in range(0, label_dict[key][i].size()):
            test_mat_file.write(label_dict[key][i].get_element(j).get_vector())
            test_mat_file.write('\n')

            test_label_file.write(label_dict[key][i].get_element(j).get_label())
            test_label_file.write('\n')

            test_label_file_string.write(classes[int(label_dict[key][i].get_element(j).get_label())])
            test_label_file_string.write('\n')

train_mat_file.close()
test_mat_file.close()
train_label_file.close()
test_label_file.close()
