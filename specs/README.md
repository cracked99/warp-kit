# Specifications

This directory contains all feature specifications, implementation plans, and task breakdowns for this project.

## Structure

Each feature is organized in its own directory:

```
specs/
├── 001-feature-name/
│   ├── spec.md          # What should this feature do?
│   ├── plan.md          # How will we build it?
│   ├── tasks.md         # Ordered task breakdown
│   └── ...              # Supporting docs (contracts, research, etc.)
├── 002-another-feature/
│   └── ...
└── _templates/          # Base templates for new features
```

## Workflow

1. Create a new feature directory (or use `/speckit.specify`)
2. Write the functional specification (spec.md)
3. Clarify ambiguities with `/speckit.clarify`
4. Design the technical plan (plan.md)
5. Break into tasks (tasks.md)
6. Execute with `/speckit.implement`

## SDD Commands

- `/speckit.specify` – Create or refine a specification
- `/speckit.clarify` – Clarify ambiguous requirements
- `/speckit.plan` – Design the technical approach
- `/speckit.tasks` – Generate task breakdown
- `/speckit.implement` – Execute tasks
- `/speckit.analyze` – Cross-check artifact consistency
- `/speckit.checklist` – Generate quality checklists

## Tips

- Keep specs focused on WHAT and WHY, not HOW
- Use clarifications to record decisions
- Tasks should be granular and testable
- Reference the constitution for quality standards
