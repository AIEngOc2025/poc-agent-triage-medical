import { Component, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { Chessground } from 'chessground';
import { Chess } from 'chess.js';
import { ChessAgentService } from '../../services/chess-agent.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements AfterViewInit {
  @ViewChild('boardContainer') boardContainer!: ElementRef;
  
  // Ces variables sont celles qui manquaient dans ton composant
  currentFen: string = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
  aiAnalysis: string = "Posez une question ou jouez un coup pour commencer.";
  userInput: string = "";
  isLoading: boolean = false;
  errorMessage: string = "";

  private game = new Chess();
  private cg: any;

  constructor(private chessAgentService: ChessAgentService) {}

  ngAfterViewInit() {
    this.cg = Chessground(this.boardContainer.nativeElement, {
      fen: this.game.fen(),
      events: { move: (orig: string, dest: string) => this.onMove(orig, dest) }
    });
  }

  onMove(orig: string, dest: string) {
    const move = this.game.move({ from: orig, to: dest, promotion: 'q' });
    if (move) {
      this.currentFen = this.game.fen(); // Mise à jour de la variable pour l'affichage
      this.cg.set({ fen: this.currentFen });
      this.chessAgentService.analyzePosition(this.currentFen).subscribe();
    }
  }

  sendChatMessage() {
    if (!this.userInput.trim()) return;
    this.isLoading = true;
    
    this.chessAgentService.sendChatMessage(this.userInput, this.currentFen).subscribe({
      next: (response: any) => {
        this.aiAnalysis = response.response || "Réponse reçue.";
        this.userInput = "";
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = "Impossible de contacter l'assistant.";
        this.isLoading = false;
      }
    });
  }
}
