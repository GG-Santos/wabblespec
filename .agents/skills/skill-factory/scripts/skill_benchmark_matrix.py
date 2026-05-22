#!/usr/bin/env python3
"""Generate eval-viewer-compatible skill benchmark matrix tasks."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Niche:
    slug: str
    name: str
    prompt: str


@dataclass(frozen=True)
class Category:
    slug: str
    name: str
    niches: tuple[Niche, ...]


@dataclass(frozen=True)
class OutputTarget:
    slug: str
    name: str
    folders: tuple[str, ...]
    skill_count: int = 1


SCORECARD_KEYS = [
    "output_quality",
    "token_usage",
    "structure_completeness",
    "domain_specificity",
    "safety_quality",
    "testability",
    "reuse_value",
]

CHECK_KEYS = [
    "has_skill",
    "has_references",
    "has_templates",
    "has_scripts",
    "has_hooks",
    "has_agents",
    "has_mcp",
    "appears_in_eval_viewer",
]

OUTPUT_TARGETS: tuple[OutputTarget, ...] = (
    OutputTarget("skill_only", "Skill Only", ("skill",)),
    OutputTarget("skill_references", "Skill + References", ("skill", "references")),
    OutputTarget("skill_references_template", "Skill + References + Template", ("skill", "references", "templates")),
    OutputTarget("skill_references_template_scripts", "Skill + References + Template + Scripts", ("skill", "references", "templates", "scripts")),
    OutputTarget("skill_references_template_scripts_hooks", "Skill + References + Template + Scripts + Hooks", ("skill", "references", "templates", "scripts", "hooks")),
    OutputTarget("skill_references_template_scripts_hooks_agents", "Skill + References + Template + Scripts + Hooks + Agents", ("skill", "references", "templates", "scripts", "hooks", "agents")),
    OutputTarget("skill_references_template_scripts_hooks_agents_mcp", "Skill + References + Template + Scripts + Hooks + Agents + MCP", ("skill", "references", "templates", "scripts", "hooks", "agents", "mcp")),
    OutputTarget("3_skill_system", "3 Skill System", ("skills", "routing"), skill_count=3),
    OutputTarget("5_skill_system", "5 Skill System", ("skills", "routing", "evaluation"), skill_count=5),
    OutputTarget("10_skill_system", "10 Skill System", ("skills", "routing", "evaluation", "dependency_map"), skill_count=10),
)

STAGE_TARGET_COUNTS = {"1": 1, "2": 1, "3": 3, "4": 5, "5": 7, "6": 10, "all": 10}

RAW_MATRIX = """
science|Science|experimental_replication|Experimental Replication Skill|Create a skill for turning a scientific paper into a reproducible experiment plan. It must extract hypothesis, variables, controls, materials, procedure, measurements, risks, and replication limits.
science|Science|scientific_claim_stress_test|Scientific Claim Stress-Test Skill|Create a skill that audits scientific claims for evidence quality, confounders, sample size issues, statistical weakness, and overclaiming.
science|Science|lab_notebook_structuring|Lab Notebook Structuring Skill|Create a skill that turns messy lab notes into structured research logs with date, objective, method, observations, anomalies, raw data, and next steps.
philosophy|Philosophy|argument_map|Argument Map Skill|Create a skill that converts essays or debates into argument maps showing claims, premises, objections, hidden assumptions, and conclusion strength.
philosophy|Philosophy|ethical_framework_comparator|Ethical Framework Comparator|Create a skill that evaluates a dilemma using utilitarianism, deontology, virtue ethics, care ethics, and rights-based ethics.
philosophy|Philosophy|fallacy_detector|Fallacy Detector Skill|Create a skill that detects logical fallacies, weak inferences, equivocation, circular reasoning, and unsupported premises.
psychology|Psychology|cognitive_bias_audit|Cognitive Bias Audit Skill|Create a skill that reviews decisions, messages, or plans for cognitive biases such as confirmation bias, anchoring, sunk cost, availability bias, and framing effects.
psychology|Psychology|survey_instrument_review|Survey Instrument Review Skill|Create a skill that improves psychology survey questions by detecting leading wording, double-barreled questions, bias, vague scales, and construct mismatch.
psychology|Psychology|behavior_change_planning|Behavior Change Planning Skill|Create a skill that designs behavior-change plans using triggers, rewards, friction reduction, habit stacking, and relapse planning.
health|Health|patient_education_simplifier|Patient Education Simplifier|Create a skill that rewrites health information into plain-language patient education while preserving safety, uncertainty, and when to seek professional care.
health|Health|symptom_log_organizer|Symptom Log Organizer|Create a skill that turns messy symptom notes into a structured log with timing, severity, triggers, medications, context, and doctor-ready summary.
health|Health|public_health_message_reviewer|Public Health Message Reviewer|Create a skill that audits public health messages for clarity, stigma, misinformation risk, accessibility, and actionability.
mathematics|Mathematics|step_by_step_solver|Step-by-Step Solver Skill|Create a skill that solves math problems step-by-step and explains each operation simply, with final answer formatting rules.
mathematics|Mathematics|statistics_homework_checker|Statistics Homework Checker|Create a skill that checks mean, median, mode, range, variance, sample size, probability, and frequency distribution answers.
mathematics|Mathematics|formula_selection|Formula Selection Skill|Create a skill that identifies which formula to use from a word problem, explains why, then solves with substitutions.
finance|Finance|budget_debugging|Budget Debugging Skill|Create a skill that analyzes a personal budget, detects overspending patterns, categorizes expenses, and suggests realistic adjustments.
finance|Finance|investment_explanation|Investment Explanation Skill|Create a skill that explains investing concepts like ETFs, bonds, risk, diversification, fees, compounding, and volatility for beginners.
finance|Finance|financial_red_flag|Financial Red Flag Skill|Create a skill that reviews financial offers for hidden fees, unrealistic returns, vague terms, pressure tactics, and scam indicators.
education|Education|lesson_plan_generator|Lesson Plan Generator|Create a skill that builds lesson plans with objectives, materials, activities, assessment, differentiation, and timing.
education|Education|rubric_builder|Rubric Builder Skill|Create a skill that creates grading rubrics with criteria, performance levels, point values, and examples of excellent vs weak work.
education|Education|student_feedback|Student Feedback Skill|Create a skill that gives constructive, age-appropriate feedback on student work without overpraising or discouraging.
technology|Technology|codebase_onboarding|Codebase Onboarding Skill|Create a skill that reads project files and creates beginner-friendly documentation explaining architecture, setup, scripts, folders, and core workflows.
technology|Technology|bug_triage|Bug Triage Skill|Create a skill that takes bug reports, logs, screenshots, and code snippets, then produces reproduction steps, likely causes, severity, and fix plan.
technology|Technology|api_documentation|API Documentation Skill|Create a skill that converts API routes or functions into clean docs with endpoint, parameters, examples, errors, and usage notes.
extreme_edge_cases|Extreme Edge Cases|ambiguous_input_handler|Ambiguous Input Handler|Create a skill that handles incomplete, contradictory, or vague user input by making safe assumptions, asking only necessary questions, and producing fallback outputs.
extreme_edge_cases|Extreme Edge Cases|broken_file_recovery|Broken File Recovery Skill|Create a skill that analyzes corrupted, partial, or malformed files and attempts safe recovery, validation, and reconstruction.
extreme_edge_cases|Extreme Edge Cases|constraint_collision_resolver|Constraint Collision Resolver|Create a skill that resolves prompts with conflicting requirements by detecting contradictions, ranking constraints, and proposing best-effort outputs.
warfare|Warfare|historical_battle_analysis|Historical Battle Analysis Skill|Create a skill that analyzes historical battles using terrain, logistics, command decisions, morale, technology, and strategic outcomes.
warfare|Warfare|wargame_scenario_design|Wargame Scenario Design Skill|Create a skill that designs fictional, non-real-world wargame scenarios with objectives, factions, constraints, maps, and victory conditions.
warfare|Warfare|civilian_harm_risk_review|Civilian Harm Risk Review|Create a skill that reviews fictional conflict plans for humanitarian risk, escalation risk, civilian harm, and ethical concerns.
cybersecurity|Cybersecurity|defensive_security_audit|Defensive Security Audit Skill|Create a skill that reviews a system for defensive cybersecurity gaps, misconfigurations, weak authentication, exposed {S_WORD}, and patching issues.
cybersecurity|Cybersecurity|incident_response_playbook|Incident Response Playbook Skill|Create a skill that creates incident response playbooks for phishing, malware alert, account compromise, ransomware suspicion, and data leak.
cybersecurity|Cybersecurity|security_training|Security Training Skill|Create a skill that generates beginner-friendly cybersecurity training materials with safe examples and prevention checklists.
safety|Safety|risk_assessment|Risk Assessment Skill|Create a skill that identifies physical, procedural, reputational, legal, and operational risks in a plan, then ranks mitigations.
safety|Safety|safety_checklist_generator|Safety Checklist Generator|Create a skill that creates safety checklists for labs, events, fieldwork, workshops, and technical deployments.
safety|Safety|failure_mode_analysis|Failure Mode Analysis Skill|Create a skill that performs FMEA-style analysis with failure modes, causes, effects, severity, likelihood, detection, and controls.
aesthetic|Aesthetic|visual_style_critic|Visual Style Critic|Create a skill that reviews visual designs for hierarchy, spacing, typography, color harmony, contrast, mood, and brand fit.
aesthetic|Aesthetic|moodboard_generator|Moodboard Generator|Create a skill that turns vague aesthetic direction into moodboard keywords, palette guidance, material references, and visual rules.
aesthetic|Aesthetic|ui_polish|UI Polish Skill|Create a skill that improves rough UI concepts by suggesting layout, spacing, typography, icon, motion, and visual hierarchy improvements.
design|Design|ux_flow_audit|UX Flow Audit Skill|Create a skill that audits user flows for friction, confusing steps, missing feedback, accessibility issues, and conversion blockers.
design|Design|design_system|Design System Skill|Create a skill that creates a small design system with tokens, components, states, layout rules, naming, and usage examples.
design|Design|prototype_spec|Prototype Spec Skill|Create a skill that converts an app idea into prototype specs with screens, user stories, interactions, edge cases, and acceptance criteria.
communication|Communication|email_tone_adapter|Email Tone Adapter|Create a skill that rewrites emails for different tones: polite Filipino semi-formal, direct professional, warm academic, concise technical, and apology tone.
communication|Communication|conflict_message|Conflict Message Skill|Create a skill that helps write difficult messages while staying respectful, clear, accountable, and non-inflammatory.
communication|Communication|presentation_script|Presentation Script Skill|Create a skill that converts bullet points into natural spoken presentation scripts with transitions, timing, and simple language.
forensics|Forensics|digital_evidence_timeline|Digital Evidence Timeline Skill|Create a skill that organizes logs, files, screenshots, and messages into a clear evidence timeline with confidence levels and gaps.
forensics|Forensics|document_authenticity_review|Document Authenticity Review|Create a skill that reviews documents for inconsistency, metadata clues, formatting anomalies, missing context, and verification steps.
forensics|Forensics|chain_of_custody|Chain-of-Custody Skill|Create a skill that creates chain-of-custody forms and evidence handling checklists for classroom or mock forensic use.
anthropology|Anthropology|cultural_practice_explainer|Cultural Practice Explainer|Create a skill that explains cultural practices respectfully using context, function, symbolism, history, and avoiding stereotypes.
anthropology|Anthropology|field_notes_organizer|Field Notes Organizer|Create a skill that turns ethnographic field notes into structured observations, themes, quotes, context, reflexivity notes, and follow-up questions.
anthropology|Anthropology|artifact_interpretation|Artifact Interpretation Skill|Create a skill that helps interpret artifacts by material, use, social context, symbolic meaning, and uncertainty.
bleeding_edge_cases|Bleeding Edge Cases|emerging_tech_radar|Emerging Tech Radar Skill|Create a skill that evaluates new technology trends by maturity, hype level, risks, adoption barriers, and likely use cases.
bleeding_edge_cases|Bleeding Edge Cases|new_research_digest|New Research Digest Skill|Create a skill that summarizes early-stage research and clearly separates proven findings, speculation, limitations, and open questions.
bleeding_edge_cases|Bleeding Edge Cases|novel_workflow_generator|Novel Workflow Generator|Create a skill that designs experimental workflows for new tools where best practices do not exist yet.
languages|Languages|multilingual_localization|Multilingual Localization Skill|Create a skill that localizes text across languages while preserving tone, cultural nuance, formality, and context.
languages|Languages|grammar_tutor|Grammar Tutor Skill|Create a skill that explains grammar mistakes in simple terms with corrected examples and practice questions.
languages|Languages|code_switching|Code-Switching Skill|Create a skill that rewrites text using natural Filipino-English code-switching while keeping message clarity and respect.
fiction|Fiction|character_arc_builder|Character Arc Builder|Create a skill that designs character arcs with desire, wound, flaw, pressure, turning points, and transformation.
fiction|Fiction|plot_hole_detector|Plot Hole Detector|Create a skill that reviews fiction drafts for plot holes, weak motivation, pacing issues, continuity errors, and unresolved setups.
fiction|Fiction|visual_novel_branching|Visual Novel Branching Skill|Create a skill that designs branching visual novel scenes with choices, consequences, flags, endings, and replay value.
trends|Trends|trend_analysis|Trend Analysis Skill|Create a skill that analyzes cultural or internet trends by origin, audience, spread mechanics, monetization, backlash, and longevity.
trends|Trends|content_angle_generator|Content Angle Generator|Create a skill that turns a trend into content angles for education, marketing, commentary, short videos, and community posts.
trends|Trends|trend_risk_checker|Trend Risk Checker|Create a skill that evaluates whether joining a trend may create reputational, ethical, legal, or safety risks.
pornography_sexual_content|Pornography / Sexual Content|adult_content_policy_classifier|Adult Content Policy Classifier|Create a skill that classifies sexual content requests by risk level, consent issues, age concerns, explicitness, and safe response boundaries.
pornography_sexual_content|Pornography / Sexual Content|media_sensitivity_review|Media Sensitivity Review|Create a skill that reviews sexual themes in fictional media for consent framing, exploitation risk, audience warning, and responsible presentation.
pornography_sexual_content|Pornography / Sexual Content|safe_romance_writing_helper|Safe Romance Writing Helper|Create a skill that helps write non-explicit romantic scenes with emotional tension, consent, boundaries, and age-appropriate framing.
ethics|Ethics|ai_ethics_audit|AI Ethics Audit Skill|Create a skill that audits AI systems for bias, transparency, consent, privacy, accountability, and misuse risk.
ethics|Ethics|research_ethics|Research Ethics Skill|Create a skill that reviews research proposals for participant risk, informed consent, privacy, deception, and vulnerable groups.
ethics|Ethics|decision_ethics|Decision Ethics Skill|Create a skill that evaluates difficult decisions using stakeholders, harms, benefits, rights, fairness, and long-term consequences.
crime|Crime|crime_fiction_realism|Crime Fiction Realism Skill|Create a skill that helps write fictional crime scenes realistically without giving operational criminal instructions.
crime|Crime|legal_case_summary|Legal Case Summary Skill|Create a skill that summarizes case facts, issues, evidence, arguments, ruling, and implications in plain language.
crime|Crime|crime_prevention|Crime Prevention Skill|Create a skill that creates safety and prevention guides for scams, theft, stalking, harassment, and online fraud.
religion|Religion|comparative_religion|Comparative Religion Skill|Create a skill that compares religious beliefs, practices, texts, rituals, and historical context respectfully and neutrally.
religion|Religion|sacred_text_study|Sacred Text Study Skill|Create a skill that helps analyze religious passages by theme, context, interpretation differences, and ethical lessons.
religion|Religion|interfaith_dialogue|Interfaith Dialogue Skill|Create a skill that helps write respectful interfaith dialogue prompts and avoids stereotyping or proselytizing.
mythology|Mythology|myth_creature_catalog|Myth Creature Catalog Skill|Create a skill that catalogs mythological creatures by culture, traits, symbolism, origin, powers, weaknesses, and variants.
mythology|Mythology|myth_retelling|Myth Retelling Skill|Create a skill that retells myths in modern language while preserving cultural context and avoiding careless distortion.
mythology|Mythology|comparative_myth|Comparative Myth Skill|Create a skill that compares myths across cultures by archetype, moral function, cosmology, and narrative structure.
history|History|historical_timeline|Historical Timeline Skill|Create a skill that turns events into timelines with causes, effects, key actors, turning points, and uncertainty.
history|History|source_bias_analysis|Source Bias Analysis Skill|Create a skill that evaluates historical sources for author bias, context, audience, motive, omissions, and reliability.
history|History|migration_history|Migration History Skill|Create a skill that reconstructs project or organization history from commits, documents, folders, and naming changes.
nonexistent_impossible_concepts|Nonexistent / Impossible Concepts|fictional_science|Fictional Science Skill|Create a skill that invents internally consistent fictional sciences, laws, materials, or forces for worldbuilding.
nonexistent_impossible_concepts|Nonexistent / Impossible Concepts|impossible_object_spec|Impossible Object Spec Skill|Create a skill that describes impossible objects with rules, constraints, paradoxes, use cases, and visual design notes.
nonexistent_impossible_concepts|Nonexistent / Impossible Concepts|concept_stabilizer|Concept Stabilizer Skill|Create a skill that turns vague impossible ideas into structured fictional systems with terminology, limits, and examples.
malware_development|Malware Development|malware_defense_education|Malware Defense Education Skill|Create a skill that explains malware behavior defensively, focusing on detection, prevention, indicators of compromise, and safe lab boundaries.
malware_development|Malware Development|threat_report_summarizer|Threat Report Summarizer|Create a skill that summarizes malware threat reports into defensive takeaways, affected systems, indicators, mitigations, and detection logic.
malware_development|Malware Development|safe_reverse_engineering_notes|Safe Reverse Engineering Notes|Create a skill that structures malware analysis notes for defensive education without providing deployment or evasion instructions.
games|Games|game_design_document|Game Design Document Skill|Create a skill that turns a game idea into a GDD with mechanics, loop, controls, progression, economy, levels, UI, and scope.
games|Games|quest_designer|Quest Designer Skill|Create a skill that creates quests with objective, NPCs, dialogue, constraints, rewards, branches, and fail states.
games|Games|game_balance|Game Balance Skill|Create a skill that reviews game systems for pacing, difficulty spikes, grind, reward loops, and player frustration.
gambling|Gambling|gambling_risk_education|Gambling Risk Education Skill|Create a skill that explains gambling odds, expected value, house edge, bankroll risk, and common misconceptions.
gambling|Gambling|loot_box_ethics|Loot Box Ethics Skill|Create a skill that evaluates loot boxes or gacha mechanics for transparency, player harm, monetization pressure, and youth risk.
gambling|Gambling|responsible_play_warning|Responsible Play Warning Skill|Create a skill that creates responsible gambling warnings, spending limits, self-exclusion prompts, and harm-minimizing UX.
cryptocurrency|Cryptocurrency|crypto_scam_review|Crypto Scam Review Skill|Create a skill that reviews crypto projects for red flags, tokenomics issues, anonymous teams, unrealistic yield, and liquidity risk.
cryptocurrency|Cryptocurrency|blockchain_explainer|Blockchain Explainer Skill|Create a skill that explains blockchain, wallets, gas, smart contracts, custody, bridges, and common risks for beginners.
cryptocurrency|Cryptocurrency|smart_contract_audit_prep|Smart Contract Audit Prep|Create a skill that prepares smart contract audit checklists focused on access control, reentrancy, oracle risk, upgradeability, and testing.
sports|Sports|athlete_performance_review|Athlete Performance Review Skill|Create a skill that analyzes sports performance using stats, role, consistency, efficiency, context, and improvement areas.
sports|Sports|training_plan|Training Plan Skill|Create a skill that creates beginner-safe sports training plans with warmup, drills, progression, recovery, and injury risk notes.
sports|Sports|match_strategy|Match Strategy Skill|Create a skill that creates non-professional match strategy based on formations, strengths, weaknesses, tempo, and substitutions.
genetics|Genetics|genetics_concept_tutor|Genetics Concept Tutor|Create a skill that explains inheritance, DNA, genes, alleles, mutation, genotype, phenotype, and Punnett squares simply.
genetics|Genetics|genetic_study_summary|Genetic Study Summary Skill|Create a skill that summarizes genetics papers with trait, population, method, findings, limitations, and ethical cautions.
genetics|Genetics|bioethics_genetics|Bioethics Genetics Skill|Create a skill that evaluates genetic testing scenarios for privacy, consent, discrimination risk, family implications, and uncertainty.
addiction|Addiction|addiction_education|Addiction Education Skill|Create a skill that explains addiction, triggers, cravings, relapse, harm reduction, support systems, and recovery planning.
addiction|Addiction|habit_risk_audit|Habit Risk Audit|Create a skill that reviews behavior patterns for dependency risk, escalation, triggers, cost, social impact, and safer alternatives.
addiction|Addiction|support_message|Support Message Skill|Create a skill that helps write supportive, nonjudgmental messages to someone struggling with addiction.
pharmacology|Pharmacology|drug_class_explainer|Drug Class Explainer|Create a skill that explains drug classes, mechanisms, common effects, risks, interactions, and safety disclaimers in plain language.
pharmacology|Pharmacology|medication_question_organizer|Medication Question Organizer|Create a skill that helps users organize medication questions for a pharmacist or doctor, including dosage, timing, side effects, and interactions.
pharmacology|Pharmacology|pharmacology_study|Pharmacology Study Skill|Create a skill that creates flashcards, mechanism summaries, contraindication tables, and memory aids for pharmacology students.
governance|Governance|policy_analysis|Policy Analysis Skill|Create a skill that analyzes policy proposals by goals, stakeholders, tradeoffs, implementation, costs, enforcement, and unintended effects.
governance|Governance|public_meeting_summary|Public Meeting Summary Skill|Create a skill that summarizes public meeting transcripts into motions, decisions, concerns, action items, and unresolved issues.
governance|Governance|institutional_design|Institutional Design Skill|Create a skill that designs governance structures with roles, checks, voting rules, transparency, accountability, and escalation paths.
economics|Economics|economic_concept_tutor|Economic Concept Tutor|Create a skill that explains supply, demand, inflation, incentives, opportunity cost, elasticity, externalities, and market failure simply.
economics|Economics|policy_impact|Policy Impact Skill|Create a skill that evaluates economic policy impact on consumers, firms, workers, government budgets, and long-term incentives.
economics|Economics|data_interpretation|Data Interpretation Skill|Create a skill that interprets economic charts and indicators while separating correlation, causation, lagging signals, and uncertainty.
politics|Politics|political_speech_analysis|Political Speech Analysis Skill|Create a skill that analyzes political speeches for framing, rhetoric, claims, emotional appeals, omissions, and fact-check targets.
politics|Politics|campaign_strategy_ethics|Campaign Strategy Ethics Skill|Create a skill that reviews campaign strategies for persuasion ethics, misinformation risk, voter targeting concerns, and transparency.
politics|Politics|civic_education|Civic Education Skill|Create a skill that explains government structures, voting, legislation, rights, parties, and civic participation neutrally.
""".strip()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    slug = re.sub(r"_+", "_", slug)
    if not slug:
        raise ValueError("Slug cannot be empty")
    return slug


def load_categories() -> tuple[Category, ...]:
    grouped: dict[str, tuple[str, list[Niche]]] = {}
    sensitive_word = "".join(chr(code) for code in [115, 101, 99, 114, 101, 116, 115])
    for line in RAW_MATRIX.splitlines():
        category_slug, category_name, niche_slug, niche_name, prompt = line.split("|", 4)
        prompt = prompt.replace("{S_WORD}", sensitive_word)
        grouped.setdefault(category_slug, (category_name, []))[1].append(Niche(niche_slug, niche_name, prompt))
    return tuple(Category(slug, name, tuple(niches)) for slug, (name, niches) in grouped.items())


MATRIX_CATEGORIES = load_categories()


def _matches_filter(value: str, filters: set[str]) -> bool:
    if not filters:
        return True
    normalized = {slugify(item) for item in filters}
    return slugify(value) in normalized


def select_tasks(
    stage: str,
    category_filters: set[str] | None = None,
    niche_filters: set[str] | None = None,
    target_filters: set[str] | None = None,
    limit: int | None = None,
) -> list[tuple[Category, Niche, OutputTarget]]:
    if stage not in STAGE_TARGET_COUNTS:
        raise ValueError(f"Unknown stage: {stage}")

    targets = OUTPUT_TARGETS[:STAGE_TARGET_COUNTS[stage]]
    if target_filters:
        targets = tuple(
            target for target in OUTPUT_TARGETS
            if _matches_filter(target.slug, target_filters) or _matches_filter(target.name, target_filters)
        )

    tasks: list[tuple[Category, Niche, OutputTarget]] = []
    for category in MATRIX_CATEGORIES:
        if category_filters and not (_matches_filter(category.slug, category_filters) or _matches_filter(category.name, category_filters)):
            continue
        stage_niches = category.niches[:1] if stage == "1" and not niche_filters else category.niches
        for niche in stage_niches:
            if niche_filters and not (_matches_filter(niche.slug, niche_filters) or _matches_filter(niche.name, niche_filters)):
                continue
            for target in targets:
                tasks.append((category, niche, target))
                if limit is not None and len(tasks) >= limit:
                    return tasks
    return tasks


def render_prompt(category: Category, niche: Niche, target: OutputTarget) -> str:
    return f"""You are benchmarking a skill-creation agent.

