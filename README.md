# MediTrace Sentinel

**Evidence-traced clinical note drafts from Vietnamese doctor–patient conversations.**

MediTrace Sentinel turns a Vietnamese consultation (typed, or transcribed from audio) into a
structured draft of the clinical record. It does not write the draft in one pass. It first lists every
piece of information as a separate **statement**, then checks each statement against what was actually
said. The doctor sees every line together with the turn it came from.

> MediTrace produces a *draft for review*. It does not diagnose, prescribe, or replace a clinician,
> and the draft is not an official medical record. All data used to build and measure it is
> **synthetic**. No real patient records or recordings were used.

---

## The problem

AI scribes already write fluent notes. Their dangerous errors are the quiet ones: the sentence reads
well but is wrong about *who*, *when* or *whether*:

| Said in the room | Fluent but wrong draft |
|---|---|
| Son: "**My father** has asthma." | "Patient has a history of asthma." |
| Patient: "Coughing for a week… no, actually ten days." | "Cough for one week." |
| Doctor: "**If** the fever continues tomorrow, come back for an X-ray." | "Chest X-ray ordered." |
| Doctor: "Any drug allergies?" (no answer) | "No known drug allergies." |

Vietnamese makes the first error more likely. Speakers often drop the subject ("Sốt hai hôm rồi", i.e.
"fever for two days"), and kinship words double as pronouns ("con", "cháu", "em" can mean *I* or
*the child*). Standard metrics do not see this error. When we swapped the patient and the relative in
400 notes, **ROUGE-1 stayed at 1.0000**.

## How it works

```
conversation ─► 1. extract statements (LLM) ─► 2. link people ─► 3. update state ─► 4. check evidence ─► 5. route ─► draft
                   Qwen3-4B + QLoRA             rules              rules              rules (6 checks)      rules
```

| Step | What it does | Code |
|---|---|---|
| 1. Extract | One JSON object per statement: content, **subject** (who it is about), speaker, certainty, negation, fact/hypothetical/plan, time, medication fields, **evidence turn numbers** and a verbatim quote | `src/nhanh.py`, `src/phat_bieu.py` |
| 2. Link people | Separates *who said it* from *who it is about* | `src/thuc_the.py` |
| 3. Update state | Addition, **correction** (old value marked superseded), change over time (both kept), unresolved **contradiction** | `src/cap_nhat.py` |
| 4. Check evidence | Six checks against the cited turn: quote exists, content overlaps, person words match the subject, certainty not raised, time and dose appear in the turn | `src/khoa_bang_chung.py` |
| 5. Route | Each statement goes to **the draft body**, **"Needs confirmation"** (with the reason), or **rejected** (kept in the trace) | `src/cong_rui_ro.py`, `src/canh_bao/` |
| 6. Ask | Up to 3 clarifying questions for the doctor | `src/hoi_lai.py` |

Only step 1 uses a model. Everything after it is readable rules. When the draft is wrong, you can tell
whether the model missed something or a rule misrouted it.

### Web app (`web/`)

- Review screen with **keep / edit / drop** on every statement. Each line links back to the source turn.
- Audio in: local **PhoWhisper** transcription. Optional speaker separation with **pyannote**; the
  doctor then assigns roles (doctor / patient / relative) per speaker.
- Accounts with invite codes; cases stored in SQLite, separated per user.
- An optional external-LLM switch for side tasks such as case Q&A or guideline lookup. **Off by
  default**, logged every time it is used, and never used for the draft itself.

## Results (synthetic data, development split)

Data: 5,000 rule-generated dialogues from 100 case templates, split by template. On top of that,
300 paired *challenge* dialogues: subject swap, self-correction, ASR noise, regional dialect.

| Finding | Number |
|---|---|
| Checks added on top of plain extraction, subject-swap set: F₁ | 66.1 % → **70.8 %** |
| Same set: slot error rate | 45.4 % → **36.9 %** |
| Superseded values left in the draft, correction set | 11.48 % → **0.80 %** |
| Correct statements wrongly blocked by the evidence checks | **0 of 30,136** |
| Patient ↔ relative swap in 400 notes: ROUGE-1 / our attribution score | 1.0000 (no change) / −0.1381 |

What did **not** work, reported as measured:

- **A fine-tuned model that writes the note directly scored higher** on our attribution metric on all
  four challenge sets (e.g. 0.939 vs 0.748). Part of this is because it learned to reproduce the
  generator's reference notes word for word in 30–63 % of cases, and the metric compares against
  those same notes. The rest is real: it attributed matched statements to the right person more
  often (97.1 % vs 88.3 %).
- A large commercial model assigned subjects more accurately than our 4B model (1.4 % vs 7.6 %
  subject errors on the correction set).
- The synthetic answers overlap the dialogue text heavily (extractive coverage 0.95–0.97), so none of
  this is yet evidence about real clinics.

Speed: about **3.5 minutes per draft** on a single RTX 3060 (Qwen3-4B, 4-bit). The rule steps take
under a second.

## Repository layout

| Path | Contents |
|---|---|
| `src/` | Everything in Python: data generator, extraction, rule steps, scorer, local HTTP service (`src/dich_vu.py`), audio intake (`src/audio/`) |
| `tests/` | About 1,260 tests (`pytest`) |
| `tools/` | Experiment runners (`.ps1`), packaging for Kaggle, benchmarks |
| `kaggle-kernels/` | One folder per training or inference run on Kaggle (set your own username in `kernel-metadata.json`) |
| `web/` | React + Express front end; see `web/README.md` |

Not included: datasets, model weights, run outputs, internal documents and evaluation keys. The data
can be regenerated from the code.

## Run it

Python 3.11. Main packages: `torch 2.6`, `transformers ≥ 4.51`, `peft`, `bitsandbytes`,
`lm-format-enforcer`, `pytest`. Speaker separation needs a **separate** environment
(`src/audio/pyannote-moi-truong.txt`) and a Hugging Face token.

```bash
# tests
python -m pytest tests/ -q

# generate synthetic dialogues
python -m src.sinh_hoi_thoai_viet --so-ca 1000 --seed 42

# local service for the web app (listens on 127.0.0.1 only)
python -m src.dich_vu --cong 8765
#   --khong-mo-hinh            no GPU: serve previously computed cases only
#   --tach-nguoi-noi pyannote  speaker separation (needs a Hugging Face token file)

# web app
cd web && npm install && npm run dev
```

Secrets (Hugging Face token, optional external-LLM key and endpoint) are read at runtime from
files or environment variables. None are stored in this repository.

## Limitations

- All training and evaluation data are synthetic and more regular than real speech.
- No study with clinicians yet: no timing, usability or safety outcome has been measured.
- The attribution scorer only distinguishes *patient* vs *relative* and is sensitive to how sentences
  are split.
- Speech recognition on drug names is poor (almost every drug name is misheard in our benchmark).

---

### Tóm tắt tiếng Việt

MediTrace Sentinel dựng **bản nháp hồ sơ lâm sàng có cấu trúc** từ hội thoại khám bệnh tiếng Việt.
Mỗi dòng trong bản nháp kèm lượt hội thoại làm căn cứ. Chỉ bước tách mệnh đề dùng mô hình
(Qwen3-4B + QLoRA); gom người, cập nhật trạng thái, kiểm căn cứ và xếp chỗ là luật đọc lại được.
Thông tin đáng ngờ được đưa sang mục "Cần xác nhận" kèm lý do. Toàn bộ dữ liệu là hội thoại mô
phỏng. Hệ thống không chẩn đoán, không kê đơn.
