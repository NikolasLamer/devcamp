# 01 — Classic Software-Estimation Science, and What Transfers to AI-Agent Work

Researcher angle: classic estimation research (psychology of prediction, software-estimation empirics, forecasting methods, accuracy metrics) and how each finding should be adapted when the "developer" is a human + coding-agent pair.

**Verification note.** Sources were found with web search; direct page fetches were blocked in this environment, so most numbers were confirmed via search snippets and abstracts, not full papers. Every number is tagged:
- **[V]** = confirmed via at least one search result or abstract (URL given)
- **[M]** = from my background knowledge, not re-verified here; treat as approximate
- **[Math]** = follows from arithmetic, no source needed

---

## 0. TL;DR for the cookbook

1. **Humans and LLMs both anchor.** A model's "4–5 hours" for a dashboard is an anchor drawn from human-developer training data. Anchoring research shows irrelevant anchors move estimates by large factors: one experiment roughly doubled them, from 20 to 39 hours [V]. The fix is the **outside view**: a reference class built from *your own logged agent sessions*, not the model's intuition.
2. **Durations are right-skewed (lognormal or fatter).** Point estimates track the *median*. Totals are driven by the *mean*, and a few blow-ups dominate the mean. IT projects have the fattest tails in Flyvbjerg's database. In one 1,471-project sample, 1 in 6 was a "black swan" with a +200% cost overrun [V].
3. **Track ln(actual/estimate)**, not MMRE. MMRE/MAPE systematically favor estimates that are too low [V]. The log ratio is symmetric, and its mean corresponds to the geometric mean [V].
4. **Evidence-Based Scheduling (Spolsky) is the right template.** Keep a per-person × per-task-type history of estimate/actual ratios and Monte-Carlo the plan with them [V]. Agent session logs supply exactly this data for free.
5. **Ranges are too narrow.** Nominal 90% intervals in software hit about 64% in one study [V], and as little as 10% for individuals in another [V]. Widen deliberately, then calibrate the hit rate.
6. **Decompose, but by *uncertainty type*, not just by size.** Unpacking lengthens estimates and reduces the planning fallacy [V]. For agent work, the key split is "generation" (compresses heavily) vs. "feedback-loop/discovery" work (env, auth, deploy, integration, debugging), which doesn't compress much and owns the fat tail. This split is a hypothesis; validate it against session data.
7. **Self-perception of AI speed-up is unreliable.** In METR's 2025 RCT, developers predicted a 24% speed-up and still believed afterwards that AI saved them 20%. Measured, they were 19% *slower* [V]. Calibrate only against timestamps, never recollection.

---

## 1. Planning fallacy, Hofstadter's law, optimism bias

**Summary.** Kahneman & Tversky (1979) coined the "planning fallacy": people underestimate completion times for their own tasks even when they know similar past tasks overran [M]. Their method focuses on a "best-case scenario" for *this* task (the inside view) and neglects base rates. Hofstadter's Law (Gödel, Escher, Bach, 1979) is the recursive version: "It always takes longer than you expect, even when you take into account Hofstadter's Law" [V]. Buehler, Griffin & Ross (1994) gave the classic demonstration with honours-thesis students [V]:
- Mean predicted completion was **33.9 days**; actual was **55.5 days**.
- Only about **30%** finished by their predicted date.
- Even their *worst-case* estimate (**48.6 days**) was too optimistic.

People explain away past overruns as one-offs. Asking them to *explicitly connect past experience to the forecast* removed the bias in one study [V].

A complementary account is the memory bias of Roy, Christenfeld & McKenzie (2005). People underestimate future durations partly because they *misremember past durations as shorter*. The bias shrinks when people get feedback on actual previous durations [V].

**Key numbers.**
- Thesis estimates came in at about **61% of actual** (33.9/55.5) [V].
- McConnell, citing van Genuchten (1991), says developer estimates carry an optimism factor of **20–30%** [V, secondary].
- Surveys put the average software effort overrun at **30–40%** (Moløkken & Jørgensen 2003) and about **30%** (Jørgensen 2014). **60–80%** of projects overrun [V].
- In a Norwegian survey of 52 projects, the average overrun was **41%** [V].

**Sources.**
- https://en.wikipedia.org/wiki/Planning_fallacy
- https://bear.warrington.ufl.edu/brenner/mar7588/Papers/buehler-et-al-1994.pdf
- https://en.wikipedia.org/wiki/Hofstadter%27s_law
- https://static.aminer.org/pdf/PDF/000/435/238/a_review_of_surveys_on_software_effort_estimation.pdf
- https://www.simula.no/research/what-we-do-and-dont-know-about-software-development-effort-estimation
- Roy et al.: https://facultysites.etown.edu/roym/files/2014/04/RoyetalQJEP.pdf

