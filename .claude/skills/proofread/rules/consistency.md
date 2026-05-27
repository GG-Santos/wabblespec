# Consistency

Rules for internal consistency checking during Proofread. Applied in Step 3.

## Terminology consistency

**Synonym drift:** The same concept must be referred to by the same term throughout the document. If the document introduces "API key" in section 1 and uses "access token" for the same concept in section 3, that is a WARN finding.

Detection: Build a concept map from the first occurrence of each significant noun phrase. Flag subsequent uses that refer to the same concept with different terminology.

Acceptable variation: technical synonyms that are explicitly equated ("API key (also called access token)") are not drift. The equating sentence is the anchor.

## Quantifier consistency

Absolute quantifiers applied to the same fact must agree:
- "always" in one location and "sometimes" for the same behavior → FAIL
- "all users" in one location and "most users" for the same claim → WARN

## Cross-reference integrity

Orphaned references are FAIL severity:
- "See section 3" when section 3 does not exist → FAIL
- "See Figure 2" when there are no figures → FAIL
- "as described above" when there is no prior description → WARN

## Tense consistency

Documents should not mix tenses within the same scope:
- Instructions should be imperative throughout ("Click Save" not "Click Save, then you will see...")
- Descriptions should be present tense throughout
- Historical statements may use past tense

Tense mixing within a single paragraph is always a WARN.

## List parallelism

All items in a list must follow the same grammatical structure. A list that mixes sentence fragments and full sentences is a WARN. A list where some items start with verbs and others with nouns is a WARN.
