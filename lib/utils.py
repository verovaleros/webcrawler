"""
Set of common util functions to supopr the
functionality of the web crawler
"""
import pickle
from collections import deque

def store_set_to_file(set_to_save_to_disk, output_directory, file_name):
    """
    Writes the contents of a set to a file, with each element on a new line.

    :param set_to_save_to_disk: The set whose contents need to be written to the file.
    :param output_dir: The directory to store the files.
    :param file_name: The name of the file to write to.
    """

    output_filename = f"{output_directory}/{file_name}.log"
    with open(output_filename, "wb") as file:
        pickle.dump(set_to_save_to_disk, file)


def load_set_from_file(file_name):
    """
    Loads the contents of a file into a set.

    :param file_name: The name of the file to read from.
    :return: A set containing the lines of the file.
    """
    loaded_set = set()
    try:
        with open(file_name, "rb") as file:
            loaded_set = pickle.load(file)
    except FileNotFoundError:
        pass
    except pickle.UnpicklingError:
        print(f"Error loading the queue from {file_name}. File may be corrupted.")
        pass

    return loaded_set


def load_queue_from_file(file_name):
    """
    Loads the contents of a file into a deque (queue).

    :param file_name: The name of the file to read from.
    :return: A deque containing the lines of the file.
    """
    loaded_queue = deque()
    try:
        with open(file_name, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return deque()  # Return an empty deque in case of an unpickling error
    except pickle.UnpicklingError:
        print(f"Error loading the queue from {file_name}. File may be corrupted.")
        return deque()  # Return an empty deque in case of an unpickling error

    return loaded_queue
