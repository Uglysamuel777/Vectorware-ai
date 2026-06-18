"use client";
import { useState, useRef, useEffect } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
  imageUrl?: string;
};

const MOODS = ["🧠 Focused", "😄 Casual", "🚀 Hype", "🧘 Calm", "💼 Professional"];
const SUGGESTIONS = [
  "🌐 Design a website for my business",
  "📈 Explain forex trading strategies",
  "🤖 What can AI automation do for my company",
  "📝 Write an executive pitch proposal",
  "🎯 Help me set and track a business goal",
  "🖼️ Generate an image of a futuristic city",
];

// ── GLOWING SPIRAL LOGO ──────────────────────────────────────────────────────
function SpiralLogo({ size = 48, spinning = false }: { size?: number; spinning?: boolean }) {
  return (
    <svg
      width={size} height={size} viewBox="0 0 200 200"
      style={{
        filter: "drop-shadow(0 0 10px #9b59ff) drop-shadow(0 0 20px #bf00ff)",
        animation: spinning
          ? "spin 1.2s linear infinite, glow 1.5s ease-in-out infinite"
          : "glow 4s ease-in-out infinite",
        display: "inline-block",
      }}
    >
      <defs>
        <linearGradient id="spiralGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#bf00ff" />
          <stop offset="50%" stopColor="#9b59ff" />
          <stop offset="100%" stopColor="#00d4ff" />
        </linearGradient>
      </defs>
      <path
        d="M100,100 C100,60 140,40 160,70 C180,100 160,140 130,150 C90,165 50,140 40,100 C25,50 60,15 100,15 C150,15 185,55 185,100 C185,155 140,190 90,185"
        fill="none" stroke="url(#spiralGrad)" strokeWidth="18" strokeLinecap="round"
      />
    </svg>
  );
}

