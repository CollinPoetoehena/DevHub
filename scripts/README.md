# Scripts

The `scripts/` folder contains shared utility scripts used across the project. These are standalone tools that don't belong to a specific sub-project.

| Script | Description |
|--------|-------------|
| `load_config.sh` | Shared configuration loader — sources project-wide variables and utility functions. Other scripts source this file to get the project root path and common settings. |
| `convert_md_to_docx.py` | Converts a Markdown file to a Word (.docx) document. Handles headings, tables, code blocks, inline formatting, lists, and blockquotes. Requires `python-docx` (`pip install python-docx`). Usage: `python3 scripts/convert_md_to_docx.py <input.md> [output.docx]`. |
| `terraform/` | Terraform scripts — contains various Terraform configurations and helper scripts for managing infrastructure. |
