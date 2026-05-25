import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ChessAgentService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  analyzePosition(fen: string): Observable<any> {
    console.log("Appel API Analyse:", fen);
    return this.http.post('http://127.0.0.1:8000/api/v1/analyze-position', { fen: fen });
  }

  sendChatMessage(message: string, fen: string): Observable<any> {
    console.log("Appel API Chat:", message);
    // On envoie 'prompt' car c'est ce que ton main.py attend dans ChatRequest
    return this.http.post('http://127.0.0.1:8000/api/v1/chat', { prompt: message });
  }
} 
