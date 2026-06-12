# Bitget Unified Trading Account, API, MCP et Agent Hub

Version : 1.0  
Date : 2026-06-12  
Statut : Document de référence opérationnelle  
Périmètre : portefeuille test Bitget, sous-comptes, API, MCP, Agent Hub et intégration future dans TradingAgents.

---

## 1. Objectif

Ce document ajoute à l’écosystème TradingAgents les informations nécessaires pour intégrer Bitget de manière contrôlée.

Le but n’est pas encore de déclencher du trading automatique. Le but est de structurer proprement :

1. un portefeuille test Bitget ;
2. des sous-comptes spécialisés ;
3. des clés API séparées par rôle ;
4. une intégration MCP/Agent Hub en mode read-only d’abord ;
5. une future passerelle d’exécution uniquement après validation du risk gate.

---

## 2. Sources de référence

Sources de départ et références importantes :

- Bitget Agent Hub officiel : https://www.bitget.com/fr/activity-hub/agent-hub
- Blog Bitget Agent Hub : https://www.bitget.com/blog/articles/bitget-agent-hub-ai-driven-trading
- Support Bitget Agent Hub Skills Challenge : https://www.bitget.com/support/articles/12560603881617
- GitHub officiel Bitget Agent Hub : https://github.com/Bitget-AI/agent_hub
- Documentation API Bitget : https://www.bitget.com/api-doc/common/intro
- Documentation UTA Bitget : https://www.bitget.com/api-doc/uta/intro
- Guide UTA Quick Start : https://www.bitget.com/api-doc/uta/guide
- Guide UTA Best Practices : https://www.bitget.com/api-doc/uta/best-practices
- Documentation MCP Bitget : https://github.com/Bitget-AI/agent_hub/blob/main/docs/packages/bitget-mcp.md
- Documentation Skill Hub : https://github.com/Bitget-AI/agent_hub/blob/main/docs/skill-hub.md
- Serveur MCP tiers référencé : https://mcpmarket.com/server/bitget-trading
- Package npm mentionné : https://www.npmjs.com/package/bitget-mcp-server

Priorité de fiabilité :

1. Documentation officielle Bitget.
2. GitHub officiel `Bitget-AI/agent_hub`.
3. npm officiel des packages liés au dépôt Bitget.
4. MCP Market et serveurs tiers uniquement comme inspiration, pas comme base de sécurité.

---

## 3. Compte unifié Bitget : logique générale

Le compte unifié Bitget, ou Unified Trading Account / UTA, permet d’utiliser un seul cadre de compte pour le spot et plusieurs produits dérivés.

But principal :

- réduire les transferts entre comptes ;
- mutualiser une partie du risque ;
- améliorer l’efficacité du capital ;
- permettre une gestion plus intégrée des positions, soldes, marges et PnL.

Bitget décrit trois modes UTA :

| Mode | Produits disponibles | Logique |
|---|---|---|
| Isolated margin mode | Spot, USDT-M Futures isolé, USDC-M Futures isolé | Chaque position porte son propre risque. |
| Basic mode | Spot, USDT-M Futures, USDC-M Futures | USDT et USDC peuvent partager une logique de marge selon les produits. |
| Advanced mode | Spot, margin, USDT-M, USDC-M, Coin-M | Plusieurs actifs peuvent servir de marge selon des ratios de collatéral. |

Point important : en Advanced Mode, les actifs des différents produits peuvent être utilisés comme marge partagée, et les profits/pertes peuvent se compenser. C’est puissant, mais cela augmente aussi le risque systémique du portefeuille.

---

## 4. Architecture recommandée pour le portefeuille test

Ne pas connecter l’agent IA directement au compte principal avec toutes les permissions.

Architecture recommandée :

```text
Compte principal Bitget
│
├── Sous-compte 00_readonly_radar
│   ├── API read-only
│   ├── usage : soldes, positions, funding, open interest, historiques
│   └── aucun ordre, aucun transfert, aucun retrait
│
├── Sous-compte 01_demo_agent
│   ├── Demo API Key si disponible
│   ├── usage : simulation, paper trading, tests de stratégie
│   └── aucune exposition réelle
│
├── Sous-compte 02_small_live_test
│   ├── capital limité
│   ├── API trade sans withdraw
│   ├── usage : tests réels très encadrés
│   └── risk gate obligatoire
│
├── Sous-compte 03_market_making_lab
│   ├── optionnel
│   ├── usage : tests carnet d’ordres, spreads, exécution
│   └── limites faibles
│
└── Sous-compte 99_quarantine
    ├── usage : isoler scripts douteux ou tests destructifs
    └── aucune permission critique
```

Règle : chaque sous-compte doit avoir une clé API propre. Pas de clé globale partagée entre agents.

---

## 5. Permissions API recommandées

