# Security policy

## Scope

This repository contains local test harnesses. It does not ship credentials,
model weights or a hosted network service. The direct-HTTP runners call an
OpenAI-compatible endpoint you supply. The optional BrowseComp cloud-API
runner calls a fixed provider endpoint with a key read from a local file; the
repair fixtures include known anti-cheat limitations documented in
[repair/SECURITY.md](repair/SECURITY.md).

## Reporting a vulnerability

Please **do not** open a public issue for a security problem. Use GitHub's
private vulnerability reporting on this repository, or contact the maintainer
directly. Include:

- the affected file and line;
- a description of the impact;
- a minimal reproduction;
- any suggested fix.

You should receive an acknowledgement within a few days. Please allow time for
a fix before public disclosure.

## What counts as a security issue here

- Hardcoded or exposed credentials in any file.
- A runner that sends prompts or answers to an unexpected endpoint.
- A scorer that executes candidate code with unintended privileges when used
  as documented.
- Path traversal or arbitrary file write in a runner.

## What is not a security issue

- The documented anti-cheat gaps in the repair fixtures when the harness is
  used for local model selection as intended. These are tracked in
  `repair/SECURITY.md`.
- Search-engine scraping in the optional local MCP web server. It is best
  effort, may break, and should be replaced with an official API in production.
