let server_url = "http://127.0.0.1:8000" 
let chatContainer;

document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM is loaded');
  chatContainer = document.getElementById("chat-container")
  getMessages();
  console.log("hwdgygad")
});



function createChat(data){
  for(let i = 0; i < data.length; i++) {
    console.log(data[i])
    createChatBox(data[i].user, data[i].message);
    console.log(data[i].user + data[i].message)

  }
}

function createChatBox(name, message) {
  console.log(name + message);
  const chatBoxDiv = document.createElement("div");
  chatBoxDiv.className ="chat-row";

  const nameContainer = document.createElement("div");
  nameContainer.className = "name-container";
  nameContainer.textContent = name;
  
  const messageContainer = document.createElement("div");
  messageContainer.className = "message-container";
  messageContainer.textContent = message;

  chatBoxDiv.append(nameContainer);
  chatBoxDiv.append(messageContainer);
  chatContainer.append(chatBoxDiv);


}


function getMessages() {
  fetch(server_url + "/messages")
    .then(response => {
      if(!response.ok){
        throw new Error("Could not fetch resource");
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
