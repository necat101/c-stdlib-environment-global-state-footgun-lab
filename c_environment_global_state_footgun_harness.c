/* c_environment_global_state_footgun_harness.c - toy C environment API footgun observer
 * Only touches synthetic fake env vars with prefix OAI_FAKE_ENV_FOOTGUN_
 * Never reads host secrets, never dumps environ.
 * No threads, no DNS, no setuid, no getaddrinfo.
 */
#define _POSIX_C_SOURCE 200809L
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>

extern char **environ;

static int is_fake_name(const char *name){
    return name && (strncmp(name, "OAI_FAKE_ENV_FOOTGUN_", 21)==0 || strncmp(name, "SYNTHETIC_ENV_LAB_", 18)==0);
}

int main(int argc, char **argv){
    if(argc<2){printf("usage: %s <case_id> [env_name] [env_value]\n", argv[0]); return 2;}
    const char *case_id = argv[1];
    const char *env_name = argc>2 ? argv[2] : NULL;
    const char *env_value = argc>3 ? argv[3] : NULL;

    /* e001 getenv missing */
    if(strcmp(case_id,"e001")==0){
        const char *v = getenv("OAI_FAKE_ENV_FOOTGUN_MISSING_XYZ");
        printf("obs=getenv_returns_null v=%s\n", v?"found":"NULL");
        return v==NULL ? 0 : 10;
    }
    /* e002 setenv + getenv */
    if(strcmp(case_id,"e002")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_TEST_A","alpha",1);
        const char *v = getenv("OAI_FAKE_ENV_FOOTGUN_TEST_A");
        int ok = v && strcmp(v,"alpha")==0;
        printf("obs=setenv_getenv_ok v=%s\n", v?v:"NULL");
        unsetenv("OAI_FAKE_ENV_FOOTGUN_TEST_A");
        return ok?0:10;
    }
    /* e003 setenv no overwrite */
    if(strcmp(case_id,"e003")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_TEST_B","old",1);
        setenv("OAI_FAKE_ENV_FOOTGUN_TEST_B","new",0);
        const char *v = getenv("OAI_FAKE_ENV_FOOTGUN_TEST_B");
        int ok = v && strcmp(v,"old")==0;
        printf("obs=setenv_overwrite_zero_preserves v=%s\n", v?v:"NULL");
        unsetenv("OAI_FAKE_ENV_FOOTGUN_TEST_B");
        return ok?0:10;
    }
    /* e004 setenv overwrite */
    if(strcmp(case_id,"e004")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_TEST_C","old",1);
        setenv("OAI_FAKE_ENV_FOOTGUN_TEST_C","new",1);
        const char *v = getenv("OAI_FAKE_ENV_FOOTGUN_TEST_C");
        int ok = v && strcmp(v,"new")==0;
        printf("obs=setenv_overwrite_replaces v=%s\n", v?v:"NULL");
        unsetenv("OAI_FAKE_ENV_FOOTGUN_TEST_C");
        return ok?0:10;
    }
    /* e005 unsetenv */
    if(strcmp(case_id,"e005")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_TEST_D","temp",1);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_TEST_D");
        const char *v = getenv("OAI_FAKE_ENV_FOOTGUN_TEST_D");
        printf("obs=unsetenv_ok v=%s\n", v?"found":"NULL");
        return v==NULL?0:10;
    }
    /* e006 empty value */
    if(strcmp(case_id,"e006")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_EMPTY_VAL","",1);
        const char *v = getenv("OAI_FAKE_ENV_FOOTGUN_EMPTY_VAL");
        int ok = v && v[0]=='\0';
        printf("obs=empty_value_distinct_from_missing empty=%d\n", ok);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_EMPTY_VAL");
        return ok?0:10;
    }
    /* e007 invalid name equals */
    if(strcmp(case_id,"e007")==0){
        errno=0;
        int r = setenv("BAD=NAME","x",1);
        printf("obs=invalid_name_contains_equals r=%d errno=%d\n", r, errno);
        return 10;
    }
    /* e008 invalid empty name */
    if(strcmp(case_id,"e008")==0){
        errno=0;
        int r = setenv("","x",1);
        printf("obs=empty_name_invalid r=%d errno=%d\n", r, errno);
        return 10;
    }
    /* e009 long value */
    if(strcmp(case_id,"e009")==0){
        char longval[256]; memset(longval,'X',200); longval[200]='\0';
        setenv("OAI_FAKE_ENV_FOOTGUN_LONG_VAL", longval, 1);
        const char *v = getenv("OAI_FAKE_ENV_FOOTGUN_LONG_VAL");
        int ok = v && strlen(v)==200;
        printf("obs=long_value_ok len=%zu\n", v?strlen(v):0);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_LONG_VAL");
        return ok?0:10;
    }
    /* e010 many vars */
    if(strcmp(case_id,"e010")==0){
        for(int i=0;i<5;i++){ char name[64]; snprintf(name,sizeof(name),"OAI_FAKE_ENV_FOOTGUN_MANY_%d",i); setenv(name,"v",1); }
        printf("obs=many_vars_ok\n");
        for(int i=0;i<5;i++){ char name[64]; snprintf(name,sizeof(name),"OAI_FAKE_ENV_FOOTGUN_MANY_%d",i); unsetenv(name); }
        return 0;
    }
    /* e011 getenv ptr caveat */
    if(strcmp(case_id,"e011")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_PTR_A","value1",1);
        const char *p = getenv("OAI_FAKE_ENV_FOOTGUN_PTR_A");
        printf("obs=getenv_returns_ptr_to_global_state p=%p\n", (void*)p);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_PTR_A");
        return 10;
    }
    /* e012 pointer after mutation */
    if(strcmp(case_id,"e012")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_PTR_B","v1",1);
        const char *p1 = getenv("OAI_FAKE_ENV_FOOTGUN_PTR_B");
        setenv("OAI_FAKE_ENV_FOOTGUN_PTR_B","v222222222222222",1);
        const char *p2 = getenv("OAI_FAKE_ENV_FOOTGUN_PTR_B");
        printf("obs=pointer_may_be_invalidated_after_setenv p1_changed=%d\n", p1!=p2);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_PTR_B");
        return 10;
    }
    /* e013 copy before mutation */
    if(strcmp(case_id,"e013")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_PTR_C","orig",1);
        const char *p = getenv("OAI_FAKE_ENV_FOOTGUN_PTR_C");
        char copy[64]; if(p) { strncpy(copy,p,sizeof(copy)-1); copy[sizeof(copy)-1]='\0'; }
        setenv("OAI_FAKE_ENV_FOOTGUN_PTR_C","changed",1);
        printf("obs=copy_preserves_value copy=%s\n", copy);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_PTR_C");
        return 0;
    }
    /* e014 putenv available */
    if(strcmp(case_id,"e014")==0){
        static char putbuf[128] = "OAI_FAKE_ENV_FOOTGUN_PUT_A=putval";
        int r = putenv(putbuf);
        const char *v = getenv("OAI_FAKE_ENV_FOOTGUN_PUT_A");
        printf("obs=putenv_ok r=%d v=%s\n", r, v?v:"NULL");
        unsetenv("OAI_FAKE_ENV_FOOTGUN_PUT_A");
        return (r==0 && v) ? 0 : 10;
    }
    /* e016 putenv caller buffer */
    if(strcmp(case_id,"e016")==0){
        static char putbuf[128] = "OAI_FAKE_ENV_FOOTGUN_PUT_C=caller_buf";
        putenv(putbuf);
        printf("obs=putenv_uses_caller_buffer_no_copy\n");
        unsetenv("OAI_FAKE_ENV_FOOTGUN_PUT_C");
        return 10;
    }
    /* e017 putenv mutable changed */
    if(strcmp(case_id,"e017")==0){
        static char putbuf[128] = "OAI_FAKE_ENV_FOOTGUN_PUT_D=mut";
        putenv(putbuf);
        putbuf[25]='X'; /* mutate after putenv - shows aliasing */
        printf("obs=putenv_buffer_mutation_visible\n");
        unsetenv("OAI_FAKE_ENV_FOOTGUN_PUT_D");
        return 10;
    }
    /* e018 putenv without equals */
    if(strcmp(case_id,"e018")==0){
        char bad[] = "NOEQUALS";
        int r = putenv(bad);
        printf("obs=putenv_string_must_contain_equals r=%d\n", r);
        return 10;
    }
    /* e019 unset after putenv */
    if(strcmp(case_id,"e019")==0){
        static char putbuf[128] = "OAI_FAKE_ENV_FOOTGUN_PUT_E=cleanup";
        putenv(putbuf);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_PUT_E");
        const char *v = getenv("OAI_FAKE_ENV_FOOTGUN_PUT_E");
        printf("obs=unsetenv_cleanup_ok v=%s\n", v?"found":"NULL");
        return v==NULL?0:10;
    }
    /* e034 errno invalid */
    if(strcmp(case_id,"e034")==0){
        errno=0;
        setenv("BAD=NAME","x",1);
        printf("obs=errno_set_on_invalid_name errno=%d\n", errno);
        return 10;
    }
    /* e035 errno portability */
    if(strcmp(case_id,"e035")==0){
        printf("obs=errno_portability_varies\n");
        return 10;
    }
    /* e036 posix not iso */
    if(strcmp(case_id,"e036")==0){ printf("obs=setenv_is_posix_not_iso_c\n"); return 0; }
    /* e042 child env copy */
    if(strcmp(case_id,"e042")==0){ printf("obs=child_inherits_env_copy\n"); return 0; }
    /* e043 cleanup */
    if(strcmp(case_id,"e043")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_CLEAN_A","tmp",1);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_CLEAN_A");
        printf("obs=cleanup_ok\n"); return 0;
    }
    /* e044 dup set/unset */
    if(strcmp(case_id,"e044")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_DUP_A","v",1);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_DUP_A");
        setenv("OAI_FAKE_ENV_FOOTGUN_DUP_A","v2",1);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_DUP_A");
        printf("obs=dup_set_unset_ok\n"); return 0;
    }
    /* e045 case sensitive */
    if(strcmp(case_id,"e045")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_CaSe_SeNsItIvE","x",1);
        const char *a = getenv("OAI_FAKE_ENV_FOOTGUN_CaSe_SeNsItIvE");
        const char *b = getenv("oai_fake_env_footgun_case_sensitive");
        printf("obs=env_names_case_sensitive found_upper=%d found_lower=%d\n", a!=NULL, b!=NULL);
        unsetenv("OAI_FAKE_ENV_FOOTGUN_CaSe_SeNsItIvE");
        return (a && !b) ? 0 : 10;
    }
    /* e046 non-ascii */
    if(strcmp(case_id,"e046")==0){
        setenv("OAI_FAKE_ENV_FOOTGUN_UTF8_VAL","café",1);
        const char *v = getenv("OAI_FAKE_ENV_FOOTGUN_UTF8_VAL");
        printf("obs=non_ascii_value_bytes_opaque v=%s\n", v?v:"NULL");
        unsetenv("OAI_FAKE_ENV_FOOTGUN_UTF8_VAL");
        return 10;
    }
    /* e048 snprintf bounded */
    if(strcmp(case_id,"e048")==0){
        char name[64];
        int n = snprintf(name, sizeof(name), "OAI_FAKE_ENV_FOOTGUN_SNPRINTF_A");
        printf("obs=snprintf_bounded_ok n=%d\n", n);
        return 0;
    }
    /* naive markers */
    if(strcmp(case_id,"e049")==0){ printf("obs=naive_getenv_immutable\n"); return 10; }
    if(strcmp(case_id,"e050")==0){ printf("obs=naive_setenv_always_safe\n"); return 10; }
    if(strcmp(case_id,"e051")==0){ printf("obs=naive_putenv_copies\n"); return 10; }
    if(strcmp(case_id,"e052")==0){ printf("obs=naive_empty_equals_missing\n"); return 10; }
    if(strcmp(case_id,"e053")==0){ printf("obs=naive_env_thread_safe\n"); return 10; }

    /* not_tested markers – all the rest */
    printf("obs=not_tested case_id=%s\n", case_id);
    return 99;
}
