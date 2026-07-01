#!/usr/bin/env python3
"""Generate deterministic C environment API footgun test cases."""
import json
def m(case_id, category, fake_name, **kw):
    d = {"case_id": case_id, "category": category, "fake_record_name": fake_name}
    d.update(kw); return d

P = "OAI_FAKE_ENV_FOOTGUN_"
cases = []

# getenv missing / setenv / unsetenv
cases.append(m("e001","getenv_policy","fake_env_key", env_name=P+"MISSING_XYZ", env_value=None, operation="getenv_missing", context="getenv_missing", expected_success="success", expected_observation="getenv_returns_null", expected_reason=None, naive_should_fail=False))
cases.append(m("e002","getenv_policy","demo_setting", env_name=P+"TEST_A", env_value="alpha", operation="setenv_getenv", context="setenv_getenv", expected_success="success", expected_observation="setenv_getenv_ok", expected_reason=None, naive_should_fail=False))
cases.append(m("e003","mutation_caveat","synthetic_option", env_name=P+"TEST_B", env_value="old", operation="setenv_no_overwrite", context="setenv_no_overwrite", expected_success="success", expected_observation="setenv_overwrite_zero_preserves", expected_reason=None, naive_should_fail=False))
cases.append(m("e004","mutation_caveat","toy_process_var", env_name=P+"TEST_C", env_value="new", operation="setenv_overwrite", context="setenv_overwrite", expected_success="success", expected_observation="setenv_overwrite_replaces", expected_reason=None, naive_should_fail=False))
cases.append(m("e005","getenv_policy","example_value", env_name=P+"TEST_D", env_value="temp", operation="unsetenv_removes", context="unsetenv_removes", expected_success="success", expected_observation="unsetenv_ok", expected_reason=None, naive_should_fail=False))
cases.append(m("e006","getenv_policy","fake_resolver_flag", env_name=P+"EMPTY_VAL", env_value="", operation="empty_value", context="empty_value", expected_success="success", expected_observation="empty_value_distinct_from_missing", expected_token_count=1, expected_reason=None, naive_should_fail=False))
cases.append(m("e007","getenv_policy","sample_locale_marker", env_name="BAD=NAME", env_value="x", operation="invalid_equals", context="invalid_name_equals", expected_success="caveat", expected_observation="invalid_name_contains_equals", expected_reason="POSIX: name shall not contain '='", naive_should_fail=True))
cases.append(m("e008","getenv_policy","fictional_thread_case", env_name="", env_value="x", operation="invalid_empty", context="invalid_name_empty", expected_success="caveat", expected_observation="empty_name_invalid", expected_reason="empty name invalid", naive_should_fail=True))
# long value / many vars
cases.append(m("e009","getenv_policy","test_env_slot", env_name=P+"LONG_VAL", env_value="X"*200, operation="long_value", context="long_value", expected_success="success", expected_observation="long_value_ok", expected_reason=None, naive_should_fail=False))
cases.append(m("e010","getenv_policy","demo_config_value", env_name=P+"MANY_", env_value="v", operation="many_vars", context="many_fake_prefix_vars", expected_success="success", expected_observation="many_vars_ok", expected_reason=None, naive_should_fail=False))
# pointer lifetime
cases.append(m("e011","pointer_lifetime_caveat","fake_feature_flag", env_name=P+"PTR_A", env_value="value1", operation="getenv_ptr", context="getenv_pointer_caveat", expected_success="caveat", expected_observation="getenv_returns_ptr_to_global_state", expected_reason="pointer lifetime caveat", naive_should_fail=True))
cases.append(m("e012","pointer_lifetime_caveat","fake_lookup_key", env_name=P+"PTR_B", env_value="v1", operation="ptr_after_mut", context="pointer_after_mutation_observation", expected_success="caveat", expected_observation="pointer_may_be_invalidated_after_setenv", expected_reason="pointer lifetime", naive_should_fail=True))
cases.append(m("e013","pointer_lifetime_caveat","synthetic_payload", env_name=P+"PTR_C", env_value="orig", operation="copy_before_mut", context="copy_before_mutation", expected_success="success", expected_observation="copy_preserves_value", expected_reason=None, naive_should_fail=False))
# putenv
cases.append(m("e014","putenv_ownership_caveat","fake_env_key", env_name=P+"PUT_A", env_value="putval", operation="putenv_avail", context="putenv_available", expected_success="success", expected_observation="putenv_ok", expected_reason=None, naive_should_fail=False))
cases.append(m("e015","putenv_ownership_caveat","demo_setting", env_name=P+"PUT_B", env_value="x", operation="putenv_unavail", context="putenv_unavailable", expected_success="not_tested", expected_observation="putenv_posix_not_iso_c", expected_reason="POSIX not ISO C", naive_should_fail=False))
cases.append(m("e016","putenv_ownership_caveat","synthetic_option", env_name=P+"PUT_C", env_value="caller_buf", operation="putenv_caller_buf", context="putenv_caller_buffer", expected_success="caveat", expected_observation="putenv_uses_caller_buffer_no_copy", expected_reason="putenv ownership footgun", naive_should_fail=True))
cases.append(m("e017","putenv_ownership_caveat","toy_process_var", env_name=P+"PUT_D", env_value="mut", operation="putenv_mut_changed", context="putenv_mutable_buffer_changed", expected_success="caveat", expected_observation="putenv_buffer_mutation_visible", expected_reason="caller buffer aliased", naive_should_fail=True))
cases.append(m("e018","putenv_ownership_caveat","example_value", env_name="NOEQUALS", env_value="x", operation="putenv_no_equals", context="putenv_without_equals", expected_success="caveat", expected_observation="putenv_string_must_contain_equals", expected_reason="invalid putenv string", naive_should_fail=False))
cases.append(m("e019","putenv_ownership_caveat","fake_resolver_flag", env_name=P+"PUT_E", env_value="cleanup", operation="unset_after_putenv", context="unset_after_putenv", expected_success="success", expected_observation="unsetenv_cleanup_ok", expected_reason=None, naive_should_fail=False))
# environ / host env / secrets / threads – all NOT_RUN markers
for cid, name, op, ctx, obs in [
("e020","sample_locale_marker","environ_direct","environ_direct_not_run","environ_direct_access_not_run"),
("e021","fictional_thread_case","host_dump","host_env_dump_not_run","host_environment_not_dumped"),
("e022","test_env_slot","secrets_nr","secrets_not_read","real_secrets_not_read"),
("e023","demo_config_value","thread_race","thread_race_not_run","thread_race_not_run"),
("e024","fake_feature_flag","lib_thread","library_thread_marker","library_may_spawn_threads"),
("e025","fake_lookup_key","lock_getenv","lock_getenv_caveat","lock_getenv_not_enough"),
("e026","synthetic_payload","ptr_inval","pointer_invalidation_caveat","pointer_invalidation_caveat"),
("e027","fake_env_key","locale_env","locale_env_not_run","locale_environment_not_tested"),
("e028","demo_setting","tz_env","timezone_env_not_run","timezone_not_tested"),
("e029","synthetic_option","gai_env","getaddrinfo_env_not_run","getaddrinfo_not_tested"),
("e030","toy_process_var","dns_net","dns_network_not_tested","dns_network_not_tested"),
("e031","example_value","nss_nr","nss_not_tested","nss_resolver_not_tested"),
("e032","fake_resolver_flag","secure_getenv","secure_getenv_marker","secure_getenv_availability_marker"),
("e033","sample_locale_marker","setuid_nr","setuid_security_not_tested","setuid_security_not_tested"),
]:
    cases.append(m(cid,"security_not_tested" if "security" in ctx or "secret" in ctx or "setuid" in ctx else ("thread_safety_not_tested" if "thread" in ctx else ("resolver_not_tested" if "getaddrinfo" in ctx or "dns" in ctx or "nss" in ctx else ("locale_not_tested" if "locale" in ctx or "timezone" in ctx else "global_state_caveat"))), name, env_name=P+"DUMMY", env_value=None, operation=op, context=ctx, expected_success="not_tested", expected_observation=obs, expected_reason="out of scope / not run", naive_should_fail=False))
