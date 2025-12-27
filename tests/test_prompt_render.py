from pathlib import Path
from evalpipe.prompts.render import render_prompt


def test_render_prompt(tmp_path: Path):
    template = tmp_path / "t.txt"
    template.write_text("Q: {{prompt}}\nA:")

    test_case = {"prompt": "What is 2+2?"}

    rendered = render_prompt(template, test_case)

    assert rendered == "Q: What is 2+2?\nA:"

