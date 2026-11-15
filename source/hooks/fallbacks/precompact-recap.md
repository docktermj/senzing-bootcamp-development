## Fold the recap before the conversation is shortened

Nothing runs when the conversation is compacted or trimmed, so fold the in-progress recap
checkpoint into the recap at every point where it could be lost: at module completion, at
graduation, when the bootcamper says they are stopping, and whenever you are told the
conversation is about to be compacted. Run:

```bash
python3 "{{host.scripts_dir}}/precompact-recap.py" < /dev/null
```

It is safe to run more than once.