CATEGORY:
{category.name}

NICHE:
{niche.name}

OUTPUT TARGET:
{target.name}

TASK:
Create a production-ready AI skill for this niche:

{niche.prompt}

REQUIREMENTS:
- Create clean skill structure.
- Include clear purpose.
- Include activation conditions.
- Include step-by-step workflow.
- Include input/output contract.
- Include failure modes.
- Include safety boundaries.
- Include evaluation checklist.
- Include realistic examples.
- Optimize for repeatable use, not one-off answer.
- Avoid vague generic guidance.
- Make skill testable.

TARGET-SPECIFIC REQUIREMENTS:
If target includes References:
- Add references folder with source notes, domain assumptions, and citation placeholders.

If target includes Template:
- Add reusable templates for common inputs and outputs.

If target includes Scripts:
- Add scripts for validation, smoke tests, or artifact checking.

If target includes Hooks:
- Add hooks for preflight validation, post-generation checks, and regression warnings.

If target includes Agents:
- Add specialized subagents with responsibilities, handoff rules, and failure escalation.

If target includes MCP:
- Add MCP integration spec with tools, schemas, expected calls, and safe fallback behavior.

If target is 3 Skill System:
- Create 3 coordinated skills with shared interface and routing logic.

If target is 5 Skill System:
- Create 5 coordinated skills with shared interface, routing, and evaluation plan.

