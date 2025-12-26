let rec, sessionId = null;

if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
  rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  rec.lang = 'en-US';
}

document.getElementById('voiceBtn').onclick = () => {
  if (!rec) return alert("Voice not supported");
  rec.start();
  document.getElementById('voiceBtn').textContent = "Listening...";
};

rec && (rec.onresult = e => {
  let t = e.results[0][0].transcript.toLowerCase()
    .replace(/zero/g,"0").replace(/one/g,"1").replace(/two/g,"2")
    .replace(/three/g,"3").replace(/four/g,"4").replace(/five/g,"5")
    .replace(/six/g,"6").replace(/seven/g,"7").replace(/eight/g,"8")
    .replace(/nine/g,"9").replace(/[^0-9]/g,"");
  document.getElementById('phone').value = t;
  document.getElementById('voiceBtn').textContent = "Speak";
});

document.getElementById('searchBtn').onclick = async () => {
  const no = document.getElementById('phone').value.trim();
  if (!no) return;
  const res = await fetch('/search', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({contact_no:no})});
  const d = await res.json();
  if (d.error) return showError(d.error);

  sessionId = d.session_id;
  document.getElementById('step1').classList.add('d-none');
  document.getElementById('step2').classList.remove('d-none');
  document.getElementById('accountsList').innerHTML = d.accounts.map(a => `
    <div class="col-md-6">
      <div class="card account-card border-primary shadow-sm clickable" data-val="${a.value}">
        <div class="card-body text-center">
          <h5 class="text-primary">${a.ref_no}</h5>
          <small>${a.text}</small>
        </div>
      </div>
    </div>
  `).join('');

  document.querySelectorAll('.account-card').forEach(c => c.onclick = async () => {
    const r = await fetch('/select_account', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({session_id:sessionId, account_value:c.dataset.val})});
    const data = await r.json();
    if (data.error) return showError(data.error);

    document.getElementById('step2').classList.add('d-none');
    document.getElementById('step3').classList.remove('d-none');
    document.getElementById('infoTable').innerHTML = Object.entries(data.consumer_info).map(([k,v]) => `<tr><td><strong>${k}</strong></td><td>${v}</td></tr>`).join('');
    document.getElementById('billing').innerHTML = data.billing_data.map(r => r.join(" → ")).join("<br>");
    document.getElementById('status').textContent = `Ref: ${data.reference_no} | ${data.recent_bill_status}`;
  });
};

document.getElementById('genBtn').onclick = async () => {
  const ref = document.getElementById('status').textContent.match(/\d{14,}/)[0];
  const r = await fetch('/generate_bill', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({session_id:sessionId, reference_no:ref})});
  const d = await r.json();
  if (d.success) {
    const a = document.createElement('a');
    a.href = `/download/${d.filename}`;
    a.download = '';
    a.click();
    document.getElementById('status').textContent = "Downloaded!";
  } else showError(d.error || "Failed");
};

function showError(msg) {
  const el = document.getElementById('error');
  el.textContent = msg;
  el.classList.remove('d-none');
}