export default function Home() {
  const [userName, setUserName]     = useState<string | null>(null);
  const [nameInput, setNameInput]   = useState("");
  const [messages, setMessages]     = useState<Message[]>([]);
  const [input, setInput]           = useState("");
  const [loading, setLoading]       = useState(false);
  const [mood, setMood]             = useState<string | null>(null);
  const [followups, setFollowups]   = useState<string[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [histories, setHistories]   = useState<{ title: string; messages: Message[] }[]>([]);
  const [memoryFacts, setMemoryFacts] = useState<string[]>([]);
  const [goals, setGoals]           = useState<{ goal: string; steps: string[]; timeline: string }[]>([]);
  const [darkMode, setDarkMode]     = useState(true);
  const [listening, setListening]   = useState(false);
  const [speaking, setSpeaking]     = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const bottomRef   = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, loading]);

  // ── WEB SPEECH RECOGNITION (mic) ──────────────────────────────────────────
  const startListening = () => {
    const SR = (window as unknown as { SpeechRecognition?: typeof SpeechRecognition; webkitSpeechRecognition?: typeof SpeechRecognition }).SpeechRecognition
            || (window as unknown as { webkitSpeechRecognition?: typeof SpeechRecognition }).webkitSpeechRecognition;
    if (!SR) { alert("Your browser doesn't support voice input. Try Chrome."); return; }
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = false;
    rec.onstart  = () => setListening(true);
    rec.onend    = () => setListening(false);
    rec.onerror  = () => setListening(false);
    rec.onresult = (e: SpeechRecognitionEvent) => {
      const transcript = e.results[0][0].transcript;
      setInput(transcript);
      setTimeout(() => handleSend(transcript), 300);
    };
    rec.start();
    recognitionRef.current = rec;
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setListening(false);
  };

  // ── TEXT TO SPEECH ────────────────────────────────────────────────────────
  const speakText = (text: string) => {
    if (!ttsEnabled || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const clean = text.replace(/[*_`#]/g, "").slice(0, 600);
    const utt   = new SpeechSynthesisUtterance(clean);
    utt.rate    = 1.05;
    utt.pitch   = 1;
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(v =>
      v.name.includes("Google") || v.name.includes("Samantha") || v.name.includes("Karen")
    );
    if (preferred) utt.voice = preferred;
    utt.onstart = () => setSpeaking(true);
    utt.onend   = () => setSpeaking(false);
    window.speechSynthesis.speak(utt);
  };

  const stopSpeaking = () => {
    window.speechSynthesis?.cancel();
    setSpeaking(false);
  };

  // ── HELPERS ───────────────────────────────────────────────────────────────
  const extractFacts = (text: string) => {
    const facts: string[] = [];
    const patterns = [
      /I(?:'m| am) (?:a |an )?(.+?)(?:\.|,|$)/gi,
      /I work (?:as |in |at )(.+?)(?:\.|,|$)/gi,
      /my (?:company|business|startup) (?:is |called )?(.+?)(?:\.|,|$)/gi,
    ];
    for (const p of patterns) {
      let m;
      while ((m = p.exec(text)) !== null) {
        const f = m[1].trim();
        if (f.length > 3 && f.length < 80) facts.push(f);
      }
    }
    return facts;
  };

  const isImageRequest = (t: string) =>
    /generate image|draw|create image|show me a picture|make an image|imagine|paint|illustrate|picture of|image of/i.test(t);

  const isGoalRequest = (t: string) =>
    /my goal|set a goal|i want to achieve|help me achieve|track my goal|goal is to|my target/i.test(t);

  const greeting = () => {
    const h = new Date().getHours();
    return h < 12 ? "Good morning" : h < 17 ? "Good afternoon" : "Good evening";
  };

  const saveHistory = (prompt: string, msgs: Message[]) => {
    setHistories(prev => [{ title: prompt.slice(0, 28) + (prompt.length > 28 ? "…" : ""), messages: msgs }, ...prev]);
  };

  // ── SEND MESSAGE ──────────────────────────────────────────────────────────
  const handleSend = async (text?: string) => {
    const prompt = (text || input).trim();
    if (!prompt || loading) return;
    setInput("");
    setFollowups([]);
    stopSpeaking();

    const newMsg: Message = { role: "user", content: prompt };
    const updated = [...messages, newMsg];
    setMessages(updated);

    const facts = extractFacts(prompt);
    if (facts.length) {
      setMemoryFacts(prev => {
        const merged = [...prev];
        facts.forEach(f => { if (!merged.includes(f)) merged.push(f); });
        return merged;
      });
    }

    setLoading(true);

    // IMAGE GENERATION
    if (isImageRequest(prompt)) {
      try {
        const res  = await fetch("/api/image", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ prompt }) });
        const data = await res.json();
        const reply: Message = { role:"assistant", content:`Here's your image, ${userName}! Rendered from your description.`, imageUrl: data.url };
        const final = [...updated, reply];
        setMessages(final);
        speakText(reply.content);
        if (final.length === 2) saveHistory(prompt, final);
      } catch {
        setMessages(prev => [...prev, { role:"assistant", content:"Image generation failed. Try again!" }]);
      }
      setLoading(false);
      return;
    }

    // GOAL MODE
    if (isGoalRequest(prompt)) {
      try {
        const res  = await fetch("/api/chat", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({ messages:[{role:"user",content:prompt}], userName, mood, memoryFacts, goalMode:true }) });
        const data = await res.json();
        if (data.goal) {
          setGoals(prev => [...prev, data.goal]);
          const txt = `Goal saved, ${userName}! Check your sidebar.\n\n🎯 ${data.goal.goal}\n${data.goal.steps.map((s:string)=>`• ${s}`).join("\n")}\n⏱ ${data.goal.timeline}`;
          const final = [...updated, { role:"assistant" as const, content: txt }];
          setMessages(final);
          speakText(`Goal saved! ${data.goal.goal}`);
          if (final.length === 2) saveHistory(prompt, final);
          setLoading(false);
          return;
        }
      } catch {}
    }

    // NORMAL STREAMING CHAT
    try {
      const res = await fetch("/api/chat", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ messages: updated, userName, mood, memoryFacts }),
      });
      if (!res.body) throw new Error("no stream");
      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let fullText  = "";
      setMessages(prev => [...prev, { role:"assistant", content:"" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const lines = decoder.decode(value).split("\n").filter(l => l.startsWith("data: "));
        for (const line of lines) {
          const json = line.replace("data: ","").trim();
          if (json === "[DONE]") break;
          try {
            const delta = JSON.parse(json).choices?.[0]?.delta?.content || "";
            fullText += delta;
            setMessages(prev => { const c=[...prev]; c[c.length-1]={role:"assistant",content:fullText}; return c; });
          } catch {}
        }
      }

      speakText(fullText);

      // Follow-ups
      fetch("/api/chat", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ messages:[], userName, mood, memoryFacts, followupMode:true, lastResponse: fullText }),
      }).then(r=>r.json()).then(d=>{ if(d.followups) setFollowups(d.followups); }).catch(()=>{});

      const finalMsgs = [...updated, { role:"assistant" as const, content: fullText }];
      if (finalMsgs.length === 2) saveHistory(prompt, finalMsgs);

    } catch {
      setMessages(prev => [...prev, { role:"assistant", content:"Something went wrong. Please try again." }]);
    }

    setLoading(false);
  };

  // ── THEME ─────────────────────────────────────────────────────────────────
  const bg       = darkMode ? "linear-gradient(135deg,#150a3a 0%,#05030d 100%)" : "linear-gradient(135deg,#f0ebff 0%,#ffffff 100%)";
  const sidebarBg= darkMode ? "#090615" : "#f5f0ff";
  const text     = darkMode ? "#f3f4f6" : "#1a1a2e";
  const inputBg  = darkMode ? "#160f33" : "#ffffff";
  const msgText  = darkMode ? "#e2e8f0" : "#1f2937";
  const border   = "rgba(147,85,255,0.25)";

  // ── ONBOARDING ────────────────────────────────────────────────────────────
  if (!userName) return (
    <div style={{ minHeight:"100vh", background:bg, display:"flex", alignItems:"center", justifyContent:"center", padding:"20px" }}>
      <style>{`@keyframes glow{0%,100%{filter:drop-shadow(0 0 6px #9b59ff)}50%{filter:drop-shadow(0 0 20px #00d4ff)}} @keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <div style={{ background:"rgba(147,85,255,0.07)", border:`1px solid ${border}`, borderRadius:"24px", padding:"40px 32px", maxWidth:"420px", width:"100%", textAlign:"center" }}>
        <SpiralLogo size={64} />
        <p style={{ color:text, fontSize:"1.5rem", fontWeight:300, margin:"16px 0 0" }}>Welcome to</p>
        <p style={{ fontSize:"1.8rem", fontWeight:700, background:"linear-gradient(90deg,#9b59ff,#bf00ff,#00d4ff)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", margin:"0 0 8px" }}>VectorWare AI</p>
        <p style={{ color:"#9ca3af", marginBottom:"24px" }}>Next-generation AI. What's your name?</p>
        <input value={nameInput} onChange={e=>setNameInput(e.target.value)}
          onKeyDown={e=>e.key==="Enter"&&nameInput.trim()&&setUserName(nameInput.trim())}
          placeholder="Enter your name…"
          style={{ width:"100%", padding:"12px 16px", borderRadius:"14px", border:`1px solid ${border}`, background:inputBg, color:text, fontSize:"1rem", marginBottom:"12px", boxSizing:"border-box", outline:"none" }}
        />
        <button onClick={()=>nameInput.trim()&&setUserName(nameInput.trim())}
          style={{ width:"100%", padding:"12px", borderRadius:"14px", border:"none", background:"linear-gradient(90deg,#9b59ff,#bf00ff)", color:"#fff", fontSize:"1rem", fontWeight:600, cursor:"pointer" }}>
          Let's Go →
        </button>
      </div>
    </div>
  );

  // ── MAIN APP ──────────────────────────────────────────────────────────────
  return (
    <div style={{ minHeight:"100vh", background:bg, fontFamily:"'Inter',sans-serif", display:"flex" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        *{box-sizing:border-box;margin:0;padding:0;}
        body{font-family:'Inter',sans-serif;}
        ::-webkit-scrollbar{width:4px;}
        ::-webkit-scrollbar-thumb{background:rgba(147,85,255,0.3);border-radius:4px;}
        @keyframes glow{0%,100%{filter:drop-shadow(0 0 6px #9b59ff)}50%{filter:drop-shadow(0 0 20px #00d4ff)}}
        @keyframes spin{to{transform:rotate(360deg)}}
        @keyframes bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-8px)}}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
        button{font-family:'Inter',sans-serif;transition:all 0.2s;}
        input{font-family:'Inter',sans-serif;}
      `}</style>

      {/* ── SIDEBAR ── */}
      <div style={{ width:sidebarOpen?"270px":"0", minWidth:sidebarOpen?"270px":"0", overflow:"hidden", transition:"all 0.3s ease", background:sidebarBg, borderRight:`1px solid ${border}`, display:"flex", flexDirection:"column", height:"100vh", position:"sticky", top:0 }}>
        {sidebarOpen && (
          <div style={{ padding:"20px 14px", overflowY:"auto", height:"100%", display:"flex", flexDirection:"column" }}>
            <div style={{ textAlign:"center", marginBottom:"16px" }}>
              <SpiralLogo size={42} />
              <p style={{ color:"#fff", fontWeight:600, margin:"8px 0 0" }}>VectorWare AI</p>
            </div>
            <div style={{ background:"rgba(147,85,255,0.12)", borderRadius:"10px", padding:"6px 10px", textAlign:"center", fontSize:"0.8rem", color:"#d8b4fe", marginBottom:"10px" }}>👤 {userName}</div>

            <SideBtn onClick={()=>{setMessages([]);setFollowups([]);}} label="✨ New Chat" />
            <SideBtn onClick={()=>{setUserName(null);setMessages([]);setMemoryFacts([]);setGoals([]);}} label="🔄 Change Name" />
            <SideBtn onClick={()=>setDarkMode(d=>!d)} label={darkMode?"☀️ Light Mode":"🌙 Dark Mode"} />
            <SideBtn onClick={()=>setTtsEnabled(t=>!t)} label={ttsEnabled?"🔊 Voice: ON":"🔇 Voice: OFF"} active={ttsEnabled} />

            <p style={{ color:"#6b7280", fontSize:"0.68rem", fontWeight:700, letterSpacing:"0.08em", margin:"14px 0 6px" }}>AI TONE</p>
            {MOODS.map(m=>(
              <SideBtn key={m} onClick={()=>setMood(mood===m?null:m)} label={m} active={mood===m} />
            ))}

            {goals.length>0&&<>
              <p style={{ color:"#6b7280", fontSize:"0.68rem", fontWeight:700, letterSpacing:"0.08em", margin:"14px 0 6px" }}>🎯 MY GOALS</p>
              {goals.slice(0,3).map((g,i)=>(
                <div key={i} style={{ background:"rgba(0,212,255,0.05)", border:"1px solid rgba(0,212,255,0.2)", borderRadius:"10px", padding:"8px 10px", marginBottom:"6px", fontSize:"0.75rem", color:msgText }}>
                  <b>{g.goal.slice(0,35)}</b>
                  {g.steps.slice(0,3).map((s,j)=><div key={j} style={{ color:"#a78bfa", marginTop:"2px" }}>• {s}</div>)}
                  <div style={{ color:"#6b7280", marginTop:"4px" }}>⏱ {g.timeline}</div>
                </div>
              ))}
            </>}

            {memoryFacts.length>0&&<>
              <p style={{ color:"#6b7280", fontSize:"0.68rem", fontWeight:700, letterSpacing:"0.08em", margin:"14px 0 6px" }}>🧠 MEMORY</p>
              {memoryFacts.slice(0,5).map((f,i)=>(
                <div key={i} style={{ background:"rgba(0,212,255,0.08)", border:"1px solid rgba(0,212,255,0.2)", borderRadius:"20px", padding:"3px 10px", fontSize:"0.72rem", color:"#00d4ff", marginBottom:"4px" }}>• {f.slice(0,40)}</div>
              ))}
            </>}

            {histories.length>0&&<>
              <p style={{ color:"#6b7280", fontSize:"0.68rem", fontWeight:700, letterSpacing:"0.08em", margin:"14px 0 6px" }}>HISTORY</p>
              {histories.slice(0,8).map((h,i)=>(
                <button key={i} onClick={()=>setMessages(h.messages)}
                  style={{ width:"100%", textAlign:"left", background:"rgba(147,85,255,0.06)", border:`1px solid ${border}`, borderRadius:"8px", padding:"6px 10px", color:text, fontSize:"0.75rem", marginBottom:"4px", cursor:"pointer" }}>
                  {h.title}
                </button>
              ))}
            </>}

            <div style={{ marginTop:"auto", paddingTop:"16px", borderTop:`1px solid ${border}`, fontSize:"0.7rem", color:"#6b7280", textAlign:"center", lineHeight:"1.6" }}>
              <div style={{ color:"#00d4ff", fontWeight:600, marginBottom:"4px" }}>Llama 4 Scout 17B</div>
              Vision · Search · Memory · Image Gen · TTS · Goals<br/>
              <span style={{ color:"#9b59ff" }}>Samuel Frimpong</span> · Cardinal Kofi Nsiah<br/>
              Gabriel Ahwireng · Gideon Ahwireng<br/>
              © 2026 VectorWare Inc.
            </div>
          </div>
        )}
      </div>

      {/* ── MAIN ── */}
      <div style={{ flex:1, display:"flex", flexDirection:"column", height:"100vh", overflow:"hidden" }}>

        {/* Top bar */}
        <div style={{ display:"flex", alignItems:"center", padding:"12px 16px", borderBottom:`1px solid ${border}`, gap:"12px", flexShrink:0, background: darkMode?"rgba(5,3,13,0.8)":"rgba(255,255,255,0.8)", backdropFilter:"blur(10px)" }}>
          <button onClick={()=>setSidebarOpen(o=>!o)}
            style={{ background:"rgba(147,85,255,0.1)", border:`1px solid ${border}`, borderRadius:"10px", padding:"8px 12px", color:text, cursor:"pointer", fontSize:"1.1rem" }}>
            ☰
          </button>
          <SpiralLogo size={28} spinning={loading} />
          <span style={{ fontSize:"1rem", fontWeight:700, background:"linear-gradient(90deg,#9b59ff,#00d4ff)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>VectorWare AI</span>
          {mood&&<span style={{ fontSize:"0.73rem", background:"rgba(147,85,255,0.15)", border:`1px solid ${border}`, borderRadius:"20px", padding:"3px 10px", color:"#d8b4fe" }}>{mood}</span>}
          {speaking&&(
            <button onClick={stopSpeaking} style={{ marginLeft:"auto", background:"rgba(0,212,255,0.1)", border:"1px solid rgba(0,212,255,0.3)", borderRadius:"20px", padding:"4px 12px", color:"#00d4ff", fontSize:"0.75rem", cursor:"pointer", animation:"pulse 1.5s infinite" }}>
              🔊 Speaking… tap to stop
            </button>
          )}
        </div>

        {/* Messages */}
        <div style={{ flex:1, overflowY:"auto", padding:"20px 16px", display:"flex", flexDirection:"column", gap:"16px" }}>

          {messages.length===0&&(
            <div style={{ textAlign:"center", paddingTop:"30px" }}>
              <SpiralLogo size={60} />
              <p style={{ fontSize:"1.9rem", fontWeight:300, color:text, margin:"16px 0 0" }}>{greeting()},</p>
              <p style={{ fontSize:"1.9rem", fontWeight:700, background:"linear-gradient(90deg,#9b59ff,#bf00ff,#00d4ff)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", margin:"0 0 6px" }}>{userName}</p>
              <p style={{ color:"#9ca3af", marginBottom:"24px", fontSize:"0.95rem" }}>How can I help you today?</p>
              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(200px,1fr))", gap:"8px", maxWidth:"520px", margin:"0 auto" }}>
                {SUGGESTIONS.map((s,i)=>(
                  <button key={i} onClick={()=>handleSend(s)}
                    style={{ textAlign:"left", background:"rgba(147,85,255,0.07)", border:`1px solid ${border}`, borderRadius:"12px", padding:"10px 12px", color:text, fontSize:"0.82rem", cursor:"pointer" }}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg,i)=>(
            <div key={i} style={{ display:"flex", justifyContent:msg.role==="user"?"flex-end":"flex-start", gap:"10px", alignItems:"flex-start" }}>
              {msg.role==="assistant"&&<div style={{ flexShrink:0, marginTop:"4px" }}><SpiralLogo size={28} /></div>}
              <div style={{
                maxWidth:"75%", padding:"12px 16px",
                borderRadius:msg.role==="user"?"18px 18px 4px 18px":"18px 18px 18px 4px",
                background:msg.role==="user"?"linear-gradient(135deg,#9b59ff,#bf00ff)":(darkMode?"rgba(255,255,255,0.05)":"rgba(0,0,0,0.04)"),
                border:msg.role==="assistant"?`1px solid ${border}`:"none",
                color:msg.role==="user"?"#fff":msgText,
                fontSize:"0.92rem", lineHeight:"1.75", whiteSpace:"pre-wrap",
              }}>
                {msg.imageUrl&&<img src={msg.imageUrl} alt="generated" style={{ width:"100%", borderRadius:"12px", marginBottom:"8px" }}/>}
                {msg.content}
                {msg.role==="assistant"&&msg.content&&(
                  <button onClick={()=>speakText(msg.content)}
                    style={{ display:"block", marginTop:"8px", background:"transparent", border:"none", color:"#6b7280", fontSize:"0.72rem", cursor:"pointer", padding:0 }}>
                    🔊 Read aloud
                  </button>
                )}
              </div>
              {msg.role==="user"&&<div style={{ fontSize:"1.4rem", flexShrink:0, marginTop:"4px" }}>👤</div>}
            </div>
          ))}

          {loading&&(
            <div style={{ display:"flex", alignItems:"center", gap:"10px" }}>
              <SpiralLogo size={28} spinning />
              <div style={{ display:"flex", gap:"5px" }}>
                {[0,1,2].map(i=>(
                  <div key={i} style={{ width:"8px", height:"8px", borderRadius:"50%", background:"#9b59ff", animation:`bounce 1.2s ${i*0.2}s infinite` }}/>
                ))}
              </div>
            </div>
          )}

          {followups.length>0&&!loading&&(
            <div style={{ display:"flex", flexWrap:"wrap", gap:"8px", marginTop:"4px" }}>
              {followups.map((f,i)=>(
                <button key={i} onClick={()=>handleSend(f)}
                  style={{ background:"rgba(147,85,255,0.1)", border:`1px solid ${border}`, borderRadius:"20px", padding:"6px 14px", fontSize:"0.78rem", color:"#d8b4fe", cursor:"pointer" }}>
                  {f}
                </button>
              ))}
            </div>
          )}

          <div ref={bottomRef}/>
        </div>

        {/* ── INPUT BAR ── */}
        <div style={{ padding:"12px 16px", borderTop:`1px solid ${border}`, flexShrink:0, background:darkMode?"rgba(5,3,13,0.9)":"rgba(255,255,255,0.9)", backdropFilter:"blur(10px)" }}>
          <div style={{ display:"flex", gap:"8px", alignItems:"center" }}>

            {/* Mic button */}
            <button
              onClick={listening?stopListening:startListening}
              title={listening?"Stop listening":"Voice input"}
              style={{
                flexShrink:0, width:"44px", height:"44px", borderRadius:"50%", border:`1px solid ${listening?"#00d4ff":border}`,
                background:listening?"rgba(0,212,255,0.2)":"rgba(147,85,255,0.1)",
                color:listening?"#00d4ff":"#9b59ff", fontSize:"1.1rem", cursor:"pointer",
                animation:listening?"pulse 1s infinite":"none",
              }}>
              {listening?"⏹":"🎙️"}
            </button>

            {/* Text input */}
            <input value={input} onChange={e=>setInput(e.target.value)}
              onKeyDown={e=>e.key==="Enter"&&!e.shiftKey&&handleSend()}
              placeholder={listening?"Listening…":`Ask VectorWare anything, ${userName}…`}
              style={{ flex:1, padding:"12px 18px", borderRadius:"24px", border:`1px solid ${border}`, background:inputBg, color:text, fontSize:"0.95rem", outline:"none" }}
            />

            {/* TTS toggle */}
            <button onClick={()=>setTtsEnabled(t=>!t)} title="Toggle voice replies"
              style={{ flexShrink:0, width:"44px", height:"44px", borderRadius:"50%", border:`1px solid ${ttsEnabled?"rgba(0,212,255,0.4)":border}`, background:ttsEnabled?"rgba(0,212,255,0.1)":"rgba(147,85,255,0.05)", color:ttsEnabled?"#00d4ff":"#6b7280", fontSize:"1rem", cursor:"pointer" }}>
              {ttsEnabled?"🔊":"🔇"}
            </button>

            {/* Send button */}
            <button onClick={()=>handleSend()} disabled={loading||!input.trim()}
              style={{ flexShrink:0, padding:"12px 20px", borderRadius:"20px", border:"none", background:loading||!input.trim()?"#2d1f4a":"linear-gradient(90deg,#9b59ff,#bf00ff)", color: loading||!input.trim()?"#6b7280":"#fff", fontWeight:600, cursor:loading||!input.trim()?"not-allowed":"pointer" }}>
              {loading?"…":"→"}
            </button>
          </div>
          <p style={{ color:"#4b5563", fontSize:"0.67rem", textAlign:"center", margin:"6px 0 0" }}>VectorWare AI · Llama 4 Scout 17B · © 2026 VectorWare Inc.</p>
        </div>
      </div>
    </div>
  );
}

function SideBtn({ onClick, label, active }: { onClick:()=>void; label:string; active?:boolean }) {
  return (
    <button onClick={onClick} style={{
      width:"100%", textAlign:"left", padding:"7px 10px", borderRadius:"10px", marginBottom:"4px",
      background:active?"rgba(147,85,255,0.3)":"rgba(147,85,255,0.08)",
      border:active?"1px solid #9b59ff":"1px solid rgba(147,85,255,0.2)",
      color:active?"#e9d5ff":"#d8b4fe", fontSize:"0.8rem", cursor:"pointer",
    }}>{label}</button>
  );
}
