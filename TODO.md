# TODOs for now:


## Refactor to personal DevHub with generic development hub for myself and my personal projects
TODO: make in README.md clear that this is what I use for all my personal projects, these are the "standards" that I apply, etc.
TODO: also the reference can stay, it contains essential information and is fine to keep, et.
TODO: add this way my PPs are professionaly managed and follow consistent standards and practices, similar to how this is managed within a professional team; in that sense I treat it like the standards and best practices for my personal projects and my personal projects can be seen as a team but then with one developer. TODO: add this is NOT to mimic enterprise/industry standards, but genuinely because it adds a lot of value and is worth the effort and time invested because it provides clarity, consistency, and efficiency in managing my personal projects together with automation and tooling, etc., which saves me time, is self-documenting, etc.

TODO: add also: NOT making it an open-source repo anymore where I add many things like generic usable tools, AI skills, etc. That conflicts with my goal of keeping this repo focused on my personal development hub and personal projects management. You cannot do both. 
TODO: add but still open-source so others can see and use it, and it becomes my portfolio, etc.
TODO: so add historical note that before tried to do both open-source generic tools and personal project management in this repo, which led to conflicts and lack of focus and added a lot of unnecessary noise and complexity, etc. Now not doing that anymore because <add reasoning here why>.

TODO: also update homelab setup: reference to my DevHub for the workspace setup, personal projects things, etc. This is still the central place for instructions, etc.

## GitHub subscription
TODO: add here stating GitHub Subscription -> Pro (cheapest paid version) to unlock things like protection rules, etc. Otherwise, I do not have access to these features. 

## Improve docs setup
### Docs setup
TODO: add `docs/` folder where I add the best practice for documents, such as COPILOT-SETUP.md, STANDARDS.md, etc.
TODO: move all .github/**/*.md files to `docs/` to create 1 source of truth for the documentation in this repo, not separate scattered locations, etc.

TODO: add a file like CONVENTIONS_STANDARDS.md to define coding conventions, naming standards, and other best practices for this repo and my personal projects. 
TODO: there add repo structure/naming, such as `devhub-{category}-{project}`, where `{category}` could be `ansible`, `terraform`, `go`, `homelab`, etc., and `{project}` is the specific project name within that category.

TODO: add design for repos and packages in DevHub docs such as when to create separate repo, when to use one, etc., make it so that you version a managed “thing” together, such as if you want versioning of multiple packages together that is also fine (e.g. for monitoring a Python monitoring package and Helm chart OR for example my DevHub which contains reusable scripts, workflows/CI/CD, AI things, docs, etc.) or if you want separate that is also fine, such as a separate SDK package versioned separately, etc.
### Task tracking
TODO: add task tracking for DevHub centrally, not for individual personal projects anymore such as my homelab.
TODO: update devhub-homelab repo with explaining shortly only task tracking is a good option and should be done because <reasons present there now...>, and then add for my DevHub I centrally do it for all my projects because everything is basically DevHub, etc. :)!
TODO: consider and document homelab like it is really part of my DevHub and DevHub is really my central place, etc.

## Cleanup & Refactor of unused
TODO: remove entire `scripts/` folder and any references to it. It is not used currently and specific to Azure I had in one of my earlier PP setups, etc. Also, no need for `scripts/` for now anyway so can be removed entirely.

## Introduce `tools/` & Automated repo management in that folder and others
TODO: introduce a `tools/` folder where I can place tooling around DevHub, such as scripts for automated repo management, setup, and maintenance tasks, etc.

TODO: remove the `install/` folder and any references to it. It is not the best setup currently; move to `tools/` instead for better organization and maintainability. Keep it simple and make it into 1 script. TODO: add here a part to add in ~/.bashrc to automatically do a git pull and keep a reference to latest version/commit to update the instructions file automatically, etc. Do it in a script in `tools/` folder and add setup steps here so that it only needs to use the script and not a lot of code is in your ~/.bashrc, etc. This would likely be a git clone first, then point it to the cloned location on your disk to the script in ~/.bashrc and that script should also keep this script up to date with a `git pull`, etc.

## GitHub Actions & Versioning & Dependabot
### Actions
TODO: add GitHub Actions here, with parts:
- Generic/reusable: Reusable actions and workflows that can be used across multiple repositories and projects -> used specifically for my personal projects repos.
- This repo: Specific actions to automate tasks related to DevHub, such as checking documentation, the reusable actions, etc.

