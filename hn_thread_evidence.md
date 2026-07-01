# HN Thread Access Evidence

- **HN item ID:** 37908655
- **Title:** Getaddrinfo() on glibc calls getenv(), oh boy
- **URL:** https://news.ycombinator.com/item?id=37908655
- **Linked article:** https://rachelbythebay.com/w/2023/10/16/env/
- **Tool used:** Hacker News Firebase API via `hackernews` CLI
- **Comments fetched:** 75
- **Fetch date:** 2026-07-01
- **Raw dump:** `hn_37908655.json`

The HN thread was read BEFORE writing README.md. Comment sentiments in the README summarize the actual thread discussion – no quotes were fabricated.

Key themes observed:
- getaddrinfo() on glibc calls getenv() – surprising hidden global state
- getenv() returns pointers into process-global environment state
- setenv/unsetenv/putenv mutate shared process-global state
- environment variables behave like global/dynamic variables
- libc APIs unexpectedly consulting environment variables
- setenv after threads is dangerous – POSIX: "MT-Unsafe const:env"
- locking getenv alone is NOT enough – returned pointers can be invalidated after unlock
- glibc vs illumos behavior – illumos never frees env strings, atomically swaps environ array
- thread-safety and reentrancy are separate issues
- locale, timezone, getaddrinfo, NSS, DNS, resolver config came up
- Go/Rust/cgo/library-thread interactions – libraries may spawn threads behind your back
- fork/process isolation suggested as workaround – fork+exec is safe (copy, not shared)
- secure_getenv / setuid concerns – separate from toy lab scope
- "just don't call setenv after threads" is not enough for libraries that spawn threads
- putenv() ownership semantics – caller buffer used directly, NOT copied
- setenv() overwrite flag semantics
- empty value vs missing variable distinction
- environ as non-ISO/POSIX-ish extension
- resolver reads LOCALDOMAIN, RES_OPTIONS, HOSTALIASES, etc.
- musl / BSD / macOS behavior comparisons
- Go cgo calling into C libraries that read environ
- Rust std::env is a snapshot, not live
- config files vs environment variables for configuration
- environment variables were designed for child processes, not runtime mutation
- "environment variables are not a nice interface"
- setlocale() / localtime() / mktime() also have global state / thread-safety issues
- ISO C vs POSIX vs glibc/illumos vs resolver behavior vs thread safety vs security boundaries vs production safety are separate questions

All of the above informed the case selection and README sentiment summary.