Bitget indique que chaque UID peut créer jusqu’à 10 ensembles de clés API, avec permissions read et write. Les sous-comptes peuvent gérer leurs propres API Keys si le compte principal leur active cette permission.

Permissions UTA pertinentes :

| Permission | Usage | Recommandation |
|---|---|---|
| Unified account trade, read-only | Lire informations de trading | Autorisé pour radar et dashboard. |
| Unified account trade, read and write | Placer/annuler des ordres | Interdit en V0.1, réservé future exécution validée. |
| Unified account management, read-only | Lire informations de compte | Autorisé pour dashboard portefeuille. |
| Unified account management, read and write | Modifier paramètres, leverage, holding mode | Interdit par défaut. À isoler dans un sous-compte test. |
| Withdraw | Retraits | Toujours interdit pour agents IA. |
| Transfer | Transferts internes | Interdit au début. Autoriser uniquement via procédure humaine. |

Configuration minimale recommandée pour TradingAgents V0.1 :

```text
BITGET_API_KEY_READONLY
BITGET_SECRET_KEY_READONLY
BITGET_PASSPHRASE_READONLY
BITGET_ACCOUNT_SCOPE=read_only
BITGET_MCP_MODE=read_only
```

À ne pas mettre dans GitHub. Stockage local uniquement :

- `/root/TradingAgents/.env` sur VPS ;
- `.env` local Windows ;
- secret manager plus tard.

---

## 6. API Bitget UTA utiles

### 6.1 Authentification

Les requêtes REST privées doivent contenir :

- `ACCESS-KEY`
- `ACCESS-SIGN`
- `ACCESS-TIMESTAMP`
- `ACCESS-PASSPHRASE`
- `Content-Type: application/json`
- `locale`

Domaine REST principal :

```text
https://api.bitget.com
```

WebSocket public :

```text
wss://ws.bitget.com/v3/ws/public
```

WebSocket privé :

```text
wss://ws.bitget.com/v3/ws/private
```

Demo trading :

- REST : ajouter header `paptrading: 1`
- WebSocket public demo : `wss://wspap.bitget.com/v3/ws/public`
- WebSocket privé demo : `wss://wspap.bitget.com/v3/ws/private`

### 6.2 Compte et actifs

Endpoint UTA pour les actifs :

```text
GET /api/v3/account/assets
```

Utilité :

- récupérer l’equity globale ;
- récupérer l’equity USDT/BTC ;
- récupérer les balances par coin ;
- lire le PnL non réalisé ;
- lire margin ratio, initial margin, maintenance margin.

Usage dans TradingAgents :

- dashboard portefeuille ;
- surveillance du risque ;
- vérification que le sous-compte test ne dépasse pas les limites ;
- alerte Telegram si equity baisse ou si margin ratio augmente.

### 6.3 Paramètres de compte

Endpoint cité dans les bonnes pratiques :

```text
GET /api/v3/account/settings
```

Utilité :

- lire le mode de compte ;
- lire le mode de position ;
- lire le mode d’actif ;
- lire les paramètres associés.

### 6.4 Leverage et holding mode

Endpoints cités :

```text
POST /api/v3/account/set-leverage
POST /api/v3/account/set-hold-mode
```

Statut recommandé : désactivé pour les agents en V0.1/V0.2.

Ces endpoints doivent être placés derrière un **Risk Gate** et une confirmation explicite si un jour ils sont utilisés.

### 6.5 Ordres

Endpoint UTA pour placer un ordre :

```text
POST /api/v3/trade/place-order
```

Bitget supporte Spot, Margin, USDT Futures, Coin Futures et USDC Futures via ce endpoint selon le champ `category`.

Champs importants :

- `category`
- `symbol`
- `qty`
- `price`
- `side`
- `orderType`
- `timeInForce`
- `posSide`
- `reduceOnly`
- `clientOid`

Règle TradingAgents : ne pas intégrer cet endpoint dans le radar read-only. À documenter uniquement pour la future passerelle d’exécution.

---

## 7. Risques spécifiques du compte unifié

Le compte unifié améliore l’efficacité du capital, mais il rend le système plus interconnecté.

Risques :

1. Un mauvais paramètre de leverage peut affecter plusieurs positions.
2. Une perte sur futures peut consommer la marge disponible liée à d’autres actifs.
3. En Advanced Mode, la logique multi-collatéral augmente la complexité du risk monitoring.
4. Les agents peuvent mal interpréter `available`, `equity`, `locked`, `debt`, `unrealizedPnl`.
5. Les transferts internes ou modifications de leverage doivent rester humains au départ.

Conséquence architecturale : utiliser des sous-comptes séparés et des permissions minimales.

---

## 8. MCP Bitget officiel

Le dépôt officiel `Bitget-AI/agent_hub` présente `bitget-mcp-server` comme serveur MCP officiel Bitget.

