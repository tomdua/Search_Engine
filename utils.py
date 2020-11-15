import pickle


def save_obj(obj, name):
    """
    This function save an object as a pickle.
    :param obj: object to save
    :param name: name of the pickle file.
    :return: -
    """
    with open('./pickles/'+name+'.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)




def load_obj(name):
    """
    This function will load a pickle file
    :param name: name of the pickle file
    :return: loaded pickle file
    """
    with open('./pickles/'+name+'.pkl', 'rb') as f:
        objs = []
        while 1:
            try:
                objs.append(pickle.load(f))
            except EOFError:
                break
    return objs
