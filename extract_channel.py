from pytesseract import image_to_string
from PIL import Image
import pandas as pd
import numpy as np
import cv2
import os
import re


"""
    Core Module containing functions to pick out most probable channel from the text extracted out of the frames of a 
    video. 
        
    Procedure:
        1) Given the directory containing the frames of a video, perform a selected OCR approach on part of the frame
            most likely to contain the channel name.
        2) Capture text from all the frames in the given directory.
        3) Perform a couple of cleaning tasks on the raw extracted text to better prepare for processing. 
        
        4) Given a list of channels active in India, count for every channel how many times it occurs in the cleaned 
            form of extracted text.
        5) The channel with max count of occurrence is the most likely channel for the frames. 
        
    Directories and Files:
        1) basedir : current working directory
        2) basedir/channel_list: directory containing the master list of active channels(obtained from Min. of I&B, GoI)
            and cleaned list of channels.
        4) basedir/date/channel/time/images/: Directory that will contain the frames initially
"""


base_dir = os.getcwd()


def get_text_from(img_path):
    """
        To Extract Text from a single image.
        Works in the directory containing the image
        :param img_path: full path of the image
        :return: list of strings (text extracted from the image)
    """
    img = cv2.imread(img_path)  # Reading Frame Image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)     # converting to grey scale

    # Performing clean up operations on the image for optimum character recognition
    kernel = np.ones((1, 1), np.uint16)     # Kernel Matrix to perform matrix operations
    img = cv2.dilate(img, kernel, iterations=1)     # Dilation
    img = cv2.erode(img, kernel, iterations=1)      # Erosion

    # Cropping Image to perform Selected OCR
    img = img[0:300, 0:1650]
    path_to_write = os.path.join(os.getcwd(), 'cleaned.jpg')    # Path to save cropped image
    cv2.imwrite(path_to_write, img)  # Saving cropped image

    result = image_to_string(Image.open(path_to_write))  # Performing OCR on the cropped Image
    result = result.lower().split('\n')  # Splitting the entire text extracted about '\n' to ease out processing
    os.remove('cleaned.jpg')  # removing temporary cleaned image
    return result


def extract_text_bulk(images_dir):
    """
        To extract text from a bulk of frames stored in the given directory.
        Calls the get_text_from(img_path) function
        :param images_dir: directory containing the frame images
        :return: extracted text from the entire frame set, in the form of list of strings
    """
    text, ctr = [], 0   # counter variable to count and log the number of frames complete with extraction
    for each in os.listdir(images_dir):
        if each.endswith('.jpg') and not each.startswith('cleaned'):
            print(f'current image {each}  images done = {ctr}   in {images_dir}')   # Logging extraction for each image

            # Extracting text from current frame by calling get_text_frame() function
            ext_text = get_text_from(os.path.join(images_dir, each))
            text += ext_text    # appending the extracted text into previously extracted text
            ctr += 1    # incrementing counter of images done

    text = list(set(text))  # De-duping the text extracted
    return text     # List of strings


def clean_extracted_text(raw_text):
    """
        To clean the extracted text into compatible form with the list of channels.
        The cleaned list of strings contains strings with underscore separated lowercase alphanumeric words
        :param raw_text: list of strings extracted from the frames
        :return: cleaned : list of cleaned strings
    """
    cleaned = []
    for each in raw_text:
        if len(each) > 1:
            # Removing special characters
            temp = ''.join([word.lower() for word in each if (word.isalnum() or word.isspace())])
            temp = '_'.join(temp.split())
            # Removing numeric words
            temp = '_'.join([word for word in temp.split('_') if not word.isnumeric()])
            if len(temp) > 1:
                cleaned.append(temp)
    return cleaned


def count_occurrence_of(channel_name, text):
    """
        Function to count the occurrence of given channel name in the cleaned list of extracted text
        :param channel_name: Current Channel to count occurrences for
        :param text: cleaned list of strings extracted from the frames
        :return: integral count of current channel in the given text
    """
    count = 0
    for line in text:
        matches = re.findall(channel_name, line)
        if matches:
            count += len(matches)
    return count


def get_channel_from_text(cleaned_text, path_channel_list):
    """
        Function to extract channel name out of the cleaned text obtained from frames
        :param cleaned_text: list of cleaned strings to get the channel from
        :param path_channel_list: path of the excel file containing the cleaned channels data
        :return: channel name extracted from the text.
    """
    channels = pd.read_excel(path_channel_list, squeeze=True)   # Reading in channels as Pandas Series object

    # Applying count function to get a Mask Series containing counts of each channel
    mask = channels.apply(count_occurrence_of, args=(cleaned_text,))
    result = pd.concat([channels, mask], axis=1)    # Concatenating two series
    result.columns = ['Channel Name', 'Count']  # Renaming columns for better identification
    final_result = result[result['Count'] > 0]  # Masking out rows with non-zero count of occurrence

    # Returning the channel with max number of occurrences as the most probable channel
    return final_result['Channel Name'][final_result['Count'] == final_result['Count'].max()].values[0]
