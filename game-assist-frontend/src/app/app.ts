import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  title = 'game-assist-frontend';
  selectedFandom: string | null = null;
  isLoading = false;
  messages: Message[] = [];
  currentMessage = 'minecraft';
  isTyping = false;
  private apiBaseUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) {
    this.addMessage('Type a fandom\'s name to generate a RAG context for it', false);
  }

  sendMessage() {
    if (!this.currentMessage.trim() || this.isTyping || this.isLoading) return;
    
    const userMessage = this.currentMessage.trim();
    this.addMessage(userMessage, true);
    
    if (!this.selectedFandom) {
      this.setupFandom(userMessage);
    } else {
      this.askQuestion(userMessage);
    }
    
    this.currentMessage = '';
  }

  private setupFandom(fandomName: string) {
    this.selectedFandom = fandomName;
    this.isLoading = true;
    this.addMessage(`Setting up ${fandomName} wiki database...`, false);
    
    this.http.get(`${this.apiBaseUrl}/gen-rag-database?wiki_name=${encodeURIComponent(fandomName)}`).subscribe({
      next: () => {
        this.isLoading = false;
        this.addMessage(`${fandomName} wiki is ready! Ask me anything about ${fandomName}.`, false);
      },
      error: () => {
        this.isLoading = false;
        this.addMessage(`Failed to load ${fandomName} wiki data. Please try a different fandom name.`, false);
        this.selectedFandom = null;
      }
    });
  }

  private askQuestion(question: string) {
    this.isTyping = true;
    this.http.get(`${this.apiBaseUrl}/search-wiki?wiki_name=${encodeURIComponent(this.selectedFandom!)}&query=${encodeURIComponent(question)}`).subscribe({
      next: (response: any) => {
        this.isTyping = false;
        this.addMessage(response.answer, false);
      },
      error: () => {
        this.isTyping = false;
        this.addMessage('Error processing your question. Please try again.', false);
      }
    });
  }

  addMessage(text: string, isUser: boolean) {
    this.messages.push({ text, isUser, timestamp: new Date() });
    setTimeout(() => {
      const messagesContainer = document.querySelector('.chat-messages');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 100);
  }

  resetChat() {
    this.selectedFandom = null;
    this.messages = [];
    this.currentMessage = '';
    this.isTyping = false;
    this.isLoading = false;
    this.addMessage('Type a fandom\'s name to generate a RAG context for it', false);
  }

  getPlaceholderText(): string {
    return !this.selectedFandom ? 'Enter a fandom name (e.g., Minecraft, Pokemon, etc.)' : `Ask about ${this.selectedFandom}...`;
  }

  formatTime(date: Date): string {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
}
