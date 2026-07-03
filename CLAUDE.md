# CLAUDE.md — axm-fleet

## What this repository is

axm-fleet is a **spoke** of the AXM ecosystem: a small domain package that
turns fleet sustainment records (`node_record.json`) into shards compiled,
signed, and sealed by the **axm-genesis kernel**. It is the ecosystem's
worked answer to the sustainment control question:

> Can you prove what is running on a deployed asset, who built it, who
> signed it, what it contains, when it changed, and what key authorized the
> change — **offline**, with no vendor infrastructure in the loop?

One record shard answers that for one asset at one moment. An update is a
**new** shard that `supersedes` the previous one (the kernel seals
`manifest.supersedes` + `ext/lineage@1`); the chain of shards is the
asset's lifecycle. Records are never mutated, they are succeeded.

## Why it is a separate repository

This is deliberate, not incidental — do not merge it back into the kernel:

1. **Ecosystem rule.** Genesis is the kernel; every spoke (axm-show,
   axm-chat, axm-embodied, axm-sfn, axm-fleet) is a separate package that
   depends on the kernel through pip (see `docs/ADOPTING.md` in
   axm-genesis). Genesis keeps only the neutral `templates/spoke-template`.
2. **The separation IS the demo.** This spoke's thesis is
   vendor-substitutability of the evidence layer. It was first built inside
   the genesis tree (axm-genesis branch `claude/show-function-analysis-qh7p9i`,
   commit `4e8ac71`, lifted out in `6f5a60d`) and needed **zero kernel
   changes** — living apart, pinned to a published kernel commit, makes
   that structural rather than asserted.
3. Own CI, own release cadence, own Pages slot in the ecosystem nav.

## The contract: the four-beat demo

`./demo.sh` is the product. CI runs it on every push. Do not let it rot:

1. **RECORD** — compile a node record; verify offline with a trusted key
   supplied out of band.
2. **PATCH** — compile a successor with `--supersedes`; the kernel seals
   the lineage; `axm-fleet history` walks the chain.
3. **TAMPER** — one flipped byte → `E_MERKLE_MISMATCH`; wrong trusted key
   → `E_SIG_INVALID`.
4. **REMOVE THE VENDOR** — the independent Go verifier in axm-genesis
   (`verifiers/go`, built from the spec and vectors alone) accepts the same
   shard. The record layer passes its own substitution test.

## Hard boundaries (kernel discipline)

- **Genesis compiles and signs; everything else reads.** This spoke owns
  exactly three things: domain extraction (`record_schema.py`,
  `record_compile.py`), its CLI, and its dependency pins. It must NEVER
  implement or copy signing, hashing, Merkle construction, manifest
  encoding, identity derivation, or resealing. (axm-sfn's two-pass reseal
  is the anti-pattern; RFC 0004 in genesis is the sanctioned path if
  post-compile injection is ever needed.)
- **No default signing key, ever.** Keys come from `axm-build keygen`;
  tests use throwaway keypairs per run; a committed or hardcoded key is a
  regression (show shipped one once — SHA-256 of "123" — and it was purged).
- **Trust is anchored out of band.** Never verify against the
  `publisher.pub` embedded in the shard being verified.
- **Identity is derived, never stored**: `sh1_` + BLAKE3 of manifest bytes.
- **Honest evidence.** The digests in `examples/*.json` are the real
  sha256 of the files in `examples/artifacts/`;
  `test_artifact_digests_bind` enforces it. If you change an artifact,
  regenerate the digests. Every README claim must be a runnable command or
  a CI-run test.

## Kernel dependency

Pinned to an exact axm-genesis commit until the kernel is on PyPI
(pin sites: `pyproject.toml` is a range, `README.md` install line and
`.github/workflows/ci.yml` carry the commit). After the v1.0.0 PyPI
release, switch to `axm-genesis[mldsa-compat]>=1.0.0,<2` — range, never an
exact pin (COMPATIBILITY.md guarantees every 1.x verifies these shards).
Beat 4 and one test locate `verifiers/go` via the `AXM_GENESIS` env var or
a sibling `../axm-genesis` checkout, and skip cleanly if absent.

## Relation to sibling spokes

- **axm-show** seals *mission authorization* (what may fly, under which
  ceiling — one-shot).
- **axm-fleet** (this repo) seals *lifecycle* (what is running and how it
  got there — a supersedes chain over time).
- **axm-sfn** seals *hardware custody* (what the machine attested it did —
  TPM-bound session journals).

Same kernel, three record types. A future `tpm-attestation@1` capsule on
fleet records (node TPM quote at record time) should follow axm-sfn's
conventions (RFC 0006) rather than inventing new ones — the kernel seals it
in one pass via `extra_content`/`extra_ext`. Note `tpm-attestation@1` (what
hardware attested) is distinct from RFC 0005's `attestations@1` (when a
shard existed).

## Working here

```bash
pip install 'axm-genesis[mldsa-compat] @ git+https://github.com/BigBirdReturns/axm-genesis@<pinned commit>'
pip install -e '.[dev]'
python -m pytest tests/ -v      # 9 tests; Go test skips without a toolchain
AXM_GENESIS=/path/to/axm-genesis ./demo.sh
```

Content stays **generic**: no vendor names, no program names, no customer
strategy material. "Vendor A / som-vendor-a" phrasing is intentional.
