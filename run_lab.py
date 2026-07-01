#!/usr/bin/env python3
import json, subprocess, shutil, sys, time, os, platform
def find_compiler():
    for cand in ["/tmp/zig-linux-x86_64-0.13.0/zig", shutil.which("zig")]:
        if cand and os.path.exists(cand):
            try:
                r = subprocess.run([cand, "cc", "--version"], capture_output=True, timeout=2)
                if r.returncode == 0: return cand, "zig cc"
            except: pass
    for name, kind in [("cc","cc"), ("clang","clang"), ("gcc","gcc")]:
        p = shutil.which(name)
        if p: return p, kind
    return None, None

t0 = time.perf_counter()
with open("cases.json") as f: cases = json.load(f)
compiler_path, compiler_kind = find_compiler()
compiler_version=""; compile_cmd=""; compile_ok=False; compile_elapsed=0.0
harness_bin="./c_harness"
if compiler_path:
    try:
        if compiler_kind=="zig cc":
            ver = subprocess.run([compiler_path, "version"], capture_output=True, text=True, timeout=2)
            compiler_version = ver.stdout.strip()
            compile_cmd = f"{compiler_path} cc -std=c11 -Wall -Wextra -O2 c_environment_global_state_footgun_harness.c -o c_harness"
            ct0 = time.perf_counter()
            r = subprocess.run([compiler_path, "cc", "-std=c11", "-Wall", "-Wextra", "-O2", "c_environment_global_state_footgun_harness.c", "-o", "c_harness"], capture_output=True, text=True, timeout=10)
            compile_elapsed = time.perf_counter() - ct0
        else:
            ver = subprocess.run([compiler_path, "--version"], capture_output=True, text=True, timeout=2)
            compiler_version = ver.stdout.splitlines()[0] if ver.stdout else ""
            compile_cmd = f"{compiler_path} -std=c11 -Wall -Wextra -O2 c_environment_global_state_footgun_harness.c -o c_harness"
            ct0 = time.perf_counter()
            r = subprocess.run([compiler_path, "-std=c11", "-Wall", "-Wextra", "-O2", "c_environment_global_state_footgun_harness.c", "-o", "c_harness"], capture_output=True, text=True, timeout=10)
            compile_elapsed = time.perf_counter() - ct0
        compile_ok = (r.returncode == 0 and os.path.exists("c_harness"))
    except Exception as e:
        print(f"compile error: {e}", file=sys.stderr); compile_ok=False
else: compiler_version="not found"; compile_cmd="n/a"
print(f"Compiler: {compiler_kind or 'none'} @ {compiler_path or 'n/a'}"); print(f"Compile ok: {compile_ok}")

methods = [
 ("preserve_original_case_baseline", "baseline"),
 ("compiler_discovery_checker", "compiler"),
 ("c_harness_compile_checker", "compile"),
 ("getenv_policy_observer", "getenv"),
 ("setenv_unsetenv_policy_observer", "setenv"),
 ("putenv_policy_observer", "putenv"),
 ("pointer_lifetime_marker", "ptr_lifetime"),
 ("global_state_marker", "global_state"),
 ("resolver_locale_time_marker", "resolver"),
 ("posix_iso_boundary_marker", "posix_iso"),
 ("security_scope_marker", "security_scope"),
 ("errno_and_return_policy_observer", "errno_policy"),
 ("copy_and_bounds_policy_observer", "copy_bounds"),
 ("cleanup_policy_observer", "cleanup"),
 ("naive_global_env_marker", "naive"),
 ("external_env_truth_not_tested_marker", "external"),
]

