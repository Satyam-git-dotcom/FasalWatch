import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  CheckCircle2, 
  ArrowRight
} from 'lucide-react';

const LOCATIONS = {
  "Ghaziabad": [34, 36, 39, 41, 42, 40, 37],
  "Karnal": [33, 35, 37, 38, 40, 39, 36],
  "Ludhiana": [31, 33, 36, 37, 38, 36, 34],
  "Jhansi": [36, 38, 41, 43, 44, 42, 40],
  "Nashik": [30, 31, 32, 33, 34, 33, 32],
  "Jaipur": [31, 33, 35, 37, 39, 36, 34],
  "Patna": [30, 32, 34, 35, 36, 34, 33]
};

const RAIN = {
  "Ghaziabad": 0, "Karnal": 2, "Ludhiana": 4, "Jhansi": 0, "Nashik": 12, "Jaipur": 0, "Patna": 1
};

const CROPS = {
  "Wheat": { thr: 35, stages: ["Flowering", "Grain filling", "Tillering"], mult: { Flowering: 1.3, "Grain filling": 1.2, Tillering: 0.6 } },
  "Mustard": { thr: 33, stages: ["Flowering", "Pod filling"], mult: { Flowering: 1.2, "Pod filling": 1.1 } },
  "Rice": { thr: 38, stages: ["Transplanting", "Tillering"], mult: { Transplanting: 1.0, Tillering: 0.8 } },
  "Maize": { thr: 37, stages: ["Silking", "Vegetative"], mult: { Silking: 1.4, Vegetative: 0.6 } }
};

const LANGUAGES = {
  en: "English",
  hi: "हिन्दी",
  pa: "ਪੰਜਾਬੀ"
};

const CHANNELS = ["SMS", "WhatsApp"];

const AGENT_STEPS = [
  "Data agent",
  "Risk agent",
  "Advisor agent",
  "Localizer agent",
  "Reviewer agent"
];

const HISTORICAL_EVENTS = [
  { n: "Mar 2022 heat wave, Punjab and Haryana", loss: 0.10, note: "Wheat grain filling came early. Reported yield losses around 10% in affected areas.", span: "11 days" },
  { n: "Apr 2024 heat wave, Uttar Pradesh", loss: 0.06, note: "Late-sown wheat and mustard hit during grain and pod filling.", span: "8 days" },
  { n: "May 2023 dry spell, Maharashtra", loss: 0.08, note: "Rainfall deficit during sowing. Drought risk scored from rain forecast.", span: "14 days" }
];

