# Local "Sandbox" in a Pod

Run processes in a container
with fine-grained control over filesystem and network access.

Use [`podman`] to bind-mount directories from the host machine
in read-write, read-only, or overlay modes.

Use [`mitmproxy`] addon scripts to inspect, modify, block, or redirect
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
declare -a SANDBOX_MOUNTS=(
  "${HOME}":'/root':O
  "${PWD}":"${SANDBOX_WORKDIR}":rw
)

# Array of environment variables to set in the sandbox
# using Podman's `NAME=VALUE` or simply `NAME` syntax.
# By default, set various environment variables to trust the proxy's ephemeral CA in most apps,
# since the proxy intercepts all network traffic, terminating TLS if necessary.
# Also set `IS_SANDBOX=1`
# which is required by Claude Code to run as root with `--dangerously-skip-permissions`.
# https://github.com/anthropics/claude-code/issues/9184
declare -a SANDBOX_ENV=(
  SSL_CERT_FILE='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  CURL_CA_BUNDLE='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  GIT_SSL_CAINFO='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  CARGO_HTTP_CAINFO='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  NODE_EXTRA_CA_CERTS='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  REQUESTS_CA_BUNDLE='/root/.mitmproxy/mitmproxy-ca-cert.pem'
  IS_SANDBOX=1
)
```

## Dependencies

- `bash`
- `podman`
