---
name: artifact
description: |-
  The `/artifact` entry point — read, create, update, delete, list, and traverse artifacts of any scheme (PR, issue, release, document, execution, file, directory, artifact-template, …) through the uniform provider contract. Also authors new templates + exposes the artifact graph. Triggered by "show a PR", "list my issues", "create a design-document", "edit artifact foo.md", "graph from release v2.3", "add a new backend", or any artifact-scheme URI like `issue|gh-issue/...`.
---

# artifact

All artifact operations route through the same contract: `run-provider.sh <URI-or-scheme>
<subcommand> [args...]`. The dispatcher resolves the backend (from the URI or from user
preference); the backend implements the scheme's subcommand surface.

## Sub-command shape

| Pattern                                    | What to do                                                   |
|--------------------------------------------|--------------------------------------------------------------|
| `show <uri>`                               | `run-provider.sh <uri> get --uri <uri>`                      |
| `list <scheme> [--filter ...]`             | `run-provider.sh <scheme> list [--filter ...]`               |
| `create <scheme> [key=val ...]`            | `run-provider.sh <scheme> create --data <json>`              |
| `create <template-uri> [inputs ...]`       | Instantiate from an `artifact-template` artifact             |
| `update <uri> --patch <json>`              | `run-provider.sh <uri> update --uri <uri> --patch <json>`    |
| `delete <uri>`                             | `run-provider.sh <uri> delete --uri <uri>`                   |
| `status <uri>`                             | `run-provider.sh <uri> status --uri <uri>`                   |
| `progress <uri>`                           | `run-provider.sh <uri> progress --uri <uri>`                 |
| `lock <uri> --owner <user>`                | `run-provider.sh <uri> lock --uri <uri> --owner <user>`      |
| `graph <uri> [--relation R] [--depth N]`   | `scripts/graph.sh expand --uri <uri> …`                      |
| `list schemes` / `list backends`           | Read `$ARTIFACT_CACHE_DIR/registry.json`                     |
| `show discovery`                           | Print the registry                                           |

URI format is `<scheme>|<backend>/<backend-specific-id>` (e.g.
`issue|gh-issue/myorg/myrepo#42`, `document|document-filesystem/notes/design.md`).

## Backend resolution

Kind-addressed calls (`create`, `list` without URI) resolve in this strict order:

1. Per-call `--backend <name>` override.
2. Saved preference `backends.<scheme>.default`.
3. Sole-backend short-circuit (persisted as the new default).
4. Prompt the user once, persist the answer.

URI-addressed calls dispatch to the backend named in the URI directly. Never alphabetical.

## Extending with your own providers, backends, templates

Four scopes by precedence (highest first):

| Scope       | Path                                                            | Purpose                                    |
|-------------|-----------------------------------------------------------------|--------------------------------------------|
| `override`  | `$CWD/.artifact-override/<bucket>/<name>/`                      | One-off; for this working tree only        |
| `workspace` | `$REPO/.claude/<bucket>/<name>/`                                | Project-specific; committed to repo        |
| `user`      | `~/.claude/<bucket>/<name>/`                                    | Personal; across all your projects         |
| `plugin`    | `<installed-plugin>/<bucket>/<name>/`                           | Shipped by a plugin; immutable via Claude Code |

`<bucket>` ∈ `artifact-providers`, `artifact-backends`, `artifact-templates`. Plugin scope is
immutable to agents (`pretooluse-no-self-edit.sh` refuses writes); author via override /
workspace / user scope or open a PR.

Recommended authoring flow:

```text
/artifact create artifact-template name=my-design-doc scope=workspace scheme=document ...
/artifact create artifact-provider name=jira-issue scope=user                   (future)
```

(The `conductor` workflow in the `workflow` plugin wraps this with an interactive draft →
review → write gate; either entry point works.)

## References

- `references/artifact-contract.md` — provider + backend subcommand surface, JSON shapes, error
  paths. Load when authoring or debugging a provider/backend.
- `references/discovery.md` — registry shape, scope precedence, diagnosing missing entries.
- `references/extension-scaffold.md` — step-by-step new-provider/new-backend guide.
- `references/creation.md` — template authoring.
- `references/composition.md` — graph edges (`composed_of`, `depends_on`, …) and how workflows
  use them for dep-gating + progress aggregation.

## Related skills

- `/workflow` — run and author workflows (which produce artifacts).
