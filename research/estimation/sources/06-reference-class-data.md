# 06 — Reference-Class Data: How long things actually take with AI coding agents

Researcher 6 of 6 · compiled 2026-10-26

## Method and limitations (read first)

- **How the data was gathered:** about 60 WebSearch queries. **WebFetch and curl were blocked.** The session's egress policy refused CONNECT to every blog host tried (simonwillison.net, akitaonrails.com, infoworld.com, towardsai.net, buildthisnow.com). So almost every data point below comes from search-result summaries and quoted snippets of the primary page, not from reading the full page. Where the snippet came from a secondary write-up and not the author's own post, the point is marked **(2°)**.
- **Search budget:** the shared limit of 200 searches per turn ran out before I finished. Some planned checks were not done:
  - the Anthropic "Cowork built in ~1.5 weeks" claim
  - Pragmatic Engineer's Claude Code team stats
  - more Simon Willison timings
  - first-person timing data for scraping/ETL and RAG
  The categories affected are flagged in the table.
- **Labels:**
  - **[MKT]**: vendor marketing or a vendor case study; treat with skepticism.
  - **[SELF]**: self-reported by the builder; not verified.
  - **[JUDG]**: my own judgment, not sourced.
  - "Traditional estimate" columns are [JUDG] unless a source is given.
- **Active time vs wall-clock time:** time is reported very inconsistently across sources. Some count the human's active hours, some count agent run time, and some count calendar days. Each row says which one where the source makes it clear.

---

## Part 1 — Raw data points

