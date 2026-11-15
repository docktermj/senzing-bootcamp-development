## Resume at the start of a session

At the start of every session in a bootcamp project, before anything else, run:

```bash
python3 "{{host.scripts_dir}}/session-start.py" < /dev/null
```

Follow what it prints: it names the module to resume, or says the bootcamp is complete. When it
prints nothing, no bootcamp is in progress in this project, and the four cases in
`SKILL.md` ("Fresh start vs. resume") decide what happens next.
