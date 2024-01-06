import os
import re
import argparse
import datetime
from typing import Tuple
import pyperclip

# Constants for directory paths
PYTHON_SCRIPTS_DIR = "/Users/brice/Documents/LogSeq-GitHub/python"
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
        if len(chatgpt_output) != len(files_and_lines_ref):
            message = (
                "Error: The number of"
                f" lines from ChatGPT ({len(chatgpt_output)}) does not match the number of"
                f" references ({len(files_and_lines_ref)}).\n"
                f"chatgpt_output:\n{chatgpt_output}\n"
                f"files_and_lines_ref:\n{files_and_lines_ref}\n"
                "Canceling the program.\n"
            )
            log.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {message}')
            print(message)
            exit()
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
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        path_markdown_files = "/Users/brice/Documents/LogSeq-GitHub/python/test"
    else:
        path_markdown_files = "/Users/brice/Documents/LogSeq-GitHub/LogSeq-GitHub/journals"

    with open(LOG_FILE, "a") as log:
        (
            chinese_voc_no_pinyin,
            files_and_lines_ref,
        ) = get_all_chinese_lines_without_pinyin(path_markdown_files)
        if not files_and_lines_ref:
            log.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - All voc already"
                " have pinyin.\n"
            )
            print("All voc already have pinyin.\n")
            exit()
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
        markdown_paths_to_be_updated = [sublist[0] for sublist in files_and_lines_ref]
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
# TODO: Create new test python script for chatgpt based on theme, e.g.:
# Give me all the vocabulary related to negativity (emotions, actions, etc.) among my voc list below.
# Do not change anything, just give me the negative Chinese voc lines.
# Do not add anything that is not in the list

# Cleaning
# TODO: create helpers.py and consolidate some functions used accross add_pinyin and ask_test_chatgpt
# TODO: do the tests