Fonction : connecter Claude Code, Cursor, Codex, OpenClaw, VS Code Copilot, Windsurf et autres clients MCP à Bitget.

Commande générique :

```bash
npx -y bitget-mcp-server --modules all
```

Mode recommandé pour TradingAgents au début :

```bash
npx -y bitget-mcp-server --modules spot,futures,account --read-only
```

Modules disponibles selon documentation :

| Module | Usage |
|---|---|
| spot | Données et opérations spot |
| futures | Données et opérations futures |
| account | Soldes, balances, comptes |
| margin | Margin trading |
| copytrading | Copy trading |
| convert | Convert |
| earn | Earn |
| p2p | P2P |
| broker | Broker / sous-comptes selon droits |

Le preset par défaut `spot + futures + account` reste adapté car il limite le nombre d’outils exposés aux agents.

---

## 9. Configuration MCP recommandée

### 9.1 Claude Code

```bash
claude mcp add -s user \
  --env BITGET_API_KEY=your-api-key \
  --env BITGET_SECRET_KEY=your-secret-key \
  --env BITGET_PASSPHRASE=your-passphrase \
  bitget \
  -- npx -y bitget-mcp-server --modules spot,futures,account --read-only
```

### 9.2 Cursor

`.cursor/mcp.json` :

```json
{
  "mcpServers": {
    "bitget": {
      "command": "npx",
      "args": ["-y", "bitget-mcp-server", "--modules", "spot,futures,account", "--read-only"],
      "env": {
        "BITGET_API_KEY": "your-api-key",
        "BITGET_SECRET_KEY": "your-secret-key",
        "BITGET_PASSPHRASE": "your-passphrase"
      }
    }
  }
}
```

### 9.3 VS Code Copilot MCP

`.vscode/mcp.json` :

```json
{
  "servers": {
    "bitget": {
      "command": "npx",
      "args": ["-y", "bitget-mcp-server", "--modules", "spot,futures,account", "--read-only"],
      "env": {
        "BITGET_API_KEY": "your-api-key",
        "BITGET_SECRET_KEY": "your-secret-key",
        "BITGET_PASSPHRASE": "your-passphrase"
      }
    }
  }
}
```

### 9.4 Codex

`~/.codex/config.toml` ou `codex.toml` :

```toml
[[mcp_servers]]
name = "bitget"
command = "npx"
args = ["-y", "bitget-mcp-server", "--modules", "spot,futures,account", "--read-only"]

[mcp_servers.env]
BITGET_API_KEY = "your-api-key"
BITGET_SECRET_KEY = "your-secret-key"
BITGET_PASSPHRASE = "your-passphrase"
```

---

## 10. Bitget Agent Hub et Skills officielles

Bitget Agent Hub propose deux axes d’intégration :

1. **MCP Server** pour les assistants compatibles MCP.
2. **CLI `bgc` + Skills** pour les agents shell comme Claude Code ou OpenClaw.

Commande QuickStart officielle mentionnée :

```bash
npx bitget-hub upgrade-all --target claude
```

Déploiement vers plusieurs outils :

```bash
npx bitget-hub install --target claude,codex
npx bitget-hub install --target all
```

Packages mentionnés dans le dépôt officiel :

| Package | Usage |
|---|---|
| `bitget-client` | CLI `bgc`, accès shell aux outils Bitget |
| `bitget-skill` | Skill trading utilisant `bgc` comme pont API |
| `bitget-skill-hub` | Skills d’analyse de marché |
| `bitget-mcp-server` | Serveur MCP officiel |

Skills d’analyse disponibles :

| Skill | Usage |
|---|---|
| `macro-analyst` | Analyse macro, Fed, DXY, Nasdaq, Gold, VIX, corrélations BTC |
| `market-intel` | Intelligence on-chain, institutionnelle, ETF, whales, DeFi TVL |
| `news-briefing` | News aggregation et synthèse narrative |
| `sentiment-analyst` | Sentiment, positioning, funding, long/short ratios |
| `technical-analysis` | Analyse technique, indicateurs, signaux |

Positionnement : ces skills sont utiles pour produire des analyses, pas pour autoriser un agent à trader directement.

---

## 11. Serveurs MCP tiers

Le serveur listé sur MCP Market indique des capacités de market data, paper trading, spot, USDT futures, balances, positions, leverage et opérations d’ordre.

Position dans TradingAgents :

- utilisable comme source d’inspiration ;
- ne pas lui confier de clés réelles sans audit ;
- préférer le dépôt officiel Bitget-AI/agent_hub ;
- vérifier tout serveur tiers avant usage : code source, dépendances, permissions, logs, exfiltration potentielle.

---

## 12. Architecture d’intégration dans TradingAgents

Architecture cible :

