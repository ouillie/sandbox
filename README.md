# Local "Sandbox" in a Pod

Run processes in a container
with fine-grained control over filesystem and network access.

Use [`podman`] to bind-mount directories from the host machine
in read-write, read-only, or overlay modes.

Use [`mitmproxy`] addon scripts to inspect, modify, block, or redirect
any HTTP request, TCP stream, UDP packet, DNS query, etc.
with all the expressive power of Python.
All traffic is allowed by default.

[`podman`]: https://podman.io/
[`mitmproxy`]: https://www.mitmproxy.org/

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
Each such directory may contain any of the following optional files:

- `configure.sh`: A Bash script that is sourced to customize [settings] for the sandbox.
- `proxy.py`: An `mitmproxy` [addon script] to customize network access.

In both cases, child directories take precedence over parent directories.
For `mitmproxy` addon scripts,
that means the leaf is processed first, followed by ancestors up the path.
For configuration scripts,
that means the root is processed first, followed by children down the path.

Before starting the sandbox,
the URL of a locally-accessible `mitmweb` console to monitor network traffic
is displayed.

[settings]: #settings
[addon script]: https://docs.mitmproxy.org/stable/addons/overview/

## Settings

The sandbox can be customized by setting the following environment variables,
shown with their default values:

```bash
# Sandbox container image.
SANDBOX_IMAGE='debian:latest'

# Sandbox container username.
SANDBOX_USER='root'

# Sandbox container hostname.
SANDBOX_HOSTNAME='sandbox'

# Working directory in the sandbox at entry.
# By default, use the current working directory on the host.
# If that path starts with the host's `${HOME}` path, swap out the prefix for `/root`,
# because the process in the sandbox runs as root by default.
SANDBOX_WORKDIR="${PWD/#${HOME}//root}"

# Array of mount points to bind-mount from the host into the sandbox,
# using Podman's `<host-path>:<guest-path>[:<mode>]` syntax,
# where `<mode>` can be `ro`, `rw`, or `O` (overlay).
# By default, mount the host's `${HOME}` directory to `/root` as an overlay,
# and mount the host's working directory to the guest's working directory read-write.
SANDBOX_MOUNTS=(
  "${HOME}":'/root':O
  "${PWD}":"${SANDBOX_WORKDIR}":rw
)

# Array of environment variables to set in the sandbox
# using Podman's `NAME=VALUE` or simply `NAME` syntax.
# By default, set various environment variables to trust the proxy's ephemeral CA in most apps,
# since the proxy intercepts all network traffic, terminating TLS if necessary.
# Also set `IS_SANDBOX=1`
# which is required by Claude Code to run as root with `--dangerously-skip-permissions`.
SANDBOX_ENV=(
  SSL_CERT_FILE='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  CURL_CA_BUNDLE='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  GIT_SSL_CAINFO='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  CARGO_HTTP_CAINFO='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  NODE_EXTRA_CA_CERTS='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  REQUESTS_CA_BUNDLE='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  IS_SANDBOX=1
)
```

If any of these variables are already set when `sandbox` is invoked,
that value will be used *instead of* the default.

> [!IMPORTANT]
> When customizing array-valued settings in a `configure.sh` script,
> be careful as to whether you want to overwrite, append, or otherwise modify the inherited value.

## Example Use Cases

<details>
<summary><strong>Full System Mount</strong></summary>

If your host system is Linux,
and you want the sandbox to look just like the host,
you can simply bind-mount huge parts of it into the sandbox.

```bash
# configure.sh

# Be sure to set the image to something that's compatible with your host system.
SANDBOX_IMAGE='archlinux:latest'

# Bind huge parts of the host system into the sandbox in overlay mode (:O)
# so the sandbox has access to all the host's binaries, libraries, etc.
# and can "modify" everything at will without actually modifying anything on the host.
SANDBOX_MOUNTS+=(
  /usr:/usr:O
  /opt:/opt:O
)

# Use the same default shell as the user on the host system.
SANDBOX_ENV+=(
  SHELL
)
```

</details>

<details>
<summary><strong>Sophisticated Network Control</strong></summary>

You can basically do anything you want with `mitmproxy` addons.

```python
# proxy.py

import socket

from mitmproxy.dns import DNSFlow, response_codes, types
from mitmproxy.http import HTTPFlow, Response
from mitmproxy.tcp import TCPFlow
from mitmproxy.udp import UDPFlow


def request(flow: HTTPFlow):
    # Block anything that might modify state on well-behaving HTTP services
    # (only allow RFC 9110 "safe" methods).
    if flow.request.method.upper() not in {"GET", "HEAD", "OPTIONS", "TRACE"}:
        flow.response = Response.make(
            502,
            b"You're in a nice little sandbox where you can't break anything."
            + b" If you really need to access this endpoint, ask your human to whitelist it.",
            {"Content-Type": "text/plain"},
        )


def response(flow: HTTPFlow):
    # Insert an extra header into all HTTP responses.
    flow.response.headers['Intercepted'] = 'For sure'


def tcp_start(flow: TCPFlow):
    # Block any SSH connection to GitHub.
    address = flow.server_conn.address
    if address and address[1] == 22 and address[0] in _github_ssh_ips():
        flow.kill()


def _github_ssh_ips() -> set[str]:
    github_ssh_addresses = set()
    for host in ["github.com", "ssh.github.com"]:
        try:
            github_ssh_addresses.update(
                info[4][0] for info in socket.getaddrinfo(host, SSH_PORT)
            )
        except socket.gaierror:
            pass
    return github_ssh_addresses


def dns_request(flow: DNSFlow):
    # Refuse mail-exchanger lookups so the workload can't discover where to deliver email.
    if any(question.type == types.MX for question in flow.request.questions):
        flow.response = flow.request.fail(response_codes.REFUSED)


def dns_response(flow: DNSFlow):
    # Effectively disable IPv6 by erasing all IPv6 addresses from DNS query responses.
    flow.response.answers = [
        answer for answer in flow.response.answers if answer.type != types.AAAA
    ]
```

</details>

## Dependencies

- `bash`
- `podman`
