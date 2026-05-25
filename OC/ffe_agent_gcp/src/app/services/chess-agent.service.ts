import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChessAgentService {
  private apiUrl = 'http://localhost:8000/api'; // Port FastAPI par défaut

  constructor(private http: HttpClient) {}

  /**
   * Envoie la position FEN au backend pour analyse Stockfish / FFE
   */
  analyzePosition(fen: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/analyze`, { fen });
  }

  /**
   * Envoie une question ouverte à l'agent LLM
   */
  chatWithAgent(prompt: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/chat`, { prompt });
  }
}