# errno / posix / portability markers
cases.append(m("e034","getenv_policy","fictional_thread_case", env_name=P+"ERR_A", env_value=None, operation="errno_invalid", context="errno_invalid_name", expected_success="caveat", expected_observation="errno_set_on_invalid_name", expected_reason=None, naive_should_fail=False))
cases.append(m("e035","portability_not_tested","test_env_slot", env_name=P+"ERR_B", env_value=None, operation="errno_port", context="errno_portability_caveat", expected_success="caveat", expected_observation="errno_portability_varies", expected_reason="errno not always set", naive_should_fail=False))
cases.append(m("e036","posix_extension_caveat","demo_config_value", env_name=P+"POSIX_A", env_value="x", operation="posix_iso", context="posix_not_iso_c", expected_success="success", expected_observation="setenv_is_posix_not_iso_c", expected_reason=None, naive_should_fail=False))
cases.append(m("e037","portability_not_tested","fake_feature_flag", env_name=P+"GLIBC_A", env_value="x", operation="glibc_marker", context="glibc_not_generalized", expected_success="not_tested", expected_observation="glibc_specific_not_generalized", expected_reason="libc-specific", naive_should_fail=False))
cases.append(m("e038","portability_not_tested","fake_lookup_key", env_name=P+"ILLUMOS_A", env_value="x", operation="illumos_marker", context="illumos_not_tested", expected_success="not_tested", expected_observation="illumos_behavior_not_tested", expected_reason="not tested", naive_should_fail=False))
cases.append(m("e039","portability_not_tested","synthetic_payload", env_name=P+"MUSL_A", env_value="x", operation="musl_bsd_macos", context="musl_bsd_macos_not_tested", expected_success="not_tested", expected_observation="musl_bsd_macos_not_tested", expected_reason="single libc only", naive_should_fail=False))
cases.append(m("e040","portability_not_tested","fake_env_key", env_name=P+"CGO_A", env_value="x", operation="cgo_rust", context="cgo_rust_not_tested", expected_success="not_tested", expected_observation="cgo_rust_behavior_not_tested", expected_reason="C only", naive_should_fail=False))
cases.append(m("e041","security_not_tested","demo_setting", env_name=P+"FORK_A", env_value="x", operation="fork_iso", context="fork_isolation_not_run", expected_success="not_tested", expected_observation="fork_isolation_not_tested", expected_reason="no fork/exec in harness", naive_should_fail=False))
cases.append(m("e042","getenv_policy","synthetic_option", env_name=P+"CHILD_A", env_value="childval", operation="child_env", context="child_env_copy_marker", expected_success="success", expected_observation="child_inherits_env_copy", expected_reason=None, naive_should_fail=False))
cases.append(m("e043","getenv_policy","toy_process_var", env_name=P+"CLEAN_A", env_value="tmp", operation="cleanup_case", context="cleanup_after_case", expected_success="success", expected_observation="cleanup_ok", expected_reason=None, naive_should_fail=False))
cases.append(m("e044","getenv_policy","example_value", env_name=P+"DUP_A", env_value="v", operation="dup_set_unset", context="duplicate_set_unset_sequence", expected_success="success", expected_observation="dup_set_unset_ok", expected_reason=None, naive_should_fail=False))
cases.append(m("e045","getenv_policy","fake_resolver_flag", env_name=P+"CaSe_SeNsItIvE", env_value="x", operation="case_sense", context="case_sensitive_name", expected_success="success", expected_observation="env_names_case_sensitive", expected_reason=None, naive_should_fail=False))
cases.append(m("e046","getenv_policy","sample_locale_marker", env_name=P+"UTF8_VAL", env_value="café", operation="non_ascii", context="non_ascii_value_caveat", expected_success="caveat", expected_observation="non_ascii_value_bytes_opaque", expected_reason="bytes not validated", naive_should_fail=False))
cases.append(m("e047","getenv_policy","fictional_thread_case", env_name=P+"NUL_A", env_value="x\x00y", operation="nul_byte", context="nul_byte_not_run", expected_success="not_tested", expected_observation="nul_byte_impossible_in_env_string", expected_reason="NUL terminates C string", naive_should_fail=False))
cases.append(m("e048","getenv_policy","test_env_slot", env_name=P+"SNPRINTF_A", env_value="constructed", operation="snprintf_bound", context="snprintf_bounded_construction", expected_success="success", expected_observation="snprintf_bounded_ok", expected_reason=None, naive_should_fail=False))
# naive markers
for cid, name, op, obs in [
("e049","demo_config_value","naive_immutable","naive_getenv_immutable"),
("e050","fake_feature_flag","naive_setenv_safe","naive_setenv_always_safe"),
("e051","fake_lookup_key","naive_putenv_copy","naive_putenv_copies"),
("e052","synthetic_payload","naive_empty_missing","naive_empty_equals_missing"),
("e053","fake_env_key","naive_thread_safe","naive_env_thread_safe"),
]:
    cases.append(m(cid,"naive_negative",name, env_name=P+"NAIVE_"+cid.upper(), env_value="x", operation=op, context="naive_global_env_marker", expected_success="caveat", expected_observation=obs, expected_reason="naive env footgun", naive_should_fail=True))

for c in cases:
    c.setdefault("expected_errno_observation","n/a")
    c.setdefault("expected_compiler_observation","n/a")
    c.setdefault("expected_portability_truth","not_tested")
    c.setdefault("expected_security_truth","not_tested")
    c.setdefault("expected_thread_safety_truth","not_tested")
    c.setdefault("expected_resolver_truth","not_tested")
    c.setdefault("input_byte_len", len((c.get("env_value") or "").encode()))
    c.setdefault("expected_token_count", 0)

with open("cases.json","w") as f: json.dump(cases, f, indent=2)
print(f"Wrote {len(cases)} cases to cases.json")
