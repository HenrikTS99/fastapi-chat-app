let server_url = "http://127.0.0.1:8000";
let ws_url = "ws://127.0.0.1:8000";
let chatContainer;
let name;
let socket;


document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM is loaded');
  chatContainer = document.getElementById("chat-container");
  getMessages();
  name = getName();
  socket = connectWebSocket();
});


function getName() {
  let name = localStorage.getItem("username");
  if (!name || name === "null") {
    name = changeName();
  }
  return name;
}


function changeName() {
  name = prompt("Enter name:");
  if (!name) {
    name = "Anonymous";
  }
  localStorage.setItem("username", name);
  return name;
}

function createChat(data){
  for(let i = 0; i < data.length; i++) {
    createChatBox(data[i].user, data[i].message);
  }
}

function createChatBox(name, message) {
  const chatBoxDiv = document.createElement("div");
  chatBoxDiv.className = name === "System" ? "chat-row system" : "chat-row";

  const nameContainer = document.createElement("div");
  nameContainer.className = "name-container";
  nameContainer.textContent = name + ":";
  
  const messageContainer = document.createElement("div");
  messageContainer.className = "message-container";
  messageContainer.textContent = message;

  chatBoxDiv.append(nameContainer);
  chatBoxDiv.append(messageContainer);
  chatContainer.append(chatBoxDiv);
}


function connectWebSocket() {
  const socket = new WebSocket(ws_url + "/ws");

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("New message:", data);
    createChatBox(data.user, data.message)
  };
  socket.onopen = () => {
    console.log("WebSocket connected");
    socket.send(JSON.stringify({user: name, message: "__joined__"}))
  };
  return socket;
}


function submitMessage() {
  if(!name) {
    alert("Warning! You need a name to send messages. refresh browser.")
    return;
  }
  if(!socket) {
    alert("Error: No websocket is connected.")
    return;
  }
  let messageInput = document.getElementById("message-input");
  let message = messageInput.value;
  if (message === "") { return; }
  messageInput.value = "";
  socket.send(
    JSON.stringify({
      user: name,
      message: message
    })
  )
}


function getMessages() {
  fetch(server_url + "/messages")
    .then(response => {
      if(!response.ok){
        throw new Error("Error, Response status: " + response.status);
      }
      return response.json();
    })
    .then(data => createChat(data))
    .catch(error => console.error(error));
}

// For comparison purposes
async function getMessagesAwait() {
  try{
    const response= await fetch(server_url + "/messages")

    if (!response.ok){
      throw new Error("Could not fetch resource")
    }

    const data = await response.json();
    console.log(data);
  }
  catch(error){
    console.error(error)
  }
}

// No longer used, keeping for reference
function postMessage(name, message) {
  fetch(server_url + "/message", {
    method: "POST",
    headers: {
      'Content-type': 'application/json'
    },
    body: JSON.stringify(
      {
        user: name,
        message: message
      }
    )
  })
}
