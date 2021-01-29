# Overview
This fork enables exporting annotations made in [hypothes.is](https://web.hypothes.is/) into local files in markdown format. This way it simplifies integration of web-annotation workflows into daily note processing with personal knowledge management apps like [Obsidian](https://obsidian.md/) or [Foam](https://github.com/foambubble/foam/).

For more details on how the general API for hypothes.is works, please visit the [original repo](https://github.com/judell/h_notify).

# Usage
First of all, make sure to properly edit the lines below from the `fetch_annotations.py` file to configure `h_notify` script to use your personal token and account information from `hypothes.is`:

```python
hypothesis_api_token = <your-secret-token-here>  # from your user account, typically starts with `6879-`
group_id = <your-secret-group-id>  # from your hypothesis account
group_name = <your-secret-group-name>  # from your hypothesis account
folder = <where markdown notes will be placed> # e.g., Daily Notes folder in Obsidian, can be empty
```

After that, the fetching process can be launched by running the command:
```bash
python fetch_annotations.py
```