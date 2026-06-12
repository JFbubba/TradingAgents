# Cartographie des flux d'information trading

Objectif : construire un radar d'information multi-plateformes pour capter les annonces officielles, listings, delistings, maintenances, incidents, changements API, restrictions régionales, signaux communautaires et informations administratives utiles à une stratégie de trading algorithmique.

Cette documentation doit servir de cahier des charges pour un collecteur n8n, Python, Node.js ou agent IA.

---

## 1. Priorité de fiabilité

Ordre de confiance recommandé :

1. Pages officielles d'annonces des exchanges
2. Status pages officielles
3. API officielles, changelogs et WebSocket announcements
4. Canaux Telegram/Discord officiels vérifiés
5. Comptes X/Twitter officiels vérifiés
6. Agrégateurs externes reconnus
7. Communautés publiques Reddit, Telegram, Discord, Binance Square, forums
8. Rumeurs non confirmées

Règle stricte : aucune exécution automatique de trade sur une source communautaire seule. Une source faible peut déclencher une surveillance, pas une position.

---

## 2. Sources officielles exchange

| Exchange | Source | Type d'information | Priorité |
|---|---|---|---|
| Binance | https://www.binance.com/en/support/announcement | Annonces globales, listings, campagnes, produits | Haute |
| Binance | https://www.binance.com/en/support/announcement/list/161 | Delistings | Critique |
| Binance | https://www.binance.com/en/square/news/all | News, Square, contenu semi-officiel | Moyenne |
| Bitget | https://www.bitget.com/support/announcement-center | Annonces globales | Haute |
| Bitget | https://www.bitget.com/support/categories/360002621832 | Support, annonces, catégories | Haute |
| Bybit | https://announcements.bybit.com/en/ | Annonces globales | Haute |
| Bybit | https://announcements.bybit.com/en/?category=delistings | Delistings | Critique |
| OKX | https://www.okx.com/help/section/announcements-latest-announcements | Annonces globales | Haute |
| OKX | https://www.okx.com/help/section/announcements-delistings | Delistings | Critique |
| MEXC | https://www.mexc.com/announcements | Annonces globales | Haute |
| MEXC | https://www.mexc.com/announcements/delistings | Delistings | Critique |
| KuCoin | https://www.kucoin.com/announcement | Annonces globales | Haute |
| KuCoin | https://www.kucoin.com/announcement?category=delisting | Delistings | Critique |
| Gate.io | https://www.gate.com/announcements | Annonces globales | Haute |
| Gate.io | https://www.gate.com/announcements/delisted | Delistings | Critique |
| HTX / Huobi | https://www.htx.com/en-us/support/list/64971881385864/ | Delistings et annonces importantes | Haute |
| Kraken | https://support.kraken.com/sections/delistings | Delistings | Critique |
| Kraken | https://status.kraken.com/ | Incidents, maintenance, API status | Critique |
| Coinbase | https://www.coinbase.com/listings | Listings | Haute |
| Coinbase | https://status.exchange.coinbase.com/ | Exchange status | Critique |
| Coinbase | https://help.coinbase.com/en/coinbase/trading-and-funding/advanced-trade/delisted-assets | Actifs delistés | Haute |
| Crypto.com | https://crypto.com/exchange/announcements/list | Listings, delistings, annonces exchange | Haute |
| Bitfinex | https://www.bitfinex.com/posts/ | Annonces exchange | Moyenne |
| Deribit | https://support.deribit.com/hc/en-us | Support et annonces options/futures | Haute |

---

## 3. Sources API, changelog et infrastructure

| Source | URL | Utilité |
|---|---|---|
| Binance Spot API Docs | https://developers.binance.com/docs/binance-spot-api-docs | REST, WebSocket, limites, changements techniques |
| Binance Derivatives Changelog | https://developers.binance.com/docs/derivatives/change-log | Futures, WebSocket trading, endpoints, rate limits |
| Binance API Telegram | https://t.me/binance_api_announcements | Annonces API officielles |
| Bybit API Changelog | https://bybit-exchange.github.io/docs/changelog/v5 | Changelog V5, endpoints, orderbook, market data |
| Bybit API Telegram | https://t.me/Bybit_API_Announcements | Annonces API et changements techniques |
| OKX API Docs | https://www.okx.com/docs-v5/en/ | REST/WebSocket trading, market data, account, funding |
| Deribit API Docs | https://docs.deribit.com/ | Options/futures, WebSocket, subscriptions |
| Deribit WebSocket announcements | https://docs.deribit.com/subscriptions/announcements/announcements | Canal natif annonces/maintenance/incidents |
| CCXT | https://github.com/ccxt/ccxt | Normalisation multi-exchange : marchés, tickers, OHLCV, order books |
| CoinGecko API | https://docs.coingecko.com/reference/introduction | Coins, exchanges, tickers, recently added |
| CoinGecko recently added | https://docs.coingecko.com/reference/coins-list-new | Détection nouveaux tokens ajoutés |

