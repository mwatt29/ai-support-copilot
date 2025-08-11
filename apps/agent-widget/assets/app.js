(function() {
  var client = ZAFClient.init();
  const API_BASE_URL = "http://localhost:8000"; // Set to your API

  let lastSuggestionId = null;

  async function getTicketId() {
    const data = await client.get('ticket.id');
    return data['ticket.id'];
  }

  async function ensureTicketInAPI(ticketId) {
    const ticketData = await client.get(['ticket.subject', 'ticket.description', 'currentUser.email', 'currentAccount.name']);
    const payload = {
      org: ticketData['currentAccount.name'] || 'Acme Inc',
      ticket: {
        id: ticketId,
        subject: ticketData['ticket.subject'] || '',
        body: ticketData['ticket.description'] || '',
        requester: ticketData['currentUser.email'] || ''
      }
    };
    await fetch(API_BASE_URL + "/webhooks/zendesk", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
  }

  document.getElementById('suggestBtn').addEventListener('click', async function() {
    const tid = await getTicketId();
    await ensureTicketInAPI(tid);
    const lookup = await fetch(API_BASE_URL + "/lookup-ticket?externalId=" + encodeURIComponent(tid));
    const { ticket_uuid } = await lookup.json();

    const res = await fetch(API_BASE_URL + "/suggest", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ ticketId: ticket_uuid })
    });
    const data = await res.json();
    document.getElementById('answer').value = data.answer || '';
    lastSuggestionId = data.suggestionId;
    const srcDiv = document.getElementById('sources');
    srcDiv.innerHTML = '';
    (data.sources || []).forEach((s, i) => {
      const d = document.createElement('div');
      d.className = 'src';
      d.textContent = `[S${i+1}] ${s.title} — ${s.snippet}`;
      srcDiv.appendChild(d);
    });
  });

  document.getElementById('usedBtn').addEventListener('click', async function() {
    if (!lastSuggestionId) return;
    const before = "";
    const after = document.getElementById('answer').value;
    await fetch(API_BASE_URL + "/feedback", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ suggestionId: lastSuggestionId, used: true, editDiff: { before, after } })
    });
    alert("Feedback recorded.");
  });
})();