TODO: add a GitHub action that checks the documentation, here can just add in the action itself such as checking that all workflows and actions have been referenced in the corresponding documentation files, the Copilot skills and instructions have their own files, etc.; see my work projects for an example how you can do that.
### Versioning
TODO: add CHANGELOG.md to this DevHub and release 1.0.0 after all the changes in this TODO.md.
TODO: add a GitHub action that does this automatically for DevHub with git tag and also checks that the CHANGELOG.md contains the corresponding version entry (e.g. can check if the current latest git tag is not equal to the latest version in the CHANGELOG.md, because that would indicate that the new version is not in CHANEGLOG.md because the CHANGELOG.md has not been updated yet for the new version in the repository) -> also the CHANGELOG.md is the source of truth for the versioning information (it is present for each version anyway), so the action can release the version based on the CHANGELOG.md entry. This ensures that the versioning is consistent and automated, reducing manual errors and keeping the repository up to date with the latest release information.
### Dependabot
TODO: also add dependabot here, used for the reusable workflow dependencies. See my work projects for an example.
### Templates
TODO: add templates for the specific repos, such as an Ansible repo, Terraform, Go projects, containers, etc.
### Homelab updates
TODO: add a TODO for homelab public actions where it checks that each file follows the structure, etc.
### Rollout & Integration
TODO: make a TODO for roll out and integration.

## Tools setup such as packaging & Actions design
TODO: see dns-devhub, use the same setup here with a `devhub-tools` package used for all things like packaging, etc.
TODO: add same reasoning in that README.md as with my work projects such as independently versioned, local usage, not vendor-lockin for GitHub Actions, etc. And also it can be properly tested, etc.
TODO: GitHub Actions are wrappers that use that tooling, etc.
TODO: add the package `devhub-tools` in separate repo and link to it in this DevHub repo.
TODO: make it in Python; add in README.md tool choice Python because it is widely used, has a rich ecosystem for packaging and tooling, and allows for easy integration with GitHub Actions and other automation workflows, etc.

## DevHub SDK repos
TODO: split up into separate repos, allows specific versioning and independent release cycles for each SDK component, also specific selection for actions based on langauge such as Go and Python, and no drawback because it can be added in the same workspace in VS Code anyway to have it open next to each other, etc.

## GitHub Copilot
TODO: Copilot setup: add specific for this repo that usually you also have work and you can still use both. For example, you can create a `~/projs/personal` and `~/projs/work` structure and add the `copilot-instructions.md` file in each to guide Copilot accordingly, which allows you to use a work `copilot-instructions.md` and a personal `copilot-instructions.md` without conflicts.

TODO: update setup in homelab repos -> NO copilot setup needed anymore, also not the sanitize because that can just be a prompt and the copilot-instructions.md uses it correctly, etc.

### Remove all those unnecessary AI skills and agents; improve setup
TODO: the AI skills and agents setup is now very bad, it is so much information and noise and it is maintenance-heavy because it is 1 skill per type such as devhub-terraform-change, devhub-ansible-change, devhub-docs, devhub-generic-change, etc. Also, I am trying to steer Copilot for everything now, such as with auto-discover, etc. However, the default Copilot setup should be used and that is the best setup; I am only creating a lot of noise that can steer it in the wrong direction and make it harder to maintain and use effectively. What I am trying to do is basically the `copilot-instructions.md`. Therefore, I need to remove all unnecessary AI skills and agents and improve the overall setup to be simpler, more maintainable, and aligned with the default Copilot configuration.

TODO: do create separate instructions in instructions folder for specifics such as Java, Go, Python, Docker, etc.

TODO: add in `COPILOT-SETUP.md` the design and shortly the explanation that is now in `.github/AI.md` or `.github/OVERVIEW.md`; focus on only shortly adding what each part is such as instructions, skills and agents, etc. **TODO: add stating also how to create an instructions file with only keeping it short and avoiding very long and unnecessary explanations, etc.**

TODO: also add a document in `docs/` explaining the design of Copilot things like skills, agents, instructions, etc., and add the learning of this point here for me, such as not those skills anymore because then I am reinventing Copilot and providing so much unnecessary noise, etc., but just mostly in 1 `copilot-instructions.md` file with all the generic things like code standards, etc., and then for specific tools/languages another instructions part such as Dockerfile, Java, Go, Python, etc.

