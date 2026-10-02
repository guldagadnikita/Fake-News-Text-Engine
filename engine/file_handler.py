"""
================================================================================
Module: file_handler.py (Part of 'engine' package)
================================================================================
Python Concepts Demonstrated:
- File Handling: Reading and writing files using 'with open(...) as file:'
- Context Managers: Automatic resource closing via 'with' statement
- Exception Handling: Comprehensive try-except blocks for FileNotFoundError,
  PermissionError, UnicodeDecodeError, and general Exceptions
- Tuples: Returning (success_flag, result_message_or_data)
- Dictionaries & Lists: Parsing categorized text files
- Strings: Line stripping, case normalization, and comment filtering
================================================================================
"""

import os


def load_word_list(file_path: str) -> tuple:
    """
    Loads a simple word list from a text file (one word/phrase per line).
    Lines starting with '#' are treated as comments and skipped.

    Demonstrates: File handling, Lists, Exception handling.

    Returns:
    - Tuple: (success: bool, list_of_words_or_error_msg)
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        words = []
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    words.append(line.lower())

        return (True, words)

    except FileNotFoundError as e:
        return (False, f"File Error: {e}")
    except PermissionError:
        return (False, f"Permission Denied: {file_path}")
    except UnicodeDecodeError:
        return (False, f"Encoding Error: {file_path} is not valid UTF-8.")
    except Exception as e:
        return (False, f"Unexpected error: {str(e)}")


def load_keywords_from_file(file_path: str) -> tuple:
    """
    Reads a categorized keywords file with section headers like:
    [SUSPICIOUS_WORDS], [CLICKBAIT_PHRASES], [CREDIBLE_WORDS]

    Demonstrates: File handling, Dictionaries, Lists, Loops, Conditionals.

    Returns:
    - Tuple: (success: bool, data_dict_or_error_msg)
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

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

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
                    if current_category in categories:
                        categories[current_category].append(line.lower())

        return (True, categories)

    except FileNotFoundError as e:
        return (False, f"File Error: {e}")
    except PermissionError:
        return (False, f"Permission Denied: {file_path}")
    except UnicodeDecodeError:
        return (False, f"Encoding Error: {file_path} is not valid UTF-8.")
    except Exception as e:
        return (False, f"Unexpected error: {str(e)}")


def read_text_file(file_path: str) -> tuple:
    """
    Reads a user-selected text file with comprehensive error handling.

    Demonstrates: File handling, Exception handling, Tuples.

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
            return (False, "Encoding Error: File could not be decoded.")
    except Exception as err:
        return (False, f"Unexpected error while reading: {str(err)}")


def write_text_file(file_path: str, content: str) -> tuple:
    """
    Writes content to a text file with proper error checking.

    Demonstrates: File handling, Exception handling, os.makedirs.

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
        return (False, f"Unexpected error while saving: {str(err)}")
