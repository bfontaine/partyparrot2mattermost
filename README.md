# Partyparrot2mattermost

This repository contains a simple Python script to bulk-import [Party Parrot emojis][pp] in Mattermost.

## Usage

Clone the repository or copy the script somewhere on your server (e.g. `/tmp`), then run it:

    $ python gen_data.py

It downloads all emojis under a directory `partyparrot2mattermost` (use `--output <path>` to change this) and generates
a [JSONL metadata file][jsonl] for the import.

If needed, you can edit the file to remove the emojis you don’t want. Then, [follow the official instructions][howto] to
run the import:

```bash
cd /opt/mattermost
sudo -u mattermost bin/mattermost import bulk /path/to/the/file.jsonl --validate
sudo -u mattermost bin/mattermost import bulk /path/to/the/file.jsonl --apply
```

Once done, you can safely remove the script as well as the `partyparrot2mattermost` directory.

----
Note: this script is not affiliated nor endorsed in any way by the Party Parrot authors.

[pp]: https://cultofthepartyparrot.com/

[jsonl]: https://docs.mattermost.com/deployment/bulk-loading.html#data-format

[howto]: https://docs.mattermost.com/deployment/bulk-loading.html#running-the-bulk-loading-command