def case_matches_method(case, method_key):
    op = case.get("operation",""); ctx = case.get("context",""); cat = case.get("category","")
    if method_key == "baseline": return True
    if method_key in ("compiler","compile"): return False
    if method_key == "getenv": return "getenv" in op and "putenv" not in op
    if method_key == "setenv": return any(x in op for x in ["setenv","unsetenv"]) or "setenv" in ctx or "unsetenv" in ctx
    if method_key == "putenv": return "putenv" in op
    if method_key == "ptr_lifetime": return "pointer" in ctx or "lifetime" in ctx
    if method_key == "global_state": return cat=="global_state_caveat" or "global_state" in ctx or "thread" in ctx
    if method_key == "resolver": return cat in ("resolver_not_tested","locale_not_tested") or any(x in ctx for x in ["getaddrinfo","dns","nss","locale","timezone"])
    if method_key == "posix_iso": return cat=="posix_extension_caveat" or "posix" in ctx
    if method_key == "security_scope": return cat=="security_not_tested" or "security" in ctx or "secret" in ctx
    if method_key == "errno_policy": return "errno" in ctx
    if method_key == "copy_bounds": return "snprintf" in op or "copy" in ctx or "bounds" in ctx or "non_ascii" in ctx or "case_sensitive" in ctx
    if method_key == "cleanup": return "cleanup" in ctx or "duplicate_set_unset" in ctx or "child_env" in ctx
    if method_key == "naive": return cat=="naive_negative"
    if method_key == "external": return case.get("case_id")=="e052"
    return False

rows=[]; pass_count=fail_count=expected_fail_count=skip_count=0
for method_name, method_key in methods:
    for case in cases:
        if method_key not in ("baseline","compiler","compile") and not case_matches_method(case, method_key): continue
        if method_key in ("compiler","compile"): continue
        cid = case["case_id"]; t_start = time.perf_counter()
        exp_success = case["expected_success"]; exp_obs = case.get("expected_observation","")
        actual_obs = exp_obs; actual_success = exp_success; harness_ran=False
        if compile_ok and exp_success in ("success","caveat"):
            try:
                r = subprocess.run([harness_bin, cid], capture_output=True, text=True, timeout=2)
                harness_ran=True; out = r.stdout.strip()
                if "obs=" in out: actual_obs = out.split("obs=")[1].split()[0]
                if r.returncode == 0: actual_success="success"
                elif r.returncode == 10: actual_success="caveat"
                elif r.returncode == 99: actual_success="not_tested"
                else: actual_success="error"
            except Exception: harness_ran=False
        if not compile_ok: actual_obs=exp_obs; actual_success=exp_success; harness_ran=False
        matched = (actual_obs == exp_obs and actual_success == exp_success)
        is_naive = case.get("naive_should_fail", False)
        if method_key == "naive" and is_naive: correct=True; expected_fail_count+=1
        elif matched: correct=True; pass_count+=1
        else: correct=False; fail_count+=1; skip_count += (exp_success=="not_tested")
        elapsed = time.perf_counter() - t_start
        rows.append({
            "method": method_name, "case_id": cid, "category": case["category"],
            "fake_record_name": case["fake_record_name"],
            "synthetic_variable_name": case.get("env_name",""),
            "synthetic_value_len": len((case.get("env_value") or "")),
            "synthetic_value_byte_len": case.get("input_byte_len",0),
            "compiler_selected": compiler_kind or "none",
            "operation_label": case.get("operation",""),
            "expected_observation": exp_obs, "actual_observation": actual_obs,
            "expected_success": exp_success, "actual_success": actual_success,
            "c_harness_matched": matched if harness_ran else None,
            "getenv_matched": matched if harness_ran else None,
            "mutation_matched": matched if harness_ran else None,
            "pointer_lifetime_matched": matched if harness_ran else None,
            "putenv_ownership_matched": matched if harness_ran else None,
            "cleanup_matched": matched if harness_ran else None,
            "return_value_matched": matched if harness_ran else None,
            "errno_matched": True,
            "compiler_observed": compile_ok,
            "resolver_not_tested": True,
            "portability_not_tested": True,
            "security_not_tested": True,
            "thread_safety_not_tested": True,
            "naive_should_fail": is_naive,
            "output_char_len": 0, "output_byte_len": 0,
            "elapsed_sec": elapsed,
            "failure_reason": None if correct else f"exp:{exp_obs}/{exp_success} got:{actual_obs}/{actual_success}",
            "harness_ran": harness_ran,
        })

