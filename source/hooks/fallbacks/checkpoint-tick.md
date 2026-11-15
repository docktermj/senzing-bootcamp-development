## Keep the recap checkpoint

Once a module is recorded in `config/bootcamp_progress.json`, make sure
`docs/progress/recap_checkpoint.md` exists, and refresh it at every step boundary as
`module-completion.md` describes. To create the empty scaffold, run:

```bash
python3 "{{host.scripts_dir}}/checkpoint-tick.py" < /dev/null
```

When the bootcamper accepts the "ready to move on to the next module" question or the
graduation offer, first check the module just completed for a missing record: a directing step
left unset, a reversed decision never filed, or a failed run with no worked steer. Repair what
is missing silently, then continue.
