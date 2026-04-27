# Phenotype Ralph Controller

This is a local controller for a Ralph-style Codex loop over the Phenotype shelf.

Start one iteration:

```bash
npx -y @iannuttall/ralph build 1 --agent=codex --no-commit --prd .agents/tasks/phenotype-perpetual-loop.json
```

Stop the perpetual wrapper:

```bash
touch /Users/kooshapari/CodeProjects/Phenotype/repos/.ralph-controller/STOP
```