```text
Bitget API / MCP / Agent Hub
          │
          ▼
Bitget Connector Layer
          │
          ├── read_only_account_snapshot
          ├── market_data_snapshot
          ├── positions_snapshot
          ├── funding_snapshot
          ├── open_orders_snapshot
          └── execution_gateway future, désactivé par défaut
          │
          ▼
SQLite / PostgreSQL
          │
          ▼
Terminal Dashboard + Telegram Alerts
          │
          ▼
Risk Gate future
          │
          ▼
Execution Layer future, sous-compte test uniquement
```

À développer dans cet ordre :

1. `bitget_readonly_client.py`
2. `collectors/bitget_account.py`
3. `collectors/bitget_market.py`
4. `collectors/bitget_positions.py`
5. `terminal_dashboard.py`
6. `bitget_mcp_readonly_config.md`
7. seulement ensuite : `execution_gateway.py` en mode simulation.

---

## 13. Variables d’environnement proposées

```env
# Bitget read-only API for test portfolio
BITGET_API_KEY_READONLY=
BITGET_SECRET_KEY_READONLY=
BITGET_PASSPHRASE_READONLY=
BITGET_API_BASE_URL=https://api.bitget.com
BITGET_ACCOUNT_MODE=UTA
BITGET_SUBACCOUNT_LABEL=00_readonly_radar
BITGET_MCP_MODULES=spot,futures,account
BITGET_MCP_READ_ONLY=true

# Demo trading only
BITGET_DEMO_API_KEY=
BITGET_DEMO_SECRET_KEY=
BITGET_DEMO_PASSPHRASE=
BITGET_DEMO_MODE=true
BITGET_PAPER_TRADING_HEADER=1

# Hard safety flags
TRADING_EXECUTION_ENABLED=false
ALLOW_WITHDRAW=false
ALLOW_TRANSFER=false
ALLOW_LEVERAGE_CHANGE=false
ALLOW_LIVE_ORDERS=false
```

---

## 14. Gouvernance de sécurité

Règles non négociables :

1. Pas de clé API dans GitHub.
2. Pas de permission withdraw pour IA.
3. Pas de permission transfer au début.
4. Pas de write permission sur compte principal.
5. Un sous-compte par agent ou stratégie.
6. Read-only tant que le radar n’est pas stabilisé.
7. Demo API avant toute exécution réelle.
8. Si live test : capital limité, sous-compte séparé, taille minimale.
9. Confirmation humaine pour toute action destructive.
10. Journalisation obligatoire de toute action API.

---

## 15. Prompt complémentaire pour Claude / Antigravity

```text
Lis docs/bitget-unified-account-agent-hub.md.

Objectif : préparer l’intégration Bitget dans TradingAgents sans trading automatique.

Tâches :
1. Créer un connecteur Bitget read-only compatible UTA.
2. Lire les variables d’environnement BITGET_API_KEY_READONLY, BITGET_SECRET_KEY_READONLY, BITGET_PASSPHRASE_READONLY.
3. Implémenter uniquement les appels de lecture : account assets, account settings, market data, positions, open orders.
4. Ne jamais placer d’ordre.
5. Ne jamais modifier le leverage.
6. Ne jamais transférer ni retirer de fonds.
7. Ajouter un dashboard terminal affichant equity, available, debt, unrealizedPnL, margin ratio, positions et alertes.
8. Ajouter un mode demo/paper trading séparé.
9. Préparer une configuration MCP read-only avec bitget-mcp-server --modules spot,futures,account --read-only.
10. Ajouter des tests avec données simulées.

Résultat attendu : un module Bitget read-only sûr, utilisable pour surveiller le portefeuille test et préparer l’étape suivante.
```

---

## 16. Décision opérationnelle

Pour l’écosystème TradingAgents, Bitget doit entrer en trois phases :

### Phase A — Observation

- Read-only API.
- UTA account snapshot.
- Positions snapshot.
- Funding/open interest.
- Telegram alerts.
- Dashboard terminal.

### Phase B — Simulation

- Demo API Key.
- Paper trading.
- Backtest simple.
- Journalisation complète.
- Aucun ordre réel.

### Phase C — Live sous-compte test

- Sous-compte séparé.
- Capital limité.
- Trade permission uniquement sur ce sous-compte.
- `ALLOW_LIVE_ORDERS=true` requis.
- Risk Gate obligatoire.
- Kill switch obligatoire.

---

## 17. Positionnement final

Le compte unifié Bitget est puissant pour une architecture multi-produits, mais il ne faut pas brancher un agent IA directement sur un compte principal avec droits d’écriture.

La bonne structure est :

```text
Compte principal = coffre et supervision
Sous-comptes = laboratoires isolés
API read-only = observation
Demo API = simulation
Write API = uniquement plus tard, sous-compte limité, risk gate actif
MCP = interface d’agent, en read-only d’abord
Skills = analyse et assistance, pas autorisation de trader
```
