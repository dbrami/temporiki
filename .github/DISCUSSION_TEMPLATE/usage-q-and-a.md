---
title: "Usage Q&A"
labels: ["q-and-a"]
body:
  - type: markdown
    attributes:
      value: |
        Ask questions about setup, zero-command flow, Obsidian workflow, and temporal querying.
  - type: textarea
    id: context
    attributes:
      label: Context
      description: What are you trying to do?
      placeholder: "I clipped an article to raw/webclips and expected..."
    validations:
      required: true
  - type: textarea
    id: attempted
    attributes:
      label: What You Tried
      description: Commands, steps, and observed behavior.
    validations:
      required: true
  - type: textarea
    id: env
    attributes:
      label: Environment
      description: OS, Obsidian version, LLM CLI, Temporiki version.

