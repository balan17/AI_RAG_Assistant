function sendQuestion(){

let input = document.getElementById("question")
let q = input.value.trim()

if(q === "") return

let chat = document.getElementById("chatbox")

// show user message
chat.innerHTML += `
<div class="message user">${q}</div>
`

chat.scrollTop = chat.scrollHeight
input.value = ""

function isGreeting(text){
    text = text.toLowerCase().trim()
    return (
        /^hi+$/.test(text) ||
        /^hey+$/.test(text) ||
        /^hello+$/.test(text) ||
        /^hlo+$/.test(text) ||
        /^good\s*(morning|evening|afternoon|night)/.test(text) ||
        text === "wassup" ||
        text === "sup" ||
        text === "howdy"
    )
}

if(isGreeting(q)){

let aiDiv = document.createElement("div")
aiDiv.className = "message ai ai-typing"
chat.appendChild(aiDiv)

let greet = "Hello 👋 I am your Industrial AI Assistant.\nHow can I assist you today?"

let i = 0

let typing = setInterval(()=>{

aiDiv.innerHTML += greet.charAt(i)
i++

chat.scrollTop = chat.scrollHeight

if(i >= greet.length){
clearInterval(typing)
aiDiv.classList.remove("ai-typing")
}

},30)

return
}
// show thinking message
let thinking = document.createElement("div")
thinking.className = "message ai"
thinking.id = "thinking"
chat.appendChild(thinking)
chat.scrollTop = chat.scrollHeight

// Sentences to show one by one
let thinkingLines = [
    "🤖 Thinking...",
    "🔍 Searching knowledge base...",
    "⚙️ Analyzing..."
]

let lineIndex = 0
thinking.innerHTML = thinkingLines[0]

let thinkingInterval = setInterval(() => {
    lineIndex = (lineIndex + 1) % thinkingLines.length
    thinking.style.opacity = "0"
    thinking.style.transition = "opacity 0.3s"

    setTimeout(() => {
        thinking.innerHTML = thinkingLines[lineIndex]
        thinking.style.opacity = "1"
    }, 300)

}, 3500)  // changes every 1.5 seconds
fetch("/ask",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({question:q})
})
.then(async res => {

clearInterval(thinkingInterval)

let t = document.getElementById("thinking")
if(t) t.remove()

let aiDiv = document.createElement("div")
aiDiv.className = "message ai ai-typing"
chat.appendChild(aiDiv)

const reader = res.body.getReader()
const decoder = new TextDecoder()

let aiText = ""

while(true){

const {done,value} = await reader.read()
if(done) break

aiText += decoder.decode(value)

aiDiv.innerHTML = aiText
chat.scrollTop = chat.scrollHeight
}
aiDiv.classList.remove("ai-typing")
})

.catch(err => {
clearInterval(thinkingInterval) 
let t = document.getElementById("thinking")
if(t) t.remove()

chat.innerHTML += `
<div class="message ai">⚠️ AI server error</div>
`

})

}
document.getElementById("question").addEventListener("keypress", function(event){
    if(event.key === "Enter"){
        event.preventDefault()
        sendQuestion()
    }
})