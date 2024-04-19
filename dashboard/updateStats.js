const EC2_IP = "localhost";
const STATS_API_URL = `/processing/stats`;
const EVENTS_URL = {
  jobs: `/audit_log/job`,
  applications: `/audit_log/application`,
};
const LOG_URL = `/event_logger/events_stats`;
const ANOMALY_URL = `/anomaly_detector/anomalies`;

const getDate = () => {
  const now = new Date();

  // Extract components
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0"); // Months are zero-based
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const seconds = String(now.getSeconds()).padStart(2, "0");

  // Format the date and time
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

// This function fetches and updates the general statistics
const getStats = (statsUrl) => {
  fetch(statsUrl)
    .then((res) => res.json())
    .then((result) => {
      console.log("Received stats", result);
      updateStatsHTML(result);
    })
    .catch((error) => {
      updateStatsHTML(error.message, (error = true));
    });
};

// This function fetches a single event from the audit service
const getEvent = (eventType, index) => {
  fetch(`${EVENTS_URL[eventType]}?index=${index}`)
    .then((res) => {
      if (!res.ok) {
        throw new Error(`Error: status code ${res.status}`);
      }
      return res.json();
    })
    .then((result) => {
      console.log("Received event", result);
      updateEventHTML({ ...result, index: index }, eventType);
    })
    .catch((error) => {
      updateEventHTML(
        { error: error.message, index: index },
        eventType,
        (error = true)
      );
    });
};

// This function updates a single "event box"
const updateEventHTML = (data, eventType, error = false) => {
  const { index, ...values } = data;
  const elem = document.getElementById(`event-${eventType}`);
  elem.innerHTML = `<h5>Event ${index}</h5>`;

  // for error messages
  if (error) {
    if (values.error.includes("404")) {
      const errorMsg = document.createElement("p");
      errorMsg.innerHTML = "No data at this index";
      elem.appendChild(errorMsg);
      return;
    }
    const errorMsg = document.createElement("code");
    errorMsg.innerHTML = values.error;
    elem.appendChild(errorMsg);
    return;
  }

  // loops through the object and displays it in the DOM
  Object.entries(values).map(([key, value]) => {
    if (["job_listing_id", "trace_id", "job_application_id"].includes(key)) {
      return;
    }
    const labelElm = document.createElement("span");
    const valueElm = document.createElement("span");
    labelElm.innerText = `${key}: `;
    valueElm.innerText = value;
    const pElm = document.createElement("p");
    pElm.style.display = "flex";
    pElm.style.flexDirection = "row";
    pElm.appendChild(labelElm);
    pElm.appendChild(valueElm);
    elem.appendChild(pElm);
  });
};

// This function updates the main statistics div
const updateStatsHTML = (data, error = false) => {
  const elem = document.getElementById("stats");
  if (error === true) {
    elem.innerHTML = `<code>${data}</code>`;
    return;
  }
  data["last_updated"] = getDate();
  elem.innerHTML = "";
  Object.entries(data).map(([key, value]) => {
    const pElm = document.createElement("p");
    pElm.innerHTML = `<strong>${key}:</strong> ${value}`;
    elem.appendChild(pElm);
  });
};

const eventInput = () => {
  document.getElementById("fetchEventButton").addEventListener("click", () => {
    const index = document.getElementById("eventIndex").value;
    getEvent("jobs", index);
    getEvent("applications", index);
  });
};

const updateLogs = (index) => {
  fetch(LOG_URL)
    .then((res) => res.json())
    .then((result) => {
      const elem = document.getElementById(`event-logs`);
      elem.innerHTML = `<h5>Update count ${index}</h5>`;
      for (const [key, value] of Object.entries(result)) {
        const pElm = document.createElement("p");
        pElm.innerHTML = `<strong>${key}:</strong> ${value}`;
        elem.appendChild(pElm);
      }
    });
};

const updateAnomaliesTooHigh = () => {
  fetch(`${ANOMALY_URL}?anomaly_type=TooHigh`)
    .then((res) => res.json())
    .then((result) => {
      const elem = document.getElementById(`event-anomaly`);
      elem.innerHTML = `<h5>TooHigh</h5>`;
      for (let i = 0; i < 1; i++) {
        const entry = result[i];
        console.log(entry);
        const pElm = document.createElement("p");
        pElm.innerHTML = `<pre>Description: ${str(entry)}:</pre>`;
        elem.appendChild(pElm);
        break;
      }
    });
};

const updateAnomaliesTooLow = () => {
  fetch(`${ANOMALY_URL}?anomaly_type=TooLow`)
    .then((res) => res.json())
    .then((result) => {
      const elem = document.getElementById(`event-anomaly-low`);
      elem.innerHTML = `<h5>TooLow</h5>`;
      for (let i = 0; i < 1; i++) {
        const entry = result[i];
        console.log(entry);
        const pElm = document.createElement("p");
        pElm.innerHTML = `<pre>Description: ${str(entry)}:</pre>`;
        elem.appendChild(pElm);
        break;
      }
    });
};

const setup = () => {
  let index = 1;
  eventInput();
  const interval = setInterval(() => {
    getStats(STATS_API_URL);
    updateLogs(index);
    updateAnomaliesTooHigh();
    updateAnomaliesTooLow();
    // getEvent("jobs", index);
    // getEvent("applications", index);
    index++;
  }, 5000); // Update every 5 seconds

  // initial call
  getStats(STATS_API_URL);
  // getEvent("jobs", index);
  // getEvent("applications", index);
};

document.addEventListener("DOMContentLoaded", setup);