---

## 4. Communautés, rooms et signaux faibles

À capter uniquement si public et autorisé.

| Source | Utilité | Niveau de confiance |
|---|---|---|
| Telegram announcements officiels | Listings, delistings, maintenances rapides | Fort si canal officiel |
| Telegram groupes publics | Retraits bloqués, bugs, panique, rumeurs | Faible à moyen |
| Discord officiel exchange | Incidents, support, bugs, annonces communautaires | Moyen |
| Reddit | Plaintes utilisateurs, signaux de blocage, sentiment | Faible |
| X/Twitter officiels | Annonces rapides, incidents, marketing, listings | Moyen à fort si compte vérifié |
| Binance Square | News, posts utilisateurs, contenu semi-officiel | Moyen/faible |
| Forums spécialisés | Retours utilisateurs, arbitrage, incidents | Faible |

Exemples de communautés à surveiller :

- r/Binance
- r/Bybit
- r/OKX
- r/CryptoCurrency
- r/BitcoinMarkets
- r/ethtrader
- Telegram officiels Binance, Bitget, Bybit, OKX
- Discord officiels exchange
- Comptes X officiels des exchanges et des projets listés

---

## 5. Typologie des événements à classifier

| Catégorie | Description | Impact trading |
|---|---|---|
| listing_spot | Nouveau token spot | Pump potentiel, arbitrage CEX/DEX, hausse liquidité |
| listing_futures | Nouveau contrat perp/futures | Forte volatilité, funding, liquidations |
| delisting_spot | Suppression paire spot | Dump, retraits forcés, spreads violents |
| delisting_futures | Fermeture contrat futures/perp | Liquidité qui disparaît, positions forcées |
| deposit_suspension | Dépôts suspendus | Arbitrage bloqué, divergence de prix |
| withdrawal_suspension | Retraits suspendus | Risque exchange/token, premium/piège |
| maintenance | Maintenance wallet, futures, matching engine, API | Bot à désactiver ou passer en mode défensif |
| api_change | Changement REST/WebSocket/rate limit | Risque bug bot ou exécution incorrecte |
| risk_parameter_change | Funding, margin ratio, collateral, leverage | Impact direct futures/margin |
| kyc_region_change | Restriction pays, KYC, compliance | Impact volumes et accès utilisateur |
| token_migration | Swap, rebrand, ticker change, mainnet migration | Erreur de ticker, suspension temporaire |
| official_warning | Monitoring tag, ST zone, investment warning | Pré-delist potentiel |
| community_incident | Retraits bloqués, bug signalé par utilisateurs | Signal faible mais parfois précoce |
| status_incident | Incident officiel exchange/status page | Critique pour trading automatique |

---

## 6. Score d'impact recommandé

| Signal | Score |
|---|---:|
| Delisting futures officiel | 95 |
| Delisting spot officiel | 90 |
| Suspension retraits officielle | 85 |
| Listing spot Binance/Coinbase/Upbit/Bithumb | 85 |
| Listing futures Binance/Bybit/OKX | 80 |
| Maintenance matching engine/futures | 80 |
| Suspension dépôts officielle | 75 |
| Changement API/WebSocket critique | 70 |
| Funding/risk parameter change | 70 |
| Investment warning / monitoring tag | 65 |
| Token migration / rebrand | 60 |
| Rumeur Telegram/Discord répétée | 35 |
| Reddit plainte isolée | 20 |
| X non vérifié | 10 |

Score d'action :

- 80 à 100 : alerte critique immédiate
- 60 à 79 : surveillance active + vérification multi-source
- 35 à 59 : signal faible à enrichir
- 0 à 34 : journalisation uniquement

---

## 7. Schéma JSON normalisé

```json
{
  "source_platform": "binance",
  "source_type": "official_announcement",
  "region": "global",
  "language": "en",
  "event_type": "delisting_futures",
  "asset": "TOKEN",
  "pairs": ["TOKENUSDT"],
  "market": "futures",
  "published_at_utc": "2026-06-12T09:00:00Z",
  "effective_at_utc": "2026-06-18T08:00:00Z",
  "impact_score": 95,
  "confidence": 1.0,
  "url": "https://example.com/announcement",
  "raw_title": "Original announcement title",
  "raw_text_hash": "sha256:...",
  "summary": "Résumé court et exploitable.",
  "actions_required": [
    "close_positions",
    "cancel_orders",
    "withdraw_before_deadline"
  ],
  "detected_at_utc": "2026-06-12T09:01:00Z"
}
```

