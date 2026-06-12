# Écosystème d’Agents IA Autodidacte

**Organigramme, Flux de Communication et Protocoles de Résilience**

- Version : 1.0
- Date : 2026-06-11
- Statut : Document de référence

---

## 1. Vue d’ensemble

L’écosystème est composé de six équipes spécialisées orchestrées par un **Agent Orchestrateur Principal (AOP)**. L’ensemble fonctionne en boucle continue d’exécution, d’évaluation et d’amélioration. Tous les échanges sont centralisés sur un **Bus de Messages** qui garantit découplage, traçabilité et résilience. Une **Équipe Apprentissage & Évolution** transverse permet au système de s’auto-améliorer.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         Message Broker (RabbitMQ / Kafka / NATS)        │
│  Canaux : task.strategie, task.architecture, task.dev, task.qa,        │
│           task.ops, event.result, event.error, learning.proposal,       │
│           command.control, heartbeat                                     │
└─────────────────────────────────────────────────────────────────────────┘
       ▲         ▲         ▲         ▲         ▲         ▲         ▲
       │         │         │         │         │         │         │
 ┌─────┴───┐ ┌───┴─────┐ ┌─┴───────┐ ┌─┴───────┐ ┌─┴───────┐ ┌─┴───────┐
 │  AOP    │ │Strat.   │ │Arch.    │ │Dev.     │ │Qual.    │ │Ops      │ │Apprent. │
 │Orchest. │ │& Idéat. │ │& Données│ │& Intégr.│ │& Tests  │ │& Exploit│ │& Évol.  │
 └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

Agents transverses supplémentaires :

- **Registre** : annuaire des agents disponibles et de leur état.
- **Base de Connaissances (KB)** : leçons apprises, patterns, schémas, prompts mis à jour.

---

## 2. Organigramme des équipes

Chaque équipe contient des agents spécialisés. Les sous-agents sont notés avec un tiret.

### 2.1 Équipe STRATÉGIE & IDÉATION

Mission : analyser l’idée brute, la décomposer, prioriser et générer un plan détaillé.

- **Agent Analyste d’idée** : reformule, identifie contraintes, hypothèses et risques.
- **Agent Planificateur** : décomposition en macro-tâches, jalons, backlog initial.
- **Agent Stratège produit** : KPIs de succès, orientation technique.
- **Sous-agent Priorisation** : classe les tâches selon MoSCoW, Value/Risk.

### 2.2 Équipe ARCHITECTURE & DONNÉES

Mission : concevoir la structure de données, le modèle logique et l’infrastructure.

- **Agent Modeleur de données** : schéma conceptuel, choix SQL/NoSQL.
- **Agent Architecte système** : architecture générale, scalabilité, résilience.
- **Agent Intégrateur de sources** : ingestion de données externes, ETL/ELT.
- **Sous-agent Schéma évolutif** : migrations automatiques, versioning du schéma.

### 2.3 Équipe DÉVELOPPEMENT & INTÉGRATION

Mission : coder, assembler et intégrer les composants applicatifs.

- **Agent Développeur Core** : logique métier, tests unitaires.
- **Agent Intégrateur d’API** : connexion services, contrats, documentation.
- **Agent Build & Pipeline** : automatisation compilation, artefacts déployables.
- **Agent Référentiel de code** : branches, revues automatiques, résolution de conflits.

Sous-agents proposés par le Développeur Core :

- Rédacteur de code.
- Vérificateur syntaxique.
- Générateur de tests unitaires.
- Documentation automatique.

### 2.4 Équipe QUALITÉ & TESTS

Mission : valider, détecter les régressions, certifier la qualité.

- **Agent Testeur fonctionnel** : scénarios end-to-end.
- **Agent Testeur non-fonctionnel** : charge, résilience, sécurité.
- **Agent Validateur de régression** : comparaison inter-versions.
- **Sous-agent Générateur de cas** : création automatique de tests depuis bugs et logs.

### 2.5 Équipe DÉPLOIEMENT & EXPLOITATION

Mission : mettre en production, surveiller, maintenir.

- **Agent Déployeur** : blue/green, canary, rolling.
- **Agent Surveillant (Observability)** : métriques, logs, alertes.
- **Agent Réparateur autonome** : actions correctives automatiques, redémarrage, rollback, scaling, escalade si échec.
- **Sous-agent Backup & Recovery** : sauvegardes, restauration simulée.

### 2.6 Équipe APPRENTISSAGE & ÉVOLUTION

Mission : observer, apprendre des erreurs, optimiser, faire évoluer l’écosystème.

