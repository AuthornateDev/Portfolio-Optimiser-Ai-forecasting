import sys
import os
from box.exceptions import BoxValueError
import yaml
from FoodRecognition.constants.logging import logger
from ensure import ensure_annotations
from box import ConfigBox
from datetime import datetime
import zipfile


@ensure_annotations
def read_yaml(path: str = None) -> ConfigBox:
    """read yaml file and returns ConfigBox type
    :Params:
        path: path like input
    :returns:
        ConfigBox: ConfigBox type
    :raises:
        ValueError: if yaml file is empty
        e: empty file
    """

    try:
        path = path if path is not None else "config.yaml"
        with open(path) as yaml_file:
            content = yaml.safe_load(yaml_file)
            return ConfigBox(content)
    except BoxValueError:
        raise ValueError("Yaml File is Empty")
    except Exception as e:
        raise e


def clock_time(st, et, text):
    final_time = et - st
    print(f"{text} took {final_time} seconds")
    logger.info(f"{text} took {final_time} seconds")


@ensure_annotations
def create_directories(path_to_directories: list, verbose=True):
    """create list of directories

    :params:
        path_to_directories (list): list of path of directories
        ignore_log (bool, optional): ignore if multiple dirs is to be created. Defaults to False.
    :returns: None
    """
    for path in path_to_directories:
        os.makedirs(path, exist_ok=True)


@ensure_annotations
def extract_directory_path(text):
    # Split the text by the last '/' character
    parts = text.rsplit("/", 1)

    if len(parts) > 1:
        return parts[0]
    else:
        return ""


@ensure_annotations
def create_directories_2(path_string):
    # Split the path string into individual directory names
    directories = path_string.split("/")

    # Initialize the base path
    base_path = ""

    # Loop through the directory names and create the directories
    for directory in directories:
        base_path = os.path.join(base_path, directory)
        if not os.path.exists(base_path):
            os.mkdir(base_path)


@ensure_annotations
def convert_timestamp_to_utc(timestamp_str):
    try:
        # Convert the input string to a float
        timestamp = float(timestamp_str)

        # Convert the timestamp to a datetime object
        utc_datetime = datetime.datetime.utcfromtimestamp(timestamp)

        # Format the datetime object as a string
        utc_time_string = utc_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")

        return utc_time_string
    except ValueError:
        return "Invalid timestamp format"
    

def unzip_file(zip_file_path, extract_to_dir):
    """
    Unzips a .zip file to the specified directory.
    
    Parameters:
        zip_file_path (str): Path to the .zip file.
        extract_to_dir (str): Directory where the files will be extracted.
    """
    if not os.path.exists(extract_to_dir):
        os.makedirs(extract_to_dir)
        print(f"Created directory: {extract_to_dir}")
    
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_dir)
            print(f"Successfully extracted {zip_file_path} to {extract_to_dir}")
    except zipfile.BadZipFile:
        print(f"Error: {zip_file_path} is not a valid zip file.")
    except Exception as e:
        print(f"An error occurred: {e}")
