TODO: make this something like:
- TODO: add here also the role and that it is required to not update any files directly, etc.
- Ask relentlessly via grill-me skill adopted from https://www.aihero.dev/skills-grill-me, https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md
- Add for research and exploration (e.g. check context and relevant files, do investigations, etc.) use subagents to avoid polluting the main agent's context.
- For architecture decision making use the Architecture agent to ensure consistent and well-structured system design.
- Add no specific agents list, just state can use the general-purpose and other built-in agents (no need to reinvent this), such as for research, etc.
- TODO: output plan in cwd/tmp/plan-<id>.md
- TODO: Add also a capability to split into sub-tasks based on the work and dependencies, providing the option to let the implementation be handled in parallel and by subagents so it can be coordinated, etc.