**TRANSFER TO AI-AGENT WORK.**
- **The bias is two-sided now.** The classic bias is *under*-estimation. With agents, a model's estimate for *generation-heavy* tasks is a **large over-estimate**: the user's example is "4–5 h" vs. about 45 min. But humans and models remain prone to *under*-estimating the discovery/debugging tail. So "multiply by 1.3" is wrong; the correction depends on the task type.
- **The memory-bias mechanism applies strongly.** Nobody remembers how long agent sessions actually took, and METR shows perceived speed-up is wrong in sign [V]. The remedy from the research, feedback on actual past durations, maps directly onto *reading session logs* (first prompt → last commit/deploy timestamps).
- **Hofstadter's law applies to the agent-native estimate too.** Even a "45-minute" estimate will slip when an env/auth/deploy issue appears. Bake in an explicit tail allowance (see §2).

---

## 2. Reference class forecasting (Flyvbjerg) and fat tails in IT

**Summary.** Reference class forecasting (RCF) operationalizes Kahneman's "outside view" in three steps [V, approximate wording]:
1. Pick a reference class of similar past projects.
2. Establish the distribution of outcomes for that class (e.g., the overrun ratio).
3. Place the new project in that distribution and apply an "uplift" for the desired certainty level.

Kahneman's own curriculum-team story is the canonical example [V, single-expert recollection]:
- The team's inside view was **18–30 months**.
- The base rate from comparable teams was **7–10 years**, and **40% never finished**.
- The project took **8 years**.

The UK Treasury Green Book (2003) mandated optimism-bias uplifts. Flyvbjerg/COWI built them for UK transport, first applied to Edinburgh Tram in 2004 [V].

**IT-specific fat tails.**
- **Flyvbjerg & Budzier, HBR 2011 (1,471 IT projects):** the mean cost overrun was **27%**. But **~1 in 6 (16%)** projects were "black swans" with an average **cost overrun of 200%** and a **schedule overrun of ~70%** [V].
- **Flyvbjerg et al., JMIS 2022 (5,392 IT projects):** cost overruns follow a **power-law** distribution, not normal or even lognormal. Decision makers who assume normality severely underestimate extreme-overrun risk. The proposed mechanism is **interdependencies among technical components**, where one component failure cascades [V]. (The fitted α wasn't visible in the snippets.)
- **How Big Things Get Done** (Flyvbjerg & Gardner 2023, more than 16,000 projects across all sectors) [V]:
  - **48%** of big projects finish on budget.
  - **8.5%** finish on budget *and* on time.
  - **0.5%** finish on budget, on time *and* deliver the expected benefits.
  - IT has "the fattest tails" of all project categories.
  - A secondary summary cites a mean IT overrun of about 73%; I couldn't verify it.

**Sources.**
- https://arxiv.org/abs/1304.0265
- https://arxiv.org/abs/2210.01573
- https://arxiv.org/pdf/1302.3642
- https://corporate.jasoncollins.blog/outside-view
- https://deanebarker.net/library/titles/how-big-things-get-done/

**TRANSFER TO AI-AGENT WORK.** This is the **core method** for the cookbook.
- **Build the reference class from your own session history.** Bucket sessions by task type: CRUD/UI feature, data viz/dashboard, refactor, new third-party integration, auth, deploy/infra, debugging an unknown failure, and so on. Record agent-era actual durations per bucket. The model's training-data prior is the *wrong* reference class (human devs, pre-agent).
- **Explain the tail with interdependency.** Flyvbjerg's cascade mechanism describes the agent-work tail well. A task touching external systems (OAuth provider, cloud IAM, DNS, CI secrets, a payment sandbox) has more interdependencies the agent can't see or control, so it lands in the fat-tail bucket regardless of code size.
- **Use uplift tables.** Example shape: P50 = reference-class median, P80 = P50 × uplift_80. Fill in uplift_80 from your bucket's empirical ln-ratio distribution.
- **Plan for black swans explicitly.** If even ~1/6 of agent tasks blow up 3×, the *expected* total is dominated by them. Flag tasks with external-system dependencies as "black-swan-eligible" and give them a separate timebox and kill/escalate rule.

---

## 3. Distribution of estimate errors: lognormal, right-skewed, mean > median

**Summary.** Erik Bernhardsson (2019) models the "blowup factor" (actual / estimate) as **lognormal**. ln(actual/estimate) ~ Normal(0, σ), so estimates are *calibrated for the median*, but the *mean* exceeds the estimate [V].

His toy example has three equally likely outcomes (0.5×, 1×, 2×). The median is 1 week, but the mean is **7/6 ≈ 1.17 weeks** [V]. When you sum many tasks, the high-σ tasks dominate the total. That's why projects overrun even when the "typical" task is estimated well [V, qualitative; I couldn't access his exact dataset or fitted σ].

His 2022 follow-up ("σ-driven project management") uses the same model to decide when to abandon a project [V].

