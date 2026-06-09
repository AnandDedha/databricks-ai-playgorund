# Contributing to ShopMate AI

Thanks for your interest! This is a tutorial project, so contributions that make the learning experience clearer or more accurate are especially welcome.

## How to contribute

1. **Fork** the repo and create a feature branch from `main`:
   ```bash
   git checkout -b feat/your-improvement
   ```
2. **Make your changes.** Keep them focused — one logical change per PR.
3. **Test on a real Databricks workspace** if you're modifying SQL or notebooks.
4. **Update docs** if behaviour changes (README, CHANGELOG, relevant `docs/*.md`).
5. **Commit** with a clear message — see the convention below.
6. **Open a PR** against `main` with a short description of *what* and *why*.

## Commit message convention

We loosely follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

[optional body]
```

**Types:**

| Type | When to use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `data` | Sample data changes (CSVs, KB markdown) |
| `chore` | Tooling, gitignore, license, repo housekeeping |

**Examples:**

```
feat(uc-functions): add get_loyalty_benefits tool
fix(vector-search): correct chunking for nested markdown headers
docs(readme): clarify Volume upload step in quickstart
data(orders): add 5 Cancelled-status orders for return-eligibility demo
```

## What we WON'T accept

- 🚫 Real customer data or PII of any kind
- 🚫 Hard-coded secrets, tokens, or credentials
- 🚫 Large binary files (>5MB) — link out instead
- 🚫 Changes that make the tutorial harder to follow for a beginner

## Questions?

Open a [GitHub Discussion](../../discussions) or comment on the relevant YouTube video.
