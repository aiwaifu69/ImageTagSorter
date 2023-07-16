import os
import shutil
import tkinter as tk
from tkinter import filedialog
import re
import time
from collections import Counter
from tqdm import tqdm

# Define the additional tags here
additional_tags = ["black hair", "blonde hair", "blue hair", "brown hair", "green hair", "grey hair", "orange hair", "pink hair", "purple hair", "white hair", "multicolored hair", "gradient hair", "red hair"]

# Define the minimum number of images a tag must appear in to be moved
MIN_TAG_COUNT = 4

def remove_empty_directories(path):
    """Function to remove empty folders"""
    for (dirpath, dirnames, filenames) in os.walk(path):
        if len(dirnames) == 0 and len(filenames) == 0:  # Check if directory is empty
            os.rmdir(dirpath)  # Remove the directory

def process_files(input_folder, output_folder, additional_tags):
    # Initialize the tag counter with the additional tags
    tag_counter = Counter({tag: 0 for tag in additional_tags})
    moved_files = set()
    ignore_tags = ['1girl', '1boy', '2girls', '2boys']
    total_files = sum([len(files) for r, d, files in os.walk(input_folder)])
    progress_bar = tqdm(total=total_files, bar_format='{l_bar}{bar}| Total progress: {percentage:3.0f}% completed')

    total_images = 0
    moved_images = 0

    # Uncomment the following lines if you want to sort by the most common tags
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.txt'):
                with open(os.path.join(root, file), 'r') as f:
                    contents = f.read()
                tags = re.findall(r'(\w+ \w+|\w+)', contents)  # Modified regex to find both single and double word tags
                tags = [tag for tag in tags if tag not in ignore_tags]
                for tag in tags:
                    if tag in additional_tags or tag in tag_counter.keys():  # Check if tag is in additional tags or in most common tags
                        tag_counter[tag] += 1  # Increment count for the tag

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.txt'):
                with open(os.path.join(root, file), 'r') as f:
                    contents = f.read()
                tags = re.findall(r'(\w+ \w+|\w+)', contents)  # Modified regex to find both single and double word tags
                tags = [tag for tag in tags if tag not in ignore_tags]
                for tag in tags:
                    if tag in additional_tags or tag in tag_counter.keys():  # Check if tag is in additional tags or in most common tags
                        tag_counter[tag] += 1  # Increment count for the tag
                        if tag_counter[tag] >= MIN_TAG_COUNT:
                            tag_folder = os.path.join(output_folder, f"{tag.replace(' ', '_')}")  # Create output folder name
                            os.makedirs(tag_folder, exist_ok=True)  # Create output folder if it doesn't exist
                            try:
                                new_file_name = file
                                if os.path.exists(os.path.join(tag_folder, file)):
                                    new_file_name = f"{os.path.splitext(file)[0]}_{int(time.time())}.txt"
                                base_filename = os.path.splitext(new_file_name)[0]
                                for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                                    image_file = os.path.join(root, base_filename + ext)
                                    if os.path.exists(image_file) and file not in moved_files:
                                        shutil.move(image_file, os.path.join(tag_folder, base_filename + ext))
                                        moved_files.add(file)
                                        moved_images += 1
                                        progress_bar.update(1)
                                        progress_bar.set_postfix_str(f"Moving {moved_images}/{total_images} images")
                            except Exception as e:
                                print(f"Error moving file {file}: {e}")

    # Renaming the folders with count of images
    for tag in tag_counter.keys():
        old_folder_name = os.path.join(output_folder, f"{tag.replace(' ', '_')}")
        if os.path.exists(old_folder_name):
            # Count the number of files in the directory
            num_files = len([f for f in os.listdir(old_folder_name) if os.path.isfile(os.path.join(old_folder_name, f))])

            new_folder_name = ""
            if tag in additional_tags:
                new_folder_name = os.path.join(output_folder, f"TAGS_{num_files}_{tag.replace(' ', '_')}")
            else:
                new_folder_name = os.path.join(output_folder, f"{num_files}_{tag.replace(' ', '_')}_common")

            # Check if new folder name already exists, if yes append a unique identifier
            if os.path.exists(new_folder_name):
                new_folder_name += f"_{int(time.time())}"
            
            os.rename(old_folder_name, new_folder_name)

    progress_bar.close()

    # Remove empty directories
    remove_empty_directories(output_folder)

    print("Processing completed successfully!")

root = tk.Tk()
root.withdraw()

# Popup to select input and output folders
input_folder = filedialog.askdirectory(title='Select Input Folder')
output_folder = filedialog.askdirectory(title='Select Output Folder')

# Process the files
process_files(input_folder, output_folder, additional_tags)