Independent evidence:
- **Little (2006, IEEE Software).** Landmark Graphics data (100+ commercial projects; secondary sources say 121 projects and 882 estimates). Even seasoned leads' estimates fall significantly below actuals. The ratio distribution is commonly reported as lognormal [V for the dataset; M for the exact fit].
- **Derek Jones on the SiP dataset** (≈10,100 task estimates, 22 developers, 10 years of agile commercial work) [V]:
  - On one cleaned subset, about **30%** of tasks were under-estimated, **37%** exactly right and **33%** over-estimated.
  - The geometric-mean miss factors are **~1.9× for under-estimates and ~0.47× for over-estimates**, i.e. "off by a factor of two" either way.
  - Estimates cluster on round numbers.
- **Flyvbjerg 2022.** IT cost overruns are even fatter-tailed than lognormal (a power law) [V].

**What σ means in practice [Math].** If the median blowup = 1 and ln-ratio ~ N(0, σ):

| σ (log-sd) | mean / median = e^(σ²/2) | P90 / median = e^(1.2816σ) |
|---|---|---|
| 0.5 | 1.13 | 1.9 |
| 0.75 | 1.32 | 2.6 |
| 1.0 | 1.65 | 3.6 |
| 1.25 | 2.18 | 5.0 |
| 1.5 | 3.08 | 6.8 |

Even with an *unbiased* median estimate, a σ = 1 task class costs on average 1.65× the estimate, and a 90%-safe commitment needs 3.6×.

**Sources.**
- https://erikbern.com/2019/04/15/why-software-projects-take-longer-than-you-think-a-statistical-model.html
- https://erikbern.com/2022/04/05/sigma-driven-project-management-when-is-the-optimal-time-to-give-up.html
- https://arxiv.org/pdf/1901.01621 (SiP dataset)
- https://shape-of-code.com/tag/sip/

**TRANSFER TO AI-AGENT WORK.**
- **Expect agent task durations to be bimodal or heavy-tailed.** Hypothesis: there's a fast "happy path" mode where the agent one-shots or needs a couple of iterations, plus a long "stuck" tail (debug loops, environment fights, waiting on human credentials or decisions). That means **σ is probably larger than for human work, even as the median shrinks a lot.** Measure it: compute σ of ln(actual/estimate) per bucket from logs.
- **Always output two numbers:** a **median** ("likely ~45 min") and a **P80/P90** ("plan for 2 h"). Planning totals across several tasks should sum *means*, or Monte-Carlo the full distribution (§5), never sum medians.
- **Use σ per bucket as the key calibration parameter.** Low-σ buckets (UI scaffolding, CRUD, docs) can get tight ranges. High-σ buckets (integration/auth/deploy/debug) need wide ranges and timeboxes. Bernhardsson's "when to give up" logic maps to a rule like: "if a debug task passes ~3× its median with no new information, change approach or escalate to the human."

---

## 4. Three-point / PERT estimation

**Summary.** PERT was developed for the US Navy Polaris program around 1957–58 [V]:
- Estimate optimistic **O**, most-likely **M** and pessimistic **P** durations.
- Expected time **E = (O + 4M + P)/6**, assuming a beta distribution [V].
- Standard deviation ≈ **(P − O)/6** [M, standard textbook].

Known weaknesses [M]:
- People's O and P are anchored on M and too narrow (see the overconfidence section).
- Summing PERT means across a network ignores **merge bias** (parallel paths converging) and task correlation, so PERT systematically understates project duration. Monte Carlo schedule-risk analysis is the usual remedy.

**Key number.** For a right-skewed task (O = 0.5h, M = 1h, P = 4h), E = (0.5 + 4 + 4)/6 = 1.42h [Math]. That's 42% above the most-likely value, which shows how much the tail matters.

**Sources.**
- https://planningplanet.com/blog/conundrum-three-point-estimation-and-pert
- https://blog.codinghorror.com/how-long-would-it-take-if-everything-went-wrong (McConnell-derived: estimate the worst case first)

**TRANSFER TO AI-AGENT WORK.**
- **Use three-point estimates as the elicitation format** for the model and the human. Ask for the P value *first*: "what if the OAuth callback/env/deploy fights back?" Then ask for M, and O last, to counter anchoring on the happy path.
- **Prefer a lognormal fit over the beta-PERT formula.** For skewed agent work, fit a lognormal through M and P, e.g. treat P as the P90. The PERT beta under-weights the tail.
- **Never sum PERT means across dependent steps that share a failure cause** (e.g., three tasks all needing the same broken staging environment). Their blow-ups are correlated, so simulate them together.

---

## 5. Monte Carlo forecasting and Evidence-Based Scheduling (Spolsky / FogBugz)

**Summary.** Joel Spolsky's Evidence-Based Scheduling (Oct 2007, built into FogBugz 6.0) [V]:
1. Each developer estimates each task; when done, log the actual time. **Velocity = estimate / actual.**
2. Keep each developer's history of velocities. Discard velocities older than about **6 months**. Give new estimators a deliberately wide synthetic history [V].
3. Monte Carlo: for each simulated future, divide each remaining task's estimate by a velocity drawn at random from that developer's history. Sum the results.
4. Repeat **100+ times** to get a **probability-of-ship-by-date curve** [V].

