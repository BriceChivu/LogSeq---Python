import os
import shutil
import re
import argparse
import datetime
from typing import Tuple

# Constants for directory paths
MARKDOWN_DIR = "/Users/brice/Documents/LogSeq-GitHub/LogSeq-GitHub/journals"
PYTHON_SCRIPTS_DIR = "/Users/brice/Documents/LogSeq-GitHub/python"
BACKUP_DIR = os.path.join(PYTHON_SCRIPTS_DIR, "bak")
LOG_FILE = os.path.join(PYTHON_SCRIPTS_DIR, "change_log.log")


def extract_chinese_voc_no_pinyin(line: str) -> bool:
    """
    Check if a line contains Chinese characters but no Pinyin.
    Args:
        line (str): The line of text to be checked.
    Returns:
        bool: True if the line contains Chinese characters but no Pinyin, False otherwise.
    """
    chinese_char_pattern = r"[\u4e00-\u9fff]"
    pinyin_pattern = r"[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]"
    has_chinese_char = re.search(chinese_char_pattern, line) is not None
    has_pinyin = re.search(pinyin_pattern, line) is not None
    return has_chinese_char and not has_pinyin


def process_directory_no_pinyin(directory_path: str) -> Tuple[list[str], list[list[str, int]]]:
    """
    Process a directory to extract lines that contain Chinese vocabulary without Pinyin.
    Args:
        directory_path (str): The path to the directory containing Markdown files.
    Returns:
        Tuple[list[str], list[list[str, int]]]: A tuple containing a list of lines with Chinese vocabulary
        and a list of file paths with line numbers where these lines were found.
    """
    voc_lines = []
    files_and_lines_ref = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".md"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    if extract_chinese_voc_no_pinyin(line):
                        voc_lines.append(line.strip())
                        files_and_lines_ref.append([file_path, line_number])
    return voc_lines, files_and_lines_ref


def create_backup(
    files_and_lines_ref: list[list[str, int]],
    copy_from_path: str,
    copy_to_path: str,
) -> None:
    """
    Create a backup of files based on a reference list of files and lines.
    Args:
        files_and_lines_ref (list[list[str, int]]): A list of lists containing file paths and corresponding line numbers.
        copy_from_path (str): The directory path from which files will be copied.
        copy_to_path (str): The directory path to which files will be copied for backup.
    """
    if not os.path.exists(copy_to_path):
        os.makedirs(copy_to_path)
    mardown_files = [sublist[0] for sublist in files_and_lines_ref]
    for filename in mardown_files:
        if filename.endswith(".md"):
            shutil.copy2(os.path.join(copy_from_path, filename), copy_to_path)


def revert_changes(copy_from_path: str, copy_to_path: str) -> None:
    """
    Revert changes made to files by copying them back from the backup directory.
    Args:
        copy_from_path (str): The backup directory path from which files will be copied.
        copy_to_path (str): The original directory path to which files will be restored.
    """
    with open(LOG_FILE, "a") as log:
        for filename in os.listdir(copy_from_path):
            log.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {filename} is being"
                " reverted to previous version.\n"
            )
            print(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {filename} is being"
                " reverted to previous version."
            )
            shutil.copy2(os.path.join(copy_from_path, filename), copy_to_path)


def capture_indentation(text: str) -> str:
    """
    Capture the indentation used at the beginning of a given text.
    Args:
        text (str): The text from which to extract indentation.
    Returns:
        str: The extracted indentation characters (e.g., spaces, tabs).
    """
    match = re.match(r"[^a-zA-Z\u4e00-\u9fff]+", text)
    return match.group() if match else ""


def update_markdown_files(
    chatgpt_output: list[str], files_and_lines_ref: list[list[str, int]]
) -> None:
    """
    Update Markdown files with the output from ChatGPT, respecting the original indentation.
    Args:
        chatgpt_output (list[str]): The lines of text output by ChatGPT to be inserted into the files.
        files_and_lines_ref (list[list[str, int]]): A list of file paths and corresponding line numbers where the updates will be made.
    """
    with open(LOG_FILE, "a") as log:
        changes = list(zip(files_and_lines_ref, chatgpt_output))
        for (file_path, line_num), chatgpt_line in changes:
            filename = file_path.split("/")[-1]
            with open(file_path, "r") as file:
                lines = file.readlines()

            log.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Replaced"
                f" '{lines[line_num - 1].strip()}' with '{chatgpt_line}' in {filename}, line"
                f" {line_num}\n"
            )
            indentation = capture_indentation(lines[line_num - 1])
            lines[line_num - 1] = indentation + chatgpt_line + "\n"

            with open(file_path, "w") as file:
                file.writelines(lines)


# Main function
def main():
    parser = argparse.ArgumentParser(description="Update Markdown files with Pinyin.")
    parser.add_argument("--revert", action="store_true", help="Revert to backup files")
    parser.add_argument(
        "--path",
        default="/Users/brice/Documents/LogSeq-GitHub/LogSeq-GitHub/journals",
        help="Path to the directory containing Markdown files",
    )
    args = parser.parse_args()

    with open(LOG_FILE, "a") as log:
        if args.revert:
            revert_changes(BACKUP_DIR, args.path)
        else:
            chinese_voc_no_pinyin, files_and_lines_ref = process_directory_no_pinyin(args.path)
            create_backup(files_and_lines_ref, args.path, BACKUP_DIR)
            print(
                "\nAdd the pinyin in parentheses next to the chinese words for each vocabulary"
                " line. The format should be:\n- {chinese_characters} ({pinyin}):"
                " {english_translation}\nDo not capitalize the first letter of the pinyin (e.g.,"
                " wanted: zuò fàn, not wanted: Zuò fàn).\n"
                "Do not remove duplicates."
            )
            print("\nConsolidated Chinese cocabulary (without Pinyin):")
            for line in chinese_voc_no_pinyin:
                print(line)
            print(f"\nTotal number of Chinese vocabulary: {len(chinese_voc_no_pinyin)}")
            chatgpt_output = []
            print("\nCopy above and paste it to ChatGPT.")
            print("Now, paste the output of ChatGPT here:")
            while True:
                line = input()
                if line == "":
                    break
                chatgpt_output.append(line)
            # vocab_mapping = process_outputs(lines)
            # update_markdown_files(vocab_mapping, args.path)
            update_markdown_files(chatgpt_output, files_and_lines_ref)
            log.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Markdown files updated"
                " with Pinyin.\n"
            )
            print("Markdown files updated with Pinyin.")
        log.write("\n")


if __name__ == "__main__":
    main()


# TODO: do the tests
# TODO: clean up code
# TODO: log in revert changes should say exactly what got reverted
# TODO: if nothing changed, alert me
