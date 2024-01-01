import os
from python.add_pinyin import (
    has_chinese_without_pinyin,
    get_all_chinese_lines_without_pinyin,
    update_markdown_files,
)

# Define the test directory
test_dir = "/Users/brice/Documents/LogSeq-GitHub/python/test"

# Test data
chinese_lines_no_pinyin_from_dummy = [
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
    # Expected result based on your dummy.md and other test files
    expected_voc_lines = [
        "hello 你好",
        "hello 你好",
        "-我住在北京市。",
        "讲到 , 说起：to talk about",
        "- 我经常编程。",
        "如何 ：how",
        "to persist ：坚持",
    ]
    expected_files_and_lines_ref = [
        ["/Users/brice/Documents/LogSeq-GitHub/python/test/dummy.md", 2],
        ["/Users/brice/Documents/LogSeq-GitHub/python/test/dummy.md", 4],
        ["/Users/brice/Documents/LogSeq-GitHub/python/test/dummy.md", 5],
        ["/Users/brice/Documents/LogSeq-GitHub/python/test/dummy.md", 7],
        ["/Users/brice/Documents/LogSeq-GitHub/python/test/dummy.md", 8],
        ["/Users/brice/Documents/LogSeq-GitHub/python/test/dummy.md", 10],
        ["/Users/brice/Documents/LogSeq-GitHub/python/test/dummy.md", 11],
    ]

    # Call the function
    voc_lines, files_and_lines_ref = get_all_chinese_lines_without_pinyin(test_dir)

    # Assertions
    assert voc_lines == expected_voc_lines
    assert files_and_lines_ref == expected_files_and_lines_ref


# TODO: continue testing from create_backup()


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
