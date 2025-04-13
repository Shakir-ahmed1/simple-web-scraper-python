import os
import re
from bs4 import BeautifulSoup
import dotenv

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
    pattern = r'([ሀ-ፖ]+.*[።?|])'

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




def process_html_files(folder_path, output_folder):
    # Create the 'extracted_geez' folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    filenames = os.listdir(folder_path)
    # Loop over each HTML file in the provided folder
    counter = 0
    for filename in os.listdir(folder_path):
        counter += 1
        # print(f"{counter}/{len(filenames)}")
        if filename.endswith('.html'):  # Process only HTML files
            file_path = os.path.join(folder_path, filename)
            
            # Read the content of the HTML file
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Apply the clean_html_regex function to the HTML content
            extracted_text = clean_html_regex(html_content)

            # Create the output text file path (with .txt extension)
            output_file_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.txt")

            # Save the extracted text as a .txt file
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(extracted_text)
            

    print("Processing complete. Extracted text files are saved in 'extracted_geez' folder.")


process_html_files(downloaded_files_folder_name, extracted_geez_files_folder_name )