- **Agent Auditeur de performance** : écart KPIs réels / objectifs, goulots d’étranglement.
- **Agent Analyseur d’erreurs** : classification, causes racines.
- **Agent Proposeur d’optimisations** : pull requests automatiques sur bac à sable.
- **Agent Validateur d’évolutions** : tests sur environnement miroir, validation avant fusion.
- **Agent Mémorisation & généralisation** : stockage des leçons, mise à jour des règles et prompts.
- **Sous-agent Boucle d’auto-évaluation** : évaluation périodique de chaque agent, réglage ou remplacement.

---

## 3. Protocole de communication

Tous les agents échangent via le Message Broker en respectant un format d’enveloppe standard et des files d’attente dédiées.

### 3.1 Format standard des messages JSON

```json
{
  "messageId": "uuid",
  "correlationId": "uuid",
  "timestamp": "2026-06-11T10:00:00Z",
  "ttl": 3600,
  "type": "COMMAND | QUERY | EVENT | ERROR",
  "source": "agent_id",
  "target": "agent_id | wildcard",
  "intent": "task.create | task.result | system.heartbeat",
  "payload": {},
  "context": {
    "priority": "HIGH | MEDIUM | LOW",
    "retryCount": 0,
    "maxRetries": 3,
    "sagaId": "optional"
  }
}
```

Règles :

- **Corrélation** : toute réponse ou erreur porte le `correlationId` initial.
- **Idempotence** : chaque `messageId` est unique ; les agents ignorent les doublons.
- **Versionnement** : le contenu métier est versionné pour permettre l’évolution sans rupture.

### 3.2 Files d’attente et canaux

| Canal / Queue | Usage | Consommateurs |
|---|---|---|
| `task.strategie` | Nouvelles idées, priorisation | Stratégie & Idéation |
| `task.architecture` | Schémas, conception | Architecture & Données |
| `task.dev.{lang}` | Développement, par langage | Développement & Intégration |
| `task.qa` | Exécution des tests | Qualité & Tests |
| `task.ops` | Déploiement, rollback, scaling | Déploiement & Exploitation |
| `event.result.{success,fail}` | Résultat de toute tâche | AOP, Apprentissage |
| `event.error` | Erreurs classifiées | Apprentissage, QA |
| `command.control` | Ordres de l’AOP : pause, config, heartbeat | Tous les agents |
| `heartbeat` | Signal de vie périodique, 5 s | AOP supervision |
| `learning.proposal` | Pull request d’optimisation | Bac à sable |

Chaque équipe possède sa propre file persistante pour lisser la charge et tolérer les redémarrages.

### 3.3 Routage et orchestration

- **Orchestration par l’AOP** : une idée reçue initie une Saga. L’AOP publie sur `task.strategie`, attend `event.result.success`, puis progresse vers l’architecture, le développement, la qualité, l’exploitation et l’apprentissage.
- **Chorégraphie directe** : quand un contrat est clair, par exemple une spécification issue de l’Architecture, l’équipe émettrice envoie directement une `COMMAND` sur la file de l’équipe suivante.
- **Priorités dynamiques** : l’AOP peut modifier la priorité d’une tâche en réinjectant un message avec un nouveau contexte.

### 3.4 Modes de communication

- **Asynchrone** : privilégié pour tous les traitements métier, avec file d’attente et callback via `event.result`.
- **Synchrone HTTP/gRPC** : réservé aux interactions temps réel à faible latence, par exemple validation syntaxique, avec circuit breaker et timeout.

---

## 4. Protocole de reprise sur erreur et résilience

Le système est conçu pour qu’aucune erreur ne bloque la boucle continue.

### 4.1 Retry et Dead Letter Queue

- Retry avec backoff exponentiel : en cas d’erreur transitoire, l’agent réessaie selon les paramètres du message : `retryCount`, `maxRetries`.
- Après épuisement, le message est déplacé dans une Dead Letter Queue, puis signalé dans `event.error`.
- L’Agent Analyseur d’erreurs scrute la DLQ, regroupe par pattern, identifie la cause racine et peut créer automatiquement une tâche corrective `task.dev` si une solution connue existe.

### 4.2 Circuit Breaker et Bulkhead

Chaque agent utilise un circuit breaker pour ses appels externes. Après N échecs, le circuit s’ouvre, rejette rapidement les appels et émet un `event.error`. L’AOP peut ordonner un fallback.

Le pattern bulkhead isole les ressources par agent, équipe ou type de tâche pour éviter qu’une panne localisée ne contamine tout l’écosystème.

### 4.3 Gestion des pannes d’agents par heartbeat

