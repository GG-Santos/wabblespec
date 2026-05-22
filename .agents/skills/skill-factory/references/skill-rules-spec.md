# skill-rules.json Specification

Defines activation patterns and progressive loading for skills. This file is the mechanism that enables intelligent skill triggering and on-demand resource loading.

## Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Skill Rules",
  "type": "object",
  "required": ["version", "skill_name", "activation_patterns"],
  "properties": {
    "version": {
      "type": "string",
      "const": "1.0"
    },
    "skill_name": {
      "type": "string",
      "description": "Must match the name in SKILL.md frontmatter"
    },
    "activation_patterns": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["pattern", "weight", "context"],
        "properties": {
          "pattern": {
            "type": "string",
            "description": "Regex pattern or keyword to match"
          },
          "weight": {
            "type": "number",
            "minimum": -1.0,
            "maximum": 1.0,
            "description": "Positive = trigger, negative = suppress. Higher absolute value = stronger signal."
          },
          "context": {
            "type": "string",
            "enum": ["user_message", "file_type", "project_context", "tool_output"],
            "description": "Where to look for the pattern"
          },
          "description": {
            "type": "string",
            "description": "Human-readable explanation of this pattern"
          }
        }
      }
    },
    "progressive_loading": {
      "type": "object",
      "description": "Defines what gets loaded at each activation level",
      "properties": {
        "level_1": {
          "type": "object",
          "description": "Always in context (metadata + description)",
          "properties": {
            "files": { "type": "array", "items": { "type": "string" } }
          }
        },
        "level_2": {
          "type": "object",
          "description": "Loaded when skill activates",
          "properties": {
            "files": { "type": "array", "items": { "type": "string" } }
          }
        },
        "level_3": {
          "type": "object",
          "description": "On-demand, loaded by SKILL.md instructions",
          "properties": {
            "files": { "type": "array", "items": { "type": "string" } }
          }
        }
      }
    },
    "required_capabilities": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Runtime-neutral capabilities that must be available for this skill to work"
    },
    "file_path_patterns": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Glob patterns. When set, this skill activates only when active files match at least one pattern. Use for path-scoped rules that apply to specific directories or file types (e.g. 'firmware/**', 'src/networking/**', '*.ps1'). Omit for skills that apply regardless of active file."
    },
    "incompatible_skills": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Skills that conflict with this one"
    },
    "provider_requirements": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["any", "local", "remote", "browser", "vision", "tool-use"]
      },
      "description": "Which providers this skill supports"
    }
  }
}
```

## Example

```json
{
  "version": "1.0",
  "skill_name": "data-pipeline",
  "activation_patterns": [
    {
      "pattern": "(?i)(etl|data pipeline|transform|extract.*load)",
      "weight": 0.9,
      "context": "user_message",
      "description": "ETL and data pipeline keywords"
    },
    {
      "pattern": "(?i)(csv|parquet|json.*file|xlsx)",
      "weight": 0.6,
      "context": "user_message",
      "description": "Data file format mentions"
    },
    {
      "pattern": "(?i)(fibonacci|hello world|tutorial)",
      "weight": -0.8,
      "context": "user_message",
      "description": "Generic coding tasks — NOT data pipeline"
    }
  ],
  "progressive_loading": {
    "level_1": {
      "description": "Always in context",
      "files": ["SKILL.md"]
    },
    "level_2": {
      "description": "Loaded when skill activates",
      "files": [
        "references/formats.md",
        "schemas/pipeline_config.json"
      ]
    },
    "level_3": {
      "description": "On-demand",
      "files": [
        "scripts/transform.py",
        "scripts/validate.py",
        "data/format_specs.csv",
        "templates/pipeline_report.html.j2"
      ]
    }
  },
  "required_capabilities": ["read_files", "write_files", "run_shell_command"],
  "incompatible_skills": [],
  "provider_requirements": ["any"]
}
```

## Weight Guidelines

| Weight | Meaning | Example |
|--------|---------|---------|
| 0.9–1.0 | Strong positive: core intent match | "build a data pipeline" |
| 0.5–0.8 | Moderate positive: related keywords | "parse this CSV" |
| 0.1–0.4 | Weak positive: tangentially related | "data" (too generic alone) |
| -0.1–-0.4 | Weak negative: slightly off-topic | "database schema" (close but different) |
| -0.5–-0.8 | Moderate negative: different domain | "fibonacci sequence" |
| -0.9–-1.0 | Strong negative: clearly unrelated | "write a poem" |

## Integration

Skill Factory generates this file during the Standard tier and above. The LLM uses it to:
1. Decide whether to activate the skill (weighted pattern matching)
2. Determine which files to load first (progressive loading levels)
3. Know what capabilities are required (pre-flight check)
