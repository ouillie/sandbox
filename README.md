# Local "Sandbox" in a Pod

Run processes in a container
with fine-grained control over filesystem and network access.

Use [`podman`] to bind-mount directories from the host machine
in read-write, read-only, or overlay modes.

Use [`mitmproxy`] add-on scripts to inspect, modify, block, or redirect
any HTTP request, TCP stream, UDP packet, DNS query, etc.
with all the expressive power of Python.

[`podman`]: https://podman.io/
[mitmproxy]: https://www.mitmproxy.org/

## Usage

```bash
# Example: Open the default shell.
sandbox

# Example: Open a custom process.
sandbox claude --dangerously-skip-permissions
```

The tool first walks the directory tree backward
from the current working directory to the root,
looking for directories named `.sandbox`.
Each such directory may contain any of the following files:

- `proxy.py`: An `mitmproxy` add-on script to customize network access.
- `settings.json`: A JSON file containing configuration settings for the sandbox.

Before starting the sandbox,
the URL of a locally-accessibly web console to monitor network traffic
is displayed.

## Settings

TODO

## Dependencies

- `podman`
- `jq`
