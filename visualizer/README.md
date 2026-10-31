# Equifax lab visualization

This optional local dashboard displays the result returned by the Kali demo script. It does not send attack requests. It binds to Kali loopback (`127.0.0.1`) and keeps the latest 40 events in memory only.

## Run it on Kali

Open one Kali terminal in the `visualizer` folder and run:

```bash
python3 dashboard.py
```

Open `http://127.0.0.1:8090` in Kali's browser. Keep this terminal running.

## Send results from another Kali terminal

Run the attack commands from the `attacker` folder. Replace the sample IP with the Ubuntu target VM's host-only address:

```bash
python3 equifax_demo.py 192.168.56.20 --port 8080 --dashboard
python3 equifax_demo.py 192.168.56.20 --port 8081 --dashboard
```

The direct path should show HTTP 200 and `X-Lab-Proof: 54289`. The guarded path should show HTTP 403. The dashboard displays the returned status and a short explanation. The proxy's detailed event remains available on Ubuntu with `docker compose logs --no-color --tail=30 guard`.

If `--dashboard` is omitted, the original terminal demonstration works as before and does not contact the dashboard. If the dashboard is stopped, the attack command still reports its result in the terminal.

## Safety boundary

Use only the isolated coursework VMs and the host-only lab network. Do not expose port 8090 beyond Kali loopback. This visualization shows the lab result; it does not reproduce the full Equifax incident or run an operating-system command.