from datetime import datetime
import subprocess
import cv2
import os

"""
    Module to capture videos from Webcam and saving the .mpg files in defined directory
    
    Procedure:
        1) Record the video using opencv2 methods in .avi format
        2) Convert the .avi files to .mpg using ffmpeg
        3) Save .mpg files in the defined directory with defined file name
        4) Delete the temporary recorded .avi file.
    
    Directories:
        1) basedir : current working directory
        2) basedir/temp : directory for storing the captured .avi file as output.avi
        3) basedir/date/channel/time : directory to save the .mpg file as date_time_channel.mpg
        4) basedir/date/channel/time/conversion_log.txt : log file to log the conversion process
"""     

base_dir = os.getcwd()


def get_channel():
    """
        To get channel name
        Placeholder function
    """
    return 'generic_channel'


def covert_video_to_mpg(video_to_convert):
    """
        To convert a video file into .mpg using ffmpeg.
        Return: True if conversion was successful else False
        Input : Path of the video to convert
        Saves the .mpg video into the directory : basedir/date/channel with the video file name: date_time_channel.mpg
    """
    current_date = str(datetime.now().date())
    channel = get_channel()
    full_date_channel_path = os.path.join(base_dir, os.path.join(current_date, channel))  # path: base_dir/date/channel
    if not os.path.isdir(full_date_channel_path):
        os.makedirs(full_date_channel_path)  # if above directory doesn't exists, create it

    # command to to run for conversion :
    # ffmpeg -i <input_video_path> -c:v libx264 <output_file_name_with_full_path>
    static_command1 = 'ffmpeg -i '
    static_command2 = ' -c:v libx264 '

    current_time = ''.join(str(datetime.now().time())[:5].split(':'))  # grabbing current time in hhmm format
    full_time_path = os.path.join(full_date_channel_path, current_time)  # creating full path:basedir/date/channel/time
    if not os.path.isdir(full_time_path):
        os.makedirs(full_time_path)  # if above directory doesn't exists, create it (will be the target directory)

    file_name = ('_'.join([current_date, current_time, channel])) + '.mpg'  # filename in format: date_time_channel.mpg
    path_to_save_in = os.path.join(full_time_path, file_name)  # output_file_name_with_full_path
    command = static_command1 + video_to_convert + static_command2 + path_to_save_in  # command to execute

    # Opening log file for logging the conversion
    log_file_path = os.path.join(full_time_path, 'conversion_log.txt')
    log_file, status = open(log_file_path, 'w'), True
    try:
        # creating subprocess to run the command in shell to convert
        subprocess.check_call(command, shell=True, stderr=log_file)
    except subprocess.CalledProcessError:
        print('Conversion not successful. Check log file')
        status = False
    finally:
        log_file.close()
    return status


def capture_video_from_webcam():
    """
        To capture and save a video in the defined directory
        Return : None
        Input : None
        1) Captures video from webcam in .avi format, saves in basedir/temp directory as output.avi.
        2) Calls convert_video_to_mpg() for conversion and further relocation of the video
        3) Deletes the temporary recorded video in .avi format
    """
    temp_path = os.path.join(base_dir, 'temp')  # to store the temporary .avi file
    if not os.path.isdir(temp_path):
        os.makedirs(temp_path)  # if above directory doesn't exists, create it

    full_temp_path = os.path.join(temp_path, 'output.avi')  # full file name of the recorded video
    codec = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    frame_rate = 25
    resolution = (640, 480)
    vid_recorder = cv2.VideoWriter(full_temp_path, codec, frame_rate, resolution)  # video_writer object to store frames
    window_name = 'Video Capture'  # name of the window that will display the video feed
    cv2.namedWindow(window_name)
    cap = cv2.VideoCapture(0)  # Object to capture frames

    if not cap.isOpened():
        cap.open(0)

    # Keep recording until space-bar is pressed
    while True:
        status, frame = cap.read()  # capturing the current frame
        if status:
            cv2.imshow(window_name, frame)  # displaying the current frame in a live video feed
            vid_recorder.write(frame)  # Saving current frame into the video
            if cv2.waitKey(2) == 32:
                # recording stopped
                break

    vid_recorder.release()
    cap.release()
    cv2.destroyWindow(window_name)

    # Converting the .avi recorded video to .mpg required format via ffmpeg
    if covert_video_to_mpg(full_temp_path):
        print('Success. Video recorded, converted and saved to the directory')
    else:
        print('Not successful conversion')
    os.remove(full_temp_path)  # Removing the temporary .avi file


""" Test Code Below"""


def main():
    capture_video_from_webcam()


if __name__ == '__main__':
    main()
