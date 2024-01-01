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


# Backup creation
def create_backup(files_and_lines_ref, copy_from_path, copy_to_path):
    if not os.path.exists(copy_to_path):
        os.makedirs(copy_to_path)
    mardown_files = [sublist[0] for sublist in files_and_lines_ref]
    for filename in mardown_files:
        if filename.endswith(".md"):
            shutil.copy2(os.path.join(copy_from_path, filename), copy_to_path)


# Revert to backup
def revert_changes(copy_from_path, copy_to_path):
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


# Read and process outputs
def process_outputs(chatgpt_output):
    vocab_mapping = {}
    for line in chatgpt_output:
        parts = line.strip().split(
            ":"
        )  # assumes there is a ":" after the pinyin and before the english translation
        if len(parts) >= 2:
            chinese_pinyin = parts[0].strip()
            chinese = re.split(r"[ 。]", chinese_pinyin)[
                0
            ]  # assumes there is a space or a 。 after the chinese characters and before the pinyin
            vocab_mapping[chinese] = chinese_pinyin
    return vocab_mapping


# Update Markdown Files Function
def update_markdown_files(vocab_mapping, path_folder_markdown):
    with open(LOG_FILE, "a") as log:
        for filename in os.listdir(path_folder_markdown):
            if filename.endswith(".md"):
                filepath = os.path.join(path_folder_markdown, filename)
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


def capture_indentation(text):
    match = re.match(r"[^a-zA-Z\u4e00-\u9fff]+", text)
    return match.group() if match else ""


def update_markdown_files_2(chatgpt_output, files_and_lines_ref):
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
    python_bak = "/Users/brice/Documents/LogSeq-GitHub/python/bak"

    with open(LOG_FILE, "a") as log:
        if args.revert:
            revert_changes(python_bak, args.path)
        else:
            chinese_voc_no_pinyin, files_and_lines_ref = process_directory_no_pinyin(args.path)
            create_backup(files_and_lines_ref, args.path, python_bak)
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
            update_markdown_files_2(chatgpt_output, files_and_lines_ref)
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
# NOTE：讲到 , 说起：to talk about didnt work
# TODO: log in revert changes should say exactly what got reverted
# TODO: if nothing changed, alert me
# TODO: indentation and hyphens are not respected !! TO FIX
