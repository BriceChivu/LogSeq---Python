# Revised script to closely align with the original logic of the two scripts

import os
import shutil
import re
import argparse
import datetime

# Constants for directory paths
MARKDOWN_DIR = "/Users/brice/Documents/LogSeq-GitHub/LogSeq-GitHub/journals"
PYTHON_SCRIPTS_DIR = "/Users/brice/Documents/LogSeq-GitHub/python"
BACKUP_DIR = os.path.join(PYTHON_SCRIPTS_DIR, "bak")
LOG_FILE = os.path.join(PYTHON_SCRIPTS_DIR, "change_log.log")


# Function to check if a line contains Chinese characters but no Pinyin
def extract_chinese_voc_no_pinyin(line):
    chinese_char_pattern = r"[\u4e00-\u9fff]"
    pinyin_pattern = r"[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]"
    has_chinese_char = re.search(chinese_char_pattern, line) is not None
    has_pinyin = re.search(pinyin_pattern, line) is not None
    return has_chinese_char and not has_pinyin


def process_directory_no_pinyin(directory_path):
    """
    Process all Markdown files in a directory to find lines with Chinese vocabulary without Pinyin.
    :param directory_path: Path to the directory containing Markdown files.
    :return: A list of lines containing Chinese vocabulary without Pinyin.
    """
    voc_lines = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".md"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    if extract_chinese_voc_no_pinyin(line):
                        voc_lines.append(line.strip())
    return voc_lines


# Backup creation
def create_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    for filename in os.listdir(MARKDOWN_DIR):
        if filename.endswith(".md"):
            shutil.copy2(os.path.join(MARKDOWN_DIR, filename), BACKUP_DIR)


# Revert to backup
def revert_changes():
    for filename in os.listdir(BACKUP_DIR):
        shutil.copy2(os.path.join(BACKUP_DIR, filename), MARKDOWN_DIR)


# Read and process outputs
def process_outputs(chatgpt_output):
    vocab_mapping = {}
    for line in chatgpt_output:
        parts = line.strip().split(":")
        if len(parts) >= 2:
            chinese_pinyin = parts[0].strip()
            chinese = chinese_pinyin.split(" ")[0].strip()
            vocab_mapping[chinese] = chinese_pinyin
    return vocab_mapping


# Update Markdown Files Function
def update_markdown_files(vocab_mapping):
    with open(LOG_FILE, "a") as log:
        for filename in os.listdir(MARKDOWN_DIR):
            if filename.endswith(".md"):
                filepath = os.path.join(MARKDOWN_DIR, filename)
                with open(filepath, "r") as file:
                    content = file.readlines()

                for chinese, replacement in vocab_mapping.items():
                    pattern = r"(?<![\w])" + re.escape(chinese) + r"(?![\w])"
                    matches = [
                        (line_num, line.strip())
                        for line_num, line in enumerate(content)
                        for m in re.finditer(pattern, line)
                    ]

                    if len(matches) > 1:
                        log_entry = (
                            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Multiple"
                            f" matches for '{chinese}' in file {filename}:\n"
                        )
                        print(log_entry, end="")
                        for i, (line_num, line) in enumerate(matches):
                            match_info = f"{i + 1}) Line {line_num + 1}: {line}\n"
                            print(match_info, end="")
                            log_entry += match_info
                        log.write(log_entry)
                        while True:
                            choice = (
                                input("Enter the number to replace, 'a' for all, or 's' to skip: ")
                                .strip()
                                .lower()
                            )
                            log.write("Enter the number to replace, 'a' for all, or 's' to skip:\n")
                            log.write(f"User's choice: {choice}\n")  # Log the user's choice
                            if choice.isdigit() and 1 <= int(choice) <= len(matches):
                                selected_line_num = matches[int(choice) - 1][0]
                                content[selected_line_num] = re.sub(
                                    pattern, replacement, content[selected_line_num]
                                )
                                log.write(
                                    f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -"
                                    f" Replaced '{chinese}' with '{replacement}' in {filename},"
                                    f" line {selected_line_num + 1}\n"
                                )
                                break
                            elif choice == "a":
                                for line_num, _ in matches:
                                    content[line_num] = re.sub(
                                        pattern, replacement, content[line_num]
                                    )
                                log.write(
                                    f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -"
                                    f" Replaced all instances of '{chinese}' with '{replacement}'"
                                    f" in {filename}\n"
                                )
                                break
                            elif choice == "s":
                                print("Skipped.")
                                log.write("Skipped as per user's choice.\n")
                                break
                            else:
                                print("Invalid input, please try again.")
                                log.write("Invalid input received.\n")
                    elif matches:
                        line_num, _ = matches[0]
                        content[line_num] = re.sub(pattern, replacement, content[line_num])
                        log.write(
                            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Replaced"
                            f" '{chinese}' with '{replacement}' in {filename}, line"
                            f" {line_num + 1}\n"
                        )

                with open(filepath, "w") as file:
                    file.writelines(content)


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
            revert_changes()
            log.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Reverted changes from"
                " backups (bak folder).\n"
            )
            print("Reverted changes from backups (bak folder).")
        else:
            create_backup()
            chinese_voc_no_pinyin = process_directory_no_pinyin(args.path)
            print(
                "\nAdd the pinyin in parentheses next to the chinese words for each vocabulary"
                " line.\nThe format should be:\n- {chinese_characters} ({pinyin}):"
                " {english_translation}\nDo not change the existing English translation!"
            )
            print("\nConsolidated Chinese cocabulary (without Pinyin):")
            for line in chinese_voc_no_pinyin:
                print(line)
            print(f"\nTotal number of Chinese vocabulary: {len(chinese_voc_no_pinyin)}")
            lines = []
            print("\nCopy above and paste it to ChatGPT.")
            print("Now, paste the output of ChatGPT here:")
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            vocab_mapping = process_outputs(lines)
            update_markdown_files(vocab_mapping)
            log.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Markdown files updated"
                " with Pinyin.\n"
            )
            print("Markdown files updated with Pinyin.")
        log.write("\n")


if __name__ == "__main__":
    main()


# TODO: do the tests
# TODO: Do not backup ALL the markdown files, just those that will be changed (or should I leave it like this?)
# TODO: clean up code
