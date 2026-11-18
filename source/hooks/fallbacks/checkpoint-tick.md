## Keep the recap checkpoint

Once a module is recorded in `config/bootcamp_progress.json`, make sure
`docs/progress/recap_checkpoint.md` exists, and refresh it at every step boundary as the
"In-progress recap checkpoint" rule in `ground-rules.md` describes. To create the empty
scaffold, run:

```bash
python3 "{{host.scripts_dir}}/checkpoint-tick.py" < /dev/null
```

Where your shell is PowerShell, run this form instead:

```powershell
$null | python3 "{{host.scripts_dir_powershell}}/checkpoint-tick.py"
```

When the bootcamper accepts the "ready to move on to the next module" question or the
graduation offer, first check the module just completed for a missing record: a directing step
left unset, a reversed decision never filed, or a failed run with no worked steer. Repair what
is missing silently, then continue.
