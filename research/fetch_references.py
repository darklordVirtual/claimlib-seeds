# SPDX-License-Identifier: Apache-2.0
"""Fetch registrar-verified records for seeded research references.

THE SEEDING CONTRACT: titles (and any DOIs) below are SEEDS — proposed from
model knowledge or supplied by the curator — never citations. Each seed is
resolved against a registrar (DOI lookup, Crossref title search, arXiv
title-phrase search, in that order) and the returned record must AGREE with
the seeded title under the strict token guard. Only the registrar's
metadata is committed; a seed nothing agrees with is dropped and reported.

    PYTHONPATH=/Users/stian/vericlaim python3 research/fetch_references.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, "/Users/stian/vericlaim/integrations/library")
from biblio_curate import titles_agree  # noqa: E402
from litfetch import _http_get, crossref_search, parse_arxiv_atom, parse_crossref  # noqa: E402

# (id, title-seed, optional doi-seed, expected-surname, expected-year, why).
# Everything is a SEED: the resolved record must agree on TITLE (strict token
# guard), carry the expected AUTHOR surname, and land within 2 years of the
# expected YEAR — title alone proved insufficient live (a 2025 critique
# titled "Is Attention All You Need?", a book REVIEW of GEB, and an
# unrelated Apress chapter all passed the title guard).
SEEDS = [
    ("REF-001", "Time-uniform, nonparametric, nonasymptotic confidence sequences",
     None, "howard", 2021, "anytime-valid monitoring bounds; used by library bundle CLAIM-011"),
    ("REF-002", "Selective classification for deep neural networks",
     None, "geifman", 2017, "the canonical accuracy/coverage trade-off formulation"),
    ("REF-003", "On Calibration of Modern Neural Networks",
     None, "guo", 2017, "temperature scaling and modern-miscalibration baseline"),
    ("REF-004", "Conformal Risk Control",
     None, "angelopoulos", 2022, "distribution-free risk guarantees beyond coverage"),
    ("REF-005", "AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents",
     None, "andriushchenko", 2024, "external agent-safety benchmark; used by library bundle CLAIM-002"),
    ("REF-006", "Attention Is All You Need",
     None, "vaswani", 2017, "the transformer architecture underlying modern LLMs"),
    ("REF-007", "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification",
     None, "angelopoulos", 2021, "standard on-ramp to conformal prediction"),
    ("REF-008", "Multilayer feedforward networks are universal approximators",
     None, "hornik", 1989, "Hornik/Stinchcombe/White 1989 — the universal approximation theorem; context for THM-UAT-001"),
    ("REF-009", "Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services",
     "10.1145/564585.564601", "gilbert", 2002, "Gilbert & Lynch 2002 — the CAP theorem, formally proved"),
    ("REF-010", "Flow diagrams, turing machines and languages with only two formation rules",
     "10.1145/355592.365646", "bohm", 1966, "Bohm & Jacopini 1966 — the structured program theorem"),
    ("REF-011", "Pattern Recognition and Machine Learning",
     None, "bishop", 2006, "Bishop 2006 — Bayes-based ML; context for THM-BAYES-001"),
    ("REF-012", "All of Statistics: A Concise Course in Statistical Inference",
     None, "wasserman", 2004, "Wasserman — CLT and inference; context for THM-CLT-001"),
    ("REF-013", "Introduction to Algorithms",
     None, "cormen", 2009, "CLRS — the master theorem; context for THM-MASTER-001"),
    ("REF-014", "Learning with Kernels",
     None, "scholkopf", 2002, "Scholkopf & Smola — Mercer's theorem and the kernel trick"),
    ("REF-015", "Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I",
     None, "godel", 1931, "Godel 1931 — the incompleteness theorems, original paper"),
    ("REF-016", "Gödel, Escher, Bach: An Eternal Golden Braid",
     None, "hofstadter", 1979, "Hofstadter — popular exposition connecting Godel to computation (context, not a proof source)"),
    # --- batch 3: optimization, information/learning theory, graphs, logic ---
    ("REF-017", "The Lack of A Priori Distinctions Between Learning Algorithms",
     None, "wolpert", 1996, "Wolpert — the No Free Lunch theorem for learning; context for THM-NFL-001"),
    ("REF-018", "On the Uniform Convergence of Relative Frequencies of Events to Their Probabilities",
     None, "vapnik", 1971, "Vapnik & Chervonenkis — VC dimension and uniform convergence; context for THM-VC-001"),
    ("REF-019", "A Mathematical Theory of Communication",
     None, "shannon", 1948, "Shannon 1948 — information theory and the sampling context for THM-NYQ-001"),
    ("REF-020", "Classes of Recursively Enumerable Sets and Their Decision Problems",
     None, "rice", 1953, "Rice's theorem — undecidability of nontrivial semantic properties"),
    ("REF-021", "Convex Optimization",
     None, "boyd", 2004, "Boyd & Vandenberghe — KKT conditions; context for THM-KKT-001"),
    ("REF-022", "Understanding Machine Learning: From Theory to Algorithms",
     None, "shalev-shwartz", 2014, "Shalev-Shwartz & Ben-David — Rademacher/VC generalization theory"),
    ("REF-023", "Introduction to Graph Theory",
     None, "west", 2001, "West — Euler circuits and fundamental graph theory; context for THM-EULER-001"),
    ("REF-024", "Lectures on the Curry-Howard Isomorphism",
     None, "sorensen", 2006, "Sorensen & Urzyczyn — proofs-as-programs; context for THM-CH-001"),
    ("REF-025", "Matrix Analysis",
     None, "horn", 1985, "Horn & Johnson — Perron-Frobenius theory; context for THM-PF-001"),
    # --- batch 4/5: dimensionality, information, graphs, research front ---
    ("REF-026", "Extensions of Lipschitz mappings into a Hilbert space",
     None, "johnson", 1984, "Johnson & Lindenstrauss — the JL lemma; context for THM-JL-001"),
    ("REF-027", "Asymptotic Statistics",
     None, "vaart", 1998, "van der Vaart — Glivenko-Cantelli and empirical processes; context for THM-GC-001"),
    ("REF-028", "Probability and Computing: Randomization and Probabilistic Analysis in Algorithms and Data Structures",
     None, "mitzenmacher", 2005, "Mitzenmacher & Upfal — Markov/Chebyshev in algorithm analysis; context for THM-INEQ-001"),
    ("REF-029", "The Two-Valued Iterative Systems of Mathematical Logic",
     None, "post", 1941, "Post — functional completeness; context for THM-POST-001"),
    ("REF-030", "Maximal Flow Through a Network",
     None, "ford", 1956, "Ford & Fulkerson — the max-flow min-cut theorem; context for THM-MFMC-001"),
    ("REF-031", "Algebraic Geometry and Statistical Learning Theory",
     None, "watanabe", 2009, "Watanabe — singular learning theory (research front; no bounded instance attempted)"),
    ("REF-032", "Flow Matching for Generative Modeling",
     None, "lipman", 2022, "Lipman et al. — flow matching / optimal-transport paths; 1-D OT instance is THM-OT-001"),
    ("REF-033", "Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges",
     None, "bronstein", 2021, "Bronstein et al. — equivariance program (research front; no bounded instance attempted)"),
    ("REF-034", "Topology and Data",
     None, "carlsson", 2009, "Carlsson — topological data analysis (research front; no bounded instance attempted)"),
    ("REF-035", "Algorithmic Learning in a Random World",
     None, "vovk", 2005, "Vovk, Gammerman & Shafer — the founding conformal-prediction monograph; context for THM-CONF-001..004"),
    ("REF-036", "The Lean 4 Theorem Prover and Programming Language",
     None, "moura", 2021, "de Moura & Ullrich — the kernel that checks THM-LEAN-001..003"),
    # --- batch A: alignment & safety landmarks ---
    ("REF-037", "Training language models to follow instructions with human feedback",
     None, "ouyang", 2022, "InstructGPT — RLHF as the alignment baseline of modern assistants"),
    ("REF-038", "Constitutional AI: Harmlessness from AI Feedback",
     None, "bai", 2022, "principle-guided self-critique replacing human harm labels"),
    ("REF-039", "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
     None, "rafailov", 2023, "preference optimization without an explicit reward model"),
    ("REF-040", "Concrete Problems in AI Safety",
     None, "amodei", 2016, "the agenda paper that framed practical safety research"),
    ("REF-041", "Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training",
     None, "hubinger", 2024, "deceptive behavior surviving safety training — core threat model for gating"),
    ("REF-042", "Weak-to-Strong Generalization: Eliciting Strong Capabilities with Weak Supervision",
     None, "burns", 2023, "supervising models stronger than the supervisor — scalable-oversight core"),
    ("REF-043", "AI safety via debate",
     None, "irving", 2018, "adversarial verification as an oversight mechanism"),
    # --- batch B: scaling, reasoning, interpretability ---
    ("REF-044", "Scaling Laws for Neural Language Models",
     None, "kaplan", 2020, "the power-law compute/data/parameter relations"),
    ("REF-045", "Training Compute-Optimal Large Language Models",
     None, "hoffmann", 2022, "Chinchilla — data/parameter rebalancing of scaling"),
    ("REF-046", "Emergent Abilities of Large Language Models",
     None, "wei", 2022, "capability discontinuities with scale — governance-relevant"),
    ("REF-047", "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
     None, "wei", 2022, "reasoning elicitation by intermediate steps"),
    ("REF-048", "LoRA: Low-Rank Adaptation of Large Language Models",
     None, "hu", 2021, "parameter-efficient adaptation standard"),
    ("REF-049", "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
     None, "lewis", 2020, "grounding generation in retrieval — the RAG baseline"),
    ("REF-050", "Toy Models of Superposition",
     None, "elhage", 2022, "mechanistic interpretability of feature superposition"),
    # --- batch C: AI governance & accountability ---
    ("REF-051", "Toward Trustworthy AI Development: Mechanisms for Supporting Verifiable Claims",
     None, "brundage", 2020, "the verifiable-claims agenda VeriClaim operationalizes in CI"),
    ("REF-052", "Model Cards for Model Reporting",
     None, "mitchell", 2019, "structured model disclosure — governance documentation standard"),
    ("REF-053", "Datasheets for Datasets",
     None, "gebru", 2021, "dataset provenance disclosure"),
    ("REF-054", "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?",
     None, "bender", 2021, "scaling-risk critique; documentation-debt argument"),
    ("REF-055", "Frontier AI Regulation: Managing Emerging Risks to Public Safety",
     None, "anderljung", 2023, "regulatory instruments for frontier models"),
    ("REF-056", "Managing extreme AI risks amid rapid progress",
     None, "bengio", 2024, "consensus risk-management agenda (Science)"),
    ("REF-057", "Open Problems in Technical AI Governance",
     None, "reuel", 2024, "the technical governance research map"),
    ("REF-058", "Auditing large language models: a three-layered approach",
     None, "mokander", 2023, "governance/model/application audit layers — REMORA-relevant"),
    # --- batch D: enterprise architecture & the TOGAF lineage ---
    # TOGAF itself is an Open Group standard without a registrar record with
    # named authors — it cannot pass the guards and is honestly absent; the
    # scholarly lineage below carries the field.
    ("REF-059", "A framework for information systems architecture",
     None, "zachman", 1987, "Zachman — the framework TOGAF and enterprise architecture descend from"),
    ("REF-060", "Enterprise Architecture at Work",
     None, "lankhorst", 2005, "Lankhorst — EA modelling/analysis (ArchiMate lineage)"),
    ("REF-061", "Artificial Intelligence Risk Management Framework (AI RMF 1.0)",
     None, "tabassi", 2023, "NIST AI RMF — the enterprise AI governance baseline REM-024..031 aligns to"),
    ("REF-062", "Enterprise Architecture as Strategy: Creating a Foundation for Business Execution",
     None, "ross", 2006, "Ross, Weill & Robertson — EA as operating-model foundation"),
    ("REF-063", "Who Needs an Architect?",
     None, "fowler", 2003, "Fowler — architecture as shared understanding, not artifacts"),
    # --- batch E: security — classics, ML attacks, privacy ---
    ("REF-064", "Reflections on Trusting Trust",
     None, "thompson", 1984, "the compiler-backdoor argument — the root problem vericlaim's provenance chain addresses"),
    ("REF-065", "The Protection of Information in Computer Systems",
     None, "saltzer", 1975, "Saltzer & Schroeder — the design principles (fail-safe defaults = our fail closed)"),
    ("REF-066", "Intriguing properties of neural networks",
     None, "szegedy", 2013, "the discovery of adversarial examples"),
    ("REF-067", "Explaining and Harnessing Adversarial Examples",
     None, "goodfellow", 2014, "FGSM — adversarial vulnerability as linearity"),
    ("REF-068", "Extracting Training Data from Large Language Models",
     None, "carlini", 2020, "memorization leakage — LLM data-security baseline"),
    ("REF-069", "Universal and Transferable Adversarial Attacks on Aligned Language Models",
     None, "zou", 2023, "GCG jailbreaks — transferable attacks on alignment"),
    ("REF-070", "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection",
     None, "greshake", 2023, "indirect prompt injection — the agent-security threat REMORA gates against"),
    ("REF-071", "Calibrating Noise to Sensitivity in Private Data Analysis",
     None, "dwork", 2006, "differential privacy — the definition"),
    ("REF-072", "Deep Learning with Differential Privacy",
     None, "abadi", 2016, "DP-SGD — private training in practice"),
    ("REF-073", "Understanding the Mirai Botnet",
     None, "antonakakis", 2017, "IoT botnet anatomy — context for the Luftfiber UDM incident class"),
    # --- batch F: architecture landmarks, uncertainty, evaluation ---
    ("REF-074", "Deep Residual Learning for Image Recognition",
     None, "he", 2015, "ResNet — residual connections that made very deep nets trainable"),
    ("REF-075", "Adam: A Method for Stochastic Optimization",
     None, "kingma", 2014, "the default optimizer of deep learning"),
    ("REF-076", "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift",
     None, "ioffe", 2015, "normalization that stabilized deep training"),
    ("REF-077", "Denoising Diffusion Probabilistic Models",
     None, "ho", 2020, "the diffusion generative baseline flow matching descends from"),
    ("REF-078", "Auto-Encoding Variational Bayes",
     None, "kingma", 2013, "the VAE — variational deep generative models"),
    ("REF-079", "Generative Adversarial Networks",
     None, "goodfellow", 2014, "GANs — adversarial generative modelling"),
    ("REF-080", "Dropout: A Simple Way to Prevent Neural Networks from Overfitting",
     None, "srivastava", 2014, "the canonical regularizer"),
    ("REF-081", "Deep Reinforcement Learning from Human Preferences",
     None, "christiano", 2017, "preference-based RL — the root of RLHF"),
    ("REF-082", "Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles",
     None, "lakshminarayanan", 2016, "deep ensembles — practical uncertainty for governance"),
    ("REF-083", "Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning",
     None, "gal", 2015, "MC-dropout — uncertainty from a trained net"),
    # --- batch E (2026-07-06): the principal-AI-architect enterprise stack —
    # NIST risk/OT security, AI auditing, MLOps, industrial digital twins,
    # privacy engineering. EU law (GDPR, NIS2, AI Act, DPIA guidance) has no
    # registrar records; those live as hash-locked web snapshots in the
    # vericlaim literature catalog instead of dying here.
    ("REF-084", "Guide to Operational Technology (OT) security",
     "10.6028/nist.sp.800-82r3", "stouffer", 2023,
     "the OT/ICS security baseline for industrial (e.g. energy) AI deployments"),
    ("REF-085", "Closing the AI accountability gap",
     "10.1145/3351095.3372873", "raji", 2020,
     "internal algorithmic auditing framework — the enterprise AI audit playbook"),
    ("REF-086", "Machine Learning Operations (MLOps): Overview, Definition, and Architecture",
     "10.1109/access.2023.3262138", "kreuzberger", 2023,
     "canonical MLOps reference architecture for production ML at enterprise scale"),
    ("REF-087", "Digital Twin: Values, Challenges and Enablers From a Modeling Perspective",
     "10.1109/access.2020.2970143", "rasheed", 2020,
     "digital-twin foundations (NTNU/SINTEF lineage) — core for asset-heavy industry"),
    ("REF-088", "Physics-informed machine learning",
     "10.1038/s42254-021-00314-5", "karniadakis", 2021,
     "physics-constrained ML — the honest way to model industrial processes"),
    ("REF-089", "The Algorithmic Foundations of Differential Privacy",
     "10.1561/0400000042", "dwork", 2014,
     "the formal privacy foundation behind GDPR-grade data protection engineering"),
    ("REF-090", "k-ANONYMITY: A MODEL FOR PROTECTING PRIVACY",
     "10.1142/s0218488502001648", "sweeney", 2002,
     "the classic re-identification result — why 'anonymized' data usually is not"),
    # --- batch F (2026-07-06): frontier stack — training your own models,
    # software engineering / SaaS-scale systems, marketing science, finance.
    ("REF-091", "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
     None, "devlin", 2018, "bidirectional pretraining — the fine-tuning paradigm"),
    ("REF-092", "Language Models are Few-Shot Learners",
     None, "brown", 2020, "GPT-3 — in-context learning at scale"),
    ("REF-093", "LLaMA: Open and Efficient Foundation Language Models",
     None, "touvron", 2023, "the open foundation-model recipe (data + compute discipline)"),
    ("REF-094", "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
     None, "dao", 2022, "IO-aware exact attention — the systems trick behind long context"),
    ("REF-095", "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism",
     None, "shoeybi", 2019, "tensor/model parallelism for training at scale"),
    ("REF-096", "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models",
     None, "rajbhandari", 2019, "optimizer-state sharding — how large training fits in memory"),
    ("REF-097", "Mixed Precision Training",
     None, "micikevicius", 2017, "fp16/loss-scaling — the efficiency baseline for training"),
    ("REF-098", "QLoRA: Efficient Finetuning of Quantized LLMs",
     None, "dettmers", 2023, "4-bit finetuning — own-model adaptation on modest hardware"),
    ("REF-099", "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer",
     None, "shazeer", 2017, "conditional computation / MoE — frontier scaling pattern"),
    ("REF-100", "Distilling the Knowledge in a Neural Network",
     None, "hinton", 2015, "knowledge distillation — big teacher, deployable student"),
    ("REF-101", "Neural Machine Translation of Rare Words with Subword Units",
     None, "sennrich", 2015, "BPE tokenization — the vocabulary layer of every LLM"),
    ("REF-102", "The Pile: An 800GB Dataset of Diverse Text for Language Modeling",
     None, "gao", 2020, "curated pretraining data — composition documented and auditable"),
    ("REF-103", "On the criteria to be used in decomposing systems into modules",
     "10.1145/361598.361623", "parnas", 1972, "information hiding — the root of modular design"),
    ("REF-104", "No Silver Bullet: Essence and Accidents of Software Engineering",
     "10.1109/mc.1987.1663532", "brooks", 1987, "essence vs accident — why tooling alone cannot save you"),
    ("REF-105", "Letters to the editor: go to statement considered harmful",
     "10.1145/362929.362947", "dijkstra", 1968, "structured programming — reasoning over control flow"),
    ("REF-106", "Communicating Sequential Processes",
     "10.1145/359576.359585", "hoare", 1978, "CSP — the concurrency model behind Go channels et al."),
    ("REF-107", "Dynamo",
     "10.1145/1294261.1294281", "decandia", 2007, "eventual consistency in production — SaaS availability"),
    ("REF-108", "MapReduce",
     "10.1145/1327452.1327492", "dean", 2008, "the batch-compute abstraction that scaled the industry"),
    ("REF-109", "Spanner",
     "10.1145/2491245", "corbett", 2013, "globally consistent transactions — TrueTime"),
    ("REF-110", "Borg, Omega, and Kubernetes",
     "10.1145/2890784", "burns", 2016, "a decade of container orchestration lessons"),
    ("REF-111", "A New Product Growth for Model Consumer Durables",
     "10.1287/mnsc.15.5.215", "bass", 1969, "the Bass diffusion model — adoption curves"),
    ("REF-112", "Counting Your Customers: Who Are They and What Will They Do Next?",
     "10.1287/mnsc.33.1.1", "schmittlein", 1987, "Pareto/NBD — the probabilistic customer-base model"),
    ("REF-113", "RFM and CLV: Using Iso-Value Curves for Customer Base Analysis",
     "10.1509/jmkr.2005.42.4.415", "fader", 2005, "customer lifetime value from RFM — SaaS unit economics"),
    ("REF-114", "Controlled experiments on the web: survey and practical guide",
     "10.1007/s10618-008-0114-1", "kohavi", 2009, "A/B testing done right — the growth experimentation bible"),
    ("REF-115", "Using Online Conversations to Study Word-of-Mouth Communication",
     "10.1287/mksc.1040.0071", "godes", 2004, "measuring word-of-mouth — organic growth signal"),
    ("REF-116", "Portfolio Selection",
     "10.1111/j.1540-6261.1952.tb01525.x", "markowitz", 1952, "mean-variance portfolio theory"),
    ("REF-117", "Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk",
     "10.1111/j.1540-6261.1964.tb02865.x", "sharpe", 1964, "CAPM — priced risk vs diversifiable risk"),
    ("REF-118", "The Pricing of Options and Corporate Liabilities",
     "10.1086/260062", "black", 1973, "Black-Scholes option pricing"),
    ("REF-119", "Efficient Capital Markets: A Review of Theory and Empirical Work",
     "10.2307/2325486", "fama", 1970, "efficient-market hypothesis — the null you must beat"),
    ("REF-120", "Prospect Theory: An Analysis of Decision under Risk",
     "10.2307/1914185", "kahneman", 1979, "loss aversion — how decisions actually get made"),
    ("REF-121", "A New Interpretation of Information Rate",
     "10.1002/j.1538-7305.1956.tb03809.x", "kelly", 1956, "the Kelly criterion — information-theoretic bet sizing"),
    # --- batch G (2026-07-06): capability via verification, not scale —
    # the literature behind verify-route-abstain (THM-VOTE/THM-ROUTE math).
    ("REF-122", "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
     None, "wang", 2022, "majority voting over samples — the Condorcet pattern in practice"),
    ("REF-123", "Let's Verify Step by Step",
     None, "lightman", 2023, "process supervision — verifiers over reasoning steps"),
    ("REF-124", "STaR: Bootstrapping Reasoning With Reasoning",
     None, "zelikman", 2022, "self-taught reasoning — verified traces become training data"),
    ("REF-125", "Self-Refine: Iterative Refinement with Self-Feedback",
     None, "madaan", 2023, "iterative self-feedback loops — and their limits (see REF-126)"),
    ("REF-126", "Large Language Models Cannot Self-Correct Reasoning Yet",
     None, "huang", 2023, "the honest limit: intrinsic self-correction does not work — external verification does"),
    ("REF-127", "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance",
     None, "chen", 2023, "LLM cascades — the cost side of THM-ROUTE-001"),
    ("REF-128", "RouteLLM: Learning to Route LLMs with Preference Data",
     None, "ong", 2024, "learned routing between weak and strong models"),
    ("REF-129", "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters",
     None, "snell", 2024, "test-time compute beats parameter scale — capability another way"),
    # --- batch I (2026-07-06): the latest AGI/frontier frameworks —
    # reasoning, agents, world models, architectures, multimodal,
    # interpretability, and honest counterpoints.
    ("REF-130", "Large Language Models are Zero-Shot Reasoners",
     None, "kojima", 2022, "'let's think step by step' — zero-shot CoT"),
    ("REF-131", "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning",
     None, "deepseek", 2025, "RL-trained reasoning — the open R1 recipe"),
    ("REF-132", "Reasoning with Language Model is Planning with World Model",
     None, "hao", 2023, "RAP — search over an LLM's own world model"),
    ("REF-133", "Voyager: An Open-Ended Embodied Agent with Large Language Models",
     None, "wang", 2023, "open-ended skill acquisition — lifelong agent learning"),
    ("REF-134", "Generative Agents: Interactive Simulacra of Human Behavior",
     None, "park", 2023, "memory+reflection+planning agents — believable behavior"),
    ("REF-135", "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering",
     None, "yang", 2024, "agent-computer interface design for real SWE tasks"),
    ("REF-136", "Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets",
     None, "power", 2022, "delayed generalization — the grokking phenomenon"),
    ("REF-137", "In-context Learning and Induction Heads",
     None, "olsson", 2022, "the mechanistic account of in-context learning"),
    ("REF-138", "Are Emergent Abilities of Large Language Models a Mirage?",
     None, "schaeffer", 2023, "the honest counterpoint: emergence as a metric artifact"),
    ("REF-139", "Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model",
     None, "schrittwieser", 2019, "MuZero — planning with a learned world model"),
    ("REF-140", "Decision Transformer: Reinforcement Learning via Sequence Modeling",
     None, "chen", 2021, "RL as conditional sequence modeling"),
    ("REF-141", "Mamba: Linear-Time Sequence Modeling with Selective State Spaces",
     None, "gu", 2023, "selective state spaces — a Transformer alternative"),
    ("REF-142", "Efficiently Modeling Long Sequences with Structured State Spaces",
     None, "gu", 2021, "S4 — the state-space-model line for long context"),
    ("REF-143", "Learning Transferable Visual Models From Natural Language Supervision",
     None, "radford", 2021, "CLIP — contrastive image-text representation"),
    ("REF-144", "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
     None, "dosovitskiy", 2020, "ViT — transformers for vision"),
    ("REF-145", "Flamingo: a Visual Language Model for Few-Shot Learning",
     None, "alayrac", 2022, "few-shot multimodal in-context learning"),
    ("REF-146", "Sparks of Artificial General Intelligence: Early experiments with GPT-4",
     None, "bubeck", 2023, "the AGI-claims paper — read alongside REF-138's caution"),
    ("REF-147", "Levels of AGI for Operationalizing Progress on the Path to AGI",
     None, "morris", 2023, "a taxonomy for AGI progress — capability x autonomy"),
    ("REF-148", "Discovering Language Model Behaviors with Model-Written Evaluations",
     None, "perez", 2022, "scaling evals by having models write them"),
    ("REF-149", "Representation Engineering: A Top-Down Approach to AI Transparency",
     None, "zou", 2023, "reading and steering internal representations"),
    ("REF-150", "Studying Large Language Model Generalization with Influence Functions",
     None, "grosse", 2023, "which training data drove a behavior — influence functions"),
    ("REF-151", "Measuring Progress on Scalable Oversight for Large Language Models",
     None, "bowman", 2022, "can humans supervise superhuman models? the sandwich method"),
    ("REF-152", "Graph of Thoughts: Solving Elaborate Problems with Large Language Models",
     None, "besta", 2023, "reasoning as an arbitrary graph, not just a tree"),
    ("REF-153", "The Platonic Representation Hypothesis",
     None, "huh", 2024, "models converge to a shared representation of reality"),
    ("REF-154", "Mastering Diverse Domains through World Models",
     None, "hafner", 2023, "DreamerV3 — one world-model agent across domains"),
    ("REF-155", "RWKV: Reinventing RNNs for the Transformer Era",
     None, "peng", 2023, "attention-free recurrence at transformer quality"),
    ("REF-156", "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation",
     None, "wu", 2023, "multi-agent conversation as an application framework"),
    ("REF-157", "Chain-of-Thought Reasoning Without Prompting",
     None, "wang", 2024, "eliciting latent reasoning by decoding, not prompting"),
]


def _norm(s: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def _record_agrees(seed_title, surname, year, work) -> bool:
    """Title tokens + author surname + year window — all three, always."""
    if not titles_agree(seed_title, work["title"]):
        return False
    if not any(_norm(surname) in _norm(a) for a in work.get("authors", [])):
        return False
    wy = work.get("year")
    return isinstance(wy, int) and abs(wy - year) <= 2


def _lookup(title: str, doi: str | None, surname: str, year: int):
    """Registrar resolution order: DOI -> Crossref title -> arXiv phrase.
    Every path ends at the same title+author+year guard."""
    if doi:
        try:
            works = parse_crossref(_http_get("https://api.crossref.org/works/"
                                             + urllib.parse.quote(doi)))
            if works and _record_agrees(title, surname, year, works[0]):
                return works[0], "doi"
            if works:
                return None, (f"DOI seed resolves to {works[0]['title']!r} "
                              f"({works[0].get('year')}) — fails the "
                              f"title+author+year guard")
        except Exception as exc:  # noqa: BLE001
            return None, f"doi lookup failed: {exc}"
    try:
        # generic titles drown in look-alikes: search with the author
        # appended too, and scan more candidates — the guard still decides.
        seen = []
        for q in (f"{title} {surname}", title):
            for w in crossref_search(q, 10):
                if w["work_id"] in seen:
                    continue
                seen.append(w["work_id"])
                if _record_agrees(title, surname, year, w):
                    return w, "crossref-title"
    except Exception:  # noqa: BLE001 — fall through to arXiv
        pass
    time.sleep(3)
    try:
        q = urllib.parse.quote(f'ti:"{title}"')
        for w in parse_arxiv_atom(_http_get(
                "https://export.arxiv.org/api/query?search_query="
                + q + "&max_results=3")):
            if _record_agrees(title, surname, year, w):
                return w, "arxiv-title-phrase"
    except Exception as exc:  # noqa: BLE001
        return None, f"arxiv lookup failed: {exc}"
    return None, "no registrar record with an agreeing title"


def main() -> int:
    only_new = "--only-new" in sys.argv
    out_dir = Path(__file__).resolve().parent / "extracts"
    out_dir.mkdir(exist_ok=True)
    index, dropped = {}, []
    prior_verified, prior_dropped = {}, {}
    ref_path = out_dir.parent / "references.json"
    if only_new and ref_path.exists():
        prior = json.loads(ref_path.read_text())
        prior_verified = prior.get("verified", {})
        prior_dropped = {d["id"]: d for d in prior.get("dropped", [])}
    for rid, title, doi, surname, year, why in SEEDS:
        if only_new and rid in prior_verified:
            index[rid] = prior_verified[rid]
            continue
        if only_new and rid in prior_dropped:
            d = prior_dropped[rid]
            dropped.append((rid, d.get("seed_title", title), d["reason"]))
            continue
        found, how = _lookup(title, doi, surname, year)
        if found is None:
            dropped.append((rid, title, how))
            print(f"[DROPPED] {rid}: {how} — the seed dies here, honestly")
            time.sleep(1)
            continue
        acc = ("peer-reviewed venue" if found.get("accredited")
               else found.get("source_type", "?"))
        extract = (
            f"# {found['title']}\n\n"
            f"REGISTRAR-VERIFIED metadata (via {how}, retrieved at build "
            f"time); the seed was only a search key. This work supports "
            f"*context* for library claims — it proves nothing about them.\n\n"
            f"- id: {found['work_id']}\n"
            f"- authors: {', '.join(found['authors'][:6])}"
            f"{' et al.' if len(found['authors']) > 6 else ''}\n"
            f"- year: {found['year']}\n"
            f"- venue: {found.get('venue') or 'n/a'}\n"
            f"- source_type: {found['source_type']} ({acc})\n"
            f"- url: {found['url']}\n"
            f"- curation note: {why}\n\n"
            f"## Abstract (registrar snapshot)\n\n"
            f"{found['abstract'] or '(registrar record carries no abstract)'}\n")
        (out_dir / f"{rid.lower()}.md").write_text(extract, encoding="utf-8")
        index[rid] = {"work_id": found["work_id"], "title": found["title"],
                      "year": found["year"], "url": found["url"],
                      "how": how, "accredited": bool(found.get("accredited")),
                      "extract": f"research/extracts/{rid.lower()}.md",
                      "why": why}
        print(f"[OK] {rid}: {found['work_id']} ({how}, {acc}) — "
              f"{found['title'][:50]}")
        time.sleep(2)
    (out_dir.parent / "references.json").write_text(
        json.dumps({"schema": "references_v2", "verified": index,
                    "dropped": [{"id": r, "seed_title": t, "reason": why}
                                for r, t, why in dropped]},
                   indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[OK] {len(index)} verified, {len(dropped)} dropped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