The insight is that individual estimators are *consistently* off by their own factor, so their history corrects them. Their *variance* (consistency) matters more than their bias [V, practitioner summary].

Spolsky also says to:
- Track *all* time, including interruptions [V].
- Break tasks down to at most about **16 hours** [M].

**Sources.**
- https://www.joelonsoftware.com/2007/10/26/evidence-based-scheduling/
- https://en.wikipedia.org/wiki/Evidence-based_scheduling
- https://www.infoq.com/news/2007/11/evidence-based-scheduling

**TRANSFER TO AI-AGENT WORK.** This is **the most directly transferable classic method.** Agent sessions produce timestamped logs automatically, so EBS's biggest practical obstacle, manual time-tracking, disappears.
- **Velocity history keyed by (human, task bucket, agent/model version).** Velocity drifts as models improve, so use a short window (weeks, not 6 months) or weight recent sessions more heavily.
- **Estimate in the model's own units, then correct.** Let the LLM estimate in agent-native terms (human-equivalent hours, or better, its own "agent-minutes" guess). Then apply the *empirical* correction ratio. If the model always says "4h" for things that take 45 min, the history learns a velocity of ~5.3 for that bucket, and the bias is removed automatically.
- **Monte-Carlo a multi-task plan.** Sample from the per-bucket ratio history and report P50/P80/P95 completion times.
- **Track all time, as Spolsky insisted.** That includes human review, waiting on CI/deploys, credential hunting and context switching. For agent work, *human attention minutes* and *wall-clock minutes* should be logged separately.

---

## 6. Throughput forecasting and #NoEstimates (Duarte, Magennis)

**Summary.** #NoEstimates (Vasco Duarte, Woody Zuill) argues that if work items are sliced to roughly similar size, **counting completed items per period** (throughput) and Monte-Carlo-sampling that throughput forecasts delivery as well as story points do, at much lower cost [V].
- Duarte reports a close correlation between story points and story counts [V, via Allan Kelly].
- A secondary summary claims that replacing all point values with "1" changed a forecast by only **8%** [V-secondary, treat as anecdotal].
- Troy Magennis (Focused Objective) popularized throughput Monte Carlo and small-sample reasoning.
- Rule of thumb [Math]: with *n* past samples, the probability that the next one falls inside the observed min–max range is **(n−1)/(n+1)**:
  - **5** samples → 67%
  - **11** samples → **83%**
  - **20** samples → about **90%**
  - Kanban guidance commonly uses **8–12 weeks** of throughput history [V].
- Independent research (ESEM 2022, open-source projects) found story points may not be an accurate indicator of effort [V].

**Sources.**
- https://allankelly.net/archives/680/points-conclusions-and-hypothesis
- https://www.hanssamios.com/dokuwiki/_media/forecasting_using_data_-_troy_magennis_agile_2016_.pdf
- https://prokanban.org/forecasting-pocket-guide
- https://conf.researchr.org/details/esem-2022/esem-2022-technical-track/6/On-the-Relationship-Between-Story-Points-and-Development-Effort-in-Agile-Open-Source-

**TRANSFER TO AI-AGENT WORK.**
- **Throughput units suit agent work:** "PRs merged per session-hour", "features shipped per day".
- **Slicing matters even more with agents.** Small, verifiable slices keep the agent on the happy path and make throughput stable. Big ambiguous slices are where the tail lives.
- **The (n−1)/(n+1) rule says how much history is enough:** about **10–20 logged sessions per bucket** before trusting the bucket's range. Below that, fall back to a broader bucket or a wide default.
- **Points are pointless here.** Story points mostly encode human effort, and the agent changes effort per point non-uniformly, so a point no longer means the same thing across task types. Prefer counts within a type bucket plus measured durations.

---

## 7. Wideband Delphi and planning poker

**Summary.**
- **Wideband Delphi** (Boehm 1981, building on RAND's Delphi method and Farquhar's 1970 application to software) [V]: experts estimate anonymously, a coordinator shares a summary, discussion focuses on the *largest disagreements*, and rounds repeat. I found no controlled accuracy studies in this search [V: absence noted].
- **Planning poker**, studied by Moløkken-Østvold, Haugen & Benestad (2007 conference paper, 2008 JSS) [V]:
  - Group consensus estimates were **less optimistic and more accurate** than mechanically combining individual estimates.
  - Individual-expert estimates on control tasks reached *similar* accuracy, so the benefit is not dramatic.
- Jørgensen's broader finding: **combining independent estimates improves accuracy**, and combination methods perform about as well as the best single method [V].
- Within-person inconsistency is large. When **the same expert estimated the same task twice**, the estimates differed by **71% on average** (correlation 0.7) (Grimstad & Jørgensen 2007; small n: 7 professionals, 6 repeated tasks) [V].

