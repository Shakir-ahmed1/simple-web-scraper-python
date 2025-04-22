from dotenv import load_dotenv
import os
import sys
load_dotenv('.env')

project_folder = os.getenv('PROJECT_FOLDERNAME')
if len(sys.argv) == 2:
    project_folder = sys.argv[1]

print(project_folder)
text_corpus_output_file = os.path.join(project_folder, os.getenv('TEXT_CORPUS_FILENAME'))
extracted_geez = os.path.join(project_folder, os.getenv('EXTRACTED_GEEZ_FILES_FOLDER'))
print(project_folder)
print(text_corpus_output_file)
print(extracted_geez)



filenames = os.listdir(extracted_geez)
def join_files(files, prefix):
    counter = 0

    all_text = ''
    counter = 0
    total_files = len(files)
    for filename in files:
        counter += 1
        print(prefix, '-',counter,'/', total_files)
        file_path = os.path.join(extracted_geez,filename)
        with open(file_path, 'r', encoding='utf-8')as f:
            all_text = all_text + '\n'+ f.read()
    text_corpus_output_file = os.path.join(project_folder, prefix + '-' + os.getenv('TEXT_CORPUS_FILENAME'))
    with open(text_corpus_output_file, 'w', encoding='utf-8') as corpus:
        data_list = all_text.split('\n')
        processed_string = '\n'.join(list(set(data_list)))
        corpus.write(processed_string)

from math import floor
from random import shuffle
file_len = len(filenames)
filename1 = filenames[:floor(file_len*0.33)]
filename2 = filenames[floor(file_len*0.33):floor(file_len*0.66)]
filename3 = filenames[floor(file_len*0.66):]

join_files(filename1, '1')
join_files(filename2, '2')
join_files(filename3, '3')

print(f"text processing complete for '{project_folder}'. the output is in '{text_corpus_output_file}'")
