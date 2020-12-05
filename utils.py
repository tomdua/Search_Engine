import pickle

def save_obj(obj, name):
    """
    This function save an object as a pickle.
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """
    with open('./'+name+'.pkl', 'ab') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)




def load_obj(name):
    """
    This function will load a pickle file
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    with open('./'+name+'.pkl', 'rb') as f:
        objs = []
        while 1:
            try:
                objs.append(pickle.load(f))
            except EOFError:
                break
    return objs


def read_text_file(file):
    file_list = []
    file_in = open(file, encoding="utf8")

    while True:
        try:
            line = file_in.readline()
            if line != '\n':
                line = line.split(".", 1)[1]
                line = line.split("\n", 1)[0]
                file_list.append(line)
        except:
            break
    file_in.close()
    return file_list


def load_inverted_index(path):

    dictionary = load_obj(path+'/dict_dictionary_after_indexer')

    return dictionary[0]