**Sources.**
- https://en.wikipedia.org/wiki/Wideband_delphi
- https://www.simula.no/research/using-planning-poker-combining-expert-estimates-software-projects
- https://www.simula.no/research/inconsistency-expert-judgment-based-estimates-software-development-effort
- https://web-backend.simula.no/sites/default/files/publications/Jorgensen.2007.2.pdf

**TRANSFER TO AI-AGENT WORK.**
- **Self-ensemble the model.** LLM estimates are also noisy run to run, the analogue of the 71% inconsistency. Sample **k independent estimates**, e.g. from different decompositions or personas ("pessimistic SRE", "frontend dev who has done this 10×"). Take the **median**, and treat the spread as an uncertainty signal.
- **Apply Delphi's "discuss the outliers" step.** When one decomposition says 30 min and another 4 h, the *reason* is usually a hidden risk (e.g., "needs OAuth app registration"). Surfacing it is the real value.
- **Human + model as a two-person poker.** The human estimates first (blind), then the model. Discuss only when they disagree by more than 2×.

---

## 8. McConnell — Software Estimation: Demystifying the Black Art (2006)

**Summary of the key ideas.**
- **Estimate vs. target vs. commitment** [V]:
  - An *estimate* is a prediction.
  - A *target* is a desired business objective.
  - A *commitment* is a promise to deliver defined functionality at a set quality by a date.
  - Conflating them is a major source of "estimation" failure.
- **Cone of Uncertainty** (originated by Boehm 1981, popularized by McConnell) [V]:

  | Project stage | Range of estimates |
  |---|---|
  | Initial concept | **0.25×–4×** (16× spread) |
  | Approved product definition | ~0.5×–2× |
  | Requirements complete | ~0.67×–1.5× |
  | Design complete | ~0.8×–1.25× [M for the middle steps] |

  This is a *best-case* bound; skill doesn't beat it. The cone narrows **only through decisions that remove variability**, not with time [V]. Bossavit and others note that Boehm's original ranges were judgment-based, not measured [V].
- **Count, Compute, Judge** [V]:
  1. First *count* something that correlates with size (screens, endpoints, tables, tasks).
  2. *Compute* from historical ratios.
  3. Use *judgment* only as a last resort or adjustment.
- **Decomposition** [M]. Summing many independently estimated small pieces lets over- and under-estimates partially cancel (law of large numbers), *provided* errors are not all biased the same way. Decomposition also exposes forgotten work. McConnell cites the 20–30% developer optimism factor (van Genuchten 1991) [V]. He recommends estimating at fine granularity and using ranges.
- **Supporting evidence on decomposition:**
  - Kruger & Evans (2004): **unpacking a task into steps produced longer, more accurate estimates and reduced the planning fallacy**, with bigger effects for complex tasks [V]. A 2021 replication on to-do lists failed to find the effect [V].
  - Jørgensen (2004, top-down vs bottom-up): accurate top-down estimates need **very similar recently completed projects**. Otherwise **bottom-up** estimation was recommended [V].

**Sources.**
- https://www.construx.com/blog/the-cone-of-uncertainty/
- https://www.construx.com/wp-content/uploads/2019/02/CxWhitePaper_ConeOfUncertainty.pdf
- https://resources.rework.com/libraries/project-management/cone-of-uncertainty
- https://wikizibet.nfshost.com/wiki.pl/Software_Estimation
- https://www.oreilly.com/library/view/code-complete-2nd/0735619670/ch28s03.html
- https://www.simula.no/research/top-down-and-bottom-expert-estimation-software-development-effort

**TRANSFER TO AI-AGENT WORK.**
- **Estimate vs. target vs. commitment matters more with agents.** An optimistic agent-native estimate ("45 min") easily becomes a commitment. Present the **median as the estimate and P80 as the commitment**.
- **Narrow the cone by buying information.** With agents, a **10–15 minute spike** (scaffold it, hit the real API once, try the deploy) can collapse much of the initial 16× spread. Recommended pattern: "architect → spike the riskiest unknown → *then* estimate". Prototyping is cheap now; estimating blind is relatively expensive.
- **Count-Compute-Judge with agent-era ratios.** Count screens, endpoints, tables, integrations and deploy targets. Compute with *your* logged minutes-per-unit by bucket. Judge last. The LLM's "4–5 hours" is pure *judge* with a stale prior; replace it with count + compute.
- **Decompose by uncertainty type.** Errors only cancel when they're independent and unbiased. Agent-work errors are *systematically* different by type: generation is over-estimated by a human-prior LLM, and integration/debug is under-estimated. So decompose into typed subtasks and correct each type with its own ratio.
- **Decomposition also exposes forgotten work:** environment setup, secrets, migrations, deploy config, test data, human review. These are exactly the agent-era tail items.

---

## 9. Jørgensen (Simula) — expert judgment, anchoring, request format, overconfidence

**Summary.** Magne Jørgensen and colleagues at Simula have produced the largest body of empirical work on judgment-based software estimation.