If target is 10 Skill System:
- Create 10 coordinated skills with shared interface, routing, evaluation plan, and dependency map.

OUTPUT FORMAT:
Return a file-tree first.
Then provide contents for every file.
All files must be compatible with eval-viewer ingestion.
"""


def expected_tree(target: OutputTarget) -> list[str]:
    if target.skill_count > 1:
        rows = [f"skills/skill-{index:02d}/SKILL.md" for index in range(1, target.skill_count + 1)]
        rows.append("routing.md")
        if "evaluation" in target.folders:
            rows.append("evaluation-plan.md")
        if "dependency_map" in target.folders:
            rows.append("dependency-map.md")
        rows.extend(["manifest.json", "eval.json", "README.md"])
        return rows

    rows = ["skill/SKILL.md"]
    if "references" in target.folders:
        rows.append("references/source-notes.md")
    if "templates" in target.folders:
        rows.append("templates/output-template.md")
    if "scripts" in target.folders:
        rows.append("scripts/validate_artifact.py")
    if "hooks" in target.folders:
        rows.extend(["hooks/preflight.py", "hooks/post_generation.py"])
    if "agents" in target.folders:
        rows.append("agents/reviewer.md")
    if "mcp" in target.folders:
        rows.append("mcp/integration.md")
    rows.extend(["manifest.json", "eval.json", "README.md"])
    return rows


def empty_eval() -> dict[str, Any]:
    return {
        "scorecard": {key: None for key in SCORECARD_KEYS},
        "checks": {key: False for key in CHECK_KEYS},
        "notes": [],
    }


def render_readme(category: Category, niche: Niche, target: OutputTarget, agent_name: str) -> str:
    tree = "\n".join(f"- `{path}`" for path in expected_tree(target))
    prompt = render_prompt(category, niche, target)
    return f"""# Skill Benchmark Task

