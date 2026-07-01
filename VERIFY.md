# VERIFY – fresh clone (zig cc validated)

```
$ python3 -m py_compile generate_cases.py run_lab.py
py_compile: OK

$ python3 generate_cases.py
Wrote 53 cases to cases.json

$ python3 run_lab.py
Compiler: zig cc @ /tmp/zig-linux-x86_64-0.13.0/zig
Compile ok: True
Done. pass=100 fail=0 expected_fail=5 compile_ok=True
```

## Environment

- Python 3.12.3
- Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39
- Compiler: **zig cc 0.13.0** (`/tmp/zig-linux-x86_64-0.13.0/zig`)
- Compile command: `zig cc -std=c11 -Wall -Wextra -O2 c_environment_global_state_footgun_harness.c -o c_harness`
- Compile elapsed: ~0.5s
- Binary: c_harness, 23072 bytes
- Cases: 53
- Methods: 16
- Results: results_rows.csv (105 rows, 100 pass, 0 fail, 5 expected naive failures)
- setenv/unsetenv available: True
- putenv available: True
- secure_getenv available: False

The C harness (`c_environment_global_state_footgun_harness.c`, 9960 bytes) compiles cleanly with `-std=c11 -Wall -Wextra` and runs all applicable cases. No UB. Only synthetic fake environment variables with prefix `OAI_FAKE_ENV_FOOTGUN_` – never reads host secrets, never dumps environ. All synthetic variables cleaned up after test. Thread races / DNS / getaddrinfo / setuid / locale / timezone all correctly marked NOT_TESTED / NOT_RUN.

This is a compiler-validated fresh-clone verification.
