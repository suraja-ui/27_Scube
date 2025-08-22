// Live backend on Render
const API = "https://website-audit-backend-8b6k.onrender.com";

// elements
const urlEl   = document.getElementById("url");
const runEl   = document.getElementById("run");
const spin    = document.getElementById("spin");
const results = document.getElementById("results");
const rawEl   = document.getElementById("raw");
const recsEl  = document.getElementById("recs");
const passesEl= document.getElementById("passes");
const issuesEl= document.getElementById("issues");
const dlBtn   = document.getElementById("download");

// helper: set badge colour
function setScore(id, val){
  const el = document.getElementById(id);
  el.textContent = val;
  el.className = "score " + (val>=80 ? "good" : val>=50 ? "ok" : "bad");
}

// helper: escape html
function escapeHtml(s){return s.replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}

// call API with small retry (handles Render cold start)
async function callAudit(url, tries=6){
  let lastErr;
  for(let i=0;i<tries;i++){
    try{
      const r = await fetch(`${API}/audit`,{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ url })
      });
      if(r.ok) return await r.json();
      if([429,502,503,504].includes(r.status)){ // transient
        await new Promise(res=>setTimeout(res, 4000));
        continue;
      }
      const t = await r.text();
      throw new Error(`HTTP ${r.status}: ${t.slice(0,200)}`);
    }catch(e){
      lastErr = e;
      await new Promise(res=>setTimeout(res, 4000));
    }
  }
  throw lastErr || new Error("Network error");
}

// show report
function showReport(j){
  results.style.display = "block";
  setScore("sec",  j.scores.security);
  setScore("seo",  j.scores.seo);
  setScore("perf", j.scores.performance);
  setScore("a11y", j.scores.accessibility);

  recsEl.innerHTML   = (j.summary.recommendations||[]).map(x=>`<li>${escapeHtml(x)}</li>`).join("");
  passesEl.innerHTML = (j.summary.passes||[]).map(x=>`<span class="chip">${escapeHtml(x)}</span>`).join(" ");
  issuesEl.innerHTML = (j.summary.issues||[]).map(x=>`<span class="chip">${escapeHtml(x)}</span>`).join(" ");

  rawEl.textContent = JSON.stringify(j, null, 2);

  dlBtn.disabled = false;
  dlBtn.onclick = ()=>{
    const blob = new Blob([JSON.stringify(j, null, 2)], {type:"application/json"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "audit-report.json";
    a.click();
    URL.revokeObjectURL(a.href);
  };
}

// click handler with spinner
runEl.addEventListener("click", async ()=>{
  const target = (urlEl.value||"").trim();
  if(!target){ alert("Enter a URL like https://example.com"); return; }

  runEl.disabled = true;
  dlBtn.disabled = true;
  results.style.display = "none";
  spin.style.display = "grid";

  try{
    const data = await callAudit(target);
    showReport(data);
  }catch(e){
    console.error(e);
    alert("Failed to reach backend at " + API + "/audit\n\n" + e.message);
  }finally{
    spin.style.display = "none";
    runEl.disabled = false;
  }
});
