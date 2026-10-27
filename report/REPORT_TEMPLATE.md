# Case Study Report: Equifax and Apache Struts S2-045

Use this as the scaffold for the required 10-15 page team report. Replace bracketed notes with your team's own research and observed lab evidence. Do not claim the lab reproduces Equifax's complete breach.

## Suggested Page Plan

1. Cover page and executive summary (1 page)
2. Incident background and impact (1-2 pages)
3. Technical root cause and vulnerability analysis (2 pages)
4. Reconnaissance and Kill Chain mapping (1-2 pages)
5. Isolated lab architecture and safety controls (1 page)
6. Red-team simulation method and observed evidence (1-2 pages)
7. Blue-team control, proxy logic, logs, and validation (1-2 pages)
8. Lessons, recommendations, limitations, and conclusion (1-2 pages)
9. References and appendices (as needed)

## 1. Executive Summary

[Summarize the incident, CVE-2017-5638, the safe lab proof, the observed defensive block, and the main recommendation. State that the lab does not execute OS commands or reproduce Equifax's production environment.]

## 2. Incident Background

[Describe the 2017 Equifax breach and reported impact using authoritative sources. Distinguish established facts from estimates. Explain that a vulnerable Apache Struts component was left unpatched after the S2-045 advisory.]

## 3. Technical Root Cause

- Product/component: Apache Struts Jakarta Multipart parser.
- CVE: CVE-2017-5638, S2-045.
- Affected historical versions: Struts 2.3.x before 2.3.32 and 2.5.x before 2.5.10.1.
- Vulnerability behavior: crafted multipart-related HTTP headers could reach unsafe expression evaluation, enabling remote code execution.
- Lab proof: a harmless OGNL expression adds `X-Lab-Proof: 54289` to the response; no shell command runs.
- Root-cause themes to research: patch management, asset inventory, logging/monitoring, and data access controls.

## 4. Cybersecurity Kill Chain Mapping

Do not invent facts where public reporting does not establish an action. Separate the historical incident from what your lab demonstrates.

| Kill Chain phase | Historical incident evidence | Lab evidence |
| --- | --- | --- |
| Reconnaissance | [What sources establish; otherwise state not publicly established.] | [Target and service identification performed inside host-only lab.] |
| Weaponization | [Crafted request exploiting S2-045; attribute only what sources support.] | [Safe response-header expression prepared in the provided script.] |
| Delivery | [HTTP request to vulnerable application, if supported by sources.] | [POST request sent from Kali to target VM.] |
| Exploitation | [CVE-2017-5638 / unsafe expression evaluation.] | [Direct path returns the lab proof header.] |
| Installation | [State only documented evidence; otherwise not established.] | [Not performed; no payload is installed.] |
| Command and Control | [State only documented evidence; do not infer.] | [Not performed.] |
| Actions on Objectives | [Summarize documented access/exfiltration at a high level.] | [No data access or exfiltration; proof is limited to a response header.] |

## 5. Lab Design and Authorization Boundary

[Insert a network diagram or hand-drawn diagram showing Kali and Ubuntu connected only through a VirtualBox Host-only Adapter. Document VM addresses, snapshots, Docker internal network, target port 8080, guard port 8081, and confirmation that NAT/bridged adapters were disconnected during testing.]

## 6. Red-Team Simulation

[List tool and version information, the exact commands your team ran, timestamps, and screenshots. Include the observed status and proof header. Explain why this is a safe proof of the vulnerable expression-evaluation path rather than OS command execution.]

## 7. Blue-Team Defense

[Explain the guard rule for OGNL-like values in `Content-Type`, include the JSON blocked event, and show the same request returned HTTP 403 through port 8081. Discuss false positives and why a proxy rule is a compensating control.]

Primary remediation: upgrade the affected Struts library to a currently supported fixed release, test the application, and maintain an asset inventory and patch process. Do not treat the demo proxy as a substitute for patching.

## 8. Lessons and Recommendations

1. Maintain a current inventory of applications and third-party components.
2. Prioritize vendor security advisories and verify patch deployment.
3. Centralize application and network logs and alert on suspicious parser errors or exploit-shaped headers.
4. Apply least privilege and segment sensitive data stores from public-facing application tiers.
5. Test incident response and preserve evidence without exposing real data.

## 9. Limitations

[Identify that the lab uses an intentionally vulnerable training image, a safe non-shell proof, synthetic data, and a simplified proxy. The historic incident included real-world actions beyond this lab; do not claim those actions were reproduced.]

## References

- NIST NVD CVE-2017-5638: https://nvd.nist.gov/vuln/detail/CVE-2017-5638
- Apache Struts 2017 announcements: https://struts.apache.org/announce-2017.html
- Vulhub S2-045 environment: https://github.com/vulhub/vulhub/tree/master/struts2/s2-045
- U.S. House Committee report, *The Equifax Data Breach*: https://oversight.house.gov/wp-content/uploads/2018/12/Equifax-Report.pdf
