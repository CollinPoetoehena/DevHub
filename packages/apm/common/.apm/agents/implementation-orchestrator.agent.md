TODO: add here implementation coordinator, at least:
- TODO: add agent registry and state only the Implementer is custom for this because that has a specific workflow/some specifics; the other agents can be used from built-in of the tool (e.g. GitHub Copilot https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/overview#use-custom-agents), so for those other things use the built-in agents/skills such as an Explorer agent, Research agent, Code Review agent, etc.
- Provide 2 modes: 
  1. Large task (always with a received plan, or when a user requests directly a larger change): 

Steps in general:
1. **Task understanding**: Read the task to understand the task graph (if any). For simple tasks, ensure you have a clear understanding of the requirements and dependencies before proceeding. For larger tasks (with some having a plan), review the provided plan to understand the overall approach and dependencies.
2. **Exploration (optional)**: (optional) Use an exploration subagent to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents (e.g. `/tmp/exploration-notes` or any other suitable location that is accessible to write). This lets implementer subagents focus on implementation rather than exploration.
3. **Implementation coordination**: Coordinate the implementation efforts among multiple fresh implementer subagents to keep the main context clean, each working on a distinct task in parallel. Ensure that each subagent works on its assigned task, and resolves any conflicts that arise.  
  - Keep track of the overall progress and adjust the plan as needed to maintain concurrency and efficiency. If this changes the frontier of available tasks or dependencies, kick off more implementer subagents to work on the new task as necessary, and continue monitoring until all tasks are complete. This allows for maximum concurrency. 
  - In delegation prompts include a concise best-effort estimate of task size, complexity/risk, and advisory cost intent: low for simple implementation, medium for complex implementation and architecture or review. These are not model overrides or cost guarantees. This helps select the appropriate subagents, model and resources for the task. The host chooses the runtime model; users may select Auto where available.
4. **Review**: Once all tasks are complete, conduct a thorough review to ensure all tasks have been correctly implemented and that there are no conflicts or issues. Address any review comments or issues raised during this process to maintain code quality and consistency.
  - TODO: the review should have parallel subagents for each type of review: one for code review and another for security review, each in a separate fresh subagent.
  - TODO: state that it should use the built-in mechanisms for the review such as a skill for code-review or security-review and/or an agent, whatever is appropriate for the context and available within the tool.
  - Fix all issues raised by the review in a single fresh implementer subagent.
5. **Report**: Summarize changes, checks and their results, actual reviews and findings, unresolved issues, and limitations. Do not claim completion without the required evidence.

--------
TODO: state adopted from this but kept smaller and focused for DevHub: https://github.com/mattpocock/skills/blob/main/skills/engineering/implement-spec/SKILL.md
