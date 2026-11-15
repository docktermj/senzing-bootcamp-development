<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/senzing-logo-dark-theme.png">
    <img src="assets/senzing-logo-light-theme.png" alt="Senzing" width="240">
  </picture>
</p>

<h1 align="center">Senzing Agentic AI Bootcamp</h1>

<p align="center"><b>Go from zero to working entity resolution, inside your AI assistant.</b></p>

<img src="assets/ember-rule.svg" alt="" width="100%" height="4">

A guided, hands-on bootcamp for learning SENZING® entity resolution. Install it in your AI
assistant, say **"start the bootcamp"** and it walks you through the Senzing SDK module by
module, on your own data.

## Choose your assistant

The bootcamp is the same in every assistant. Pick yours for the install steps.

<!-- site:assistant-table -->

## What the bootcamp covers

A guided sequence of hands-on modules takes you from zero to working entity resolution:

- ***Bootcamp preparation:*** choose your curriculum, level of detail and programming language
- ***Entity Resolution Concepts:*** a primer on how entity resolution works *(optional)*
- ***Discover the Business Problem:*** describe the problem you are trying to solve
- ***SDK setup:*** install and configure the Senzing SDK
- ***System verification:*** end-to-end checks that the Senzing SDK works on your machine *(optional)*
- ***Truth Set visualization:*** an interactive web app of the resolved Truth Set data *(optional)*
- ***Data collection:*** identify and collect your data sources
- ***Data Quality, Mapping, and Transformation:*** make your data "Senzing-ready"
- ***Data processing:*** ingest your Senzing-ready data
- ***Query, Visualize and Discover:*** see what the Senzing SDK can do for you
- ***Bootcamp graduation:*** wrap up your bootcamp with a bow

## Requirements

- Network access to the [Senzing MCP server].
  The bootcamp cannot proceed without it.
  It generates SDK code,
  looks up Senzing facts
  and provides working examples.
- Python 3.
  The bootcamp's hooks and its graduation recap run on it.
- A plan on your assistant.
  Each assistant's minimum is in the table above.
- *Recommended, but not mandatory:*
  A business problem requiring entity resolution
  and 5,000 to 20,000 records that illustrate the problem.

## What you finish with

The bootcamp is a guided, module-by-module tutorial.
You end with working Senzing code and data in your project (`src/`, `data/`, `database/`),
a professional recap PDF you can keep and share (e.g. [bootcamp_recap.pdf], but yours will differ),
a write-up of what the Senzing SDK found in your data (`docs/bootcamp_data_discoveries.md`, also rendered as a PDF)
and a `production/` starter project.
At graduation you are also offered a narrated 2-minute graduation video
(`docs/bootcamp_recap.mp4`); say no and nothing is rendered.

## Feedback

Say **"bootcamp feedback"** at any time.
The bootcamp saves what you tell it to `docs/feedback/SENZING_BOOTCAMP_FEEDBACK.md` in your
project, and records which assistant you used so a problem in one assistant can be told from
a problem in the bootcamp itself.
Nothing is sent anywhere without your yes.
To share your feedback with Senzing, email that file to <support@senzing.com>.

## What is in this repository

| Path | What it holds |
| --- | --- |
| `plugins/<assistant>/senzing-bootcamp/` | The bootcamp, packaged for each assistant |
| `docs/` | The pages published at [hub.senzing.com/bootcamp] |

Every package is built from one source, so the bootcamp cannot differ between assistants.
The packages are generated; changes are made in the development repository and arrive here
as a tested release.

[bootcamp_recap.pdf]: https://raw.githubusercontent.com/Senzing/bootcamp/refs/heads/main/plugins/claude/senzing-bootcamp/docs/examples/bootcamp_recap.example.pdf
[hub.senzing.com/bootcamp]: https://hub.senzing.com/bootcamp/
[Senzing MCP server]: https://mcp.senzing.com/mcp
