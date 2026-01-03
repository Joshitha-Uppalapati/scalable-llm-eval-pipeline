from evalpipe.prompt import load_prompt


def test_prompt_hash_changes_on_content_change(tmp_path):
    p = tmp_path / "p.txt"

    p.write_text("hello")
    text1, hash1 = load_prompt(str(p))

    p.write_text("hello world")
    text2, hash2 = load_prompt(str(p))

    assert text1 != text2
    assert hash1 != hash2