**Expert judgment vs. models** [V]:
- Expert judgment is the dominant method in practice.
- In **10 of 16** comparative studies, expert estimates were more accurate than formal models.
- There's "no substantial evidence" that models beat experts.
- Average overruns have stayed around **30%** since the 1980s.
- Jørgensen 2014 lists the lessons with research support [V]:
  - There's no single best method.
  - Clients' focus on low price drives overruns.
  - Min–max intervals are too narrow.
  - It's easy to mislead estimators (anchoring).
  - Relevant historical data and checklists improve accuracy.
  - Combining independent estimates helps.
  - Estimates themselves can be harmful.

**Anchoring and irrelevant information** [V]:
- Jørgensen & Grimstad (IEEE TSE 2011): adding *irrelevant* information to a spec raised the mean estimate from **20 to 39 work-hours** in one experiment. The effect was smaller in field settings.
- Low customer expectations and budget anchors pull estimates down [V qualitatively; M for the specific "customer expectation" experiments].

**Request format and units** [V]:
- **Inverted question.** Asking "**how much can be completed in X hours?**" instead of "how long will Y take?" produced **much lower** effort estimates (more optimism). The authors attribute this to anchoring and **advise against the "how much in X" format** (Jørgensen & Halkjelsvik 2010).
- **Size effect.** People under-estimate large tasks and over-estimate small ones. Inverting the question reverses the pattern ("To read two pages I need 5 minutes, but give me 5 minutes and I will read four", Halkjelsvik, Jørgensen & Teigen).
- **Units.** Estimating in **work-hours gives lower estimates than estimating in workdays** (Jørgensen 2016, JSS).
- **Sequence effects.** Estimating a larger task right after a smaller one *lowered* estimates by **~24%**; the reverse order *raised* them by **~25%**. Competence didn't remove the effect (Jørgensen & Halkjelsvik).

**Overconfidence in intervals** [V]:
- Across 18 projects, only **64%** of nominal **90%** effort prediction intervals contained the actual effort.
- In another study, individual professionals' 90% intervals contained only **10%** of actuals. Team-discussion intervals contained **40%**.
- Teigen & Jørgensen (2005), "When 90% confidence intervals are only 50% certain": people treat their "90%" intervals as roughly 50% certain.
- **Remedy (Jørgensen & Sjøberg 2003).** Derive prediction intervals from the **empirical distribution of your previous estimation accuracy** rather than from gut-feel min/max. This was demonstrated on 145 tasks [V].

**Sources.**
- https://www.simula.no/research/what-we-do-and-dont-know-about-software-development-effort-estimation
- https://acawiki.org/What_we_do_and_don%27t_know_about_software_development_effort_estimation
- https://www.simula.no/research/anchoring-effects-important-cause-too-optimistic-effort-estimates-software-development
- https://www.simula.no/research/effects-request-formats-judgment-based-effort-estimation
- https://www.simula.no/research/unit-effects-software-project-effort-estimation-work-hours-gives-lower-effort-estimates
- https://oda.oslomet.no/handle/10642/7997 (sequence effects)
- https://web-backend.simula.no/sites/default/files/publications/SE.5.Joergensen.2002.a.pdf (64% hit rate)
- https://www.simula.no/research/when-90-confidence-intervals-are-only-50-certain-credibility-credible-intervals
- https://www.simula.no/research/effort-prediction-interval-approach-based-empirical-distribution-previous-estimation
- Halkjelsvik & Jørgensen, *Time Predictions* (open-access book, Springer 2018): https://link.springer.com/book/10.1007/978-3-319-74953-2

**TRANSFER TO AI-AGENT WORK.** This is the most important section for *why LLM estimates are wrong*.
- **The LLM's human-developer prior is an anchor.** Anchors move estimates even when known to be irrelevant (20 → 39 h). Don't let the model produce an hours number first and then "adjust" it, because adjustments from anchors are insufficient. Get the estimate from the reference class / count-compute *first*, and let the model only flag risks.
- **Units effect: estimate in the unit of the reference data.** Asking a model "how many hours?" invites human-scale hour-blocks. Use the unit of your logged data (minutes of agent wall-clock + minutes of human attention), or the model will round into human chunks (½ day, 2 h, 4 h). Jones's SiP data also shows strong round-number clustering [V].
- **Format effect: "what can we ship in the next hour?" is the optimistic format.** It's fine for *scoping a timebox*, but treat its answer as optimistic.
- **Sequence effect: estimate in a deliberate order.** After a run of tiny agent tasks, the next big task will be under-estimated, and the reverse also holds. Estimate high-uncertainty items independently, e.g. in a fresh context or sub-agent, so the previous number in context doesn't act as an anchor.
- **Overconfidence: derive intervals from data, not from the model's stated range.** Use the Jørgensen–Sjøberg method: interval = point estimate × empirical quantiles of past (actual/estimate) for that bucket.
- **The size effect may invert for agents (hypothesis).** "Small" tasks may still be over-estimated by models (a 5-minute fix quoted as an hour), while "large, integration-heavy" tasks are under-estimated.

