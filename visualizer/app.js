const events=document.querySelector("#events");
const connection=document.querySelector("#connection");
const poll=document.querySelector(".poll");
function esc(value){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]);}
function render(items){
 if(!items.length){events.innerHTML='<tr class="empty"><td colspan="5">Waiting for a run. Start the dashboard, then run the Kali command in another terminal.</td></tr>';return;}
 events.innerHTML=items.map(e=>{const guarded=Number(e.port)===8081;const blocked=e.result==="blocked";return `<tr><td>${esc(e.time)}</td><td><span class="path-chip ${guarded?"guarded":"direct"}">${guarded?"GUARDED":"DIRECT"} · :${esc(e.port)}</span></td><td class="${blocked?"status-block":"status-ok"}">HTTP ${esc(e.status)}</td><td><code>${esc(e.proof)}</code></td><td>${esc(e.action)}</td></tr>`;}).join("");
}
async function refresh(){try{const r=await fetch("/api/state",{cache:"no-store"});if(!r.ok)throw Error();const data=await r.json();render(data.events||[]);connection.textContent="Connected · localhost";poll.classList.remove("offline");}catch{connection.textContent="Waiting for local dashboard";poll.classList.add("offline");}}
document.querySelector("#copy").addEventListener("click",async()=>{const button=document.querySelector("#copy");try{await navigator.clipboard.writeText("python3 equifax_demo.py 192.168.56.20 --port 8080 --dashboard\npython3 equifax_demo.py 192.168.56.20 --port 8081 --dashboard");button.textContent="COPIED";}catch{button.textContent="SELECT COMMANDS";}setTimeout(()=>button.textContent="COPY",1400);});
refresh();setInterval(refresh,1000);
