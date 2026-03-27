# Final Year Project — Development & Report Plan

## Deadline: February 3, 2026

---

## CURRENT STATUS OVERVIEW

| Task | Status |
|---|---|
| Bandpass filter (`src/working_fsk.py`) | DONE |
| AGC normalization (`src/working_fsk.py`) | DONE |
| Barker-7 sync (`src/working_fsk.py`) | DONE |
| Persistent nonce logging (`src/crypto_core.py`) | DONE |
| Protocol layer wired into auth flow (`src/acoustic_auth.py`) | DONE |
| Test framework output fixed (`tests/test_framework.py`) | DONE |
| Protocol layer tests — 10 test cases | DONE |
| FSK signal processing tests — 5 test cases | DONE |
| **33/33 tests passing (100%)** | DONE |
| Repo restructured (src/, tests/, planning/, ios/) | DONE |
| Frequency decision (8/10 kHz vs 18/19 kHz) | PENDING — needs hardware |
| Tkinter GUI (`src/gui.py`) | TODO |
| iOS Swift app skeleton (`ios/`) | TODO |
| Report writing | TODO |
| Demo video | TODO |

---

## PHASE 1: CODE — REMAINING TASKS

### 1.1 Frequency Decision — PENDING (needs hardware)
- **Problem:** Report specifies 18/19 kHz, code uses 8/10 kHz
- **Action:** Run empirical test at both frequency pairs, measure BER and signal strength at 30cm
- **Decision criteria:** Pick whichever gives <1% BER
- **Outcome:** Lock in one pair, update `self.f0` and `self.f1` in `src/working_fsk.py`, document justification in report
- **Note:** Bandpass filter range in `bandpass_filter()` must also be updated to match chosen frequencies

### 1.2 Tkinter GUI — TODO
- **File:** `src/gui.py`
- **Why:** Report 1 Section 4.2 explicitly promises a GUI — must be delivered
- **Spec:** Cross-platform (macOS + Windows), Tkinter (built-in, no extra dependencies)
- **Required screens:**
  - Status label: Idle / Transmitting / Waiting / Verifying / Authenticated / Denied
  - Start Authentication button
  - Progress indicator during transmission
  - Clear success/failure message with colour (green/red)
- **Integration:** Calls `AcousticAuthenticator` from `src/acoustic_auth.py` in a background thread

### 1.3 iOS Swift App Skeleton — TODO
- **Folder:** `ios/AcousticAuth/`
- **Why:** Report 1 Section 1.5 lists iOS app as a core deliverable — completely absent
- **Files to create:**
  - `ContentView.swift` — SwiftUI interface (Authenticate button, status display)
  - `AcousticAuthenticator.swift` — protocol orchestration
  - `FSKDecoder.swift` — Goertzel algorithm in Swift
  - `CryptoEngine.swift` — HMAC-SHA256 using Apple CryptoKit
- **Note:** Code will be syntactically correct Swift mirroring the Python implementation. Full hardware integration pending Xcode testing.

### 1.4 Run Coverage Report — TODO
- **Action:** Run after GUI is added to capture updated coverage numbers for report
- **Commands (from tests/ folder):**
  ```
  python -m coverage run test_framework.py
  python -m coverage report
  python -m coverage html
  ```
- **Result:** Real coverage % figures for the report

---

## PHASE 2: DIAGRAMS — TODO (do after code is final)

### 2.1 UML Class Diagram
- Classes: `AcousticAuthenticator`, `AuthenticationProtocol`, `CryptographicCore`, `WorkingFSK`, `EnhancedFSK`, `ProtocolLayer`, `AudioFrame`, `FrameHeader`, `CRC16`
- Show: inheritance (EnhancedFSK extends WorkingFSK), uses, depends-on relationships
- Label key attributes and methods
- **Goes in:** Design section of report as Figure X.X

### 2.2 Sequence Diagram
- Full auth flow: Laptop → iPhone → Laptop
- Steps: generate challenge → Barker preamble + FSK encode → transmit → bandpass filter + AGC + Barker sync + Goertzel decode → HMAC compute → FSK encode → transmit → decode → verify
- Include timing (challenge tx ~13s, response tx ~26s)
- **Goes in:** Design section of report