---

## 10. COCOMO, function points, and why parametric models fail here

**Summary.**
- **COCOMO** (Boehm 1981; COCOMO II 2000) predicts effort as **a × Size^b × Π(effort multipliers)**, with size in KLOC or function points [M].
- **Function points** (Albrecht 1979) size software by counting inputs, outputs, inquiries, files and interfaces [M].
- **Kemerer (CACM 1987)** tested SLIM, COCOMO, Function Points and ESTIMACS on **15** business projects. Function-point models were validated with recalibration. Uncalibrated models produced very large errors [V for the study; the commonly cited "COCOMO MRE ~600%" figure is **unverified**, M].
- Boehm reported that locally calibrated COCOMO II reaches roughly "within 30% of actuals 70–75% of the time" [M].
- Jørgensen's reviews find **no consistent evidence that formal models beat expert judgment** [V].

**Sources.**
- https://en.wikipedia.org/wiki/COCOMO
- https://cacm.acm.org/research/an-empirical-validation-of-software-cost-estimation-models
- https://web-backend.simula.no/sites/default/files/publications/Jorgensen.2007.2.pdf

**TRANSFER TO AI-AGENT WORK.** Parametric models **don't transfer**:
1. **Size (LOC/FP) is no longer the cost driver.** The agent emits LOC almost for free. Cost now tracks *verification and feedback loops*: running, testing, deploying, human review, and external-system friction.
2. **The calibration constants (a, b, multipliers) encode human productivity.** The agent era changes them non-uniformly by task type and model version.
3. **The superlinear size exponent (b > 1, from communication overhead) may not hold.** It could be replaced by context-window and coherence limits, which is untested.

What does transfer is the *idea* of local calibration: a model is only as good as its fit to *your* recent data. A light "parametric" model, minutes ≈ Σ (count_i × median-minutes-per-unit_i) per bucket, fit on session logs, is fine.

---

## 11. Calibration training (Douglas Hubbard, *How to Measure Anything*)

**Summary.** Hubbard teaches estimators to produce **calibrated 90% confidence intervals** with these techniques:
- **Trivia-question drills with scoring feedback.** In an illustrative first round, only about 12 of 20 (60%) intervals contained the answer [V].
- **The equivalent bet test.** Would you rather win $X if the true value is in your range, or spin a wheel with a 90% chance to win? If you prefer the wheel, your range is too narrow, so widen it until you're indifferent [V].
- **Treat each bound separately** ("am I 95% sure it's above the lower bound?").
- **Assume you're wrong and ask why** (pre-mortem-style).

Hubbard claims that most people become nearly calibrated after about half a day of training. That figure is widely repeated but I **couldn't verify it against published data** [V that the claim exists; unverified effect size]. The general overconfidence literature finds nominal 90% intervals capture the truth only **30–60%** of the time [V].

**Sources.**
- https://www.lesswrong.com/posts/5XBv2onWGRKFtAEMN/link-how-to-calibrate-your-confidence-intervals
- https://www.theuncertaintyproject.org/tools/estimator-calibration
- https://pages.ucsd.edu/~cmckenzie/McKenzieetal2008OBHDP.pdf
- https://forum.effectivealtruism.org/posts/qFkEhW7Hn2mkJvjNv/does-calibrated-probability-assessment-training-work

**TRANSFER TO AI-AGENT WORK.**
- **Calibrate the model the same way.** Feed it its own track record ("your last 20 P80 estimates contained the actual 55% of the time; widen accordingly").
- **Adopt calibration as an explicit metric:** the percentage of tasks finishing ≤ P50 (target ~50%) and ≤ P80 (target ~80%). A P80 hit rate below 70% means widen; above 90% means tighten.
- **Use the equivalent bet test as a prompt step:** "Would you bet at 9:1 odds that this finishes within 2 h? If not, widen."
- **Run a pre-mortem per task:** "It's 3× over. Most likely why?" This surfaces env/auth/deploy risks.

---

## 12. Accuracy metrics: MRE, MMRE, MdMRE, PRED(25), log ratio

**Definitions** [M, standard]:
- **MRE** = |actual − estimate| / actual.
- **MMRE** = the mean of MRE; **MdMRE** = the median of MRE.
- **PRED(25)** = the share of estimates within 25% of actual. The traditional "acceptable" bar is MMRE ≤ 25% and PRED(25) ≥ 75% (Conte, Dunsmore & Shen 1986) [M].

**Problems** [V and M]:
- **MRE is asymmetric** [Math]. An under-estimate's MRE is bounded at 1 (estimate = 0 gives MRE = 1). An over-estimate's MRE is unbounded (estimate = 3× actual gives MRE = 2). So **MMRE and MAPE reward models that under-estimate**:
  - Tofallis (JORS 2015) shows MAPE "systematically selects" methods whose predictions are too low [V].
  - Foss, Stensrud, Kitchenham & Myrtveit (IEEE TSE 2003) showed by simulation that **MMRE does not select the best model**, and strongly recommend not using it [V].