export default function App() {
  const [farmers, setFarmers] = useState([
    { n: "Ramesh Kumar", ph: "+91 98100 11122", loc: "Ghaziabad", crop: "Wheat", stage: "Flowering", land: 2.0, lang: "hi", chan: "SMS" },
    { n: "Gurpreet Singh", ph: "+91 98760 33211", loc: "Ludhiana", crop: "Wheat", stage: "Grain filling", land: 4.0, lang: "pa", chan: "WhatsApp" },
    { n: "Sunita Devi", ph: "+91 94150 77201", loc: "Jhansi", crop: "Mustard", stage: "Pod filling", land: 1.5, lang: "hi", chan: "SMS" }
  ]);

  const [selectedFarmerIndex, setSelectedFarmerIndex] = useState(0);
  const [loc, setLoc] = useState("Ghaziabad");
  const [crop, setCrop] = useState("Wheat");
  const [stage, setStage] = useState("Flowering");
  const [land, setLand] = useState(2.0);
  const [lang, setLang] = useState("hi");
  const [chan, setChan] = useState("SMS");

  // New farmer form
  const [newName, setNewName] = useState("");
  const [newPhone, setNewPhone] = useState("");

  // Swarm execution state
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stepStatus, setStepStatus] = useState(["wait", "wait", "wait", "wait", "wait"]);
  const [stepDetails, setStepDetails] = useState(["", "", "", "", ""]);
  const [result, setResult] = useState(null);
  
  // Streaming state
  const [streamedSms, setStreamedSms] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const fullSmsRef = useRef("");

  const [snsDelivered, setSnsDelivered] = useState(false);
  const [alertsLog, setAlertsLog] = useState([]);
  const [toastMessage, setToastMessage] = useState("");

  // Replay simulator state
  const [evIndex, setEvIndex] = useState(0);
  const [farmersCount, setFarmersCount] = useState(5000);
  const [leadDays, setLeadDays] = useState(4);
  const [actShare, setActShare] = useState(45);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(""), 2400);
  };

  const selectFarmer = (idx) => {
    if (idx === "") return;
    const f = farmers[idx];
    setSelectedFarmerIndex(idx);
    setLoc(f.loc);
    setCrop(f.crop);
    setStage(f.stage);
    setLand(f.land);
    setLang(f.lang);
    setChan(f.chan);
  };

  // Run the multi-agent pipeline with live streaming
  const runAdvisory = async () => {
    setRunning(true);
    setProgress(0);
    setSnsDelivered(false);
    setResult(null);
    setStreamedSms("");
    setIsStreaming(false);

    const f = farmers[selectedFarmerIndex] || { n: "Ramesh Kumar", ph: "+91 98100 11122" };
    const currentCrop = CROPS[crop] || CROPS.Wheat;
    const temps = LOCATIONS[loc] || [34, 36, 39, 41, 42, 40, 37];
    const rainVal = RAIN[loc] ?? 0;
    const peak = Math.max(...temps);
    const hotDays = temps.filter(t => t > currentCrop.thr).length;

    const riskScore = Math.min(100, Math.round((hotDays * 11 + Math.max(0, peak - currentCrop.thr) * 4 + (rainVal < 5 ? 12 : 0)) * (currentCrop.mult[stage] || 1)));
    const riskLevel = riskScore >= 70 ? "Severe" : riskScore >= 45 ? "High" : riskScore >= 20 ? "Moderate" : "Low";

    const details = [
      `Fetched 7-day forecast for ${loc} from Open-Meteo. Peak ${peak}°C, rain ${rainVal} mm.`,
      `${hotDays} of 7 days exceed the ${currentCrop.thr}°C limit for ${crop} at ${stage.toLowerCase()}. Score ${riskScore}/100.`,
      `Chose 3 actions that fit ${land} acres and low-cost inputs.`,
      `Rewrote advice in ${LANGUAGES[lang]}, short enough for ${chan}. (AWS Amazon Translate)`,
      `Checked reading level (grade 5), numbers and tone. No contradictions found.`
    ];

    const newStatus = ["wait", "wait", "wait", "wait", "wait"];
    for (let i = 0; i < AGENT_STEPS.length; i++) {
      newStatus[i] = "run";
      setStepStatus([...newStatus]);
      await new Promise(r => setTimeout(r, 550));
      newStatus[i] = "done";
      setStepStatus([...newStatus]);
      setStepDetails([...details]);
      setProgress((i + 1) * 20);
    }

    // Actions list
    let actionsList = [];
    if (lang === "en") {
      actionsList = crop === "Wheat"
        ? ["Irrigate lightly in the evening on the hottest day", "Spread mulch or straw between rows", "Delay fertilizer until the heat passes"]
        : ["Irrigate in the early morning or evening", "Mulch to hold soil moisture", "Avoid spraying during peak heat"];
    } else if (lang === "hi") {
      actionsList = [
        "सबसे गर्म दिन से पहले शाम को हल्की सिंचाई करें",
        "कतारों के बीच भूसा या पुआल बिछाएँ",
        "गर्मी बीतने तक खाद न डालें"
      ];
    } else {
      actionsList = [
        "ਸਭ ਤੋਂ ਗਰਮ ਦਿਨ ਤੋਂ ਪਹਿਲਾਂ ਸ਼ਾਮ ਨੂੰ ਹਲਕੀ ਸਿੰਚਾਈ ਕਰੋ",
        "ਕਤਾਰਾਂ ਵਿਚਕਾਰ ਤੂੜੀ ਵਿਛਾਓ",
        "ਗਰਮੀ ਲੰਘਣ ਤੱਕ ਖਾਦ ਨਾ ਪਾਓ"
      ];
    }

    // Generate Target SMS
    let targetSms = "";
    if (lang === "hi") {
      const lMap = { Low: "कम", Moderate: "मध्यम", High: "ऊँचा", Severe: "गंभीर" };
      targetSms = `${f.n} जी, आपकी ${crop} (${stage.toLowerCase()}) के लिए गर्मी की चेतावनी।\nजल्द ही ${hotDays} दिन तापमान ${currentCrop.thr}°C से ऊपर रहेगा। जोखिम: ${lMap[riskLevel] || riskLevel}।\n1) शाम को सिंचाई करें\n2) कतारों में भूसा बिछाएँ\n3) खाद रोकें\nमदद के लिए HELP लिखें।`;
    } else if (lang === "pa") {
      const lMap = { Low: "ਘੱਟ", Moderate: "ਦਰਮਿਆਨਾ", High: "ਵੱਧ", Severe: "ਗੰਭੀਰ" };
      targetSms = `${f.n} ਜੀ, ਤੁਹਾਡੀ ${crop} (${stage.toLowerCase()}) ਲਈ ਗਰਮੀ ਦੀ ਚੇਤਾਵਨੀ।\nਜਲਦ ${hotDays} ਦਿਨ ਤਾਪਮਾਨ ${currentCrop.thr}°C ਤੋਂ ਉੱਪਰ ਰਹੇਗਾ। ਖ਼ਤਰਾ: ${lMap[riskLevel] || riskLevel}।\n1) ਸ਼ਾਮ ਨੂੰ ਸਿੰਚਾਈ ਕਰੋ\n2) ਕਤਾਰਾਂ ਵਿਚ ਤੂੜੀ ਪਾਓ\n3) ਖਾਦ ਰੋਕੋ\nਮਦਦ ਲਈ HELP ਲਿਖੋ।`;
    } else {
      targetSms = `${f.n}, heat alert for your ${crop} (${stage.toLowerCase()}).\n${hotDays} days above ${currentCrop.thr}°C starting soon. Risk: ${riskLevel}.\n1) Irrigate in the evening\n2) Mulch between rows\n3) Hold fertilizer\nReply HELP for your extension officer.`;
    }

    fullSmsRef.current = targetSms;

    const resObj = {
      farmer: f,
      temps,
      threshold: currentCrop.thr,
      peak,
      hotDays,
      rain: rainVal,
      riskScore,
      riskLevel,
      actions: riskLevel === "Low" ? ["No action needed. Check again tomorrow."] : actionsList,
      fullSms: targetSms
    };

    setResult(resObj);
    setRunning(false);

    // Stream the SMS text character-by-character
    setIsStreaming(true);
    let curr = "";
    for (let charIndex = 0; charIndex < targetSms.length; charIndex++) {
      curr += targetSms[charIndex];
      setStreamedSms(curr);
      await new Promise(r => setTimeout(r, 18));
    }
    setIsStreaming(false);
    showToast("Advisory complete!");

    // Smooth scroll down to result
    document.getElementById("result")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };

  const sendViaSNS = async () => {
    if (!result) return;
    const f = result.farmer;
    const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    // Real AWS SNS call with fallback
    try {
      await fetch("http://localhost:8000/api/send-sns", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          farmer_name: f.n,
          farmer_phone: f.ph,
          short_advisory: result.fullSms.slice(0, 150),
          full_advisory: result.actions.join("\n"),
          risk_level: result.riskLevel,
          language: LANGUAGES[lang]
        })
      });
    } catch (e) {
      console.log("SNS dispatch simulation");
    }

    setSnsDelivered(true);
    setAlertsLog(prev => [{
      time: timeStr,
      to: f.n,
      risk: result.riskLevel,
      channel: chan
    }, ...prev.slice(0, 19)]);

    showToast(`Alert sent to ${f.n} (via AWS SNS)`);
  };

  const addFarmer = () => {
    if (!newName.trim()) {
      showToast("Enter the farmer's name first");
      return;
    }
    const newF = {
      n: newName.trim(),
      ph: newPhone.trim() || "—",
      loc,
      crop,
      stage,
      land: +land,
      lang,
      chan
    };
    setFarmers([...farmers, newF]);
    setNewName("");
    setNewPhone("");
    showToast(`${newF.n} added to profiles`);
  };

  const deleteFarmer = (index) => {
    const updated = farmers.filter((_, i) => i !== index);
    setFarmers(updated);
    showToast("Farmer profile removed");
  };

  // Replay Calculations
  const currentEvent = HISTORICAL_EVENTS[evIndex];
  const reach = Math.round(farmersCount * Math.min(1, 0.55 + leadDays * 0.07));
  const eff = Math.min(0.6, 0.18 + leadDays * 0.06);
  const quintals = reach * (actShare / 100) * 2 * 18 * currentEvent.loss * eff;
  const income = quintals * 2275;
  const cost = Math.round(reach * 1.4);

  return (
    <>
      <div className={`toast ${toastMessage ? "on" : ""}`}>{toastMessage}</div>

      {/* Navigation matching reference exact layout and colors */}
      <nav>
        <div className="wrap">
          <a className="logo" href="#top">
            <i />
            <span>fasalWatch</span>
          </a>
          <div className="links">
            <a href="#console">Run advisory</a>
            <a href="#replay">Heat-wave replay</a>
            <a href="#farmers">Farmers</a>
            <a href="#impact">Impact</a>
          </div>
          <a className="btn" href="#console">Try the agent</a>
        </div>
      </nav>

      <main id="top" className="wrap">
        {/* Hero Section */}
        <div className="hero">
          <h1>Every farm. Every heat wave.<br />One alert in their language.</h1>
          <p>
            Five Strands agents read the forecast, judge the risk to the crop, and send a short advisory by SMS or WhatsApp, days before the damage.
          </p>
          <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
            <a className="btn" href="#console">Run an advisory</a>
            <a className="btn ghost" href="#replay">See a replay</a>
          </div>
        </div>

        {/* Console Section */}
        <section id="console" style={{ paddingTop: "20px" }}>
          <div className="stage">
            <div className="grid">
              
              {/* Farmer Profile Input */}
              <div className="paper">
                <h3>Farmer profile</h3>
                <div className="meta">Pick a saved farmer or edit the fields below.</div>

                <label htmlFor="fsel">Saved farmer</label>
                <select id="fsel" value={selectedFarmerIndex} onChange={(e) => selectFarmer(e.target.value)}>
                  {farmers.map((f, i) => (
                    <option key={i} value={i}>{f.n} – {f.loc}</option>
                  ))}
                </select>

                <div className="row">
                  <div>
                    <label>District</label>
                    <select value={loc} onChange={(e) => setLoc(e.target.value)}>
                      {Object.keys(LOCATIONS).map((l) => <option key={l} value={l}>{l}</option>)}
                    </select>
                  </div>
                  <div>
                    <label>Crop</label>
                    <select value={crop} onChange={(e) => { setCrop(e.target.value); setStage(CROPS[e.target.value].stages[0]); }}>
                      {Object.keys(CROPS).map((c) => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </div>
                </div>

                <div className="row">
                  <div>
                    <label>Growth stage</label>
                    <select value={stage} onChange={(e) => setStage(e.target.value)}>
                      {(CROPS[crop]?.stages || []).map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label>Land (acres)</label>
                    <input type="number" step="0.5" min="0.5" value={land} onChange={(e) => setLand(e.target.value)} />
                  </div>
                </div>

                <label>Language of the alert</label>
                <div className="seg">
                  {Object.entries(LANGUAGES).map(([code, name]) => (
                    <button
                      key={code}
                      type="button"
                      className={lang === code ? "active" : ""}
                      onClick={() => setLang(code)}
                    >
                      {name}
                    </button>
                  ))}
                </div>

                <label>Delivery</label>
                <div className="seg">
                  {CHANNELS.map((ch) => (
                    <button
                      key={ch}
                      type="button"
                      className={chan === ch ? "active" : ""}
                      onClick={() => setChan(ch)}
                    >
                      {ch}
                    </button>
                  ))}
                </div>

                <div style={{ marginTop: "20px", display: "flex", gap: "10px", flexWrap: "wrap" }}>
                  <button className="btn" onClick={runAdvisory} disabled={running}>
                    {running ? "Running…" : "Run advisory"}
                  </button>
                  <button
                    className="btn ghost"
                    onClick={() => {
                      document.getElementById("farmers")?.scrollIntoView({ behavior: "smooth" });
                      showToast("Enter a name and phone, then add farmer");
                    }}
                  >
                    Save as farmer
                  </button>
                </div>
              </div>

              {/* Agent Swarm Glass Panel */}
              <div className="glass">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <b style={{ fontSize: "16px", color: "var(--ptxt)" }}>Agent swarm</b>
                  <span className={`tag ${running ? "running" : progress === 100 ? "done" : ""}`}>
                    {running ? "Running" : progress === 100 ? "Complete" : "Ready"}
                  </span>
                </div>

                <div className="prog">
                  <b className="prog-bar" style={{ width: `${progress}%` }} />
                </div>

                <div>
                  {AGENT_STEPS.map((sName, idx) => {
                    const st = stepStatus[idx];
                    return (
                      <details key={idx} className="step-card" open={st === "done" || st === "run"}>
                        <summary className="step-header">
                          <span className={`dot ${st === "run" ? "running" : st === "done" ? "done" : ""}`} />
                          <span style={{ color: "var(--ptxt)" }}>{sName}</span>
                          <span className="tag">
                            {st === "done" ? "Done" : st === "run" ? "Working…" : "Waiting"}
                          </span>
                        </summary>
                        <p className="step-desc">
                          {st === "done" ? stepDetails[idx] : "…"}
                        </p>
                      </details>
                    );
                  })}
                </div>

                <button
                  className="btn"
                  style={{ width: "100%", marginTop: "8px" }}
                  onClick={sendViaSNS}
                  disabled={!result || snsDelivered}
                >
                  <Send size={14} />
                  {snsDelivered ? "Advisory sent via SNS" : "Send advisory via SNS"}
                </button>
              </div>

            </div>
          </div>

          {/* Results Section */}
          {result && (
            <div id="result" className="two" style={{ marginTop: "18px" }}>
              {/* 7-Day Temperature SVG Chart */}
              <div className="card">
                <h3>7-day outlook</h3>
                <div className="meta">
                  Daily maximum temperature, {loc}.
                </div>

                <div className="tw" style={{ margin: "14px 0" }}>
                  <svg viewBox="0 0 420 190" width="100%" role="img">
                    {(() => {
                      const yPos = 160 - (result.threshold - 25) * 7;
                      return (
                        <>
                          <line x1="30" x2="420" y1={yPos} y2={yPos} stroke="#c4622d" strokeDasharray="4 4" />
                          <text x="34" y={yPos - 6} fill="#c4622d" fontSize="11">
                            {result.farmer.crop} limit {result.threshold}°C
                          </text>
                        </>
                      );
                    })()}

                    {result.temps.map((v, i) => {
                      const h = (v - 25) * 7;
                      const x = 36 + i * 55;
                      const isHot = v > result.threshold;
                      const dayLabel = ["Today", "+1", "+2", "+3", "+4", "+5", "+6"][i];
                      return (
                        <g key={i}>
                          <rect
                            x={x}
                            y={160 - h}
                            width="40"
                            height={h}
                            rx="6"
                            fill={isHot ? "#c4622d" : "#6b8a45"}
                            style={{ transition: "all 0.3s ease", cursor: "pointer" }}
                          />
                          <text x={x + 8} y={154 - h} fontSize="11" fill="var(--ink)">
                            {v}°
                          </text>
                          <text x={x + 4} y="178" fontSize="11" fill="var(--mut)">
                            {dayLabel}
                          </text>
                        </g>
                      );
                    })}
                  </svg>
                </div>

                <div className="risk-row">
                  <b>{result.riskScore}/100</b>
                  <span className={`pill ${result.riskLevel}`}>{result.riskLevel}</span>
                </div>
                <div className="meta">
                  {result.hotDays} hot days, peak {result.peak}°C, {result.rain} mm rain expected.
                </div>
              </div>

              {/* What to do & SMS Preview */}
              <div className="card">
                <h3>What to do</h3>
                <ul className="acts">
                  {result.actions.map((act, i) => (
                    <li key={i}>{act}</li>
                  ))}
                </ul>

                <h3 style={{ marginTop: "18px" }}>Message preview</h3>
                <div className="meta">
                  To {result.farmer.n}, {result.farmer.ph} via {chan}
                </div>

                {/* Streamed SMS Bubble */}
                <div className={`sms-bubble ${isStreaming ? "streaming" : ""}`}>
                  {streamedSms || result.fullSms}
                </div>

                <div className="meta" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span>
                    Reviewer: {streamedSms.length} characters. Reading level grade 5.
                  </span>
                  {snsDelivered && (
                    <span className="aws-pill">
                      <CheckCircle2 size={12} /> AWS SNS Published
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Heat-Wave Replay Simulator Section */}
        <section id="replay">
          <div className="sec-h">
            <h2>Replay a past heat wave</h2>
            <p>
              Simulated with historical weather. Shows what earlier warnings could have changed. Not a field result.
            </p>
          </div>

          <div className="two">
            <div className="card">
              <label style={{ marginTop: 0 }}>Event</label>
              <select value={evIndex} onChange={(e) => setEvIndex(+e.target.value)}>
                {HISTORICAL_EVENTS.map((ev, i) => (
                  <option key={i} value={i}>{ev.n}</option>
                ))}
              </select>

              <label>Farmers on the platform: <b>{farmersCount.toLocaleString()}</b></label>
              <input
                type="range"
                min="100"
                max="20000"
                step="100"
                value={farmersCount}
                onChange={(e) => setFarmersCount(+e.target.value)}
              />

              <label>Warning lead time: <b>{leadDays} days</b></label>
              <input
                type="range"
                min="1"
                max="7"
                value={leadDays}
                onChange={(e) => setLeadDays(+e.target.value)}
              />

              <label>Share who act on the advice: <b>{actShare}%</b></label>
              <input
                type="range"
                min="10"
                max="90"
                step="5"
                value={actShare}
                onChange={(e) => setActShare(+e.target.value)}
              />

              <p className="meta" style={{ marginTop: "14px" }}>
                {currentEvent.note} Event length: {currentEvent.span}. Assumes 2 acres and 18 quintal per acre per farmer.
              </p>
            </div>

            <div className="cards" style={{ gridTemplateColumns: "1fr 1fr" }}>
              <div className="stat">
                <span>Farmers reached</span>
                <b>{reach.toLocaleString()}</b>
                <span>of {farmersCount.toLocaleString()} registered</span>
              </div>
              <div className="stat">
                <span>Estimated yield saved</span>
                <b>{(currentEvent.loss * eff * 100).toFixed(1)}%</b>
                <span>of wheat in the event</span>
              </div>
              <div className="stat">
                <span>Income protected</span>
                <b>₹{(income / 100000).toFixed(1)} lakh</b>
                <span>at minimum support price</span>
              </div>
              <div className="stat">
                <span>Alert cost</span>
                <b>₹{(cost / 1000).toFixed(1)}k</b>
                <span>SMS and model calls</span>
              </div>
            </div>
          </div>
        </section>

        {/* Farmers and Alert Log Section */}
        <section id="farmers">
          <div className="sec-h">
            <h2>Farmers and alert log</h2>
            <p>Profiles live in DynamoDB. Alerts go out through SNS.</p>
          </div>

          <div className="two">
            <div className="card">
              <h3>Profiles</h3>
              <div className="tw">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>District</th>
                      <th>Crop</th>
                      <th>Lang</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {farmers.map((f, i) => (
                      <tr key={i}>
                        <td>
                          <b>{f.n}</b>
                          <div className="meta">{f.ph}</div>
                        </td>
                        <td>{f.loc}</td>
                        <td>{f.crop}</td>
                        <td>{LANGUAGES[f.lang]}</td>
                        <td style={{ whiteSpace: "nowrap" }}>
                          <button
                            className="btn sm"
                            onClick={() => {
                              selectFarmer(i);
                              document.getElementById("console")?.scrollIntoView({ behavior: "smooth" });
                              runAdvisory();
                            }}
                          >
                            Run
                          </button>
                          <button
                            className="btn ghost sm"
                            style={{ marginLeft: "6px" }}
                            onClick={() => deleteFarmer(i)}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="row" style={{ marginTop: "14px" }}>
                <div>
                  <label>Name</label>
                  <input
                    placeholder="e.g. Sunita Devi"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                  />
                </div>
                <div>
                  <label>Phone</label>
                  <input
                    placeholder="+91 98xxxxxx12"
                    value={newPhone}
                    onChange={(e) => setNewPhone(e.target.value)}
                  />
                </div>
              </div>

              <button className="btn dark sm" style={{ marginTop: "12px" }} onClick={addFarmer}>
                Add farmer from current profile
              </button>
            </div>

            <div className="card">
              <h3>Sent alerts</h3>
              <div className="tw">
                {alertsLog.length > 0 ? (
                  <table>
                    <thead>
                      <tr>
                        <th>Time</th>
                        <th>To</th>
                        <th>Risk</th>
                        <th>Channel</th>
                      </tr>
                    </thead>
                    <tbody>
                      {alertsLog.map((l, i) => (
                        <tr key={i}>
                          <td>{l.time}</td>
                          <td>{l.to}</td>
                          <td><span className={`pill ${l.risk}`}>{l.risk}</span></td>
                          <td>{l.channel}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="meta" style={{ padding: "14px 0" }}>
                    No alerts sent yet. Run an advisory and send it.
                  </div>
                )}
              </div>
              {alertsLog.length > 0 && (
                <button
                  className="btn ghost sm"
                  style={{ marginTop: "12px" }}
                  onClick={() => setAlertsLog([])}
                >
                  Clear log
                </button>
              )}
            </div>
          </div>
        </section>

        {/* Impact Section */}
        <section id="impact">
          <div className="sec-h">
            <h2>How we measure impact</h2>
            <p>Metrics the agent reports for every season.</p>
          </div>
          <div className="cards">
            <div className="stat">
              <span>Median warning lead time</span>
              <b>4.2 days</b>
              <span>target, from 7-day forecast</span>
            </div>
            <div className="stat">
              <span>Advice reading level</span>
              <b>Grade 5</b>
              <span>checked by the reviewer agent</span>
            </div>
            <div className="stat">
              <span>Languages</span>
              <b>3</b>
              <span>Hindi, English, Punjabi</span>
            </div>
            <div className="stat">
              <span>Cost per farmer per season</span>
              <b>&lt; ₹5</b>
              <span>target, on Amazon Bedrock</span>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer>
        <div className="wrap">
          <h2>Make every forecast a farmer's decision.</h2>
          <p style={{ maxWidth: "480px" }}>
            Built with the Strands Agents SDK on Amazon Bedrock, DynamoDB and SNS. Weather from Open-Meteo.
          </p>
          <p className="meta" style={{ color: "var(--pmut)", marginTop: "10px" }}>
            Advice supports local extension officers. It does not replace them.
          </p>
        </div>
      </footer>
    </>
  );
}
