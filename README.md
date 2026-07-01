# c-stdlib-environment-global-state-footgun-lab

A small, local correctness and safety lab about C getenv and POSIX environment mutation footguns, inspired by a Hacker News thread on getaddrinfo() calling getenv() on glibc.

**This is a toy lab, not a network resolver test, not a setuid/security test, not a glibc test suite, and not a proof of thread safety.**

## Hacker News thread

- **HN thread:** https://news.ycombinator.com/item?id=37908655
- **Title:** "Getaddrinfo() on glibc calls getenv(), oh boy"
- **Link:** https://rachelbythebay.com/w/2023/10/16/env/
- **Comments fetched:** 75, via the Hacker News Firebase API
- **Thread read before README was written:** Yes – see `hn_thread_evidence.md`

### What HN users were actually debating

HN commenters argued that libc APIs can unexpectedly consult environment variables. `getaddrinfo()` on glibc calls `getenv()` to read resolver configuration (`LOCALDOMAIN`, `RES_OPTIONS`, `HOSTALIASES`, etc.) – surprising hidden global state.

**`getenv()` returns pointers into process-global environment state.** Environment variables behave like global or dynamic variables. `setenv`/`unsetenv`/`putenv` mutate that shared state.

**Mutating the environment after spawning threads came up as dangerous.** POSIX marks `setenv()` as "MT-Unsafe const:env" – you must not call it concurrently with `getenv()` or environment-dependent functions.

**Just locking `getenv` is not enough** if returned pointers can later be invalidated by another thread calling `setenv`/`unsetenv` after you release the lock. The returned pointer points into the global environment block, which can be reallocated.

**glibc vs illumos behavior came up.** illumos never frees environment strings and atomically swaps the environ array, so `getenv()` pointers remain valid (though possibly stale). glibc's behavior can invalidate returned pointers when the environment block is reallocated.

**Thread-safety and reentrancy are separate issues.** Even with locking, pointer lifetime remains a problem. Environment variables are fundamentally process-global mutable state.

**locale, timezone, and network APIs came up** as examples of hidden global state in libc. `setlocale()` mutates global state. Time functions consult `TZ`. `getaddrinfo()` consults environment variables for resolver configuration.

**Go/Rust/cgo/library-thread interactions came up.** Language runtimes that call into libc may encounter environment mutation races. Libraries may spawn threads behind your back. "just don't call setenv after threads" is not enough context for libraries that may create threads behind your back.

**Process isolation / fork was suggested** as a workaround. Fork+exec gives you a clean environment copy. The child process inherits a snapshot of the environment – safe because it's a copy, not shared.

**`secure_getenv` and setuid-like concerns** are separate from this lab's scope – this lab does NOT test setuid behavior, privilege boundaries, or LD_PRELOAD.

The thread distinguished carefully between: ISO C behavior, POSIX wording, glibc extensions, illumos behavior, musl/BSD/macOS behavior, resolver behavior, thread safety, security boundaries, cgo/Rust behavior, and production safety. These are separate questions.

Other recurring themes: `putenv()` ownership semantics (caller buffer is used directly, not copied – if you free/modify it, environment becomes corrupted), `setenv()` overwrite flag semantics, empty values vs missing variables, `environ` as a non-ISO/POSIX-ish extension, NSS/resolver config, DNS lookups, dynamic linking, LD_PRELOAD concerns, environment variable injection, Go's cgo calling into C libraries that read environ, Rust's std::env being a snapshot, config files vs environment variables for configuration, and "environment variables are for child processes, not runtime configuration".

### Hacker News thread access

The HN thread at https://news.ycombinator.com/item?id=37908655 was accessed via the Hacker News Firebase API (`hackernews` CLI) **before** writing this README. Comment sentiments above are summarized from 75 fetched comments. No direct quotes are fabricated; paraphrasing is used throughout. See `hn_thread_evidence.md` and `hn_37908655.json` for auditability.

## What this lab does

Tests C environment API footguns in a tiny reproducible way, using a generated C harness compiled by zig cc (if available) driven by Python.

- `getenv()` – reads process-global environment state, returns pointer with lifetime caveats
- `setenv()` / `unsetenv()` – mutate global process state, overwrite flag semantics
- `putenv()` – caller-buffer ownership footgun (buffer is used directly, NOT copied), POSIX not ISO C
- Pointer lifetime – getenv returned pointers can be invalidated by subsequent setenv/unsetenv
- Empty value vs missing variable – distinct
- Invalid names – `=` in name, empty name
- Copy-before-mutation pattern – preserve value by copying before mutating environment
- Cleanup policy – unset every synthetic variable touched
- Markers (NOT_RUN): direct `environ` access, host environment dump, secrets, thread races, library-created threads, locking getenv caveat, locale/timezone/getaddrinfo/DNS/NSS, secure_getenv, setuid security, fork isolation, cgo/Rust, cross-libc behavior

**No UB is intentionally run.** No dangling putenv buffers – putenv buffers are static and alive for whole test. No host secrets read. No environ dumps. No thread races. No DNS/getaddrinfo calls. No setuid/LD_PRELOAD.

All environment variable names use a unique fake prefix `OAI_FAKE_ENV_FOOTGUN_` – the harness never reads `PATH`, `HOME`, `USER`, `SHELL`, `LD_PRELOAD`, `TZ`, `LANG`, `LC_ALL`, `RES_OPTIONS`, `LOCALDOMAIN`, `HOSTALIASES`, or any real host variable.

## Scope limits – read this

- NOT a network resolver test / getaddrinfo test / DNS test
- NOT a setuid / security / privilege test
- NOT a glibc test suite
- NOT a sanitizer / fuzzer / static analyzer
- NOT a production environment manager
- NOT a libc conformance suite
- NOT a proof of thread safety
- Does NOT run undefined behavior
- Does NOT claim compiler warnings prove thread safety
- No external C libraries, no resolver libraries, no valgrind, no AFL
- No apt / sudo / Docker / package managers
- No network calls during the benchmark
- No downloaded corpora, glibc source, CVE PoCs, or real environment dumps

Safe claims distinguish: local compiler/libc observations vs ISO C guarantees vs POSIX wording vs glibc/illumos behavior vs resolver behavior vs thread safety vs security boundaries vs production safety.

## Running the lab

```bash
python3 -m py_compile generate_cases.py run_lab.py
python3 generate_cases.py
python3 run_lab.py
```

`run_lab.py` searches for a compiler in order: `zig cc`, `cc`, `clang`, `gcc`. No root installs. Records compiler path, version, compile command, harness run results, and optional API availability (`setenv`/`unsetenv`/`putenv`) in `RESULTS.md`.

## Results

See [RESULTS.md](RESULTS.md) and [results_rows.csv](results_rows.csv).

Compiler-validated with **zig cc 0.13.0** (clang 18.1.6).

**Development-history note:** the final committed state is compiler-validated and auditable from committed artifacts (RESULTS.md, results_rows.csv, VERIFY.md). Any "clean first run" or "no harness fixes needed" statements are self-reported and not independently proven by commit history – this repo was pushed as a single initial commit.

## Files

- `generate_cases.py` – generate 53 deterministic synthetic test cases
- `run_lab.py` – find compiler, compile C harness, run cases, write RESULTS.md
- `c_environment_global_state_footgun_harness.c` – C environment API footgun observer (no UB)
- `cases.json` – generated test cases
- `results_rows.csv` – per-case / per-method results
- `RESULTS.md` – summary with honest scope notes
- `hn_thread_evidence.md` – HN thread access evidence
- `hn_37908655.json` – raw HN comments (75)

## License

MIT
