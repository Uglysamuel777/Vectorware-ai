import { NextRequest } from "next/server";

const MOODS: Record<string, string> = {
  "🧠 Focused": "Be concise, analytical and direct. No fluff.",
  "😄 Casual": "Be warm, friendly and conversational. Light humour welcome.",
  "🚀 Hype": "Be energetic, bold and motivational. Big vision energy.",
  "🧘 Calm": "Be gentle, measured and thoughtful. Steady tone.",
  "💼 Professional": "Be formal, precise and business-ready.",
};

export async function POST(req: NextRequest) {
  const { messages, userName, mood, memoryFacts, followupMode, lastResponse, goalMode } = await req.json();

  const GROQ_API_KEY = process.env.GROQ_API_KEY;

  // ── FOLLOW-UP CHIPS MODE ──
  if (followupMode) {
    const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${GROQ_API_KEY}` },
      body: JSON.stringify({
        model: "meta-llama/llama-4-scout-17b-16e-instruct",
        max_tokens: 150,
        messages: [
          { role: "system", content: "Generate exactly 3 short follow-up questions (max 7 words each) based on the AI response. Return ONLY a JSON array of 3 strings, nothing else." },
          { role: "user", content: `AI just said: ${lastResponse?.slice(0, 400)}` },
        ],
      }),
    });
    const data = await res.json();
    try {
      let text = data.choices[0].message.content.trim();
      if (text.startsWith("```")) text = text.replace(/```[a-z]*/g, "").replace(/```/g, "").trim();
      const followups = JSON.parse(text);
      return Response.json({ followups });
    } catch {
      return Response.json({ followups: [] });
    }
  }

  // ── GOAL MODE ──
  if (goalMode) {
    const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${GROQ_API_KEY}` },
      body: JSON.stringify({
        model: "meta-llama/llama-4-scout-17b-16e-instruct",
        max_tokens: 400,
        messages: [
          { role: "system", content: `Create a goal plan. Return ONLY a JSON object with keys: "goal" (string), "steps" (array of 5 short strings), "timeline" (string). No extra text.` },
          { role: "user", content: messages[0]?.content || "" },
        ],
      }),
    });
    const data = await res.json();
    try {
      let text = data.choices[0].message.content.trim();
      if (text.startsWith("```")) text = text.replace(/```[a-z]*/g, "").replace(/```/g, "").trim();
      const goal = JSON.parse(text);
      return Response.json({ goal });
    } catch {
      return Response.json({ goal: null });
    }
  }

  // ── NORMAL STREAMING CHAT ──
  const memCtx = memoryFacts?.length
    ? `\n\nWhat you know about ${userName}: ${memoryFacts.join(", ")}`
    : "";
  const moodCtx = mood && MOODS[mood] ? `\n\nTone: ${MOODS[mood]}` : "";
  const system = `You are VectorWare AI, a highly intelligent, professional and friendly AI assistant built by VectorWare Inc. The user's name is ${userName}. Address them by name naturally. Be concise, insightful, and professional.${memCtx}${moodCtx}\n\nDetect the language the user writes in and always reply in that same language.`;

  const groqMessages = [
    { role: "system", content: system },
    ...messages.map((m: { role: string; content: string }) => ({ role: m.role, content: typeof m.content === "string" ? m.content : m.content })),
  ];

  const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${GROQ_API_KEY}` },
    body: JSON.stringify({
      model: "meta-llama/llama-4-scout-17b-16e-instruct",
      max_tokens: 2048,
      stream: true,
      messages: groqMessages,
    }),
  });

  return new Response(res.body, {
    headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" },
  });
}
