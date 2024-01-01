import os
from python.add_pinyin import (
    has_chinese_without_pinyin,
    get_all_chinese_lines_without_pinyin,
    update_markdown_files,
)

# Define the test directory
test_dir = "/Users/brice/Documents/LogSeq-GitHub/python/test"

# Test data
chinese_lines_no_pinyin = [
    "hello 你好",
    "hello 你好",
    "-我住在北京市。",
    "讲到 , 说起：to talk about",
    "- 我经常编程。",
    "如何 ：how",
    "to persist ：坚持",
]
updated_lines = [
    "你好 (nǐ hǎo): hello",
    "你好 (nǐ hǎo): hello",
    "你好 (nǐ hǎo): hello",
    "我住在北京市。 (wǒ zhù zài běijīng shì.): I live in Beijing.",
    "讲到, 说起 (jiǎng dào, shuō qǐ): to talk about",
    "我经常编程。 (wǒ jīngcháng biānchéng.): I often program.",
    "如何 (rúhé): how",
    "坚持 (jiānchí): to persist",
]


# Test for has_chinese_without_pinyin function
def test_has_chinese_without_pinyin():
    assert has_chinese_without_pinyin("今天天气不错。") == True
    assert has_chinese_without_pinyin("There is no chinese character in this line.") == False
    assert (
        has_chinese_without_pinyin(
            "我住在北京市 (wǒ zhù zài běijīng shì)。This line already has pinyin"
        )
        == False
    )


# Test for get_all_chinese_lines_without_pinyin function
def test_get_all_chinese_lines_without_pinyin():
    extracted_lines, _ = get_all_chinese_lines_without_pinyin(
        "/Users/brice/Documents/LogSeq-GitHub/python/test"
    )
    assert all(
        line in extracted_lines for line in chinese_lines_no_pinyin
    )  # tests that all the chinese lines are correctly extracted from the markdown file


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