### 2.3 State Machine Diagram
- States: IDLE → CHALLENGE_SENT → WAITING_RESPONSE → RECEIVING → VERIFYING → AUTHENTICATED / DENIED
- Include timeout transitions (30s session expiry)
- **Goes in:** Design section of report

### 2.4 Frame Structure Diagram
- Visual: [Preamble 8-bit | 0xAA] [Header 16-bit | type+seq+len] [Payload 0-255 bytes] [CRC 16-bit]
- Annotate each field
- **Goes in:** Implementation section of report

### 2.5 System Architecture Diagram
- Layered: Application Layer → Cryptographic Layer → Protocol Layer → Physical Layer → Hardware Layer
- Map each layer to its file in `src/`
- **Goes in:** Design section of report

---

## PHASE 3: REPORT WRITING

### 3.1 Required Sections Checklist

| Section | Status | Notes |
|---|---|---|
| Title Page | NOT STARTED | Download personalized cover from FYPMS |
| Declaration | NOT STARTED | Academic honesty statement — required by guidelines |
| Extended Abstract | NOT STARTED | 1-2 pages, self-contained, no abbreviations |
| Acknowledgments | NOT STARTED | Mention Prof. Hancke |
| Table of Contents | NOT STARTED | Must include appendices |
| Introduction | EXISTS | Needs minor update to reflect current implementation |
| Literature Review | WEAK | Explicitly flagged by professor — needs significant expansion |
| Design / System | EXISTS | Add UML diagrams + formal requirements table |
| Implementation | EXISTS | Update to reflect final code (bandpass, AGC, Barker, GUI, iOS) |
| Testing | PARTIAL | Add formal test case table with real results from 33 tests |
| Concluding Text | MISSING | Required by guidelines — critical review + achievements + future work |
| References | INCONSISTENT | Fix format — pick numbered or author-year, apply consistently |
| Appendices | MISSING | Monthly logs (required), test output, coverage report |

### 3.2 Literature Review Expansion (professor flagged this)
- **NFC:** Deeper treatment — specific relay attack distances from Francillon et al. (2019), hardware cost barrier
- **Bluetooth:** ECDH weakness specifics from Antonioli et al. (2020), exact range measurements
- **QR Code:** Session swapping attack mechanism from Tirfe et al. (2021), one-way channel limitation
- **Acoustic Auth — expand significantly:**
  - Dhwani (Nandakumar et al., 2014) — full paragraph on their inaudible acoustic NFC approach
  - ZEBRA (Mare et al., 2014) — zero-effort bilateral recurring authentication
  - Schürmann & Sigg (2011) — ambient audio for secure communication
  - Zhang et al. (2014) — keyless secure acoustic communication for smartphones
- **Add comparison table:**

| Method | Range | Special Hardware | Offline | Relay Attack Risk |
|---|---|---|---|---|
| NFC | <10 cm | Yes (reader) | Yes | Medium |
| Bluetooth | <100 m | No | No | High |
| QR Code | <1 m | No (camera) | Yes | Medium |
| Acoustic | <1 m | No | Yes | Low |

### 3.3 Software Engineering Section
**Formal Requirements Table:**

| ID | Type | Requirement |
|---|---|---|
| FR-01 | Functional | System shall generate 128-bit cryptographic nonce per session |
| FR-02 | Functional | System shall compute HMAC-SHA256 response using shared secret |
| FR-03 | Functional | System shall transmit data via FSK over acoustic channel |
| FR-04 | Functional | System shall detect and reject replayed challenges across sessions |
| FR-05 | Functional | System shall verify response using constant-time comparison |
| FR-06 | Functional | System shall apply bandpass filter before demodulation |
| FR-07 | Functional | System shall synchronize using Barker-7 preamble |
| FR-08 | Functional | System shall provide GUI with authentication status feedback |
| NFR-01 | Performance | Authentication cycle shall complete within 60 seconds |
| NFR-02 | Reliability | Success rate shall exceed 95% in quiet environment |
| NFR-03 | Security | False acceptance rate shall be 0% |
| NFR-04 | Reliability | Bit error rate shall be below 1% at 30cm |
| NFR-05 | Security | Replay attacks across sessions shall be blocked |