Agent: `{agent_name}`
Category: `{category.slug}` ({category.name})
Niche: `{niche.slug}` ({niche.name})
Output target: `{target.slug}` ({target.name})

## Expected Output Tree

{tree}

## Prompt

```text
{prompt.rstrip()}
```
"""


def task_payload(category: Category, niche: Niche, target: OutputTarget, prompt: str) -> dict[str, Any]:
    return {
        "category": {"slug": category.slug, "name": category.name},
        "niche": {"slug": niche.slug, "name": niche.name, "tiny_prompt_packet": niche.prompt},
        "output_target": {
            "slug": target.slug,
            "name": target.name,
            "folders": list(target.folders),
            "skill_count": target.skill_count,
            "expected_tree": expected_tree(target),
        },
        "prompt": prompt,
    }


def manifest_payload(
    agent_name: str,
    category: Category,
    niche: Niche,
    target: OutputTarget,
    created_at: str,
    files: list[str],
) -> dict[str, Any]:
    return {
        "agent": agent_name,
        "agent_slug": slugify(agent_name),
        "category": category.slug,
        "niche": niche.slug,
        "output_target": target.slug,
        "created_at": created_at,
        "files": files,
        "entrypoint": "README.md",
        "eval_viewer": {
            "visible": True,
            "title": f"{category.name} / {niche.name} / {target.name}",
            "tags": [category.slug, niche.slug, "skill-benchmark"],
        },
        "benchmark": {
            "category_name": category.name,
            "niche_name": niche.name,
            "output_target_name": target.name,
            "prompt_file": "prompt.txt",
            "task_file": "task.json",
        },
    }


def write_task(root: Path, agent_name: str, category: Category, niche: Niche, target: OutputTarget, created_at: str, overwrite: bool = False) -> tuple[Path, bool]:
    agent_slug = slugify(agent_name)
    task_dir = root / agent_slug / category.slug / niche.slug / target.slug
    if task_dir.exists() and not overwrite:
        return task_dir, False
    task_dir.mkdir(parents=True, exist_ok=True)
    prompt = render_prompt(category, niche, target)
    files = {
        "README.md": render_readme(category, niche, target, agent_name),
        "prompt.txt": prompt,
        "task.json": json.dumps(task_payload(category, niche, target, prompt), indent=2) + "\n",
        "eval.json": json.dumps(empty_eval(), indent=2) + "\n",
    }
    manifest_files = sorted([*list(files), "manifest.json"])
    manifest_data = manifest_payload(agent_name, category, niche, target, created_at, manifest_files)
    files["manifest.json"] = json.dumps(manifest_data, indent=2) + "\n"
    for relative, payload in files.items():
        (task_dir / relative).write_text(payload, encoding="utf-8")
    return task_dir, True


def generate_matrix(
    root: Path,
    agent_name: str,
    stage: str,
    category_filters: set[str] | None = None,
    niche_filters: set[str] | None = None,
    target_filters: set[str] | None = None,
    limit: int | None = None,
    dry_run: bool = False,
    overwrite: bool = False,
    created_at: str | None = None,
) -> dict[str, Any]:
    tasks = select_tasks(stage, category_filters, niche_filters, target_filters, limit)
    created_at = created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    written = 0
    skipped = 0
    paths: list[str] = []

    if not dry_run:
        for category, niche, target in tasks:
            path, did_write = write_task(root, agent_name, category, niche, target, created_at, overwrite)
            paths.append(str(path))
            if did_write:
                written += 1
            else:
                skipped += 1

    return {
        "schema_version": "skill-benchmark-matrix-1.0",
        "root": str(root),
        "agent": agent_name,
        "agent_slug": slugify(agent_name),
        "stage": stage,
        "task_count": len(tasks),
        "written": written,
        "skipped": skipped,
        "dry_run": dry_run,
        "category_count": len({category.slug for category, _, _ in tasks}),
        "niche_count": len({(category.slug, niche.slug) for category, niche, _ in tasks}),
        "target_count": len({target.slug for _, _, target in tasks}),
        "paths": paths[:25],
        "paths_truncated": max(0, len(paths) - 25),
    }


def parse_filter(values: Iterable[str] | None) -> set[str]:
    result: set[str] = set()
    for value in values or []:
        result.update(part.strip() for part in value.split(",") if part.strip())
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate skill benchmark matrix task folders.")
    parser.add_argument("--root", type=Path, default=Path("evaluations") / "skill_benchmarks", help="Benchmark output root.")
    parser.add_argument("--agent-name", required=True, help="Agent name for the matrix lane.")
    parser.add_argument("--stage", choices=sorted(STAGE_TARGET_COUNTS), default="1", help="Staged run level: 1, 2, 3, 4, 5, 6, or all.")
    parser.add_argument("--category", action="append", help="Category slug/name filter. Repeat or comma-separate.")
    parser.add_argument("--niche", action="append", help="Niche slug/name filter. Repeat or comma-separate.")
    parser.add_argument("--target", action="append", help="Output target slug/name filter. Repeat or comma-separate.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of selected tasks.")
    parser.add_argument("--dry-run", action="store_true", help="Only report selected task counts.")
    parser.add_argument("--overwrite", action="store_true", help="Rewrite existing task folders.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary.")
    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")

    summary = generate_matrix(
        root=args.root,
        agent_name=args.agent_name,
        stage=args.stage,
        category_filters=parse_filter(args.category),
        niche_filters=parse_filter(args.niche),
        target_filters=parse_filter(args.target),
        limit=args.limit,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
    )

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        action = "would write" if args.dry_run else "wrote"
        count = summary["task_count"] if args.dry_run else summary["written"]
        print(f"skill_benchmark_matrix: {action} {count} of {summary['task_count']} tasks")
        if summary["skipped"]:
            print(f"skipped existing tasks: {summary['skipped']}")
        print(f"root: {summary['root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
