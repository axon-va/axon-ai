
import os
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Axon.ai</title>
<style>
body{margin:0;background:#10121a;color:#f4f5fa;font-family:Arial,sans-serif}
main{max-width:760px;margin:auto;padding:24px}
h1{color:#85e5ff;text-align:center}
#chat{height:60vh;overflow-y:auto;background:#191d29;border-radius:16px;padding:16px}
.msg{padding:12px 15px;margin:10px 0;border-radius:12px;white-space:pre-wrap;overflow-wrap:anywhere}
.user{background:#283e59;margin-left:35px}
.bot{background:#292d3d;margin-right:35px}
form{display:flex;gap:8px;margin-top:14px}
input{flex:1;min-width:0;padding:14px;border-radius:10px;border:1px solid #41485b;background:#191d29;color:white}
button{padding:12px 18px;border:0;border-radius:10px;background:#76dcf5;color:#10121a;font-weight:bold;cursor:pointer}
#status{text-align:center;color:#a9b2c8;font-size:13px;margin:12px}
</style>
</head>
<body>
<main>
<h1>Axon.ai</h1>
<div id="chat"><div class="msg bot">Hi! I'm Axon.ai. What would you like to talk about?</div></div>
<div id="status">AI Conversation Assistant</div>
<form id="form">
<input id="message" placeholder="Message Axon.ai..." autocomplete="off" required>
<button id="send">Send</button>
</form>
</main>
<script>
const form=document.getElementById('form');
const input=document.getElementById('message');
const chat=document.getElementById('chat');
const status=document.getElementById('status');

form.addEventListener('submit',async e=>{
 e.preventDefault();
 const message=input.value.trim();
 if(!message)return;
 addMessage(message,'user');
 input.value='';
 input.disabled=true;
 document.getElementById('send').disabled=true;
 status.textContent='Axon.ai is thinking...';
 try{
  const response=await fetch('/chat',{
   method:'POST',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({message})
  });
  const data=await response.json();
  if(!response.ok)throw new Error(data.error||'Request failed');
  addMessage(data.reply,'bot');
 }catch(err){
  addMessage('Sorry, something went wrong: '+err.message,'bot');
 }finally{
  input.disabled=false;
  document.getElementById('send').disabled=false;
  status.textContent='AI Conversation Assistant';
  input.focus();
 }
});
function addMessage(text,role){
 const div=document.createElement('div');
 div.className='msg '+role;
 div.textContent=text;
 chat.appendChild(div);
 chat.scrollTop=chat.scrollHeight;
}
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(HTML)

@app.post("/chat")
def chat():
    if not client:
        return jsonify(error="GROQ_API_KEY is not configured on the server."), 500

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify(error="Please enter a message."), 400

    if len(message) > 4000:
        return jsonify(error="Message is too long (maximum 4000 characters)."), 400

    try:
        result = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Axon.ai, a friendly and helpful AI assistant. "
                        "Reply in the language the user uses, including Roman Urdu. "
                        "Be clear, useful, and honest."
                    )
                },
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        reply = result.choices[0].message.content or "I couldn't generate a reply."
        return jsonify(reply=reply)
    except Exception:
        app.logger.exception("Groq API request failed")
        return jsonify(error="AI response failed. Check the API key and Groq model settings."), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
