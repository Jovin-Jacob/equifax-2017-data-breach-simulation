# Equifax S2-045 Isolated VM Lab

This is a terminal-driven red-team/blue-team coursework lab for Apache Struts S2-045, CVE-2017-5638, which was exploited in the 2017 Equifax breach. The lab demonstrates the vulnerable request path with a harmless response-header proof, then blocks the same request through a logging proxy. It does not run ransomware, execute operating-system commands, or reproduce Equifax's full internal environment.

## Lab Layout

- **Attacker VM:** Kali Linux, running `attacker/equifax_demo.py` from a terminal.
- **Target VM:** Ubuntu Server with Docker Engine and Docker Compose. It runs the vulnerable Struts 2.3.30 training image and a small defensive proxy.
- **Network:** VirtualBox Host-only Adapter between the two VMs. No bridged adapter and no internet route during the exercise. Docker's lab network is internal-only.
- **Ports:** Target VM host-only address, TCP 8080 for the vulnerable service and TCP 8081 for the guarded path.

The Struts image is based on Vulhub's S2-045 educational environment. The safe proof adds `X-Lab-Proof: 54289` to the HTTP response; it does not invoke a shell.

## Safety Boundary

Use disposable VMs and take snapshots first. Never use bridged networking, public IPs, a real cloud account, or a system you do not own. The provided Compose file binds services to the target VM's host-only address and uses an internal Docker network. The vulnerable image is intentionally old: keep it inside the lab and shut it down when the exercise ends.

To download the container image and build the proxy, temporarily give the target VM NAT access during setup. Then power it off, remove the NAT adapter, and leave only the Host-only Adapter enabled before starting the exercise. The attacker VM should also have only its Host-only Adapter enabled during the exercise.

## Prerequisites

- VirtualBox (or another hypervisor with an isolated host-only network)
- One Kali Linux VM and one Ubuntu Server VM
- Docker Engine and the Compose plugin installed on the target VM
- Python 3 on Kali

Assign static host-only addresses in the same private subnet, for example Kali `192.168.56.10/24` and target `192.168.56.20/24`. Confirm the target VM's address with `ip -br addr` on Ubuntu. Use your actual host-only subnet if it differs.

## Setup on the Target VM

Copy the `target` directory to Ubuntu. Set the Compose bind address to the target VM's host-only IP:

```bash
cd target
cp .env.example .env
```

Edit `.env` and set `LAB_HOST_IP` to the target VM's host-only address. While setup NAT is temporarily enabled, pull/build the images:

```bash
docker compose pull struts
docker compose build guard
```

Power down the VM, remove its NAT adapter, and ensure only its Host-only Adapter remains. Boot Ubuntu again, then start the lab:

```bash
docker compose up -d
docker compose ps
```

The lab is terminal-driven. An optional dashboard can run locally on Kali and display results from the command-line script; it does not send requests to the target.

## Attack Simulation from Kali

Copy the `attacker` directory to Kali. From a terminal, record the command session, then send the safe proof request directly to the vulnerable target:

```bash
mkdir -p evidence
script -q -a evidence/attack-and-defense.log
python3 equifax_demo.py 192.168.56.20 --port 8080
```

Expected result: HTTP 200 and `X-Lab-Proof: 54289`. This proves the crafted `Content-Type` expression was evaluated by the vulnerable Struts parser. It does not execute an OS command. Replace the example IP with the target VM's host-only address.

The underlying CVE involved remote command execution. This coursework proof intentionally stops short of running a command: the evaluated expression adds a response header, which is safe, observable evidence of the vulnerable expression-evaluation path.

## Blue-Team Defense Demonstration

Send the same request through the defensive proxy:

```bash
python3 equifax_demo.py 192.168.56.20 --port 8081
```

Expected result: HTTP 403 and no proof header. On the target VM, show the proxy's detection event:

```bash
docker compose logs --no-color --tail=30 guard
```

The event records the source address, method, path, action (`blocked`), and reason. The proxy is a compensating control for the lab, not a replacement for patching. The actual remediation is to upgrade Struts to a vendor-supported fixed release; Apache's original S2-045 advisory identifies 2.3.32 and 2.5.10.1 as releases fixing this issue.

## Optional Kali Visualization

The dashboard is optional. Copy the `visualizer` directory to Kali. In one Kali terminal, start it:

```bash
cd visualizer
python3 dashboard.py
```

Open `http://127.0.0.1:8090` in Kali's browser. In another Kali terminal, run the attack commands from the `attacker` directory and add `--dashboard`:

```bash
python3 equifax_demo.py 192.168.56.20 --port 8080 --dashboard
python3 equifax_demo.py 192.168.56.20 --port 8081 --dashboard
```

Replace the example address with the Ubuntu target VM's host-only IP. The script sends the observed status and proof marker to the dashboard on Kali loopback. The dashboard binds only to `127.0.0.1`, stores up to 40 results in memory, and does not send traffic to the target. Without `--dashboard`, the terminal demo is unchanged. See [visualizer/README.md](visualizer/README.md) for details.

Finish recording the Kali session with `exit`. Capture screenshots of the direct proof response, the blocked response, and the proxy log. Keep the text log as command evidence. Redact no meaningful values, but do not include personal data; all lab data is synthetic.

## Cleanup

On the target VM:

```bash
docker compose down
```

Keep the VMs disconnected from external networks until the vulnerable container is stopped. Restore or delete the disposable VM snapshots after collecting the required evidence.

## Assignment Deliverables

| Rubric component | Evidence in this package |
| --- | --- |
| Reconnaissance and threat mapping (5) | `report/REPORT_TEMPLATE.md` includes incident background and a Kill Chain table. |
| Red-team simulation (8) | `attacker/equifax_demo.py`, recorded Kali terminal log, and screenshots of the safe proof. |
| Blue-team defense (7) | Guard proxy, blocked request result, and target-side JSON log. |
| Written report (5) | `report/REPORT_TEMPLATE.md` gives a 10-15 page structure. |
| Presentation and viva (5) | `presentation/SLIDE_OUTLINE.md` provides a 15-20 minute outline and practice questions. |

## Scope and Accuracy

This lab reproduces the S2-045 vulnerability class on an intentionally vulnerable Apache Struts instance. It does not recreate Equifax's production network, its data, the attacker's entire operation, or undocumented commands. In the report, label unknown Kill Chain phases as unknown instead of inventing details. The proxy demonstrates detection and blocking; discuss patching the vulnerable library as the primary fix.

## References

- NIST NVD, CVE-2017-5638: https://nvd.nist.gov/vuln/detail/CVE-2017-5638
- Apache Struts, 2017 security announcements: https://struts.apache.org/announce-2017.html
- Vulhub S2-045 lab and safe response-header proof: https://github.com/vulhub/vulhub/tree/master/struts2/s2-045
- U.S. House Committee report, *The Equifax Data Breach*: https://oversight.house.gov/wp-content/uploads/2018/12/Equifax-Report.pdf
