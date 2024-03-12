# AWS CLI Console

This (simple) program lets you, from any working AWS CLI profile, open its web
console on your browser. It uses credentials from your CLI, so everything that
works with it, works with this.

# Installation

I recommend pipx:
```
pipx install git+https://github.com/zoocha/awscli-console
```

But you may also use pip globally:
```
pip install --user git+https://github.com/zoocha/awscli-console
```

You can also use nix, if you're into that:
```
nix shell github:zoocha/awscli-console
```

# Usage

## CLI

It's as simple as:
```
aws-console --profile=foo
```

Should open the login URL in your browser. As long as your credentials work
(e.g. `aws --profile=foo sts get-caller-identity`), this should too.

## Qutebrowser userscript

There's also a qutebrowser userscript. On your browser, run:
```
:spawn -u aws-console-qutebrowser <profile>
```

You can also set an alias:
```
:set aliases '{"aws": "spawn -u aws-console-qutebrowser"}'
:aws <profile>
```

## As AWS CLI plugin

Open up your `~/.aws/config`, and add:
```
[plugins]
console = awscli_console.plugin
cli_legacy_plugin_path = path/to/python/site-packages
```

The `cli_legacy_plugin_path` will depend on where you installed this.
- With pipx: `~/.local/share/pipx/venvs/awscli-console/lib/python3.11/site-packages`
- With pip --user: `~/.local/lib/python3.11/site-packages`

All done! You can use it like so:

```
aws console --profile=foo
```

# Hacking

To iterate faster, install the deps (in a venv, hopefully), and run it with `python -m`, like so:

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m awscli_console
```
