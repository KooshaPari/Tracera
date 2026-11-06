import json
from pathlib import Path

p = Path(__file__).parent
s = json.loads((p / "STATUS.json").read_text())
lines = [
    "# D04 preflight evidence tree",
    "",
    "Generated: " + s["generated_at_utc"],
    "",
    "Rendered from STATUS.json; no runtime promotion.",
    "",
    "```",
]
for item in s["intents"]:
    lines.append(item["name"])
    for axis, cell in item["cells"].items():
        lines.append("  " + axis + ": " + cell["verdict"] + " | " + cell["source"])
lines.extend(["```", ""] + s["limitations"])
(p / "STATUS.md").write_text("\n".join(lines) + "\n")