- Le Registre maintient l’état des agents : `UP`, `DOWN`, `DEGRADED`.
- Chaque agent émet un heartbeat toutes les 5 secondes.
- Si un agent ne répond plus après 15 secondes, l’AOP le retire du registre et réinjecte ses tâches en cours dans la file de l’équipe pour reprise par un pair.
- L’Agent Réparateur autonome tente un redémarrage.

### 4.4 Saga et transactions longues

Les workflows multi-étapes sont orchestrés via le pattern Saga. Chaque étape possède une action compensatoire explicite. En cas d’échec, l’AOP appelle les compensations des étapes précédentes. L’état de la saga est journalisé pour reprise après crash.

### 4.5 Auto-amélioration proactive

- L’Agent Proposeur d’optimisations crée des pull requests sur un bac à sable.
- L’Agent Validateur d’évolutions teste ces PR sur un environnement miroir.
- Si les KPIs s’améliorent sans régression, la modification peut être fusionnée automatiquement selon les règles de gouvernance.
- L’Agent Mémorisation enregistre le delta et met à jour la Base de Connaissances.
- Les autres agents, par exemple le Modeleur de données, peuvent être automatiquement prévenus des patterns connus.

### 4.6 Boucles d’interaction

- **Boucle courte** : Dev → Tests → Déploiement → Surveillance → Erreur → Correction immédiate.
- **Boucle longue** : l’Apprentissage analyse les incidents sur la durée → propose des changements d’architecture ou de stratégie → la Stratégie met à jour le plan → nouveau cycle complet.
- **Auto-évaluation** : le Sous-agent Boucle d’auto-évaluation juge périodiquement chaque agent et peut recommander son réglage ou son remplacement.

---

## 5. Exemple de flux complet : gestion d’une latence

1. **Surveillance** : l’Agent Surveillant détecte un dépassement de latence et publie `event.error`.
2. **Analyse** : l’Analyseur d’erreurs identifie un index manquant et génère une tâche `task.dev` en priorité `HIGH`.
3. **Correction** : le Développeur Core crée le script d’index, le Build & Pipeline compile, le Déployeur l’applique en canary.
4. **Confirmation** : l’Agent Surveillant vérifie le retour à la normale et publie `event.result.success`.
5. **Apprentissage** : l’Agent Mémorisation enregistre le pattern “latence → index manquant” et la solution. Les futurs schémas seront vérifiés automatiquement par l’Agent Modeleur de données via la KB.

---

## 6. Schéma conceptuel du système

```text
┌──────────────┐     ┌────────────────────────────────────────────────────┐
│   Entrée     │────▶│           Agent Orchestrateur Principal            │
│ (idée brute) │     └────────────────────────────────────────────────────┘
└──────────────┘                │                     ▲
                                ▼                     │
┌──────────────────────────────────────────────────────────────────────────┐
│                           Message Broker                                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │
│  │task.strat │ │task.archi │ │ task.dev  │ │  task.qa  │ │ task.ops  │  │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐                │
│  │event.res. │ │event.error│ │learning.  │ │heartbeat  │  ...           │
│  └───────────┘ └───────────┘ │proposal   │ └───────────┘                │
│                              └───────────┘                               │
└──────────────────────────────────────────────────────────────────────────┘
         ▲                  ▲                  ▲                  ▲
         │                  │                  │                  │
  ┌──────┴─────┐   ┌───────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐
  │ Stratégie  │   │ Architecture │   │  Qualité    │   │ Apprentissage│
  │ & Idéation │   │ & Données    │   │  & Tests    │   │ & Évolution  │
  └────────────┘   └──────────────┘   └─────────────┘   └─────────────┘
                      ┌───────────┐   ┌───────────┐
                      │  Dével.   │   │Déploiement│
                      │ & Intégr. │   │& Exploit. │
                      └───────────┘   └───────────┘
```

---

## 7. Évolutions futures

- Apprentissage fédéré entre plusieurs instances de l’écosystème.
- Observabilité avancée : tableaux de bord en temps réel des KPIs par agent.
- Auto-génération de nouveaux agents spécialisés si des charges récurrentes sont détectées.

---

## 8. Positionnement dans TradingAgents

Ce document sert de **référence d’architecture cible**.

Dans l’état actuel du dépôt, il ne doit pas déclencher de complexification immédiate. L’ordre d’exécution reste :

1. Stabiliser le radar read-only : collecte, scoring, SQLite, Telegram.
2. Ajouter progressivement d’autres collecteurs : Bitget, Bybit, OKX, Kraken.
3. Ajouter observabilité et logs propres.
4. Introduire une orchestration simple.
5. Introduire seulement ensuite des agents spécialisés.

Règle de gouvernance : l’écosystème multi-agents ne doit pas piloter d’ordres de trading tant que les modules de collecte, validation, risk gate et journalisation ne sont pas fiables.
