import subprocess
from datetime import datetime
import os
import re

"""
    Module to split given video into individual frames and saving the frames in the defined directory
        
    Procedure:
        1) Split video into frames using ffmpeg into the defined directory with temporary frame name as frame_0%4d.jpg
        2) Gather the frame extraction details (time of a frame relative to start) into a text file named
            frame_extraction_log.txt 
        3) Segregate the list of time of a frame from the frame_extraction_log file into new_names list by the help of 
            regex.
        4) Perform rename operation on the bulk of frames captured
        
    Directories and Files:
        1) basedir : current working directory
        3) basedir/date/channel/time/images : directory to store frames
        4) basedir/date/channel/time/images/frame_extraction_log.txt : file to log the splitting process and gather 
            frame time information
"""

base_dir = os.getcwd()


def get_channel():
    """
        To get channel name
        Placeholder function
    """
    return 'generic_channel'


def rename_frames(target_dir):
    """
        Function to bulk rename the frames captured in the required naming convention of time_%04d.jpg
        :param target_dir: directory containing the frames
        :return: Tuple(bool, str)
        1) Opening the frame_extraction_log.txt file
        2) Grabbing the time details for each frame captured from the log in the opened file via regex
        3) Attempt renaming the contents of the target directory(containing frames) to the desired form.
        4) Return tuple with boolean and string denoting the status of the operation.
    """
    # Taking the path of the file containing the frame details
    full_target_path, new_names = os.path.join(target_dir, 'frame_extraction_log.txt'), []
    with open(full_target_path, 'r') as file:
        content = file.read()
        match_obj = re.findall(r'pts_time:[-.0-9]+', content)

        # Extracting time of each frame from the matches resulting from the regex
        new_names = [match.split(':')[1] for match in match_obj]
    if new_names:
        os.chdir(target_dir)
        for index, file_name in enumerate(os.listdir(target_dir)):
            if file_name.endswith('.jpg'):
                os.rename(file_name, '_'.join([new_names[index], file_name.split('_')[1]]))
        os.chdir(base_dir)
        return True, 'Frame times extracted. Frames renamed'
    else:
        return False, 'Frame times could not be extracted'


def split_into_frames(input_video):
    """
        Function to split a video into individual frames
        :param input_video: full path of the video to split
        :return: Tuple(bool, str)
        1) Splits the input_video into individual frames into the directory base/date/channel/time/images as
           frames_%04d.jpg
        2) Calls rename_frames() tp attempt renaming if the frames were successfully captured from the video
        3) Returns a Tuple of size 2 with a bool value and message to indicate success or failure
    """
    current_date = str(datetime.now().date())
    channel = get_channel()
    full_date_channel_path = os.path.join(base_dir, os.path.join(current_date, channel))  # path: base_dir/date/channel
    if not os.path.isdir(full_date_channel_path):
        os.makedirs(full_date_channel_path)  # if above directory doesn't exists, create it

    current_time = ''.join(str(datetime.now().time())[:5].split(':'))  # grabbing current time in hhmm format
    full_time_path = os.path.join(full_date_channel_path, current_time)  # creating full path:basedir/date/channel/time
    if not os.path.isdir(full_time_path):
        os.makedirs(full_time_path)  # if above directory doesn't exists, create it (will be the target directory)

    full_target_path = os.path.join(full_time_path, 'images')  # full path:basedir/date/channel/time/images
    if not os.path.isdir(full_target_path):
        os.makedirs(full_target_path)  # if above directory doesn't exists, create it (will be the target directory)

    file_name = 'frame_%04d.jpg'  # temporary frame name
    path_to_save_in = os.path.join(full_target_path, file_name)  # output_file_name_with_full_path

    # command to to run for splitting :
    # ffmpeg -i <input_video_path> -vf showinfo <temp_image_name>%0d.jpg
    command = f'ffmpeg -i {input_video} -vf showinfo {path_to_save_in}'

    # Opening log file for logging the frame extraction process
    log_file_path = os.path.join(full_target_path, 'frame_extraction_log.txt')
    log_file, exception, exception_msg = open(log_file_path, 'w'), False, ''
    try:
        # creating subprocess to run the command in shell to convert
        subprocess.check_call(command, shell=True, stderr=log_file)
    except subprocess.CalledProcessError:
        exception_msg = 'Extraction not successful. Check log file'
        exception = True
    finally:
        log_file.close()

    if exception:
        # If exception occurred, return exception message
        return False, exception_msg
    return rename_frames(full_target_path)


""" Test Code Below """


def main():
    video_path = os.path.join(os.getcwd(), 'TEST1_3.MPG')
    print(split_into_frames(video_path))


if __name__ == '__main__':
    main()