TODO: see full AI chat with MS Copilot for this as context, etc.:
```
Yes. The architectural change is essentially not “back to lots of skills,” but from one monolithic instruction file to layered instructions:

.github/copilot-instructions.md remains the always-applicable baseline.
.github/instructions/*.instructions.md contains focused technology/domain guidance, using applyTo.
A Java task therefore gets baseline + Java, a Python task baseline + Python, and so on.
Skills remain reserved for specialized procedures, not ordinary Java/Python/Go/Terraform development.
Agents remain reserved for genuinely distinct roles.

Below is your original context rewritten around that model, while preserving the detailed architectural reasoning.

Context: Simplify DevHub GitHub Copilot Customization Architecture Through Layered Instructions

The current DevHub approach to GitHub Copilot customization has become more complicated than necessary.

DevHub contains a growing collection of GitHub Copilot Agent Skills, such as devhub-terraform-change, devhub-ai-customization, and potentially other technology-specific change skills. These skills contain useful engineering guidance, but there is a structural problem with how responsibilities have been divided between repository-wide Copilot instructions, path-specific instructions, skills, and custom agents.

The main conclusion is:

Move general engineering behavior into .github/copilot-instructions.md, and move technology-specific conventions into focused .github/instructions/*.instructions.md files using applyTo. The central instructions remain the common baseline. Technology-specific instructions are added on top when applicable. Keep skills only for genuinely specialized reusable procedures, and custom agents only for genuinely distinct roles.

The objective is to substantially simplify the customization architecture, reduce duplication, keep irrelevant technology guidance out of tasks where it does not apply, and rely more on Copilot's normal agentic capabilities.

The desired model is:

.github/
├── copilot-instructions.md
├── instructions/
│   ├── java.instructions.md
│   ├── python.instructions.md
│   ├── go.instructions.md
│   ├── terraform.instructions.md
│   ├── ansible.instructions.md
│   ├── docker.instructions.md
│   ├── github-actions.instructions.md
│   └── ...
├── skills/
│   └── ...only genuinely specialized reusable workflows...
└── agents/
    └── ...only genuinely distinct roles...


The important architectural principle is:

Use .github/copilot-instructions.md for the rules that form the shared engineering baseline. Add focused path-specific instruction files for technologies or file categories that have meaningful specific conventions. Only promote something into a skill or custom agent when instructions are insufficient because the task itself represents a specialized procedure or role.

Conceptually:

                  Normal Copilot
                        +
          .github/copilot-instructions.md
              always-common baseline
                        +
                        |
             applicable instructions
                        |
       +----------------+----------------+
       |                |                |
     Java             Python             Go
       |                |                |
 java.instructions  python.instructions go.instructions
       |                |                |
       +----------------+----------------+
                        |
                 Development task
                        |
             Specialized procedure?
                        |
                       yes
                        v
                     Skill
                        |
               Distinct agent role?
                        |
                       yes
                        v
                  Custom agent


The central file and the specific files have different responsibilities. They are not competing alternatives.

Why the current approach became unnecessarily complex

A skill such as devhub-terraform-change looks like a Terraform-specific capability, but much of its content is not actually Terraform-specific.

It may contain concepts such as:

act as an experienced software engineer;
discover repository guidance before changing files;
inspect AGENTS.md;
inspect .github/copilot-instructions.md;
inspect relevant documentation;
understand repository structure before editing;
inspect nearby implementations;
follow existing project conventions;
preserve unrelated user changes;
avoid unrelated refactoring;
avoid unnecessary tooling;
document code appropriately;
determine whether tests are real or placeholders;
discover project validation commands;
report checks that could not be performed;
inspect Git status and diffs;
consider untracked files;
avoid committing or pushing automatically;
compose commit messages from the complete pending change set;
avoid Copilot co-author attribution by default;
provide useful completion reports.

These are not fundamentally Terraform procedures.

They describe how Copilot should generally behave as an engineer while working in a repository.

If the same philosophy is repeated in:

devhub-terraform-change
devhub-python-change
devhub-java-change
devhub-go-change
devhub-ansible-change
devhub-docker-change
devhub-documentation-change
...


DevHub effectively implements inheritance manually.

The conceptual structure becomes:

Terraform skill
    = generic engineering behavior
    + repository discovery
    + documentation policy
    + testing policy
    + Git policy
    + reporting policy
    + Terraform behavior

Python skill
    = generic engineering behavior
    + repository discovery
    + documentation policy
    + testing policy
    + Git policy
    + reporting policy
    + Python behavior

Java skill
    = generic engineering behavior
    + repository discovery
    + documentation policy
    + testing policy
    + Git policy
    + reporting policy
    + Java behavior

Go skill
    = generic engineering behavior
    + repository discovery
    + documentation policy
    + testing policy
    + Git policy
    + reporting policy
    + Go behavior


That is the wrong abstraction.

The common part belongs in one shared baseline. The technology-specific part belongs in scoped instructions.

The new layered model

Instead of reproducing the common engineering baseline inside every technology customization, define it once:

.github/copilot-instructions.md


Then layer relevant technology instructions on top:

.github/copilot-instructions.md
        +
java.instructions.md
        =
Java engineering behavior


Likewise:

.github/copilot-instructions.md
        +
python.instructions.md
        =
Python engineering behavior


and:

.github/copilot-instructions.md
        +
go.instructions.md
        =
Go engineering behavior


A task involving several technologies can consequently draw from the common baseline plus the applicable specialized instructions rather than requiring a custom "change skill" for every combination.

For example, a change involving a Java application and its Docker image conceptually becomes:

general repository instructions
            +
Java-specific instructions
            +
Docker-specific instructions
            =
context for the task


The goal is therefore composition rather than duplication.

Why not put everything in one large copilot-instructions.md?

A single file is attractive because it has one obvious location and eliminates file-management complexity.

However, once instructions become significantly technology-specific, the single-file model has disadvantages.

Suppose DevHub supports:

Java;
Python;
Go;
Terraform;
Ansible;
Docker;
Helm/Kubernetes;
GitHub Actions;
documentation conventions;
testing conventions.

If every rule lives in the central file, a Python task can unnecessarily coexist with extensive Java, Terraform, Go, Kubernetes, and Docker guidance.

More importantly, language-specific conventions may legitimately differ.

For example:

Java
- follow Java naming conventions
- use the project's build system
- follow project conventions for exceptions
- preserve framework architecture

Python
- follow Python naming conventions
- respect the project's formatter/linter configuration
- use the project's dependency-management approach
- follow project typing conventions

Go
- follow Go naming and package conventions
- keep code compatible with the module's declared Go version
- use the repository's formatting and analysis tooling
- follow normal Go error-handling patterns

Terraform
- preserve resource addresses unless changing them intentionally
- consider state compatibility
- protect sensitive values
- do not perform destructive infrastructure operations implicitly


These are useful instructions, but they do not need to consume equal attention for every task.

The layered model gives DevHub the benefits of centralization without forcing all technology guidance into the universal layer.

The central instructions are still authoritative baseline guidance

The existence of java.instructions.md, python.instructions.md, or go.instructions.md does not mean the general engineering rules should be copied into those files.

That distinction is central to the design.

For example, .github/copilot-instructions.md could contain:

# Engineering

- Understand relevant repository conventions before editing.
- Keep changes focused on the requested outcome.
- Preserve unrelated user changes.
- Prefer simple, maintainable solutions over unnecessary abstractions.
- Follow existing project architecture unless the task intentionally changes it.

# Documentation

- Keep documentation accurate, concise, and aligned with implementation.
- Update documentation when behavior or interfaces materially change.

# Validation

- Discover and use the repository's existing validation workflow.
- Validate changed behavior to the extent practical.
- Report relevant validation that could not be performed.

# Git

- Review the resulting diff before completing substantial changes.
- Do not commit, push, or modify unrelated work unless explicitly requested.


Then java.instructions.md does not repeat those rules.

It only adds Java-specific behavior, for example:

---
applyTo: "**/*.java"
---

# Java

- Follow the Java version and build configuration declared by the project.
- Follow existing package and module boundaries.
- Prefer established project patterns over introducing a new framework or library.
- Follow the repository's conventions for nullability, exceptions, logging, and dependency injection.
- Use the project's existing test framework and build tooling.


Likewise:

---
applyTo: "**/*.py"
---

# Python

- Follow the Python version declared by the project.
- Follow the repository's formatter, linter, type-checker, and import conventions.
- Preserve the project's dependency-management approach.
- Follow existing typing and exception-handling conventions.
- Use the project's established test framework.


And:

---
applyTo: "**/*.go"
---

# Go

- Follow the Go version declared by the module or project.
- Preserve established package boundaries.
- Follow standard Go formatting and repository naming conventions.
- Handle errors explicitly and consistently with surrounding code.
- Use the project's established test and static-analysis tooling.


The important architectural relationship is:

copilot-instructions.md provides the shared engineering baseline; applicable .instructions.md files provide the delta.

This prevents every language file from becoming another self-contained engineering handbook.

Instructions versus skills: the key distinction

The useful distinction should no longer be:

Terraform = skill
Python    = skill
Java      = skill
Go        = skill
Ansible   = skill
Docker    = skill


Technology alone does not make something a skill.

Instead:

Repository-wide instructions describe how work in the repository should normally be done regardless of technology.

Path-specific instructions describe additional conventions that apply to particular files, languages, technologies, or areas of the repository.

Skills describe how to perform a specialized reusable procedure.

Custom agents represent genuinely distinct roles or operating behavior.

This produces a much cleaner separation.

Consider:

"Add input validation to this Terraform module."

Terraform is technological context.

The task does not inherently require a Terraform workflow skill.

Copilot already understands Terraform editing. DevHub needs to supply the engineering constraints that matter:

preserve resource addresses unless intentionally changing them;
consider Terraform state compatibility;
handle sensitive values appropriately;
respect provider/version constraints;
use repository validation tooling;
avoid implicitly executing destructive infrastructure operations.

Those belong naturally in:

.github/instructions/terraform.instructions.md


The general rules about Git, documentation, repository discovery, focused changes, and validation remain in:

.github/copilot-instructions.md


The same applies to:

"Fix this Java service."

"Refactor this Python function."

"Improve this Go package."

"Fix this Ansible task."

"Improve this Dockerfile."

These are ordinary engineering tasks carried out in different technological contexts.

Technology-specific instruction files now have a clear purpose

The previous architecture risked making either skills or one giant central file responsible for every technology.

The better structure is deliberate layering:

.github/
├── copilot-instructions.md
└── instructions/
    ├── java.instructions.md
    ├── python.instructions.md
    ├── go.instructions.md
    ├── terraform.instructions.md
    ├── ansible.instructions.md
    ├── docker.instructions.md
    ├── helm.instructions.md
    └── github-actions.instructions.md


But these files should exist because there are useful specific instructions, not simply because a technology happens to exist in the repository.

For example, do not create:

ruby.instructions.md


merely because one Ruby file exists.

Create it when DevHub has meaningful Ruby conventions worth giving Copilot.

This guards against replacing "skill explosion" with "instruction-file explosion."

Avoid duplication between central and specific instructions

The most important maintenance rule for the new setup is:

Technology-specific instruction files should contain the smallest useful delta from the central instructions.

Do not write every file as if it must function independently.

Bad:

java.instructions.md

- inspect the repository
- inspect AGENTS.md
- inspect documentation
- preserve unrelated changes
- don't commit automatically
- inspect Git diff
- run validation
- report failures
- follow Java conventions


Then:

python.instructions.md

- inspect the repository
- inspect AGENTS.md
- inspect documentation
- preserve unrelated changes
- don't commit automatically
- inspect Git diff
- run validation
- report failures
- follow Python conventions


That recreates the original problem.

Instead:

copilot-instructions.md

- repository discovery
- change discipline
- documentation principles
- validation principles
- Git behavior
- completion/reporting expectations


while:

java.instructions.md
    = Java-specific delta

python.instructions.md
    = Python-specific delta

go.instructions.md
    = Go-specific delta

terraform.instructions.md
    = Terraform-specific delta


Conceptually:

effective Java guidance
    = central baseline
    + Java delta

effective Python guidance
    = central baseline
    + Python delta

effective Go guidance
    = central baseline
    + Go delta


This is the core of the revised architecture.

Avoid over-instructing the agent

The move to separate instruction files should not become an excuse to add enormous technology manuals.

For example, Terraform instructions do not need to tell Copilot mechanically to inspect every possible file:

main.tf
variables.tf
outputs.tf
versions.tf
providers.tf
.terraform.lock.hcl
modules/
examples/
tests/
test/
*.tftest.hcl
Makefile
Taskfile.yml
.github/workflows/
docs/
...


Likewise, Java instructions do not need an exhaustive list such as:

pom.xml
build.gradle
build.gradle.kts
settings.gradle
src/main/java
src/test/java
application.yml
application.properties
...


And Python does not need:

pyproject.toml
setup.py
setup.cfg
requirements.txt
requirements-dev.txt
tox.ini
pytest.ini
...


unless a particular file has special significance that Copilot repeatedly misses.

The better policy is outcome-oriented:

Inspect the repository structure, nearby implementation, project configuration, documentation, tests, and validation tooling relevant to the requested change before editing.

Then technology instructions describe the differences that actually matter.

The customization should not re-teach Copilot how to navigate a software repository.

Team and project truth still needs the correct scope

The distinction between reusable DevHub guidance and project-specific facts remains important.

For example:

artifacts.kpn.org
jip/{category}/{module}
specific OpenShift permission conventions
specific test-results locations
team-specific CI requirements


are facts about a particular environment.

They should not accidentally become universal engineering assumptions.

The architecture therefore distinguishes four levels.

1. General engineering behavior

Examples:

preserve unrelated edits
keep changes focused
discover existing conventions
prefer simple maintainable solutions
validate relevant changes
do not commit automatically


These belong in:

.github/copilot-instructions.md

2. Technology-specific engineering behavior

Examples:

Java package/exception conventions
Python typing and formatter conventions
Go package/error conventions
Terraform state compatibility
Docker build/security conventions
Ansible idempotency conventions


These belong in:

.github/instructions/*.instructions.md


with appropriate applyTo scoping.

3. Project/team-specific facts

Examples:

registry = artifacts.kpn.org
specific image naming conventions
OpenShift runtime model
specific CI requirements
team-specific directory conventions


These belong only in repository instructions where they are actually true.

Depending on their applicability, they may be central repository instructions or appropriately scoped path-specific instructions.

4. Specialized procedures

Examples:

perform a release
migrate a Terraform provider
diagnose a particular CI failure
create or restructure a DevHub Copilot customization
perform a complex repository migration


These may justify skills.

This prevents DevHub from turning organizational assumptions into universal engineering laws.

When a skill is still appropriate

Skills should not disappear.

A skill is valuable when there is a meaningful reusable procedure, instead of merely a collection of conventions.

Potentially good skill concepts include:

devhub-release-package
devhub-debug-github-actions-failure
devhub-migrate-terraform-provider
devhub-ai-customization


For example, a release skill might genuinely encode:

determine release scope
        ↓
inspect pending/released changes
        ↓
determine version
        ↓
update version metadata
        ↓
update changelog/release notes
        ↓
run release-specific validation
        ↓
verify artifacts
        ↓
prepare release handoff


That is qualitatively different from:

Follow the project's Java package naming conventions.


or:

Preserve Terraform resource addresses unless intentionally changing them.


The first is a reusable procedure.

The latter examples are engineering instructions.

devhub-terraform-change should probably stop being a skill

Under this revised model, devhub-terraform-change remains a prime candidate for dissolution, but its content now has two instruction destinations rather than one.

Its reusable components should be divided into:

General engineering behavior

Move principles such as:

engineering judgment;
repository discovery;
focused changes;
preservation of unrelated edits;
documentation philosophy;
general validation philosophy;
Git handling;
reporting expectations;
attribution policy;

into:

.github/copilot-instructions.md

Terraform-specific engineering behavior

Move rules concerning:

Terraform state compatibility;
resource addresses;
variables and outputs;
provider compatibility;
sensitive values;
Terraform-specific validation;
infrastructure side effects;
destructive operations;

into:

.github/instructions/terraform.instructions.md


with appropriate Terraform applyTo patterns.

Procedural noise

Remove text that merely gives Copilot exhaustive instructions for navigating an ordinary repository unless it addresses a demonstrated recurring problem.

The result preserves the engineering safeguards without retaining the unnecessary wrapper of a Terraform "change workflow."

The same migration strategy applies to Java, Python, and Go

Do not replace:

devhub-java-change
devhub-python-change
devhub-go-change


with three equally huge instruction files.

Instead, decompose each source customization.

For each rule, ask:

Is this universally useful engineering behavior?

Move it to:

.github/copilot-instructions.md

Is this genuinely specific to Java?

Move it to:

.github/instructions/java.instructions.md

Is this genuinely specific to Python?

Move it to:

.github/instructions/python.instructions.md

Is this genuinely specific to Go?

Move it to:

.github/instructions/go.instructions.md

Is this an actual reusable workflow?

Keep or create a skill.

Does it need a fundamentally different role?

Only then consider a custom agent.

devhub-ai-customization remains more defensible as a skill

devhub-ai-customization is different because it describes an actual specialized task:

understand requested customization
        ↓
determine whether customization adds value
        ↓
determine correct customization mechanism
        ↓
determine appropriate scope
        ↓
create/update the correct customization
        ↓
update catalogs/references when relevant
        ↓
validate customization
        ↓
report result


That has procedural identity.

Therefore it can remain a skill.

However, it should be substantially smaller than a skill that carries its own complete engineering policy.

It should rely on:

.github/copilot-instructions.md


for normal engineering behavior.

If its implementation touches Java, Python, Markdown, YAML, or another scoped area, the corresponding applicable instructions can provide the relevant technological conventions.

The skill itself should concentrate on the knowledge specific to designing and maintaining Copilot customizations.

Revised customization decision hierarchy

The DevHub customization philosophy should become:

1. Can normal Copilot already perform the task adequately?
                |
          yes -> nothing
                |
               no
                v
2. Is the missing guidance universal repository behavior?
                |
          yes -> .github/copilot-instructions.md
                |
               no
                v
3. Is the missing guidance specific to files, languages,
   technologies, or repository areas?
                |
          yes -> .github/instructions/*.instructions.md
                 with appropriate applyTo scope
                |
               no
                v
4. Is this a reusable specialized procedure?
                |
          yes -> SKILL.md
                |
               no
                v
5. Does the use case genuinely require a distinct
   agent role, boundaries, or behavior?
                |
          yes -> custom agent


This is a more precise hierarchy than either extreme:

everything -> one copilot-instructions.md


or:

every technology -> skill


The intended middle ground is:

shared policy -> central instructions
specific policy -> scoped instructions
procedure      -> skill
role           -> agent

A useful classification test

For every rule, first ask:

Should this rule apply regardless of which technology I am changing?

If yes:

.github/copilot-instructions.md


Examples:

Preserve unrelated edits.
Do not commit automatically.
Keep changes focused.
Inspect relevant existing implementation before changing behavior.
Use project-native validation.


If no, ask:

Is the rule a convention associated with a particular language, technology, file type, or repository area?

If yes:

.github/instructions/<scope>.instructions.md


Examples:

Java exception conventions
Python typing conventions
Go package conventions
Terraform state compatibility
Docker image conventions
Ansible idempotency requirements


Then ask:

Is this actually a sequence of actions representing a reusable operation rather than a convention?

If yes:

SKILL.md


Finally:

Does it require a genuinely distinct operating role or agent behavior?

If yes:

.agent.md


This classification is stronger than using the technology name alone to decide the customization type.

Keep copilot-instructions.md relatively small and universal

Under the revised design, there is value in keeping the central file focused.

Not because it must be arbitrarily short, but because every entry there should justify being part of the shared baseline.

A good test is:

Would I want Copilot to consider this rule while editing Java, Python, Go, Terraform, YAML, Markdown, a Dockerfile, or another normal part of this repository?

If yes, central instructions are appropriate.

This can include:

general engineering behavior;
repository discovery principles;
change discipline;
documentation philosophy;
general testing/validation policy;
Git behavior;
dependency principles that truly apply repository-wide;
security principles that truly apply repository-wide;
completion/reporting expectations.

It should normally not contain detailed conventions for every language simply because DevHub happens to support them.

But do not over-fragment instructions either

The new architecture should not become:

java-naming.instructions.md
java-testing.instructions.md
java-spring.instructions.md
java-errors.instructions.md
java-logging.instructions.md
python-formatting.instructions.md
python-testing.instructions.md
python-typing.instructions.md
...


That merely introduces another composition framework to maintain.

Prefer one coherent scoped file per meaningful technological area:

java.instructions.md
python.instructions.md
go.instructions.md
terraform.instructions.md
docker.instructions.md


Split further only when there is a real scoping reason.

For example, if a large monorepo contains two genuinely different Java application families with incompatible architectural expectations, narrower path-specific files may make sense.

The goal remains:

Minimum customization structure necessary to express the actual engineering differences.

Avoid turning scoped instruction files into giant skills

Moving content out of skills does not mean copying each skill verbatim into .github/instructions/.

That would just rename the problem.

Migration requires compression, deduplication, and classification.

Suppose six existing skills contain variations of:

Read README.
Read CONTRIBUTING.
Find AGENTS.md.
Read Copilot instructions.
Check docs.
Inspect CI.
Inspect tests.
Inspect neighboring modules.
Discover conventions.
Run validation.
Review Git status.
Report validation.


Do not put those paragraphs into all six new .instructions.md files.

Centralize the underlying intention once in .github/copilot-instructions.md, for example:

Discover and follow repository-local guidance, existing implementation patterns, documentation, tests, and project-native validation relevant to the requested change before making substantial edits.

Then allow each specific file to concentrate on its actual subject.

Migration should repeatedly ask:

What behavior were these paragraphs actually trying to guarantee, and at what scope should that behavior live?

Desired end state

The intended DevHub architecture should be simple enough to explain in a few sentences:

.github/copilot-instructions.md defines the common engineering baseline for work in the repository.

.github/instructions/*.instructions.md adds specific conventions for applicable languages, technologies, file types, or areas, such as Java, Python, Go, Terraform, Docker, Ansible, and GitHub Actions.

The central guidance is not duplicated into those files. Instead, the specific instructions add the rules that differ or matter only in their scope.

Skills exist only for specialized reusable procedures whose workflow adds material value beyond normal Copilot behavior plus instructions.

Custom agents exist only where a genuinely different role or operating model is useful.

Visually:

                     Normal Copilot
                           |
                           v
              +--------------------------+
              | copilot-instructions.md  |
              |                          |
              | Common engineering       |
              | Repository behavior      |
              | Git / docs / validation  |
              +------------+-------------+
                           |
                    always baseline
                           |
                           v
              +--------------------------+
              | Applicable scoped        |
              | instructions             |
              +--------------------------+
                 /       |       \
                /        |        \
             Java      Python      Go
               |          |         |
            *.java      *.py       *.go

       Terraform / Docker / Ansible / etc.
             applied when relevant

                           |
                           v
                Most development tasks
                           |
                 Specialized procedure?
                           |
                          yes
                           v
                       SKILL.md
                           |
                  Distinct agent role?
                           |
                          yes
                           v
                       .agent.md


This is considerably simpler than:

generic-change
terraform-change
python-change
java-change
go-change
ansible-change
docker-change
helm-change
documentation-change
testing-change
...


where each customization partially reimplements the same engineering philosophy.

Concrete setup change to make

Treat the migration as one architectural simplification, not as creating another customization framework.

Establish .github/copilot-instructions.md as the source of common repository-wide engineering guidance.

Consolidate shared engineering behavior there:

repository discovery;
focused changes;
preservation of unrelated work;
documentation principles;
general testing and validation;
safe Git handling;
general security/safety expectations;
completion/reporting expectations.

Establish .github/instructions/ as the location for scoped engineering conventions.

Create focused files only where meaningful conventions exist, for example:

java.instructions.md
python.instructions.md
go.instructions.md
terraform.instructions.md
ansible.instructions.md
docker.instructions.md
github-actions.instructions.md
helm.instructions.md


Give each file an appropriate applyTo scope so its guidance is relevant to the files/tasks it is intended to govern.

Do not repeat central engineering rules inside the scoped files.

Keep project/team-specific facts only where they are actually applicable. Do not globally impose DNS/KPN-specific assumptions on unrelated projects.

Review every existing DevHub skill.

For each skill, classify its contents into:

common repository-wide instruction;
scoped technology instruction;
actual reusable procedure;
unnecessary procedural narration.

Move common rules into .github/copilot-instructions.md.

Move genuinely technology-specific rules into the corresponding .github/instructions/*.instructions.md.

Delete skills whose remaining content does not represent a meaningful specialized procedure.

Keep and simplify skills that genuinely implement reusable procedures, such as devhub-ai-customization.

Do not create new custom agents merely to compensate for removing technology-specific skills.

Do not create excessive tiny scoped instruction files merely for organizational purity.

Reduce wordiness during migration. Preserve important constraints and reasoning, not every navigation step previously encoded in skills.

Update DevHub's own customization guidance so the default hierarchy becomes:

normal Copilot
     ↓
common repository instructions
     ↓
applicable scoped instructions
     ↓
specialized skill, only when needed
     ↓
custom agent, only when genuinely needed


The outcome should be fewer skills, less duplicated text, better scoping, and clearer ownership of every engineering rule.

Core principle to preserve

This simplification does not mean abandoning detailed engineering standards.

It means placing each standard at the correct abstraction level.

The existing DevHub skills may contain valuable thinking around:

compatibility;
testing;
repository discovery;
documentation;
safe Git handling;
language conventions;
infrastructure side effects;
maintainability.

That work should not be discarded.

Instead:

Preserve the engineering intent while removing the machinery that repeatedly delivers the same intent.

Much of the current thoroughness is policy expressed as procedure.

The new model turns that into layered policy:

Universal policy
    -> .github/copilot-instructions.md

Technology/file-specific policy
    -> .github/instructions/*.instructions.md

Specialized procedure
    -> skill

Distinct role
    -> custom agent


This allows Copilot to handle ordinary engineering tasks normally while still receiving precise instructions for the technology actually involved.

Final decision

Use .github/copilot-instructions.md as the common engineering baseline and .github/instructions/*.instructions.md for focused technology-specific guidance. The specific instructions complement the central instructions rather than replacing or duplicating them.

Provide scoped instruction files for technologies such as Java, Python, Go, Terraform, Ansible, Docker, GitHub Actions, and Helm/Kubernetes when DevHub has meaningful conventions for them. Keep those files narrowly focused on what is actually specific to their scope.

Reduce or remove technology "change" skills that mostly wrap ordinary software-engineering behavior. Retain skills only where a distinct reusable procedure remains after general and technology-specific policy has been extracted. Retain custom agents only for genuinely distinct roles.

The governing architecture is therefore: central baseline + applicable scoped instructions + optional specialized procedure + optional distinct agent.

That gives DevHub a clearer composition model:

Common engineering behavior
             +
Technology-specific behavior when applicable
             +
Specialized workflow only when necessary


rather than forcing a choice between one giant instruction file and a large collection of duplicative skills.
```