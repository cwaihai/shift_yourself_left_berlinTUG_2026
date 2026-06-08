This is a mini dlthub project created while demonstrating agentic data engineering at Berlin Tableau User Group in June 2026.

Pre-requisites:
- Have uv installed
- Have python 3.13 installed



***RUN AND CHECK THIS DLT PIPELINE***

1) Clone this repo

2) Run the pipeline
```
    uv run tableau_public_pipeline.py
```

3) Check what tables have been created and what the data looks like
```
    dlthub local show
```




***DEMO PART - IF YOU WANT TO REPRODUCE IT***

## Tools I used:
- Warp, agentic Command Line Interface (optional to the demo)
- Claude Vibe subscription (dlthub currently also support Copilot and Codex)


## How I ran the demo
1) Open your empty repo

```
    cd path/to/folder
```

2) Create and activate a virtual environment
```
    uv venv
    source .venv/bin/activate
```

3)  Initialize uv and download dlthub
```
    uv init
    uv add "dlt[hub]"
```

4) Initialize dlthub ai workbench feature with Claude
```
    uv run dlthub ai init --agent claude
```

5) Add the rest api skills as we will be working with Tableau Public API
```
    uv run dlthub ai toolkit install rest-api-pipeline
```

6) Open Claude within the terminal and start prompting
```
    claude
```

7) Prompt
```
    using dlthub ai toolkit and the context of this repo https://github.com/cwaihai/shift_yourself_left_berlinTUG_2026_context please build a dlt pipeline from tableau public to duckdb
```

8) Grab a coffee, quick check and approve requests from Claude and let him do light troubleshooting until a dlt pipeline, tableau_public_pipeline.py is created and run smoothly.
