import extract_channel
import os

"""
    Test Module to Run tests
"""

base_dir = os.getcwd()


def test_extract_channel_module():
    """
        Function to test Channel Extraction Module
        :return: None
    """
    # dir containing frames
    path_to_frames = os.path.join(base_dir, os.path.join('test_frames', 'g_channel_t1'))    # Testing specific

    # dir containing excel of cleaned channels
    path_to_channels = os.path.join(base_dir, os.path.join('channel_list', 'cleaned_channels.xlsx'))
    raw_extracted_text = extract_channel.extract_text_bulk(path_to_frames)
    clean_text = extract_channel.clean_extracted_text(raw_extracted_text)

    # Picking out channel name from the cleaned text using list of channels
    channel_name = extract_channel.get_channel_from_text(clean_text, path_to_channels)
    print(channel_name)


def main():
    test_extract_channel_module()


if __name__ == '__main__':
    main()
