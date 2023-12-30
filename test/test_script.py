import os
from python.add_pinyin import (
    extract_chinese_voc_no_pinyin,
    process_directory_no_pinyin,
    update_markdown_files,
)

# Define the test directory
test_dir = "/Users/brice/Documents/LogSeq-GitHub/python/test"

# Test data
original_lines = [
    "今天天气不错。",
    "学习 Python 很有趣。",
    "我喜欢吃苹果。",
    "谢谢你。",
    "hello 你好。",
    "我住在北京市。",
]
updated_lines = [
    "今天天气不错 (jīntiān tiānqì bùcuò)。",
    "学习 Python 很有趣 (xuéxí Python hěn yǒuqù)。",
    "我喜欢吃苹果 (wǒ xǐhuān chī píngguǒ)。",
    "谢谢你 (xièxiè nǐ)。",
    "hello 你好 (hello nǐ hǎo)。",
    "我住在北京市 (wǒ zhù zài běijīng shì)。",
]


# Test for extract_chinese_voc_no_pinyin function
def test_extract_chinese_voc_no_pinyin():
    assert extract_chinese_voc_no_pinyin("今天天气不错。") == True
    assert extract_chinese_voc_no_pinyin("This is a test line.") == False
    assert extract_chinese_voc_no_pinyin("我住在北京市 (wǒ zhù zài běijīng shì)。") == False


# Test for process_directory_no_pinyin function
def test_process_directory_no_pinyin():
    extracted_lines = process_directory_no_pinyin(
        "/Users/brice/Documents/LogSeq-GitHub/python/test"
    )
    assert all(line in extracted_lines for line in original_lines)
    assert not any(line in extracted_lines for line in updated_lines)


# Test for update_markdown_files function
def test_update_markdown_files():
    test_dir = "/Users/brice/Documents/LogSeq-GitHub/python/test"
    test_file = os.path.join(test_dir, "dummy.md")

    # Original lines and their updated versions with Pinyin
    original_lines = [
        "- 今天天气不错。",
        "- 学习 Python 很有趣。",
        "- 我喜欢吃苹果。",
        "- 谢谢你。",
        "hello 你好。",
        "-我住在北京市。",
    ]
    updated_lines = [
        "- 今天天气不错 (jīn tiān tiān qì bú cuò)。",
        "- 学习 (xué xí) Python 很有趣。",
        "- 我喜欢吃苹果 (wǒ xǐ huān chī píng guǒ)。",
        "- 谢谢你 (xiè xiè nǐ)。",
        "hello 你好 (nǐ hǎo)。",
        "-我住在北京市 (wǒ zhù zài běi jīng shì)。",
    ]

    # Creating the mapping for testing
    vocab_mapping = {original: updated for original, updated in zip(original_lines, updated_lines)}

    # Run the update_markdown_files function
    update_markdown_files(vocab_mapping)

    # Verify the updates
    with open(test_file, "r", encoding="utf-8") as file:
        content = file.read()
        for original, updated in vocab_mapping.items():
            assert updated in content, f"Updated line '{updated}' not found in dummy.md"
