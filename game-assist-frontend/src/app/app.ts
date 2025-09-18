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
  currentMessage = 'https://minecraft.fandom.com';
  isTyping = false;
  private apiBaseUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) {
    this.addMessage('Enter the wiki\'s homepage to create a RAG index of its documents:', false);
  }

  sendMessage() {
    if (!this.currentMessage.trim() || this.isTyping || this.isLoading) return;
    
    const userMessage = this.currentMessage.trim();
    this.addMessage(userMessage, true);
    
    if (!this.selectedFandom) {
      this.setupFandomFromUrl(userMessage);
    } else {
      this.askQuestion(userMessage);
    }
    
    this.currentMessage = '';
  }

  private setupFandomFromUrl(url: string) {
    const fandomName = this.extractFandomName(url);
    if (!fandomName) {
      this.addMessage('Please enter a valid Fandom wiki URL (e.g., https://minecraft.fandom.com)', false);
      return;
    }
    
    this.selectedFandom = fandomName;
    this.isLoading = true;
    this.addMessage(`Currently building/accessing RAG index`, false);
    
    this.http.get(`${this.apiBaseUrl}/gen-rag-database?wiki_name=${encodeURIComponent(fandomName)}`).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        this.addMessage(`RAG index created! What can I help you with?`, false);
      },
      error: () => {
        this.isLoading = false;
        this.addMessage(`Failed to load ${fandomName} wiki data. Please try a different fandom URL.`, false);
        this.selectedFandom = null;
      }
    });
  }

  private extractFandomName(url: string): string | null {
    try {
      // Handle URLs with or without protocol
      let processedUrl = url;
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        processedUrl = 'https://' + url;
      }
      
      const urlObj = new URL(processedUrl);
      const hostname = urlObj.hostname;
      
      // Extract fandom name from URL like "minecraft.fandom.com"
      const match = hostname.match(/^(.+)\.fandom\.com$/);
      if (match) {
        return match[1];
      }
      
      return null;
    } catch {
      return null;
    }
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
    this.addMessage('Enter the wiki\'s homepage to create a RAG index of its documents:', false);
  }

  getPlaceholderText(): string {
    return !this.selectedFandom ? 'Enter a fandom wiki URL (e.g., https://minecraft.fandom.com)' : `Ask about ${this.selectedFandom}...`;
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
