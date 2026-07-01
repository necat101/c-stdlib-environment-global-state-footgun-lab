# RESULTS – c-stdlib-environment-global-state-footgun-lab

## Run summary

- Cases: 53
- Methods: 16
- Pass: 100
- Fail: 0
- Expected-fail (naive): 5
- Skip/not_tested: 0

## Category counts

- getenv: 16
- setenv/unsetenv: 5
- putenv: 6
- pointer-lifetime caveat: 3
- global-state caveat: 0
- thread-safety-not-tested: 0
- resolver/locale/time-not-tested: 5
- POSIX extension: 1
- security-not-tested: 3
- portability-not-tested: 5

## Environment

- Python: 3.12.3
- Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39
- Compiler selected: zig cc
- Compiler path: /tmp/zig-linux-x86_64-0.13.0/zig
- Compiler version: 0.13.0
- Compile command: `/tmp/zig-linux-x86_64-0.13.0/zig cc -std=c11 -Wall -Wextra -O2 c_environment_global_state_footgun_harness.c -o c_harness`
- Compile ok: True
- Compile elapsed: 0.316s
- cases.json: 39857 bytes
- c_environment_global_state_footgun_harness.c: 9960 bytes
- c_harness binary: 23072 bytes
- Total run elapsed: 0.859s
- Timing: time.perf_counter()
- setenv/unsetenv available: True
- putenv available: True
- secure_getenv available: False

## Compiler discovery

✅ C harness compiled and run

Compiler search order: zig cc → cc → clang → gcc

## HN thread access

- HN thread: https://news.ycombinator.com/item?id=37908655
- Title: "Getaddrinfo() on glibc calls getenv(), oh boy"
- Comments fetched: 75 (via Hacker News Firebase API)
- Evidence: hn_thread_evidence.md / hn_37908655.json
- Thread read BEFORE README was written: Yes

## Scope / honesty

- Network/API during benchmark: No
- Package manager / root install: No
- Downloaded corpora / glibc source / CVE PoC: No
- Undefined behavior intentionally run: No
- Sanitizer / fuzzer / static analyzer: No
- getaddrinfo / DNS / resolver test: No
- setuid / security test: No
- Thread race test: No
- Host environment secrets read: No
- Production thread-safety claim: No
- Libc portability claim: No
- Security guarantee claim: No

## Conclusion

C environment APIs expose process-global mutable state. getenv() returns pointers into shared state with lifetime caveats. setenv/unsetenv/putenv mutate global process state; putenv has caller-buffer ownership footguns. Returned pointers can be invalidated by subsequent mutations. setenv after threads is dangerous; locking getenv alone does not solve pointer-lifetime. POSIX APIs are not ISO C. Hidden environment reads inside other libc APIs (getaddrinfo/resolver/locale/timezone) are real but out of scope. Safe claims distinguish local libc observations from ISO C guarantees, POSIX wording, glibc/illumos behavior, resolver behavior, thread safety, and production security.

Per-case results: results_rows.csv

## Development-history note

The final committed state is compiler-validated and auditable from committed artifacts (RESULTS.md, results_rows.csv, VERIFY.md). Any "clean first run" or "no harness fixes needed" statements are self-reported and not independently proven by commit history – this repo was pushed as a single initial commit.
