## Close out when the bootcamper stops

Nothing runs when a session ends, so close out when the bootcamper says they are stopping, and
before any long pause. Run:

```bash
python3 "{{host.scripts_dir}}/session-end.py" < /dev/null
```

It folds the recap checkpoint into the recap and stops each container the bootcamp started.
It stops containers and never removes them, so the bootcamper's loaded data is there on resume.
Then say in one short paragraph what was completed, what is stopped but still present, and what
comes next.
