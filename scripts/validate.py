"""Validate skill structure and persisted behavioral-test artifacts."""
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "paper-close-reading"
text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
match = re.match(r"^---\n(.*?)\n---", text, re.S)
assert match, "Missing frontmatter"
meta = yaml.safe_load(match.group(1))
assert meta["name"] == SKILL.name
assert isinstance(meta["description"], str) and 0 < len(meta["description"]) <= 1024
for relative in re.findall(r"\]\((references/[^)]+)\)", text):
    assert (SKILL / relative).is_file(), relative
ids = []
for name in ["stages-1-3.md", "stages-4-7.md"]:
    ids.extend(map(int, re.findall(r"### Prompt (\d+)", (SKILL / "references" / name).read_text(encoding="utf-8"))))
assert ids == list(range(1, 27)), ids
ui = yaml.safe_load((SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8"))
assert "$paper-close-reading" in ui["interface"]["default_prompt"]
records = list((ROOT / "tests" / "evaluation" / "updated" / "paper-reading").glob("*/progress.md"))
assert len(records) == 2, "Expected two simulated reading records"
for progress in records:
    ids = list(map(int, re.findall(r"^\| (\d+) \|", progress.read_text(encoding="utf-8"), re.M)))
    assert ids == list(range(1, 27)), progress
    for name in ["notes.md", "evidence.md"]:
        assert (progress.parent / name).is_file(), name
for name in ["baseline/baseline-results.md", "control/behavior-log.md", "resume/resume-results.md", "updated/updated-results.md", "updated/index-resume-results.md"]:
    assert (ROOT / "tests" / "evaluation" / name).is_file(), name
print("PASS: skill metadata, references, 26 prompts and saved evaluation records")
print("Structural checks do not replace independent behavioral tests.")
