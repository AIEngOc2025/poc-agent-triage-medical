# Test Technique - Développeur IA - S'investir

## 🚀 Projet : Simulateur d'Investissement Crypto

### Choix Techniques
- **Framework** : Next.js 14 (App Router)
- **Styling** : Tailwind CSS (Respect de la charte graphique S'investir)
- **Logique** : TypeScript pour un calcul d'intérêts composés robuste
- **Déploiement** : Vercel

### Justification des choix
J'ai opté pour une approche modulaire où la logique de calcul est isolée de la vue. 
L'interface a été conçue pour être "embeddable" avec un minimum de dépendances externes.

### Améliorations suggérées (Bonus)
1. Ajout d'un graphique d'évolution via Recharts.
2. Intégration d'un "IA Insight" : Un petit encart analysant le résultat pour donner un conseil stratégique.
3. Export PDF du plan d'investissement.

## Installation
```bash
npm install
npm run dev
```
