# Presentation Outline (15-20 minutes)

Target 10-12 slides. Keep the terminal demo short and use screenshots captured from the team's own isolated VM run.

1. **Case and objective** (1 min): Equifax, Apache Struts S2-045, CVE-2017-5638.
2. **Incident overview** (1-2 min): what happened, impact, and why this incident was selected.
3. **Root cause** (2 min): vulnerable multipart parser and unsafe expression evaluation in crafted headers.
4. **Kill Chain map** (2 min): distinguish sourced historical facts from unknown phases.
5. **Lab architecture and safety** (1 min): Kali plus Ubuntu target over host-only networking; no bridged adapter.
6. **Red-team proof** (2 min): show the command and `X-Lab-Proof: 54289` response; explain that no shell command ran.
7. **Blue-team control** (2 min): proxy rule, same request blocked with HTTP 403, and the JSON detection log.
8. **Remediation** (1-2 min): upgrade to a supported fixed Struts release, patch governance, monitoring, and least privilege.
9. **Lessons and limitations** (1 min): simplified training target; no reproduction of Equifax's full network or exfiltration.
10. **Conclusion and questions** (1 min).

## Viva Practice

- What is CVE-2017-5638 and which component was vulnerable?
- Why does the proof request use a `Content-Type` header?
- What does the response header prove, and what does it not prove?
- Why is the guard proxy only a compensating control?
- What is the primary remediation for the vulnerable library?
- Which Kill Chain phases are not demonstrated by this lab, and why?
- How did the team isolate the target and keep the vulnerable image away from external networks?
- What false positives could the proxy rule create, and how would a production defense be improved?
- What evidence did the team capture for the red-team and blue-team rubric items?
