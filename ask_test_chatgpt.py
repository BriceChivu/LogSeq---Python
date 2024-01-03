import os
import re
import argparse


def extract_chinese_voc(line):
    """
    Check if the line contains at least one Chinese character.
    :param line: A string representing a line from the file.
    :return: True if the line contains a Chinese character, False otherwise.
    """
    chinese_char_pattern = r"[\u4e00-\u9fff]"
    return re.search(chinese_char_pattern, line) is not None


def process_directory(directory_path):
    """
    Process all Markdown files in a directory to find lines
    with Chinese vocabulary.
    :param directory_path: Path to the directory containing Markdown files.
    :return: A list of lines containing Chinese vocabulary.
    """
    voc_lines = []
    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith(".md"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    if extract_chinese_voc(line):
                        voc_lines.append(line.strip())
    return voc_lines


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate Chinese vocabulary lines from Markdown files."
    )
    parser.add_argument(
        "--path",
        default="/Users/brice/Documents/LogSeq-GitHub/LogSeq-GitHub/journals",
        help="Path to the directory containing Markdown files",
    )
    args = parser.parse_args()

    chinese_voc = process_directory(args.path)
    print(
        "\nBelow is my vocabulary list that I want to test myself on.\nSelect"
        " 50 vocabulary lines randomly and prompt me only with the English part such that I need to"
        " recollect the Chinese translation.\nThe order of the English prompts should be"
        " shuffled.\nThe test should be in the form of \n1. It's 22 dec today\n2. Christmas is"
        " coming soon\n3. To review\n4. ...\nDo not ask me the same prompts more than once."
    )
    print("\nChinese Vocabulary:")
    for line in chinese_voc:
        print(line)
    print(f"\nTotal number of Chinese vocabulary: {len(chinese_voc)}")


if __name__ == "__main__":
    main()
