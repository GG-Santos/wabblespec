# InferenceGuard Trigger Vocabulary

Source: Parseltongue algorithm (G0DM0D3 PAPER §3.4), adapted for SDLC-security vocabulary only.

## Tier 1 — Light (always checked when InferenceGuard is active)

These are common SDLC security terms that may cause false refusals in security-domain tasks.

```
hack
exploit
bypass
crack
attack
penetrate
inject
override
disable
circumvent
evade
manipulate
```

12 terms. Default for general security tasks.

## Tier 2 — Standard (adds to Tier 1; default for Red protocol)

Specific security technique and vulnerability class names. Common in CVE analysis, red-team findings, and penetration test reports.

```
malware
virus
trojan
payload
shellcode
rootkit
keylogger
backdoor
vulnerability
CVE
XSS
CSRF
SSRF
IDOR
RCE
LFI
SQLi
buffer overflow
privilege escalation
authentication bypass
directory traversal
```

21 terms. Combined with Tier 1: 33 terms active for Red protocol.

## Tier 3 — Heavy (requires explicit `inference_guard_tier: heavy` in task card)

Terms with high jailbreak/harm overlap. Only enable when the task explicitly requires working with this vocabulary (advanced threat modeling, social engineering research, fraud analysis).

```
weapon
explosive
poison
synthesize
phishing
impersonate
deceive
fraud
```

8 terms. Not active by default. Requires explicit task card flag.

## Excluded terms (NEVER triggers — regardless of tier)

These are jailbreak vocabulary, not SDLC security vocabulary. Including them would make InferenceGuard a jailbreak vector. They are permanently excluded.

```
nsfw
explicit
uncensored
unfiltered
unrestricted
jailbreak
ignore
disregard
forget
pretend
roleplay
act as
you are now
new identity
```

If these terms appear in input, InferenceGuard ignores them. The module does not transform them and does not count them as trigger hits.

## Matching rules

- Case-insensitive matching
- Whole-word matching preferred; substring matching only for acronyms (XSS, CSRF, CVE, RCE, LFI, SQLi, IDOR, SSRF)
- Multi-word terms (`buffer overflow`, `privilege escalation`, `authentication bypass`, `directory traversal`) matched as phrase
- Detection precedes transformation — detect first, then apply transform to detected tokens only
