## A failed run of generated code needs a worked steer

In Data collection; Data Quality, Mapping, and Transformation; Data processing; and Query,
Visualize and Discover: when a program you generated under `src/` fails when it runs, and the
module has no worked steer recorded yet, apply the "Worked steers" rule in `ground-rules.md`
before moving on. Only the module's first such failure needs it.