**Formal Test Case Table** — use actual TC-IDs from `tests/test_framework.py`:
- TC-CRYPTO-001 through TC-CRYPTO-004
- TC-AUTH-001 through TC-AUTH-003
- TC-FSK-001 through TC-FSK-008
- TC-PROTO-001 through TC-PROTO-010
- TC-SEC-001 through TC-SEC-002
- TC-PERF-001 through TC-PERF-003

### 3.4 Concluding Text (required by guidelines — completely missing)
- **Critical review:**
  - What went well: crypto implementation, protocol layer, test coverage, Barker sync
  - What didn't: frequency selection required empirical testing, iOS not yet integrated with hardware
  - Problems solved: synchronization improved from simple "11" pattern to Barker-7 cross-correlation; nonce logging made persistent
- **Summary of achievements:** 33 passing tests, full signal processing pipeline, CRC-16 framing, persistent replay protection
- **Future extensions:** iOS hardware integration, Reed-Solomon FEC, adaptive symbol duration, real-world noise testing, GUI polish

### 3.5 Appendices
- **Appendix A:** Monthly logs (required by guidelines — must not be omitted)
- **Appendix B:** Full test suite output (33 tests, 100% pass rate)
- **Appendix C:** Code coverage report
- **Appendix D:** Raw experimental data (BER measurements, timing data from hardware tests)

---

## PHASE 4: FORMATTING & POLISH

### 4.1 Abbreviations — Define on First Use
| Abbreviation | Full Form |
|---|---|
| FSK | Frequency-Shift Keying |
| HMAC | Hash-based Message Authentication Code |
| CRC | Cyclic Redundancy Check |
| BER | Bit Error Rate |
| NFC | Near Field Communication |
| FAR | False Acceptance Rate |
| FRR | False Rejection Rate |
| MVP | Minimum Viable Product |
| CSPRNG | Cryptographically Secure Pseudo-Random Number Generator |
| AGC | Automatic Gain Control |
| FEC | Forward Error Correction |
| SNR | Signal-to-Noise Ratio |

### 4.2 References
- Pick one style and apply consistently: numbered `[1]` or author-year `(Jones et al., 1960)`
- Every in-text citation must have a reference list entry
- Every reference list entry must be cited in the text
- Missing either direction = plagiarism per department guidelines

### 4.3 Figures and Tables
- Label as Figure X.X or Table X.X (chapter.number format)
- Every figure/table needs a descriptive caption
- Must appear on same page as the text referencing it

### 4.4 English Fixes from Report 1
- "authentification" → "authentication" (multiple occurrences)
- "3 partyy" → "third-party"
- Section 4 header duplicates Section 3 header — fix numbering
- General grammar pass — target Grade B English minimum

### 4.5 Word Count
- Target: ~10,000 words for main text (intro + main + conclusion)
- Guidelines: too short = insufficient effort, too long = unclear thinking

---

## PHASE 5: SUBMISSION PREP

| Item | Format | Destination |
|---|---|---|
| Report | PDF (preferred) | FYPMS + email supervisor |
| Source code + README | GitHub link or ZIP | FYPMS + email supervisor |
| Demo video | MP4, 5-15 mins, min 640x480, English | FYPMS |
| Presentation slides | PPT or PDF | FYPMS |
| Project screenshot | Image file | FYPMS |

### Demo Video Checklist
- [ ] Brief project introduction (problem + solution)
- [ ] Live demo: run `python src/acoustic_auth.py` showing auth cycle
- [ ] Show test suite running: `python tests/test_framework.py`
- [ ] Show GUI working
- [ ] 5-15 minutes
- [ ] MP4, minimum 640x480
- [ ] English language only

### README Checklist (already done — verify before submission)
- [x] System requirements
- [x] Installation steps
- [x] How to run
- [x] Project structure
- [x] Test instructions
- [ ] Known limitations section

---

## TIMELINE

| Week | Focus |
|---|---|
| Week 1 (Now) | GUI (1.2) + iOS skeleton (1.3) |
| Week 2 | Frequency hardware test (1.1) + all diagrams (Phase 2) |
| Week 3 | Literature review expansion + software engineering section |
| Week 4 | Concluding text + missing report sections (abstract, declaration, acknowledgments) |
| Week 5 | Formatting, references, English polish, appendices |
| Week 6 | Demo video + submission prep + Turnitin check |
| **Feb 3, 2026** | **SUBMIT** |
