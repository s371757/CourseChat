import { getAnswer } from 'chatGPT.js';
import { getQuestion } from 'chatGPT.js';

const dummyQuestion = 'Dummy question';
const dummyAnswer = 'Dummy answer';

function logToDatabase(question, answer, pageNumber, pdfId) {
    // Create the data object
    const data = {
        question: question,
        answer: answer,
        page_number: pageNumber,
        pdf_id: pdfId
    };

    // Send a POST request to the server
    fetch('/log_chat_entry', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch((error) => {
        console.error('Error:', error);
    });
}

function handleChatFormSubmit(event) {
    event.preventDefault(); // Prevent the form from submitting normally
    const pageNumber = document.getElementById('pdf-container').getAttribute('pagenumber');
    const pdfId = document.getElementById('pdf-container').getAttribute('pdf_id');
    const messageInput = document.getElementById('message-input');
    const messageText = messageInput.value.trim();
    if (messageText) {
        // Create a new message element
        const messageElement = document.createElement('div');
        messageElement.textContent = messageText;
        messageElement.classList.add('chat-message');
        // Append the message to the chat messages container
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.appendChild(messageElement);
        // Clear the input field
        messageInput.value = '';
        // Make an AJAX request to the Flask endpoint
        const formData = new FormData();
        formData.append('question', messageText);
        formData.append('pdf_id', pdfId);
        formData.append('url', yourUrl);
        formData.append('pageNumber', pageNumber);

         fetch('/ask_url', { // or '/ask_file' if you're sending a file
             method: 'POST',
             body: formData
         })
         .then(response => response.text())
         .then(answer => {
             // Create a new message element for the answer
             const answerElement = document.createElement('div');
             answerElement.textContent = answer;
             answerElement.classList.add('chat-message');
             chatMessages.appendChild(answerElement);
             logToDatabase(messageText, answer, pageNumber, pdfId);
         })
         .catch(error => {
             console.error('Error:', error);
         });
     }
 }


// Attach the event listener to the chat form
const chatForm = document.getElementById('chat-form');
chatForm.addEventListener('submit', handleChatFormSubmit);

