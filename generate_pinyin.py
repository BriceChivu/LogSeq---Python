import os
import shutil
import re
import argparse
import datetime


# Paths
MARKDOWN_DIR = "/Users/brice/Documents/LogSeq-GitHub/LogSeq-GitHub/journals"
PYTHON_SCRIPTS_DIR = "/Users/brice/Documents/LogSeq-GitHub/python"
BACKUP_DIR = os.path.join(PYTHON_SCRIPTS_DIR, "bak")
LOG_FILE = os.path.join(PYTHON_SCRIPTS_DIR, "change_log.log")
CONSO_VOC_NO_PINYIN_OUTPUT = os.path.join(
    PYTHON_SCRIPTS_DIR, "consolidate_voc_no_pinyin_output.txt"
)
CHATGPT_OUTPUT = os.path.join(PYTHON_SCRIPTS_DIR, "chatgpt_output.txt")


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
def process_outputs():
    vocab_mapping = {}
    with open(CHATGPT_OUTPUT, "r") as f:
        for line in f.readlines():
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
    args = parser.parse_args()

    with open(LOG_FILE, "a") as log:  # Open log file in append mode
        if args.revert:
            revert_changes()
            log.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Reverted changes from"
                " backups (bak folder).\n"
            )
            print("Reverted changes from backups (bak folder).")
        else:
            create_backup()
            vocab_mapping = process_outputs()
            update_markdown_files(vocab_mapping)
            log.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Markdown files updated"
                " with Pinyin.\n"
            )
            print("Markdown files updated with Pinyin.")
        log.write("\n")


if __name__ == "__main__":
    main()