---

## 8. Pipeline n8n recommandé

1. Cron toutes les 1 à 5 minutes pour sources critiques.
2. HTTP Request / RSS Trigger / Telegram Trigger / Discord Bot.
3. HTML Extract ou Code Node pour extraire titre, date, catégorie, URL, texte brut.
4. Normalisation vers le schéma JSON commun.
5. Déduplication par hash : `platform + title + published_at + url`.
6. Classifier LLM local ou API : listing, delisting, maintenance, api_change, deposit_suspension, etc.
7. Scoring d'impact selon type d'événement, plateforme et marché.
8. Stockage SQLite, Postgres ou Supabase.
9. Alerte Telegram privé, Discord privé, email ou dashboard.
10. Trading Gate séparé : le module de collecte ne doit jamais passer d'ordre directement.

---

## 9. Priorité de mise en service

Phase 1 : sources officielles critiques

1. Binance announcements
2. Binance delistings
3. Binance API announcements Telegram
4. Bitget announcement center
5. Bitget delisting information
6. Bybit announcements/RSS
7. OKX latest announcements
8. OKX delistings
9. MEXC delistings
10. KuCoin delistings
11. Kraken status API
12. CoinGecko recently added API

Phase 2 : enrichissement marché

1. CCXT `load_markets()` pour apparition/disparition de paires
2. CoinGecko exchanges/tickers
3. CoinMarketCal
4. CryptoPanic
5. Funding rates futures
6. Open interest
7. Liquidation feeds

Phase 3 : communautés et rooms

1. Telegram public officiel
2. Discord officiel avec bot autorisé
3. Reddit public
4. X/Twitter comptes officiels
5. Binance Square
6. Groupes régionaux EN, FR, US, Asie, LATAM

---

## 10. Règles de sécurité opérationnelle

- Ne pas scraper de rooms privées.
- Ne pas contourner l'authentification d'une plateforme.
- Ne pas trader automatiquement sur rumeur communautaire.
- Convertir toutes les dates en UTC.
- Distinguer `published_at` et `effective_at`.
- Distinguer spot, margin, futures, options et earn.
- Archiver le contenu brut, car les pages peuvent changer.
- Vérifier les faux comptes Telegram, X et Discord.
- Détecter les duplications multilingues d'une même annonce.
- Mettre le bot de trading en mode défensif pendant maintenance matching engine/API.
- En cas de suspension retrait, bloquer toute stratégie d'arbitrage sortant.
- En cas de delisting futures, annuler les ordres et fermer les positions avant liquidation administrative.

---

## 11. Règle de décision pour un agent trading

```text
SI source officielle critique ET impact_score >= 80
ALORS envoyer alerte immédiate + enregistrer événement + bloquer trading risqué sur actif concerné.

SI source communautaire seule ET impact_score < 60
ALORS journaliser + chercher confirmation officielle + surveiller volume/prix/order book.

SI maintenance API/matching engine détectée
ALORS désactiver nouvelles entrées + maintenir uniquement gestion de risque.

SI delisting annoncé
ALORS interdire nouvelles positions longues spéculatives sauf stratégie explicitement dédiée au delisting.
```

---

## 12. Fichiers futurs à créer

Suggestions de modules à développer dans le dépôt :

- `collectors/binance_announcements.py`
- `collectors/bitget_announcements.py`
- `collectors/bybit_announcements.py`
- `collectors/okx_announcements.py`
- `collectors/mexc_announcements.py`
- `collectors/kucoin_announcements.py`
- `collectors/kraken_status.py`
- `collectors/coingecko_recently_added.py`
- `normalizers/event_schema.py`
- `scoring/impact_score.py`
- `storage/events.sqlite`
- `alerts/telegram_alerts.py`
- `workflows/n8n-exchange-intel-radar.json`

---

## 13. Principe central

Le collecteur doit être séparé du trader.

- Le collecteur observe, classe, score et alerte.
- Le module de décision valide les conditions marché.
- Le module d'exécution passe les ordres uniquement si les règles de risque sont remplies.

Architecture saine :

```text
Sources -> Collectors -> Normalizer -> Dedup -> Classifier -> Scoring -> Storage -> Alerts -> Risk Gate -> Execution
```
