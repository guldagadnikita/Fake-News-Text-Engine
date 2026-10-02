"""
================================================================================
Module: file_handler.py
================================================================================
Python Concepts Demonstrated:
- File Handling: Reading and writing files using 'with open(...) as file:'
- Context Managers: Automatic resource closing via 'with' statement
- Exception Handling: Comprehensive try-except-finally blocks for FileNotFoundError,
  PermissionError, UnicodeDecodeError, and general Exceptions
- Tuples: Returning (success_flag, result_message_or_data)
- Dictionaries & Lists: Parsing categorized text files into structured collections
- Strings: Line stripping, case normalization, and comment filtering
================================================================================
"""

import os


def load_keywords_from_file(file_path: str) -> tuple:
    """
    Reads the keywords.txt database and organizes keywords into a dictionary of lists.
    
    Expected Categories in file:
    - [SUSPICIOUS_WORDS]
    - [CLICKBAIT_PHRASES]
    - [CREDIBLE_WORDS]

    Returns:
    - A tuple: (success: bool, data_dict_or_error_msg)
    """
    categories = {
        "suspicious": [],
        "clickbait": [],
        "credible": []
    }

    current_category = None

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Keyword file not found at: {file_path}")

        # File reading using context manager
        with open(file_path, "r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()

                # Skip empty lines and comment lines
                if not line or line.startswith("#"):
                    continue

                # Detect category headers
                if line == "[SUSPICIOUS_WORDS]":
                    current_category = "suspicious"
                elif line == "[CLICKBAIT_PHRASES]":
                    current_category = "clickbait"
                elif line == "[CREDIBLE_WORDS]":
                    current_category = "credible"
                else:
                    # Append lowercase keyword to active category
                    if current_category in categories:
                        categories[current_category].append(line.lower())

        return (True, categories)

    except FileNotFoundError as fnf_err:
        return (False, f"File Error: {fnf_err}")
    except PermissionError:
        return (False, f"Permission Denied: Unable to access file at {file_path}")
    except UnicodeDecodeError:
        return (False, f"Encoding Error: File at {file_path} is not valid UTF-8 text.")
    except Exception as general_err:
        return (False, f"Unexpected error reading keywords: {str(general_err)}")


def read_text_file(file_path: str) -> tuple:
    """
    Reads user-selected text file.
    
    Returns:
    - Tuple: (success: bool, text_content_or_error: str)
    """
    if not file_path:
        return (False, "No file path provided.")

    try:
        if not os.path.isfile(file_path):
            return (False, f"The specified path is not a valid file: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        if not content.strip():
            return (False, "Warning: The selected file is completely empty.")

        return (True, content)

    except FileNotFoundError:
        return (False, f"Error: File '{file_path}' was not found.")
    except PermissionError:
        return (False, f"Error: Permission denied to read file '{file_path}'.")
    except UnicodeDecodeError:
        # Fallback try with latin-1 if UTF-8 fails
        try:
            with open(file_path, "r", encoding="latin-1") as fallback_file:
                content = fallback_file.read()
            return (True, content)
        except Exception:
            return (False, f"Encoding Error: File could not be decoded as UTF-8 or text.")
    except Exception as err:
        return (False, f"An unexpected error occurred while reading the file: {str(err)}")


def write_text_file(file_path: str, content: str) -> tuple:
    """
    Writes content to a text file with proper error checking.
    
    Returns:
    - Tuple: (success: bool, message: str)
    """
    if not file_path:
        return (False, "No destination file path was specified.")

    if content is None:
        content = ""

    try:
        # Ensure parent directory exists
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        return (True, f"File successfully saved to:\n{file_path}")

    except PermissionError:
        return (False, f"Error: Permission denied to write to '{file_path}'.")
    except Exception as err:
        return (False, f"An unexpected error occurred while saving the file: {str(err)}")
