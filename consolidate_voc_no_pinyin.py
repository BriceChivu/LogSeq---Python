import os
import re
import argparse


def extract_chinese_voc_no_pinyin(line):
    """
    Check if the line contains Chinese vocabulary and does not contain Pinyin.
    :param line: A string representing a line from the file.
    :return: True if the line contains Chinese vocabulary and no Pinyin, False otherwise.
    """
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


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate Chinese vocabulary lines without Pinyin from Markdown files."
    )
    parser.add_argument(
        "--path",
        default="/Users/brice/Documents/logseq/journals",
        help="Path to the directory containing Markdown files",
    )
    args = parser.parse_args()

    chinese_voc_no_pinyin = process_directory_no_pinyin(args.path)

    print(
        "\nAdd the pinyin in parentheses next to the chinese words for each vocabulary"
        " line.\nThe format should be:\n- {chinese_characters} ({pinyin}): {english_translation}\n"
        "Do not change the existing English translation!"
    )
    print("\nConsolidated Chinese cocabulary (without Pinyin):")
    for line in chinese_voc_no_pinyin:
        print(line)
    print(f"\nTotal number of Chinese vocabulary: {len(chinese_voc_no_pinyin)}")


if __name__ == "__main__":
    main()
