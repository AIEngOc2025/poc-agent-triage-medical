#!/bin/zsh

# ==============================================================================
# Script d'automatisation et de réparation de l'application Angular Chess FFE
# Standards ZSH & Bonnes pratiques
# ==============================================================================

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "${BLUE}======================================================================${NC}"
echo "${BLUE}   🛠️  RECONSTRUCTION ET CORRECTION AUTOMATIQUE DE L'APPLICATION FFE${NC}"
echo "${BLUE}======================================================================${NC}"

# 1. Correction de src/app/app.component.ts
echo -e "\n${YELLOW}[1/4] Mise à jour de src/app/app.component.ts...${NC}"
cat << 'EOF' > src/app/app.component.ts
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: '<app-dashboard></app-dashboard>',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'ffe-chess-dashboard';
}
EOF
echo -e "${GREEN}✓ src/app/app.component.ts mis à jour (Affichage direct du Dashboard).${NC}"

# 2. Correction de src/app/app.module.ts
echo -e "\n${YELLOW}[2/4] Intégration de FormsModule dans src/app/app.module.ts...${NC}"
cat << 'EOF' > src/app/app.module.ts
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { ChessAgentService } from './services/chess-agent.service';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule
  ],
  providers: [ChessAgentService],
  bootstrap: [AppComponent]
})
export class AppModule { }
EOF
echo -e "${GREEN}✓ src/app/app.module.ts corrigé (Importation de FormsModule validée).${NC}"

# 3. Correction de src/app/services/chess-agent.service.ts
echo -e "\n${YELLOW}[3/4] Alignement des méthodes dans src/app/services/chess-agent.service.ts...${NC}"
mkdir -p src/app/services
cat << 'EOF' > src/app/services/chess-agent.service.ts
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
EOF
echo -e "${GREEN}✓ src/app/services/chess-agent.service.ts mis à jour (analyzePosition et chatWithAgent prêts).${NC}"

# 4. Nettoyage complet des caches Angular pour éviter les résidus
echo -e "\n${YELLOW}[4/4] Purge des caches et des builds Angular obsolètes...${NC}"
rm -rf .angular/
rm -rf out-tsc/
rm -rf dist/
echo -e "${GREEN}✓ Caches Angular purgés avec succès.${NC}"

echo -e "\n${GREEN}======================================================================${NC}"
echo -e "${GREEN}🎉 TOUTES LES CORRECTIONS ONT ÉTÉ APPLIQUÉES AVEC SUCCÈS !${NC}"
echo -e "${GREEN}======================================================================${NC}"
echo -e "${BLUE}Pour lancer l'application, exécute la commande suivante :${NC}"
echo -e "${YELLOW}npm run start${NC}\n"