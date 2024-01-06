import os
import shutil
import re
import argparse
import datetime
from typing import Tuple
import pyperclip

# Constants for directory paths
MARKDOWN_DIR = "/Users/brice/Documents/LogSeq-GitHub/LogSeq-GitHub/journals"
PYTHON_SCRIPTS_DIR = "/Users/brice/Documents/LogSeq-GitHub/python"
BACKUP_DIR = os.path.join(PYTHON_SCRIPTS_DIR, "bak")
LOG_FILE = os.path.join(PYTHON_SCRIPTS_DIR, "change_log.log")


def has_chinese_without_pinyin(line: str) -> bool:
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


def get_all_chinese_lines_without_pinyin(
    directory_path: str,
) -> Tuple[list[str], list[list[str, int]]]:
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
    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith(".md"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    if has_chinese_without_pinyin(line):
                        voc_lines.append(line.strip())
                        files_and_lines_ref.append([file_path, line_number])
    return voc_lines, files_and_lines_ref


def create_backup(
    markdown_paths_to_be_updated: list,
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
    for filename in markdown_paths_to_be_updated:
        if filename.endswith(".md"):
            shutil.copy2(os.path.join(copy_from_path, filename), copy_to_path)


def clear_bak_folder(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


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
                f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Replaced'
                f' "{lines[line_num - 1].strip()}" with "{chatgpt_line}" in {filename}, line'
                f" {line_num}\n"
            )
            indentation = capture_indentation(lines[line_num - 1])
            lines[line_num - 1] = indentation + chatgpt_line + "\n"

            with open(file_path, "w") as file:
                file.writelines(lines)


def create_chatgpt_prompt(chinese_voc_no_pinyin: list) -> str:
    text_prompt_to_chatgpt = (
        "\nAdd the pinyin in parentheses next to the chinese words for each vocabulary"
        " line. The format should be:\n- {chinese_characters} ({pinyin}):"
        " {english_translation}\nDo not capitalize the first letter of the pinyin (e.g.,"
        " wanted: zuò fàn, not wanted: Zuò fàn).\nIf there are lines with 2 or more Chinese"
        " words separated by a comma, put the pinyin next to its corresponding voc (e.g.,"
        " wanted: 做饭 (zuò fàn)，烹饪 (pēng rèn): to cook, not wanted: 做饭 ，烹饪 (zuò"
        " fàn, pēng rèn): to cook).\nDo not separate the pinyin into 2 parts if it"
        " corresponds to 1 word or expression (e.g., wanted: 面包 (miànbāo), not wanted:"
        " 面包 (miàn bāo))\nDo not remove duplicates. The total number of lines (Total"
        " number of Chinese vocabulary) should remain the same, i.e., do not split existing"
        " lines (e.g., - to cook: 做饭 ，烹饪 should remain 1 line only).\nAt the end,"
        " show me the total number of lines for which you added pinyin.\n\nConsolidated"
        " Chinese vocabulary (without Pinyin):\n"
    )
    all_lines = ""
    for line in chinese_voc_no_pinyin:
        all_lines += line + "\n"
    print("\033[1m" + "\nAll voc lines without pinyin:" + "\033[0m")
    str_total = f"\nTotal number of Chinese vocabulary: {len(chinese_voc_no_pinyin)}"
    print(all_lines + "\033[1m" + str_total + "\033[0m")
    all_lines += str_total
    text_prompt_to_chatgpt += all_lines

    return text_prompt_to_chatgpt


# Main function
def main():
    parser = argparse.ArgumentParser(description="Update Markdown files with Pinyin.")
    parser.add_argument("--revert", action="store_true", help="Revert to backup files. Can be combined with --path argument")
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
            clear_bak_folder(BACKUP_DIR)
            chinese_voc_no_pinyin, files_and_lines_ref = get_all_chinese_lines_without_pinyin(
                args.path
            )
            if not files_and_lines_ref:
                log.write(
                    f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - All voc already"
                    " have pinyin.\n"
                )
                print("All voc already have pinyin.\n")
                exit()
            markdown_paths_to_be_updated = [sublist[0] for sublist in files_and_lines_ref]
            create_backup(markdown_paths_to_be_updated, args.path, BACKUP_DIR)
            text_prompt_to_chatgpt = create_chatgpt_prompt(chinese_voc_no_pinyin)
            pyperclip.copy(text_prompt_to_chatgpt)

            # 2nd step: pasting the ChatGPT output
            chatgpt_output = []
            print("\nCmd + v in ChatGPT.")
            print("Now, paste the output of ChatGPT here:")
            while True:
                line = input()
                if line == "":
                    break
                chatgpt_output.append(line)

            # Replacement of lines
            update_markdown_files(chatgpt_output, files_and_lines_ref)
            markdown_filenames = ", ".join(
                set([file.split("/")[-1] for file in markdown_paths_to_be_updated])
            )
            log.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -"
                f" {markdown_filenames} files updated with Pinyin.\n"
            )
            print(f"{markdown_filenames} files updated with Pinyin.")
        log.write("\n")


if __name__ == "__main__":
    main()



# Functionality
# TODO: log in revert changes should say exactly what got reverted (IS REVERT REALLY USEFUL SINCE WE HAVE EVERYTHING TRACKED IN GIT?)
# TODO: verify that the ChatGPT output number of lines is the same as the number of voc without pinyin
# TODO: Create new test for chatgpt based on theme
# Give me all the vocabulary related to negativity (emotions, actions, etc.) among my voc list below.
# Do not change anything, just give me the negative Chinese voc lines.
# Do not add anything that is not in the list

# Cleaning
# TODO: create helpers.py and consolidate some functions used accross add_pinyin and ask_test_chatgpt
# TODO: do the tests