- Kitchenham et al. (2001) showed MMRE is really a measure of the spread of z = estimate/actual, not of accuracy [M].
- Jørgensen has also published "A Critique of How We Measure and Interpret the Accuracy of Software Development Effort Estimation" [V title].

**Recommended metric.** Use the **log accuracy ratio, ln(actual/estimate)** [V, Tofallis]. Its properties:
- **It's symmetric.** 2× over (+0.69) and 2× under (−0.69) are equal in magnitude.
- **It fits multiplicative, heteroscedastic error**, which is the lognormal picture.
- **Least squares on it predicts the geometric mean.**
- **Two summary statistics:**
  - *Bias* = mean(ln ratio). exp(bias) is the geometric-mean blowup factor.
  - *Spread* = sd(ln ratio) = σ, which directly sets the interval widths from §3.
- **Report alongside it:** median ratio, P80/P90 of the ratio, and the interval hit rate (calibration).

**Sources.**
- https://arxiv.org/abs/2105.05249 (Tofallis)
- https://en.wikipedia.org/wiki/Mean_absolute_percentage_error
- https://biopen.bi.no/bi-xmlui/handle/11250/94042 (Foss et al.)
- https://www.simula.no/research/critique-how-we-measure-and-interpret-accuracy-software-development-effort-estimation

**TRANSFER TO AI-AGENT WORK.** Directly applicable, and it matters *more* here.
- **Agent errors span orders of magnitude** (a model says 5 h, actual is 40 min: ratio 0.13, ln = −2.0). MRE-style metrics behave terribly at these ratios. Log ratio handles them naturally.
- **Calibration dashboard per bucket:** n, median ratio, exp(mean ln), σ, P80 hit rate, and trend over model versions.
- **Measure "estimate" at a fixed point in time** (e.g., after architecture/plan, before the first code). Otherwise the cone-of-uncertainty stage contaminates the comparison.

---

## 13. Bonus: direct evidence on AI-assisted work estimation (cross-link for other researchers)

**METR RCT (July 2025)** [V]:
- **Design:** 16 experienced open-source developers did 246 tasks in their *own* mature repos, with tasks randomly assigned to allow or forbid AI. The main tools were Cursor Pro with Claude 3.5/3.7 Sonnet.
- **Forecast vs. result:** developers forecast **a 24% time reduction**. Measured, they were **19% slower** with AI.
- **Perception afterwards:** they still believed AI had reduced their time by **20%**.
- **Caveats:**
  - The setting is an early-2025 snapshot of large, familiar codebases.
  - 56% had never used Cursor before.
  - The sample is small.

Source: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/

**TRANSFER.** This is the strongest evidence that **self-reported AI speed-ups are unreliable**, and the speed-up's *sign* depends on context. Greenfield/small-scope work like a dashboard may compress dramatically. Expert work in large, familiar, high-standard codebases may not compress at all. The estimation method must therefore be calibrated per context from logged timestamps, never from the human's or model's impression.

---

## 14. Synthesized method (classic science → agent-era recipe)

1. **Classify** the task into buckets. Also tag it for *external-system interdependencies* (auth, cloud, DNS, payments, CI secrets, third-party APIs), which marks it black-swan-eligible.
2. **Architect and decompose** into typed subtasks (generation / integration / env-deploy / debug-unknown / human-decision-review). Unpacking reduces optimism, and typed decomposition lets each type get its own correction.
3. **Spike the riskiest unknown** (10–15 min) if it's in the tail bucket. This is the cheapest way to move down the cone of uncertainty.
4. **Count → compute → judge:**
   - Count units per subtask.
   - Compute with per-bucket median minutes from session history (the reference class).
   - Let the model or human *judge* only the adjustments and the risks.
   - Don't take an LLM hours-number first (anchoring), and estimate risky items in fresh context (sequence effects).
5. **Produce three numbers:** a P50 and a P80, plus separately the human-attention minutes. Derive P80 from the bucket's empirical ln-ratio quantiles (Jørgensen–Sjøberg), not the model's gut range. For multi-task plans, Monte-Carlo the plan with sampled ratios (EBS).
6. **Present the P50 as the estimate and the P80 as the commitment.** Add a timebox and escalate rule for black-swan-eligible subtasks, e.g. at 3× the median with no progress.
7. **Log and calibrate:** estimate time, actual wall-clock, human minutes, bucket, model version. Track ln(actual/estimate) bias and σ, plus P50/P80 hit rates. Refresh the reference class on a short window as models change.

**Gaps and uncertainties to flag.**
- I couldn't access Bernhardsson's exact dataset and σ, or Little's exact distribution parameters.
- Hubbard's training-effect size, Kemerer's exact MRE figures and the PERT SD formula provenance are from memory.
- The claims that agent-era distributions are *bimodal* and that *σ rises while the median falls* are **hypotheses** to test on session logs, not established findings.
