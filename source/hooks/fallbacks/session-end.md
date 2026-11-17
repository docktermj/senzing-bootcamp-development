## Close out when the bootcamper stops

<!-- host:only chatgpt, claude, copilot -->
When it runs, a hook closes out as a session ends, but it may not run here.
<!-- host:end -->
<!-- host:except chatgpt, claude, copilot -->
Nothing runs when a session ends.
<!-- host:end -->
So close out when the bootcamper says they are stopping, and before any long pause. Run:

```bash
python3 "{{host.scripts_dir}}/session-end.py" < /dev/null
```

Where your shell is PowerShell, run this form instead:

```powershell
$null | python3 "{{host.scripts_dir_powershell}}/session-end.py"
```

It folds the recap checkpoint into the recap and stops each container the bootcamp started.
It stops containers and never removes them, so the bootcamper's loaded data is there on resume.
Then say in one short paragraph what was completed, what is stopped but still present, and what
comes next.
