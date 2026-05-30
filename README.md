# Top 100 Pizzarias de São Paulo 2026

Relatório interativo em Power BI com as 100 melhores pizzarias de São Paulo, distribuídas por zona geográfica.

## Arquivos do Projeto

| Arquivo | Descrição |
|---------|-----------|
| `100PizzariasSP.pbix` | Relatório Power BI |
| `data/enderecos.csv` | Lista das 100 pizzarias com endereço, bairro, zona e coordenadas |
| `data/depara_zonas_sp.csv` | Mapeamento Subprefeitura → Zona |
| `data/subprefeituras-sp.json` | GeoJSON das subprefeituras de SP |
| `data/sp_zonas_topo_final.json` | GeoJSON das zonas geográficas de SP |
| `n8n/workflow-scrape-logos.json` | Workflow n8n para scraping automático de logos |
| `scripts/scrape_logos.py` | Script Python alternativo para scraping de logos |

## Estrutura do `enderecos.csv`

Colunas: `Posição`, `Pizzaria`, `Endereço`, `Bairro`, `Cidade`, `Estado`, `CEP`, `Zona`, `Latitude`, `Longitude`

## Captura Automatizada de Logos via Google Maps

### O Desafio

O Power BI precisa dos logos das pizzarias para enriquecer o relatório. Buscar 85 logos manualmente (posições 16–100) seria muito demorado.

### A Solução: n8n + Google Maps

Automação usando [n8n](https://n8n.io) (self-hosted via Docker) para buscar automaticamente os logos no Google Maps.

#### Pré-requisitos

- Docker instalado
- Conta no Google Cloud Console com **Places API (New)** ativada
- Chave de API do Google Places

#### Setup

1. **Iniciar n8n via Docker:**

```bash
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
```

2. **Acessar n8n:**

```
http://localhost:5678
```

3. **Importar o workflow** (JSON disponível em `n8n/workflow-scrape-logos.json`)

4. **Configurar a chave da API:**
   - Crie um arquivo `.env` ou configure a variável de ambiente `GOOGLE_PLACES_API_KEY`
   - No n8n, vá em Settings → Variables e adicione `GOOGLE_PLACES_API_KEY`

#### Como Funciona o Workflow

```
┌─────────────────────┐
│  Lê enderecos.csv   │
│  (posições 16–100)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Para cada pizzaria: │
│  1. Text Search na   │
│     Places API       │
│  2. Place Details    │
│     (photo reference)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Download da foto    │
│  → pasta logos/      │
└─────────────────────┘
```

**Fluxo detalhado:**

1. **Read Spreadsheet** — carrega as pizzarias 16–100 do CSV
2. **HTTP Request (Text Search)** — busca cada pizzaria no Google Maps usando nome + endereço
3. **Code Node** — extrai o `photo_reference` do resultado
4. **HTTP Request (Place Details)** — busca a URL da foto com `maxwidth=400`
5. **HTTP Request (Download)** — baixa a imagem e salva como `{posicao}-{nome}.jpg`

#### Limites da API

| Tipo | Limite |
|------|--------|
| Text Search | 100 requisições/minuto (pagas após free tier) |
| Place Details | 100 requisições/minuto |
| Fotos | 100 requisições/minuto |

> **Dica:** O workflow inclui delay de 1s entre requisições para evitar rate limits.

#### Custo Estimado

- Places API: ~$0.032 por Text Search + ~$0.017 por Place Details
- Para 85 pizzarias: ~$4.25 total
- Free tier do Google Cloud: $200/mês (cobre facilmente)

### Alternativa: Script Python

Caso prefira sem n8n, o script `scripts/scrape_logos.py` faz o mesmo:

```bash
cd scripts
python -m venv venv
venv\Scripts\activate
pip install requests
python scrape_logos.py --api-key SUA_CHAVE --input ../data/enderecos.csv --start 16 --end 100
```

## Licença

Projeto pessoal — dados coletados de fontes públicas.
