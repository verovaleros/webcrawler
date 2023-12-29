"""
Set of common util functions to supopr the
functionality of the web crawler
"""

def store_set_to_file(set_to_save_to_disk, output_directory, file_name):
    """
    Writes the contents of a set to a file, with each element on a new line.

    :param set_to_save_to_disk: The set whose contents need to be written to the file.
    :param output_dir: The directory to store the files.
    :param file_name: The name of the file to write to.
    """

    output_filename = f"{output_directory}/{file_name}.log"
    with open(output_filename, "w") as file:
        for item in set_to_save_to_disk:
            file.write(item + "\n")
