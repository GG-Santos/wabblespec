---
name: guard-credential-detection
enabled: true
event: file
action: warn
conditions:
  - field: new_text
    operator: regex_match
    pattern: (API_KEY|SECRET_KEY|ACCESS_TOKEN|PASSWORD|PRIVATE_KEY|AWS_SECRET)\s*=\s*["'][^$\{]
  - field: file_path
    operator: regex_match
    pattern: \.(py|js|ts|go|rs|rb|php|java|cs|env\.example)$
---

Possible hardcoded credential detected in file write.

If this is a real secret: use an environment variable instead (`os.environ["KEY"]` / `process.env.KEY`).
If this is a placeholder: add a comment marking it as an example value and ensure the file is in `.gitignore`.

WabbleSpec guard rule — credential detection.
