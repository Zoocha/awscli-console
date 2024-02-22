# AWS CLI Console

This (simple) program lets you, from any working AWS CLI profile, open its web
console on your browser. It uses credentials from your CLI, so everything that
works with it, works with this.

# Installation

Either install globally with pip (or pipx, which is kinda better):
```
pip install git+https://github.com/misterio77/awscli-console
```

You can also use nix, if you're into that:
```
nix shell github:misterio77/awscli-console
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
