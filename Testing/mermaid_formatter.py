
mermaid_input = '''graph TD\n    subgraph API_Blueprint\n        style API_Blueprint fill:#f9f,stroke:#333,stroke-width:2px\n        API_Blueprint[API Blueprint]\n        \n        subgraph Routes\n            style Routes fill:#ccf,stroke:#333,stroke-width:1px\n            Route_home[GET /]\n            Route_transcribe[POST /transcribe]\n            Route_summarise[POST /summarise]\n        end'''

print(mermaid_input)