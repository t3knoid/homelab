---
title: "Building ROSIE: Learning LLMs on a Budget in a 1U Homelab Server"
---

# Building ROSIE: Learning LLMs on a Budget in a 1U Homelab Server

Nov 10, 2026

I'll be honest. Until this year, I had never built anything with a large language model. I figured the best way to learn how one works was to build one I could actually use: a local assistant that reads my homelab's own documentation and runbooks and helps me troubleshoot. On a budget, of course.

I named her ROSIE. Officially, that stands for Root-cause Observation, SRE Incident Examiner. If you grew up with a certain Space Age cartoon family and their robot maid, you may have another theory. I couldn't possibly comment. Her motto: "Observe. Simulate. Examine. Resolve."

This is not meant to be a tutorial. I'm no LLM expert, and plenty of what follows I learned the hard way. It's the story of going from zero to a working local assistant on a homelab budget: the hardware, keeping a passively cooled GPU from cooking itself in a 1U server, the DevOps work to run it all, and the problems I ran into along the way.

One confession up front: I vibe coded most of ROSIE's code. I described what I wanted to an AI coding assistant and reviewed what came back. That freed me up for the part I really wanted to learn... putting the whole thing together, from the hardware up.

If you want to skip ahead, you can talk to ROSIE yourself at [rosie.refol.us](https://rosie.refol.us), and all of her code is on GitHub at [t3knoid/ROSIE](https://github.com/t3knoid/ROSIE).

## Why build it at all

My homelab has grown to the point where I can't keep it all in my head. I have a documentation site and a few dozen runbooks for Pi-hole, certificates, Proxmox, TrueNAS, monitoring and media services. When something breaks, I end up searching the docs, opening three runbooks and piecing the answer together. Not fun when something's down.

I wanted to ask a question in plain English and get an answer from *my* docs, with links to the pages it used. I gave her three rules:

- **Local only.** My infrastructure notes don't leave the house.
- **Advisory only.** ROSIE reads documentation. She doesn't log into servers or touch anything. I stay in the loop.
- **Honest.** If my docs don't cover it, she says so instead of making something up.

The practical goal was a troubleshooting helper. The real goal was to understand what's going on under the hood, by running every piece of it myself.

## The budget build

You don't need a gaming rig or a cloud bill to run a language model at home. The whole build came to $402.01: a used Supermicro 1U server, a used datacenter GPU, two sticks of RAM and a pair of small fans. Here's the shopping list:

| Part | What it is | Price |
| --- | --- | --- |
| Supermicro 1U CS-512 | X10SLL-F board, Xeon E3-1241 v3, 16 GB RAM | $240.03 |
| Nvidia Tesla P4 | 8 GB VRAM, Pascal, low profile, passively cooled | $118.80 |
| 2 × Micron 8 GB DDR3L-1600 ECC UDIMM | PC3L-12800, takes the server from 16 GB to 32 GB | $31.19 |
| GDSTIME 40 × 10 mm blower fan (pack of 2) | 12 V, 2-pin, brushless DC; cools the P4 | $11.99 |
| **Total** |  | **$402.01** |

That's more like it.

**Why a Tesla P4?** It's the cheapest way I found to get 8 GB of VRAM into a 1U box. It's a single-slot, low-profile datacenter card that gets all its power from the PCIe slot. No extra power cables needed. It dropped right into the riser.

The catch? It has no fan. (Always read the spec sheet, folks.) It's built for servers that blow a hurricane of air across it. Let me tell you, that turned into the biggest hardware headache of the whole project.

**Why 8 GB matters.** VRAM decides which models you can run. A model's weights have to fit on the card, plus some working memory for the conversation. With 8 GB, you're looking at small models, *quantized* (squeezed down) to about 4 bits per weight. I'll get to what that means in practice.

**Why old hardware is fine.** ROSIE answers one person at a time... me. Waiting several seconds for an answer is fine for a homelab helper. I wasn't trying to build a fast chatbot. I wanted one that works and that I understand.

## Keeping a Tesla P4 cool in a 1U

I ended up fixing this two ways: a small blower fan taped to the end of the card, and a service that makes the server's fans follow the GPU's temperature. But first, the problem.

### The problem

One day, my server logged an error I had never seen before: NVIDIA **Xid 79**, "GPU has fallen off the bus." Yup, the card had dropped right off the PCIe bus. Only a reboot brought it back. I had seen the card hit 81 °C before that. I can't prove heat alone did it, but a passive card running hot in a 1U server is suspect number one.

Here's what was going on. The P4 has a heatsink and no fan. It counts on the chassis fans to push air through it. Those fans are run by the Supermicro BMC, the little management computer inside the server. The BMC sets the fan speed from the sensors it knows about: CPU, system and memory temperatures.

Here's the rub. **The BMC can't see the GPU at all.** So when the GPU was working hard and the CPU was taking it easy, the BMC kept the fans nice and quiet while the card slowly cooked.

### Fix one: give the card its own fan

If the P4 wasn't getting enough air, I'd bring some to it. I took a GDSTIME 40 × 10 mm blower fan (12 V, 2-pin, brushless DC) and attached it to the end of the card, right where the cooling fins are. I wrapped the joint with Reflectix tape, so the blower pushes its air through the fins instead of around them.

&#91;image: The Tesla P4 in the Supermicro 1U, with a 40 mm blower fan taped to the end of the card\]

*The P4 in the riser, with the 40 mm blower taped over the end of its heatsink with Reflectix tape.*

It isn't pretty... but it works. It cost me $6 and it doesn't need any software. It's a 2-pin fan, so there's no speed control. It just runs whenever the server is on.

### Fix two: make the chassis fans follow the GPU

So the BMC couldn't see the GPU. Fine. I'd watch it myself.

Supermicro X9/X10 boards accept a raw IPMI command that switches the BMC's fan *mode*: Standard, Full, Optimal or Heavy IO. I couldn't make the BMC read the GPU, but I could read it myself and tell the BMC which mode to use. I mean, it's just a thermometer and a switch, right? That became `p4-thermal`, a little Python script that runs as a systemd service on the host:

- Every 5 seconds, read the GPU with [`nvidia-smi`](https://docs.nvidia.com/deploy/nvidia-smi/index.html): temperature, clocks, power, VRAM and throttle reasons.
- At 70 °C or above, switch the fans to **Full** right away. (I started at 84 °C and lowered it after a stress test. More on that below.)
- Stay on Full until the GPU has been at 55 °C or below for 2 minutes straight, then go back to **Optimal**.
- Re-send the current mode every 60 seconds, in case the BMC changes it on its own.

The gap between 70 °C and 55 °C is deliberate. Without it, the fans would flap between Full and Optimal every time the temperature crossed one line.

&#91;embedded content: p4-thermal · the control loop and the two fan modes\]

The top row is the loop the BMC couldn't close on its own. The bottom row is the decision the controller makes on every reading.

### Plan for failure

A fan controller that crashes and leaves the fans quiet is worse than not having one at all. So every failure ends at Full:

- If the GPU can't be read three times in a row, the fans go to Full.
- If the service stops for any reason, even a crash or `kill -9`, the systemd unit's `ExecStopPost` sets the fans to Full.
- The unit starts before Docker at boot, so the fans are managed before the models load.
- A `--dry-run --once` mode reads every sensor and reports what it *would* do, without touching the fans. I used it before I let the script anywhere near real hardware.

The script also writes its readings to a small JSON file. ROSIE mounts it read-only and shows a hardware footer on the chat page, in two parts. System lists what doesn't change: the CPU, total memory, the GPU model and its VRAM. Live shows the readings, refreshed every 10 seconds: temperature, clock, power, VRAM in use and fan state. If the GPU is throttling, I see it right where I'm waiting for an answer.

### How well does it work?

With both fixes in place, the P4 has held steady at 56 °C during normal use. That's well under the 70 °C mark where the controller switches the fans to Full.

The first real test came after I moved to the bigger 8B chat model. With the GPU at 99% use, drawing 63 W of its 75 W limit while answering one question, `nvidia-smi` showed 64 °C. Not bad.

The harder test was asking ten questions back to back, to grade ROSIE's answers (more on that later). That kept the GPU at 99% for about three minutes, and the card climbed all the way to 87 °C. The controller switched the fans to Full at 84 °C, but the temperature kept rising. So I lowered the trigger to 70 °C and ran the test again. It still hit 87 °C (though it never throttled).

With the fans at Full and the blower running, a long full load is just more heat than this 1U can move. One question at a time, with some idle time in between, never gets close. For long test runs, I'll space out the questions or cap the GPU's clock.

One lesson I keep in my docs: fan control can't fix a PCIe, power, driver or hardware fault. If Xid errors come back, the logs and the physical cooling are the next places to look.

## Getting a model to run at all

When I started, I didn't even know what an embedding was. The local LLM part turned out to be two small models served by llama.cpp in Docker, plus a database for searching my docs. Not as scary as it sounds. Here are the pieces, explained the way I wish someone had explained them to me.

### What is a model, anyway?

- **Weights and GGUF.** A model is a big file of numbers. Those numbers are called *weights*, and they're what the model learned in training. GGUF is the file format llama.cpp uses for them. Everything needed to load a model is packed into one file. Very convenient.
- **Quantization.** Weights are normally stored at 16 bits each. Q4\_K\_M stores them at about 4 bits, so the model is roughly a quarter of the size, with a little loss in quality. This is what makes an 8 GB card usable at all.
- **Two different models.** You need both. A *chat model* writes the answers. An *embedding model* turns a piece of text into a list of numbers (a *vector*) that captures its meaning. Similar text gets similar vectors.
- **Context window.** How much text the model can "see" at once, counted in *tokens* (pieces of words). The instructions, the evidence and the answer all have to fit inside it. A bigger window eats more VRAM.
- **Vector database.** Qdrant stores each passage of my docs right next to its vector. When I ask a question, the question becomes a vector too, and Qdrant hands back the passages whose vectors are closest.

### What I ended up running

| Piece | What I use | Size or setting |
| --- | --- | --- |
| Chat model | Llama 3.1 8B Instruct, Q4\_K\_M GGUF | about 4.9 GB |
| Embedding model | nomic-embed-text v1.5, Q4\_K\_M GGUF | about 84 MB |
| Model server | llama.cpp `server-cuda` image, one container per model | 1 request at a time, all layers on the GPU |
| Context window | Chat model | 10,240 tokens |
| Search | Qdrant 1.12 | runs on the CPU |
| App | Python, FastAPI, LangGraph | runs on the CPU |

Everything runs under Docker Compose. Only ROSIE's web port is exposed. The model servers are reachable only on the private Compose network.

### Squeezing the biggest model onto the card

I started ROSIE on Llama 3.2 3B. It used less than half of my GPU. So naturally, I wanted to know: what's the biggest model that fits next to the embedding model?

I didn't trust spec sheets. I went by what `nvidia-smi` actually reported. Here's my card sitting idle with both models loaded:

{% raw %}
```text
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.178.04             Driver Version: 580.178.04     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|=========================================+========================+======================|
|   0  Tesla P4                       Off |   00000000:01:00.0 Off |                    0 |
| N/A   56C    P0             23W /   75W |    6207MiB /   7680MiB |      0%      Default |
+-----------------------------------------+------------------------+----------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|=========================================================================================|
|    0   N/A  N/A            1729      C   /app/llama-server                       258MiB |
|    0   N/A  N/A           49272      C   /app/llama-server                      5946MiB |
+-----------------------------------------------------------------------------------------+
```
{% endraw %}

The two `llama-server` processes at the bottom are the embedding server (258 MiB) and the 8B chat server (5,946 MiB). The numbers that matter:

| Part | VRAM |
| --- | --- |
| Tesla P4 total | 7,680 MiB |
| Embedding server | 258 MiB |
| Llama 3.2 3B chat server, measured | about 3,250 MiB |
| Llama 3.1 8B chat server, measured | 5,946 MiB |
| **In use with the 8B and embedding servers** | **6,207 MiB** |

The 8B fits with about 1.4 GB to spare. Nothing bigger fits at 4 bits with this context size. A 12B model's weights alone are about 7 GB. So 8B it is.

There's a catch, of course... speed. The P4 now does more than twice the work per answer. In my ten-question test (more on that later), the 3B answered in 8.8 seconds on average and the 8B took 18.8 seconds. Their scores were almost the same, 2.6 and 2.7 out of 5, but the 3B made up facts, like listing errors I had never reported as "verified facts." I'll take slower and honest. The big gains came later anyway, from changing what the model is shown.

### What getting the GPU into Docker taught me

- **The driver isn't enough.** The host needs the NVIDIA driver *and* the NVIDIA Container Toolkit before a container can see the GPU. `docker run --gpus all nvidia/cuda:… nvidia-smi` became my go-to test whenever something looked off.
- **Old GPUs need the right CUDA.** The P4 is a Pascal card (compute capability 6.1), and CUDA 13 dropped Pascal. The CUDA 13 image is a dead end on this card, so I pin llama.cpp's CUDA 12 `server-cuda` image. The newest image isn't always the right one.
- **`nvidia-smi` can mislead.** The "CUDA Version" it prints is the newest CUDA the driver supports, not something you need installed. Mine says 13.0 in the output above, on a card that CUDA 13 doesn't support. The CUDA runtime ships inside the container anyway.
- **Two models share one card.** Both servers sit on the same 8 GB. The weights fit easily, but the context cache and the CUDA runtime need room too. Limiting each server to one request at a time keeps memory use predictable.

## Teaching a model about my homelab without training it

I figured I'd have to train a model on my documentation. Turns out, I didn't.

ROSIE uses something called *retrieval-augmented generation*, or RAG for short. For every question, she looks up the most relevant passages in my docs and hands them to the model along with the question. The model never actually learns my homelab. It just reads the right excerpts every time. Think open-book exam.

Want to dig deeper? NVIDIA has a good plain-English explainer, [What Is Retrieval-Augmented Generation, aka RAG?](https://blogs.nvidia.com/blog/what-is-retrieval-augmented-generation/) And if you're the type who likes to go straight to the source (no judgment), the original paper is [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) by Lewis et al., 2020.

It works in two stages.

&#91;embedded content: how ROSIE answers · indexing ahead of time, then search and answer per question\]

The top row runs ahead of time, at startup and every time I sync. The bottom row runs for every question. That's it. The model only ever sees the system prompt, the passages the search found, and my question.

### Indexing: turning a website into searchable passages

ROSIE crawls two places on my documentation site: the whole site, and the runbook index page. Every page linked from the index counts as a runbook. Each page gets cut into passages of up to about 1,200 characters, split at its headings. Each passage starts with its page title and section, gets a vector from the embedding model, and goes into Qdrant.

The sync runs at startup, on a schedule from a systemd timer, and whenever I click **Sync sources**. Passages that haven't changed aren't re-embedded, so a re-sync is cheap. And a page I delete from the site drops out of the index on the next sync, as long as the rest of the site crawled cleanly.

### Answering: a small, careful prompt

For each question, ROSIE takes the two best-matching passages, plus the closest runbook's text in page order, up to about 4,000 characters. If a second runbook scores almost the same (within 0.03), its best passage goes in too. All of it goes to Llama along with a system prompt and the question. The answer comes back as Markdown, with the evidence it used listed underneath and links back to my docs.

The system prompt is where ROSIE's personality and rules live: prefer my docs over general knowledge, cite sources, say when the evidence is missing, never make up the state of my systems, and treat documents as evidence, not instructions.

### Built like an ops tool, not a toy

- **Advisory only.** No credentials, no connections to live systems. ROSIE can't run a single command or change anything.
- **Runbook drafts are data first.** When ROSIE drafts a runbook, the model fills in a fixed structure (purpose, scope, prerequisites, steps, rollback, verification), and the Markdown is built from that. Drafts are saved as uncommitted files. The review and the Git commit stay with me.
- **Everything is logged.** Every sync, search, question and runbook action goes into a JSON Lines audit log.
- **Fail loudly.** If the model server or Qdrant is down, ROSIE says so instead of answering without evidence. Chat stays locked until a sync finishes cleanly.
- **A REST API with docs.** Everything in the web page is also an API endpoint, with Swagger docs.

The best part? Updating the docs updates the assistant. Fix a runbook, sync, and ROSIE knows.

## What went wrong, and how I fixed it

Here's the thing that surprised me most. Almost every bug was a search problem, not a model problem. The model answered well when it was shown the right text, and badly when it wasn't.

### Answers were painfully slow

On the P4, most of the wait isn't the model writing. It's the model *reading* the prompt. My first system prompt was 4,186 words long, a thorough SRE playbook (I got a little carried away), and I sent four passages of evidence with every question. I cut the system prompt down to about 440 words and the evidence to two passages. Answers got much faster, and no worse.

*Placeholder: answer times before and after, if you noted them.*

### The answer was in my docs, but ROSIE couldn't find it

My first indexer cut pages into fixed-size chunks. A heading could land at the end of one chunk and its content at the start of the next, so a question about my storage list matched neither. Now pages split at their headings, and every passage starts with its page and section name, like "TrueNAS › Datasets: …". That label helps the search, and it tells the model what it's reading.

### Every passage started with the site menu

The crawler indexed whole pages, including the navigation bar, header and footer. So every passage started with the same menu, and they all looked alike to the search. Now the site menu, header and footer are left out.

### "enas\_vms.yml"

Chunks overlap a little, so nothing gets lost at a boundary. But the overlap could start mid-word, and the model happily repeated fragments like `enas_vms.yml` for `deploy_truenas_vms.yml`. Passages now start at a word boundary.

### "That page doesn't mention it"

The model would say a page didn't cover something because its *excerpt* didn't. The system prompt now explains that evidence passages are excerpts, and that the full page may say more.

### Is there a list of runbooks?

I asked ROSIE if my homelab had a list of runbooks. She said no. The list was sitting right there on my docs site. Ouch.

Fixing that took five rounds. Let me tell you, it taught me more about how these things really work than anything else in the project.

- **Round 1: "Is there a list of runbooks?" → "No."** The runbook index page was indexed, but each of its passages was one category's table. None of them actually said "this page is the list of runbooks." The fix: add a summary passage that says exactly that, with the runbook count and categories.
- **Round 2: "Summarize all the runbooks" → one runbook.** ROSIE named the categories and... a single runbook: Request Web Certificates, because its description mentions "all … in the homelab." The model only sees about three passages, and the runbook names were spread across seven category passages. The fix: the summary passage now names all 63 runbooks, grouped by category, in about 2,700 characters.
- **Round 3: the list stopped after 15 runbooks, mid-sentence.** The answer hit the 512-token output limit. And since the model only had titles, it padded every line with guesses like "likely part of the Runbook Ansible Template." The fix: raise the limit to 1,536 tokens, add a rule against guessing about items the evidence only names, and add a note to any answer that gets cut off.
- **Round 4: all 63 names, but the guesses were still there.** The 3B model listed everything, then went right back to padding the first category with "likely part of…" notes. The fix: a short, explicit rule of its own ("a plain list of the names exactly as written"), and a switch to Llama 3.1 8B. The next answer was a clean list of all 63 names. Finally!
- **Round 5: a stray last line, "The best-matching indexed runbook is…"** That one was on me. My own code told the model "Name this runbook when you refer to it" on every question, and the 8B, being better at following instructions, did exactly that. The fix: hand it over as information instead: "If it helps answer the question, name it; otherwise ignore it."

The lesson: the model can only use what the search puts in front of it. When an answer is wrong, the first thing to ask is, *what did it actually see?* ROSIE lists her evidence under every answer, and that list solved most of my bugs.

### Putting ROSIE through ten real incidents

One-off questions only showed me one bug at a time. So I put her to the test. I wrote ten incident questions based on my own runbooks: an NFS mount gone missing, a 502 from the reverse proxy, a full disk, an expired TLS certificate, an expired Entra ID client secret, a failed Ceph OSD disk, a failed TrueNAS Ansible run, Pi-hole showing IPs instead of hostnames, updating Proxmox safely, and Plex buffering. With my AI coding assistant's help, I timed each answer and graded it from 1 to 5 against the runbook it should have used.

| Run | Average score (out of 5) | Average answer time |
| --- | --- | --- |
| Llama 3.2 3B | 2.6 | 8.8 s |
| Llama 3.1 8B | 2.7 | 18.8 s |
| 8B, prompt fixes | 2.9 | 18.7 s |
| 8B, whole runbook | 4.1 | 23.8 s |

What the test turned up:

- **False gaps.** The 8B said "Runbook Gap Identified" in 6 of 10 answers... while citing the right runbook. The fix: the gap labels are now only allowed when the search finds nothing.
- **My own config, stated as fact.** Every prompt said "No live infrastructure connectors are configured," and the model repeated it as if it had checked my systems. The fix: say instead that ROSIE can't see my systems, so their state is unknown unless I describe it.
- **Answers that stopped at step 1.** The search often matched a runbook's notes or its verification section instead of its steps, so the model said the steps were missing. The fix: hand the model the closest runbook whole, in page order. This was the big one. The score jumped from 2.9 to 4.1, for about 5 extra seconds per answer. Worth it.
- **A near tie.** For the 502 question, a setup runbook edged out the Web Service Outage runbook, 0.738 to 0.723. The fix: when two runbooks are within 0.03, give the model both.
- **The one that still failed: Ceph.** Replacing a failed OSD disk scored a 1. The right page was a how-to, not linked from my runbook index, so ROSIE handed me my Proxmox update runbook. As far as ROSIE knew, I didn't have a Ceph runbook, and the evidence under her answer made that plain.

That last one turned out to be the most useful thing she does. A wrong answer, shown with its evidence, points straight at what my docs are missing. When nothing matches at all, she tells me: "Runbook Gap Identified." Either way, the fix goes in the docs, not the code. I turned my Ceph pages into three proper runbooks, and they're better for me too, not just for ROSIE. In other words, a wrong answer with its evidence is a to-do list for your docs.

There was one more twist. The old Ceph page kept turning up as evidence after I deleted it, because sync added and updated pages but never removed any. Now it does. (I haven't re-run the test since.)

### Smaller surprises

| What I saw | Cause | Fix |
| --- | --- | --- |
| Chat locked after a restart | One broken link on my docs site failed the sync, and chat waits for a clean one | Keep the docs free of broken links; check sync status first |
| Pages stored twice | The docs crawl and the runbook crawl both found them | Store each URL once, as a runbook |
| Model said a runbook matched, but not which | It was told only that one matched | Add that runbook's passage to the evidence and name it |
| Server froze during large uploads | Processing an upload blocked other requests | Uploads no longer block other requests |
| Runbook export failed | Titles with non-Latin-1 characters, quotes or line breaks | Export handles those titles |

## Lessons learned

The biggest surprise? How little of the work was actually "AI." Most of it was hardware, plumbing and search... the same kind of stuff I already do in my homelab. If you're thinking about building your own, here's what I'd tell you.

**Hardware**

- **A cheap datacenter GPU is a great ticket in, if you can cool it.** The P4 gets you 8 GB of VRAM for about $119, but a passive card in a 1U needs a plan for airflow.
- **Your BMC can't protect hardware it can't see.** If the fan controller doesn't know about the GPU, you have to close that loop yourself.
- **Make every failure fail safe.** If my controller dies, the fans go to Full. Loud is better than cooked.
- **Check what your old card supports.** Pascal means CUDA 12. The newest image isn't always the right one.
- **Low-tech fixes count.** A 40 mm blower and some foil tape gave the card airflow that no setting could.
- **Test cooling under a long, heavy load.** Normal use held 56 °C. Ten questions back to back hit 87 °C.

**LLMs**

- **You don't need to train anything.** Retrieval gives a small local model your knowledge, and updating the docs updates the assistant.
- **The model only knows what you show it.** Most "wrong answers" were the right answer to the wrong evidence. Show the evidence with every answer, and debug from there.
- **Small models need small, clear prompts.** On slow hardware, every word of the prompt costs time, and a small model follows short rules better than long ones.
- **Small models take rules literally.** "Say when evidence is missing" turned into a caveat on every line of a list. Every rule needs to spell out *how* to follow it.
- **Search is the product.** How pages are split, labeled and summarized mattered more than which model I picked.
- **Use the biggest model your VRAM allows.** Going from 3B to 8B was what finally got me a clean list. Measure what's actually in use, then do the math before you download.
- **Check your own instructions too.** The last odd line in an answer came from a sentence my own code added to every prompt, not from my docs or the model.
- **Show the model the whole procedure.** Giving it the closest runbook in page order, instead of its best-matching passage, took my test score from 2.9 to 4.1 out of 5.
- **Test with a fixed set of real questions.** Ten graded incident questions found problems one-off questions never showed me, like a false "Runbook Gap" in 6 of 10 answers.
- **A wrong answer with its evidence is a to-do list for your docs.** When ROSIE picks the wrong runbook or finds none, that's my docs telling me what's missing.

**DevOps**

- **Treat it like any other service.** Docker Compose, health checks, an audit log, read-only mounts, tests, and docs.
- **Keep it advisory.** No credentials and no live access made ROSIE easy to trust while I learned what she gets wrong.
- **Make limits visible.** Showing throttling in the footer and flagging cut-off answers saves a lot of guessing about what went wrong.

## What's next

ROSIE is at version 0.1: documentation only, on purpose. The plan is to grow her senses before her hands:

- **v0.2 to v0.4:** export runbooks as HTML, PDF and Word documents, connect to wiki platforms, and open pull requests for runbook drafts instead of leaving loose files around.
- **v1.0:** *read-only* views of the live homelab through Grafana, Prometheus and Loki, so ROSIE can compare what the docs say with what the metrics show.
- **Not scheduled:** letting her take actions. That waits until there's a proper threat model and an approval step.

I started this project not knowing what an embedding was. Now I use ROSIE to find the right runbook faster, and I understand why she sometimes gets it wrong. That second part was the real goal.

## Try ROSIE, or build your own

- **Talk to her:** <https://rosie.refol.us>. Ask her about anything in my homelab docs, and check the evidence listed under each answer.
- **Read the code:** [github.com/t3knoid/ROSIE](https://github.com/t3knoid/ROSIE). It has the app, the Docker Compose stack, the `p4-thermal` fan controller, and the docs, including the GPU setup guide and the lessons-learned page this post grew out of.

