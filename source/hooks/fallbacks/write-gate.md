## Keep files in the project, and secrets out of them

<!-- host:only chatgpt, claude, copilot, gemini, kiro -->
When it runs, a hook checks a write before it happens, but it may not run here.
<!-- host:end -->
<!-- host:except chatgpt, claude, copilot, gemini, kiro -->
Nothing checks a write before it happens.
<!-- host:end -->
So check every write yourself, every time:

- Every file the bootcamp creates or edits is written inside the bootcamper's project directory.
  Never write to the system temporary directory, to Downloads, to the home directory or above
  the project root, and never into the directory this bootcamp is installed in. That includes
  a shell command's output: `curl -o`, `wget -O`, a `>` redirect, `tee`, and the destination
  of `cp` or `mv`.
- No private key, access key or license payload goes into any file. Reference a secret by the
  name of the environment variable that holds it, never by its value.

If a step seems to need a write outside the project, stop and ask before writing.
