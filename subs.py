import argparse
import os
import re
import shutil
import zipfile


def adjust_line_width(srt_file, max_width):
    try:
        with open(srt_file, 'r', encoding='utf-8') as file:
            srt_text = file.read()
    except FileNotFoundError:
        print(f'Error: File not found: {srt_file}')
        return
    except Exception as e:
        print(f'Error: {e}')
        return
    

    # Split the text into individual subtitle blocks
    subtitle_blocks = re.split(r'\n{2,}', srt_text)

    # Process each subtitle block
    for i, block in enumerate(subtitle_blocks):
        # Find the subtitle text within the block
        match = re.search(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+)', block, re.DOTALL)
        if match:
            subtitle_number = match.group(1)
            start_time = match.group(2)
            end_time = match.group(3)
            text = match.group(4)

            # Remove line breaks and excessive whitespace
            text = re.sub(r'\s+', ' ', text.strip())

            # Adjust line width
            lines = []
            current_line = ''
            for word in text.split():
                if len(current_line) + len(word) <= max_width:
                    current_line += word + ' '
                else:
                    lines.append(current_line.strip())
                    current_line = word + ' '
            if current_line:
                lines.append(current_line.strip())

            # Join the adjusted lines
            adjusted_text = '\n'.join(lines)

            # Create the adjusted subtitle block
            adjusted_block = f'{subtitle_number}\n{start_time} --> {end_time}\n{adjusted_text}'

            # Replace the original subtitle block with the adjusted block
            subtitle_blocks[i] = adjusted_block

    # Join the subtitle blocks back into a single string
    adjusted_srt = '\n\n'.join(subtitle_blocks)

    # Save the adjusted SRT to the original file
    with open(srt_file, 'w', encoding='utf-8') as file:
        file.write(adjusted_srt)

    print(f'Success! Adjusted SRT file saved as: {srt_file}')


def zip_original_files(folder_path):
    backup_zip = os.path.join(folder_path, 'backup.zip')

    # Create a zip file to store the original files
    with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for filename in files:
                if filename.endswith('.srt'):
                    srt_file_path = os.path.join(root, filename)
                    zipf.write(srt_file_path, arcname=os.path.relpath(srt_file_path, folder_path))

    print(f'Success! Original files zipped: {backup_zip}')


def backup_srt_files(folder_path, recursive=False, create_zip=True):
    if create_zip:
        zip_original_files(folder_path)

    if recursive:
        walker = os.walk(folder_path)
    else:
        walker = [(folder_path, [], [file for file in os.listdir(folder_path) if file.endswith('.srt')])]

    for root, _, files in walker:
        for filename in files:
            srt_file_path = os.path.join(root, filename)
            max_line_width = 60

            print(f'Processing: {srt_file_path}')

            adjust_line_width(srt_file_path, max_line_width)


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Adjust line width in SRT files.')

    # Add a positional argument for the folder path
    parser.add_argument('folder_path', type=str, help='Path to the folder containing the SRT files')

    # Add an optional argument to enable recursive processing
    parser.add_argument('--recursive', dest='recursive', action='store_true',
                        help='Enable recursive processing of subdirectories')

    # Add an optional argument to skip creating the backup zip file
    parser.add_argument('--no-zip', dest='create_zip', action='store_false',
                        help='Do not create a backup zip file')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Retrieve the folder path, recursive, and create_zip values from the parsed arguments
    folder_path = args.folder_path
    recursive = args.recursive
    create_zip = args.create_zip

    backup_srt_files(folder_path, recursive, create_zip)


if __name__ == '__main__':
    main()
