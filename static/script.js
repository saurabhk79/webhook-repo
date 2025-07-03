function formatEvent(e) {
  let msg = "";
  const type = e.action;

  if (type === "PUSH") {
    msg = `<span class="type">PUSH</span>: ${e.author} pushed to ${e.to_branch} on ${e.timestamp}`;
  } else if (type === "PULL_REQUEST") {
    msg = `<span class="type">PR</span>: ${e.author} submitted a pull request from ${e.from_branch} to ${e.to_branch} on ${e.timestamp}`;
  } else if (type === "MERGE") {
    msg = `<span class="type">MERGE</span>: ${e.author} merged branch ${e.from_branch} to ${e.to_branch} on ${e.timestamp}`;
  }

  return msg;
}

async function fetchEvents() {
  try {
    const res = await fetch("/webhook/events");
    const events = await res.json();

    const container = document.getElementById("events");
    container.innerHTML = "";

    events.forEach((e) => {
      const div = document.createElement("div");
      div.className = "event";
      div.innerHTML = formatEvent(e);
      container.appendChild(div);
    });

    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    document.getElementById("refresh-info").textContent = `Last refreshed at: ${timeStr}`;
  } catch (err) {
    console.error("Error fetching events:", err);
  }
}

setInterval(fetchEvents, 15000);
fetchEvents();
