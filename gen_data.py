import argparse
import io
import json
import os
import re
from urllib import request
from zipfile import ZipFile

ROOT_URL = "https://cultofthepartyparrot.com"


def urlopen(url):
    req = request.Request(
        url,
        # For some reason the site rejects requests done with the default Python user-agent
        headers={
            'User-Agent': 'curl/7.37.0'
        })
    return request.urlopen(req)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--only-hd", action="store_true", help="Only include HD emojis")
    p.add_argument("--output", "-o", type=str, help="Output directory (will be created)",
                   default="partyparrot2mattermost")

    opts = p.parse_args()

    print("==> Getting the latest zip URL")
    with urlopen(ROOT_URL) as response:
        html = response.read().decode()

    m = re.search(r'href="(/parrots-[a-z0-9]+\.zip)"', html)
    if not m:
        raise Exception("Can't find the latest zip URL")

    zip_url = ROOT_URL + m.group(1)

    print("==> Downloading the zip")
    with urlopen(zip_url) as response:
        # we must read it entirely to seek it
        zipfile = ZipFile(io.BytesIO(response.read()))

    print("==> Preparing the emojis directory")
    output_directory = opts.output
    metadata_path = os.path.abspath(os.path.join(output_directory, "emojis.jsonl"))

    os.makedirs(output_directory, exist_ok=True)

    with open(metadata_path, "w") as metadata_writer:
        json.dump({"type": "version", "version": 1}, metadata_writer)
        metadata_writer.write("\n")

        emojis_count = 0
        for f in zipfile.infolist():
            filename = f.filename

            if not filename.startswith("parrots/") or not filename.endswith(".gif"):
                continue

            if opts.only_hd and "/hd/" not in filename:
                continue

            basename = os.path.basename(filename)
            path = os.path.abspath(os.path.join(output_directory, basename))
            with open(path, "wb") as fw:
                fw.write(zipfile.read(f))

            emojis_count += 1
            emoji_name = os.path.splitext(basename)[0]
            json.dump({
                "type": "emoji",
                "emoji": {
                    "name": emoji_name,
                    "image": path,
                },
            }, metadata_writer)
            metadata_writer.write("\n")

        print("==> Done (%d emojis)." % emojis_count)
        print("""
The emojis directory is {directory}
The JSONL metadata is in {path}

Do not move files around because the metadata refers to them using their absolute path.

To bulk import all emojis, follow the official documentation [1],
reproduced here for convenience:

    # change to the Mattermost directory
    $ cd /opt/mattermost
    
    # validate the import file
    $ sudo -u mattermost bin/mattermost import bulk {path} --validate

    # The command should print a bunch of logs, and this line near the end:
    # > Validation complete. You can now perform the import by rerunning this command with the --apply flag.
    # You can then proceed:
    sudo -u mattermost bin/mattermost import bulk {path} --apply

[1]: https://docs.mattermost.com/deployment/bulk-loading.html#running-the-bulk-loading-command
""".format(path=metadata_path, directory=output_directory))


if __name__ == '__main__':
    main()