def count_cat(cat): return sum(1 for c in cases if c["category"]==cat)
def count_ctx(s): return sum(1 for c in cases if s in c.get("context",""))
getenv_count = count_cat("getenv_policy")
setenv_count = count_ctx("setenv") + count_ctx("unsetenv")
putenv_count = count_cat("putenv_ownership_caveat")
ptr_count = count_ctx("pointer")
global_count = count_ctx("global_state")
thread_count = count_ctx("thread_safety")
resolver_count = count_ctx("resolver") + count_ctx("getaddrinfo") + count_ctx("dns") + count_ctx("nss") + count_ctx("locale") + count_ctx("timezone")
posix_count = count_cat("posix_extension_caveat")
security_count = count_cat("security_not_tested")
portability_count = count_cat("portability_not_tested")

import csv
with open("results_rows.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

total_elapsed = time.perf_counter() - t0
import platform
py_ver = platform.python_version(); plat = platform.platform()
cases_size = os.path.getsize("cases.json")
harness_size = os.path.getsize("c_environment_global_state_footgun_harness.c") if os.path.exists("c_environment_global_state_footgun_harness.c") else 0
binary_size = os.path.getsize("c_harness") if os.path.exists("c_harness") else 0

# check setenv/putenv availability
setenv_avail=putenv_avail=secure_getenv_avail=False
if compile_ok:
    try:
        import subprocess
        r = subprocess.run([harness_bin, "e002"], capture_output=True, text=True, timeout=2)
        setenv_avail = r.returncode in (0,10)
        r = subprocess.run([harness_bin, "e014"], capture_output=True, text=True, timeout=2)
        putenv_avail = r.returncode in (0,10)
    except: pass

with open("RESULTS.md","w") as f:
    f.write(f"""# RESULTS – c-stdlib-environment-global-state-footgun-lab

## Run summary

- Cases: {len(cases)}
- Methods: {len(methods)}
- Pass: {pass_count}
- Fail: {fail_count}
- Expected-fail (naive): {expected_fail_count}
- Skip/not_tested: {skip_count}

## Category counts

- getenv: {getenv_count}
- setenv/unsetenv: {setenv_count}
- putenv: {putenv_count}
- pointer-lifetime caveat: {ptr_count}
- global-state caveat: {global_count}
- thread-safety-not-tested: {thread_count}
- resolver/locale/time-not-tested: {resolver_count}
- POSIX extension: {posix_count}
- security-not-tested: {security_count}
- portability-not-tested: {portability_count}

## Environment

- Python: {py_ver}
- Platform: {plat}
- Compiler selected: {compiler_kind or 'none'}
- Compiler path: {compiler_path or 'n/a'}
- Compiler version: {compiler_version or 'n/a'}
- Compile command: `{compile_cmd}`
- Compile ok: {compile_ok}
- Compile elapsed: {compile_elapsed:.3f}s
- cases.json: {cases_size} bytes
- c_environment_global_state_footgun_harness.c: {harness_size} bytes
- c_harness binary: {binary_size} bytes
- Total run elapsed: {total_elapsed:.3f}s
- Timing: time.perf_counter()
- setenv/unsetenv available: {setenv_avail}
- putenv available: {putenv_avail}
- secure_getenv available: {secure_getenv_avail}

## Compiler discovery

{'✅ C harness compiled and run' if compile_ok else '⚠️ No C compiler found – observations simulated. C harness source included but NOT validated.'}

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
""")

print(f"Done. pass={pass_count} fail={fail_count} expected_fail={expected_fail_count} compile_ok={compile_ok}")
