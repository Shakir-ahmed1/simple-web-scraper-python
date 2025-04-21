import os
import re
from bs4 import BeautifulSoup
import dotenv
import chardet


dotenv.load_dotenv('.env')

project_folder_name = os.getenv("PROJECT_FOLDERNAME")
downloaded_files_folder_name = os.path.join(project_folder_name, os.getenv("DOWNLOADED_FILES_FOLDERNAME"))
extracted_geez_files_folder_name = os.path.join(project_folder_name, os.getenv("EXTRACTED_GEEZ_FILES_FOLDER"))

def clean_html(html_content):
    """ removes the html markup"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Step 3: Remove all <script> and <style> elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()  # Completely remove the tag and its content

    # Step 4: Get the plain text
    # Get the text, separate by newlines
    plain_text = soup.get_text(separator='\n')

    # Step 5: Clean up the text by stripping leading/trailing spaces on each line
    lines = (line.strip() for line in plain_text.splitlines())

    # Step 6: Filter out any blank lines or excessive whitespace
    cleaned_text = '\n'.join(line for line in lines if line)

    # Step 7: Write the cleaned text to the output file
    return cleaned_text


def apply_regex(input_text):

    # Regular expression to match sentences with Ethiopian script and punctuation
    pattern = r'(.*[ሀ-ፖ]+.*)'
    # pattern = r'([ሀ-ፖ]+.*[።?፣፤|])'

    # Step 1: Apply the regex to the input text
    matches = re.findall(pattern, input_text)

    # Step 2: Create 'clean_text' directory if it doesn't exist
    # output_dir = "clean_text"
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    # Step 3: Save the matches to the output file in the 'clean_text' directory
    new_list = []
    for match in matches:
        new_list.append(match)

    return '\n'.join(new_list)


def clean_html_regex(text):
    clean = clean_html(text)
    reg = apply_regex(clean)

    return reg




def is_text_file(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(1024)  # Read first 1KB to guess encoding
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    return encoding

def process_html_files(folder_path, output_folder):
    # Create the 'extracted_geez' folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    filenames = os.listdir(folder_path)
    counter = 0

    for filename in filenames:
        counter += 1
        print(f"{counter}/{len(filenames)}")

        if filename.endswith('.html'):
            file_path = os.path.join(folder_path, filename)

            # Detect encoding
            encoding = is_text_file(file_path)
            print(encoding)
            if not encoding:
                print(f"Skipping {filename}: Cannot detect encoding or binary file.")
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    html_content = file.read()

                extracted_text = clean_html_regex(html_content)

                output_file_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.txt")
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(extracted_text)

            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

    print("Processing complete. Extracted text files are saved in 'extracted_geez' folder.")


process_html_files(downloaded_files_folder_name, extracted_geez_files_folder_name )