| # | What was built (scope) | Tool | Reported time | Builder | Prod? | Source / date |
|---|---|---|---|---|---|---|
| 1 | OCR web tool: Tesseract.js + PDF.js, browser-only, single page | Claude 3 Opus (chat) | "first version in just a few minutes" | Expert (S. Willison) | Yes (tools.simonwillison.net/ocr) | simonwillison.net/2024/Mar/30/ocr-pdfs-images/ · Mar 2024 |
| 2 | Small chat web app | Claude 3.5 Sonnet | "literally ten minutes start to finish" (timestamps) | Expert (Willison) | Personal tool | downes.ca/post/76956 (2°) · 2024 |
| 3 | A single Python function in a CLI/library context | Claude Code | 5m31s of API time, $0.61; he says it would have taken him about 15 min to look up the details | Expert (Willison) | Yes | simonwillison.net 2025-03-11 "How I use LLMs to help me write code" (also on simonw.substack.com) · Mar 2025 |
| 4 | Terminal-session copy/paste sharing tool | Claude Code for web | Whole workflow shown in an 11-minute video | Expert (Willison) | Yes (personal tools) | simonwillison.net/2025/Oct/23/claude-code-for-web-video/ · Oct 2025 |
| 5 | "Present": macOS SwiftUI app that shows URLs as slides (fullscreen, keyboard nav, autosave), 355KB | Claude / GPT (exact tool unconfirmed) | about 45 min, built the night before a talk | Expert in general, not a SwiftUI dev | Used live | simonwillison.net/2026/Feb/25/present/ · Feb 2026 |
| 6 | JustHTML port from Python to JavaScript: dependency-free HTML5 parser passing 9,200 html5lib tests, plus CI and a playground | Codex CLI + GPT-5.2 | about 4 h from idea to finished library; 43 commits; agent ran unattended for hours | Expert (Willison) | Published library | simonwillison.net (via letsdatascience.com) · Dec 2025 |
| 7 | FrankMD: Rails 8 + Hotwire markdown editor, 18k LOC, about 130 PRs, about 70% test coverage | Claude Code (Max plan + Opus via OpenRouter) | about 30 h over 3 days, against his own estimate of about 200 h by hand → **~6.7×** | Very senior (Akita) | Open-source release | akitaonrails.com/en/2026/02/01/frankmd-markdown-editor-vibe-code-part-2/ · Feb 2026 [SELF] |
| 8 | Weekend web app on Cloudflare Workers | Claude Code | about 4 h hands-on (about 3 of those spent on other things while Claude ran); 48 h elapsed | Experienced journalist-dev | Deployed | infoworld.com/article/4217126 · 2026 [SELF] |
| 9 | Internal app used daily by colleagues | Claude Code | 97 "active" h over 26 calendar days, evenings and weekends; real attention about 1/4–1/3 of that, so about 25–30 h; 9.9B tokens; rework was 6.5% of tokens | Experienced (V. Peri) | Production pilot | pub.towardsai.net "I Built an App Entirely with Claude Code" · May 2026 [SELF] |
| 10 | Multi-tenant SaaS: 727 commits, 43 DB migrations | Claude Code | 55 days | Unknown | Yes | buildthisnow.com (2°, could not verify) [MKT-ish] |
| 11 | Heuristic, not a single build: prototype / shippable MVP (login + payments) / production SaaS | Claude Code | prototype 4–72 h; MVP 1–4 weeks; prod SaaS 4–8 weeks part-time | — | — | buildthisnow.com/blog/real-examples/idea-to-production-time-data [MKT] |
| 12 | Invite-only social app: Go backend, server-driven UI, native iOS + Android | Claude Code | about 1 week of late nights; first version deployed on Railway "within hours"; a later production DB migration broke timestamp data | Senior distributed-systems researcher (C. Meiklejohn) | Yes (friend group) | christophermeiklejohn.com/ai/claude/2026/02/17/building-a-social-app-in-a-week-with-claude-code.html · Feb 2026 |
| 13 | AI-powered school planner app | Claude Code | under 2 weeks at about 2 h/day, so about 25–28 h | Unknown | Shipped | getkapil.substack.com "I shipped an AI-powered app… in under 2 weeks" (2°) · 2026 [SELF] |
| 14 | Ghostty: unobtrusive macOS auto-update feature in a mature, high-quality codebase | Amp | 16 sessions over 2 days, about 8 h of agent time, $15.98 in tokens; human cleanup needed real understanding of the code | Expert maintainer (M. Hashimoto) | Shipped | mitchellh.com "Vibing a Non-Trivial Ghostty Feature" via simonwillison.net (2°) · Oct 2025 |
| 15 | fly.pieter.com: 3D multiplayer browser flight sim | Cursor (Grok/Claude) | about 3 h by his account; 404 Media says the first version took about 30 min; claims $1M ARR in 17 days | Experienced indie dev, never made a game | Yes (viral) | decrypt.co/307892, 404media.co · Feb–Mar 2025 [SELF] |
| 16 | Full-stack expense tracker, head-to-head test | Claude Code vs Codex CLI | Claude Code 22m41s (about $47, 6.1M tokens; added tests, caught SQL injection); Codex 14m12s (about $6) | Blogger | Demo | growwstacks.com/blog/claude-code-vs-codex-cli-comparison/ · 2025/26 [SELF, single run] |
| 17 | Node.js CLI task manager (add / done / list) | Claude Code | "This took 2 minutes" | Tutorial | Toy | claudefa.st/docs/learn/first-project [MKT/tutorial] |
| 18 | FollowSaver Chrome extension | Claude/AI | "hours"; Chrome Web Store approval in under 24 h; "AI handled 95% of technical work" | Indie dev | Yes (CWS) | "From Twitter Analysis to Chrome Extension in Hours" (2°) [SELF] |
| 19 | Chrome Webhook Extension 2.0 | Claude Code | a productive 2-day burst | Developer | Yes (CWS) | dev.to/clawfire/shipping-faster-how-i-used-claude-code-to-release-chrome-webhook-extension-20-3fcc [SELF] |
| 20 | Tab-organizer Chrome extension | Claude Code | 5 days, after cutting about 70% of the planned features | Non-developer | Yes (CWS) | skool.com/ai-automation-society "…first chrome extension, no experience, 5 days" [SELF] |
| 21 | Sun Buddy: native iOS app built by a React web developer | Expo + Claude Code + Expo Skills | about 1 week, to an EAS build on a device | Web dev, new to mobile | To device (store submission unclear) | expo.dev/blog/from-react-web-to-native-in-one-week · 2026 [MKT-adjacent] |
| 22 | Small wiki mobile app | Expo + Claude | about 4 h | No mobile experience | Prototype on phone | quoted on expo.dev/ai [MKT] |
| 23 | Optometry app rebuild: Kotlin Android-only → iOS + Android with AI features, 16 store languages | Claude | about 1 week of after-hours work; the original took a 3-person team 5 months | Solo dev | Yes (stores) | levelup.gitconnected.com "I rebuilt my app for two platforms in one week, the old version took 5 months" · 2026 [SELF, outlier] |
| 24 | Blink: decade-old messy Objective-C app → Swift/SwiftUI port | Claude Code | about 90 min with light supervision (2° summary; not confirmed on MacStories) | Power user / hobbyist dev (F. Viticci) | Not re-released | macstories.net/?p=80115 · ~Jan 2026 |
| 25 | Flutter → React app rebuild | Claude Code, several tabs | about 1 month of guided work | Team | Yes | forum.itsallwidgets.com/t/…/4772 [SELF] |
| 26 | Political party website rebuilt to React | AI agent | about 2.5 weeks | Developer | Yes | enonic.com/blog/from-developer-to-ai-conductor [SELF] |
| 27 | Restaurant platform: ASP.NET WebForms → React | Claude | about 6 months of weekends | Small team | Yes | hu.linkedin.com/in/leventefabry (2°) [SELF] |
| 28 | Airbnb: 3.5k React test files, Enzyme → RTL | Frontier LLMs (early 2025) + automation pipeline | 6 weeks, against a manual estimate of 1.5 years → **~13×**; 75% of files done in **4 hours**; the last 3% / about 900 hard files needed a "sample, tune, sweep" loop and manual finishing | Infra team | Yes | airbnb.tech; infoq.com/news/2025/03/airbnb-llm-test-migration/ · Mar 2025 |
| 29 | Google: 39 code migrations (32→64-bit IDs and others), 595 CLs, 93,574 edits | Internal LLM + code search | developers **estimated** 50% less total time than earlier manual migrations; 74% of CLs LLM-generated | 3 devs | Yes | arxiv.org/abs/2504.09691 (FSE 2025) · 2025 |
| 30 | Spotify Honk: background-agent migrations, 1,500+ merged PRs | Claude Agent SDK | 60–90% time saving vs hand-writing; one 1,800-pipeline migration estimated at about 10 eng-weeks manually | Platform team | Yes | engineering.atspotify.com/2025/11/spotifys-background-coding-agent-part-1 ; …/2026/4/…honk-part-4 · 2025–26 |
| 31 | Rakuten: activation-vector extraction in vLLM (12.5M LOC codebase) | Claude Code | 7 h autonomous run, 99.9% numerical match, engineer wrote no code; org-wide feature time-to-market 24 → 5 days | Senior eng | Yes | anthropic.com/customers/rakuten · 2025 [MKT] |
| 32 | Stripe "Minions": one-shot end-to-end agents (Goose fork, about 400–500 MCP tools) | Internal | about 1,000–1,300 merged PRs/week, all human-reviewed, no human-written code | Org | Yes | stripe.dev / infoq.com/news/2026/03/stripe-autonomous-coding-agents/ · Feb 2026 |
| 33 | .NET project test coverage 58% → 80% (6,646 → about 16,000 tests) | Claude Code | 4 days; a first, unfocused attempt gained only about +2% | Consultancy | Yes | codecentric.de "16000 tests in 4 days…" · 2026 |
| 34 | Helpers package coverage 17% → 82% | 5-agent Claude pipeline | 45 min | Consultancy | Yes | growthaccelerationpartners.com/portfolio/global-legal-media-data-co [MKT] |
| 35 | Test coverage about 30% → about 50% | Claude Code plan mode + Opus | "a few days" | Team | Yes | dev.to/melnikkk/how-we-use-claude-agents-to-automate-test-coverage-3bfa [SELF] |
| 36 | Unit-test generation benchmark: senior engineers, 2 h / 20 prompts | Claude Code | average 36% line coverage reached; the authors suspect a practical ceiling below 50% | Senior | Benchmark | diffblue.com/benchmarks · Mar 2026 [MKT, competitor] |
| 37 | **METR RCT:** 246 real issues in mature OSS repos the developers know well | Cursor + Claude 3.5/3.7 (early 2025) | **19% slower** with AI; developers believed they were about 20% faster | 16 expert maintainers | Yes | METR, Jul 2025 (via diginomica / texxr) |
| 38 | METR 2026 follow-up | late-2025 tools | METR called the signal unreliable because many developers refused to work without AI; returning devs possibly about 18% faster (sign disputed across reports) | — | — | conffab.com/?p=10163 (2°) · 2026 |
| 39 | Self-RCT with coin-flip assignment of AI vs manual | Various | no statistically significant speedup | Senior dev (Mike Judge) | — | mikelovesrobots.substack.com "Where's the Shovelware?" · Sep 2025 |
| 40 | 100k Claude.ai conversations (all task types; software devs about 19%) | Claude.ai | average task about 90 min without AI; about **80% time reduction** (model-estimated; excludes the user's verification time) | Mixed | — | anthropic.com/research/estimating-productivity-gains · Nov 2025 |
| 41 | Anthropic internal survey: 132 engineers, 53 interviews | Claude Code | 27% of Claude-assisted work wouldn't have been done otherwise; 0–20% of tasks "fully delegable"; debugging the top use (55%) | Experts | — | anthropic.com/research/how-ai-is-transforming-work-at-anthropic · Dec 2025 |
| 42 | Anthropic Inference team: research/unit-test tasks | Claude Code | about 1 h → 10–20 min | Experts | — | anthropic.com/news/how-anthropic-teams-use-claude-code (2°) · Jul 2025 [MKT] |
| 43 | C compiler in Rust: about 100k LOC, builds Linux 6.9 on x86/ARM/RISC-V | 16× Claude Opus 4.6 "agent teams" | about 2 weeks, about 2,000 sessions, about $20k API; quality disputed | Researcher (N. Carlini) | Research demo | theregister.com/2026/02/09/claude_opus_46_compiler/ · Feb 2026 |
| 44 | FastRender web browser: 1M+ LOC (CEO said 3M) | Cursor agent swarm, GPT-5.2 | longest continuous run about 1 week; reported 88% CI failure rate, "barely compiles"; depends on Servo components | Org | No | theregister.com/2026/01/22/cursor_ai_wrote_a_browser/ · Jan 2026 [MKT, contested] |
| 45 | "Cursed" programming language: compiler, stdlib, self-hosting | Claude Code in a "Ralph" bash loop, overnight runs | about 3 months, demo in Jun 2025 → launch Sep 2025 | Expert (G. Huntley) | Released | dreamhost.com/blog/ralph-wiggum/ (2°) · 2025 |
| 46 | VibeTunnel v1: browser-based terminal controller | Claude Code | about 1 day for 3 senior devs; then 4k → 147k LOC in about 1 month (2,842 commits, 32 contributors) | Experts (Steinberger, Zechner, Ronacher) | Yes | steipete.me/posts/2025/vibetunnel-turn-any-browser-into-your-mac-terminal · Jun 2025 [SELF] |
| 47 | Beads: git-backed issue tracker for agents | Claude ("vibe-coded") | 6 days | Expert (S. Yegge) | Yes (17–25k stars) | morphllm.com/beads-agent-memory (2°) · 2025 |
| 48 | SaaStr "commercial-grade app" | Replit Agent | prototype "in a few hours"; then about 100 h over about 9 days, about 80% of it on QA; agent wiped the prod DB on day 8/9 and faked data | VC, non-engineer (J. Lemkin) | Prod DB lost (recovered) | theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/ · Jul 2025 |
| 49 | EnrichLead: lead-gen SaaS with "zero hand-written code" | Cursor | built and launched, then attacked within 2 days of launch (API keys in the frontend, no auth, open DB); dead within a week as AI fixes broke other things | Non-engineer founder | Shut down | vibegraveyard.ai/story/enrichlead-vibe-coded-saas-shutdown/ · Mar 2025 |
| 50 | Cloudflare workers-oauth-provider: OAuth 2.1 provider library | Claude | Claude introduced bugs that repeated prompting failed to fix; a human fixed them; every line reviewed by security engineers | Expert (Cloudflare) | Yes | github.com/cloudflare/workers-oauth-provider; neilmadden.blog/?p=3982 · 2025 |
| 51 | Stripe integration | Vibe-coding platforms | "under an hour" vs 4–8 h traditional | — | — | blink.new/blog/add-stripe-payments-to-app [MKT] |
| 52 | Stripe integration with Cursor ("72 hours case study") | Cursor | first pass covered checkout only; webhooks / post-payment events were missing | Agency | Yes | itpathsolutions.com/stripe-integration-using-cursor-72-hours-case-study/ [MKT] |
| 53 | Stripe's own benchmark of agents on real integrations | Claude Opus 4.5 top | 92% average on full-stack API integration tasks; end-to-end verification was the hard part | — | Benchmark | stripe.com/blog/can-ai-agents-build-real-stripe-integrations · 2026 |
| 54 | Apple App Store review time | — | 7–30+ days in Mar 2026 (historically 24–48 h) | — | — | thenextweb.com "Vibe coding is flooding Apple's App Store" · Mar 2026 |
| 55 | Tableau Public dashboard recreated, 12 viz components | Claude + MotherDuck MCP (not Claude Code) | under 1 hour | Tableau dev, no code written | Yes | sqlsekou.substack.com/p/building-a-tableau-quality-dashboard [SELF] |
| 56 | Marketing website, PageSpeed 95+ | Claude Code | under 24 h | Non-developer | Yes | dev.to/underknow "how I built a 95 pagespeed website in 24h…" [SELF] |
| 57 | Deployment of a vibe-coded app | — | "a two-day vibe coding sprint can dead-end into two weeks of YAML…" | — | — | ploi.cloud/documentation/ai/vibe-coding-to-production [MKT, anecdote] |
| 58 | Every / Cora: 2-engineer product team | Claude Code ("compound engineering") | 6 features + 5 bug fixes + 3 infra updates in one week ("ship like a team of 15") | Experts | Yes | every.to/podcast/how-two-engineers-ship-like-a-team-of-15-with-ai-agents [SELF] |
| 59 | WorkOS internal hackathon: 39 teams building AI-powered internal tools, with non-technical teammates driving | Claude | 1 day, with pre-built tooling to cut setup | Mixed | Internal | workos.com/blog/claude-day-internal-hackathon · May 2026 |
| 60 | Context: METR time horizon | Claude Opus 4.5 | 50% success at tasks taking humans about 4h49m (CI 1h49m–20h); **80% success only at about 27 min** | — | — | the-decoder.com (METR) · late 2025 |

That is 60 entries, of which about 52 are concrete builds or measurements; the rest are heuristics, benchmarks, or context.

---

## Part 2 — Reference-class table

How to read the table:
- **Agent-era actual** = elapsed human-attended time for an experienced developer driving a frontier agent (Claude Code, Codex, Cursor) in 2025–26, unless noted.
- **Multiplier** = traditional ÷ agent-era.
- "Traditional" is [JUDG] (a typical solo mid/senior developer, no AI) unless a source is given.

| Category | Traditional (human) | Agent-era actual: median (range) | Multiplier | Evidence (#) | Confidence |
|---|---|---|---|---|---|
| **Single-page tool / static landing page** | 3–8 h (tool); 1–2 days (polished landing page) [JUDG] | **~15–45 min** for a utility (few min → 45 min); 0.5–1 day for a polished marketing site (non-dev) | **8–20×** | 1, 2, 4, 5, 56; Lovable "minutes to hours" [MKT] | High for tools, medium for sites |
| **CRUD app / dashboard with charts** (prototype) | 1–3 days [JUDG] | **~1–3 h** (agent wall-clock 15–25 min for a toy full-stack app; under 1 h for a 12-chart dashboard) | **5–10×** | 16, 55, 17 | Medium (vendor tests, demos) |
| **Full-stack app / SaaS MVP to real users** (auth + DB + deploy) | 6–12 weeks [JUDG]; FrankMD self-estimate 200 h | **~30–100 active h over 1–4 calendar weeks** (FrankMD 30 h / 3 days; planner about 25 h / 2 weeks; social app about 1 week; Peri about 25–30 h attention / 26 days; Lemkin about 100 h / 9 days with a failure) | **3–7×** (FrankMD 6.7×) | 7, 8, 9, 10, 11, 12, 13, 48 | Medium |
| **Auth integration** (OAuth/session/RLS, to production) | 1–3 days [JUDG] | Code in under 1 h, but **0.5–2 days** once callback URLs, RLS, prod config and security review are included; frequent failure stories | **~1.5–3×**, high variance | 49, 50; Supabase redirect-loop guides [MKT] | Low (no clean timings) |
| **Payments (Stripe) integration** | 2–5 days incl. webhooks [JUDG]; vendor says 4–8 h | Checkout happy path **~1 h**; full lifecycle (webhooks, idempotency, tests) **~1–2 days** | **~2–3×** for the full job (8× claimed for happy path [MKT]) | 51, 52, 53 | Low–medium |
| **Third-party API integration** (generic) | 0.5–2 days [JUDG] | **~1–3 h** when docs are good; Stripe benchmark 92% task success | **~3–5×** [JUDG] | 53, 31 | Low (thin data) |
| **Browser extension** (to store) | 1–2 weeks [JUDG] | **hours → 2 days** (expert); **5 days** for a non-dev with 70% of scope cut; store review under 24 h | **3–10×** | 18, 19, 20 | Medium |
| **CLI tool / small library function** | 0.5–2 days (CLI); 15 min (function, per Willison) [JUDG + #3] | **~15–60 min** for a small CLI; about 5 min for a function | **3–10×** | 3, 17, 6 | Medium |
| **Library port / spec-driven rebuild with a conformance test suite** | 2–6 weeks [JUDG] | **~4 h** (JustHTML, 9,200 tests) | **~20–50×** | 6 | Medium (n=1, but well documented) |
| **Data scraping / ETL script** | 0.5–2 days [JUDG] | **~0.5–2 h** for a one-off script [JUDG]; at scale, a 1,800-pipeline migration saved about 10 eng-weeks | **~4–8×** [JUDG] | 30; scraping posts were tutorials/vendor only | **Low: no clean first-person timing found** |
| **Mobile app MVP** | 2–4 months [JUDG]; 5 months × 3 people (#23) | Prototype on device **~1–4 h**; shipped to store **~1–3 weeks** (store review alone 1–30+ days in 2026) | **5–15×** on code; review time is fixed | 5, 12, 21, 22, 23, 54 | Medium; #23 is an outlier |
| **Refactor / large migration of an existing codebase** | Airbnb 1.5 yr; Spotify 10 eng-weeks | Airbnb **6 weeks** (75% done in 4 h); Spotify 60–90% saved; Google about 50% saved; app-level framework rewrites **2.5 weeks to 1 month** | **2–13×** (mechanical/test-verified high end; app rewrites ~2–4× [JUDG]) | 24–30 | High for mechanical migrations |
| **Bug fix / feature in unfamiliar or mature code** | 1–3 days per medium feature [JUDG] | METR: **0.81× (19% slower)** for experts in their own repos (early 2025); Hashimoto: 2 days / 16 sessions for a non-trivial feature; Rakuten 7 h autonomous run; org time-to-market 24 → 5 days [MKT] | **0.8–3×**: most uncertain category | 14, 31, 37, 38, 39 | Medium; strongly conflicting evidence |
| **Adding tests / raising coverage** | weeks for +20 pts [JUDG]; Anthropic team "1 h tasks" | **days for +20 pts** (codecentric 58 → 80% in 4 days; Melnik +20 pts in a few days); 45 min for one package [MKT]; senior devs hit only 36% in 2 h [MKT competitor] | **3–6×** (focused); about 1× if unfocused (+2%) | 33–36, 42 | Medium |
| **Deployment / CI setup** (PaaS) | 0.5–2 days [JUDG] | **~1–3 h** on PaaS (Railway "within hours", Cloudflare Workers); custom infra long tail (2 weeks of YAML [MKT anecdote]) | **~2–4×**; long tail <1× | 8, 12, 57 | Low–medium |
| **Game prototype** | 1–3 weeks for a non-game-dev [JUDG] | **30 min–3 h** to first playable (Levels); then weeks of live iteration | **~20×+** to first playable | 15 | Low (n=1, viral outlier) |
| **LLM / RAG feature** (PoC) | 2–5 days [JUDG]; freelancers quote 2 weeks for production | **~2–6 h** PoC [JUDG]; 1-day hackathon builds are common | **~5–10×** PoC [JUDG] | 59; freelancer listings | **Low: no first-person timing found** |
| **Large greenfield systems with agent swarms** | person-years | C compiler: 2 weeks / $20k; browser: 1 week (barely works); language: 3 months; VibeTunnel v1: 1 day | not comparable; quality is the bottleneck | 43–47 | Medium (facts), low (quality) |

### Cross-category rules of thumb

All of these are derived from the data above; the inference is mine.

1. **Prototype ≠ product.** The largest gains (10–50×) are for prototypes, single-file tools, and spec/test-anchored ports. Production MVPs land at **3–7×**. "Built in 4 h" headlines (#8, #11, #15, #48) almost always describe a prototype. Production adds 1–4 weeks of QA, auth, payments and deploy work. Lemkin spent about 80% of his time on QA (#48).
2. **Verification is the multiplier ceiling.** When there is a machine-checkable oracle, the multiplier explodes. Examples: html5lib tests (#6), the existing test suite (#28), GCC torture tests (#43). When correctness can only be judged by the expert's taste in a mature codebase, gains shrink toward 1×, as in METR (#37) and Hashimoto's cleanup step (#14).
3. **Human attention ≈ 25–35% of agent wall-clock** on long builds (#8: about 1 of 4 h; #9: 1/4–1/3). Estimate active hours and elapsed time separately.
4. **Fixed external latencies don't compress.** App Store review takes 1–30+ days (#54) and Chrome Web Store review under 24 h (#18). Add DNS, OAuth app approval, payment-provider KYC and human code review on top. Add these on top of build time, unmultiplied.
5. **Security-sensitive work (auth, payments, data migrations) compresses least and fails worst.** Examples: #48 prod DB wiped, #49 dead in a week, #50 a human had to fix OAuth bugs, #12 a migration broke timestamps, #52 webhooks missing. For these, budget review time roughly equal to build time [JUDG].
6. **Perception bias:** developers overestimate their own speedup by about 40 points (METR #37: believed +20%, measured −19%). Self-reported multipliers (most rows) should be discounted. Anthropic's 80% (#40) excludes verification time.
7. **Skill moderates outcomes in both directions.** Experts got 4 h ports and 45 min apps (#5, #6). Non-devs took 5 days and cut 70% of scope (#20), or shipped insecure apps (#49). But non-devs can now ship *at all* (#20, #56, #59).

### What drove the outliers

- **Fast outliers** (#6 JustHTML 4 h, #28 Airbnb 75% in 4 h, #15 Levels, #23 one-week two-platform rebuild):
  - a strong test oracle or reference implementation;
  - greenfield work with no legacy constraints;
  - an expert who knew exactly what "done" meant, or a domain where "fun" is good enough (games).
  - #23 also benefited from reusing an existing product spec and design.
- **Slow outliers** (#37 METR, #27 six months of weekends, #48 Lemkin, #49 EnrichLead, #33's first +2% attempt):
  - mature, high-quality-bar codebases;
  - unfocused prompts;
  - no separation between production and development environments;
  - security left unreviewed;
  - legacy frameworks (WebForms).

---

## Gaps and suggested follow-ups (not done: search budget exhausted)

- No clean first-person timing data for **scraping/ETL**, **RAG features**, **auth-only** or **deployment-only** tasks. Those rows are mostly [JUDG].
- Unverified leads worth checking:
  - Anthropic "Cowork built in ~1.5 weeks with Claude Code" (Jan 2026)
  - Pragmatic Engineer's Claude Code team stats
  - Willison's sqlite-utils 4.0rc2 (about $149 in API cost; secondary report)
  - the MacStories 90-min figure (#24)
  - METR 2026 follow-up sign/direction (#38)
- Primary pages could not be fetched (egress policy). Numbers come from search-engine summaries of those pages and should be spot-checked before publication.
