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

## Captura Automatizada de Logos

### O Desafio

O Power BI precisa dos logos das pizzarias para enriquecer o relatório. Buscar 85 logos manualmente (posições 16–100) seria muito demorado.

### Solução 1: n8n + Web Scraping (sem API keys)

Automação usando [n8n](https://n8n.io) (self-hosted via Docker) para buscar automaticamente os logos.

#### Setup

1. **Iniciar n8n via Docker:**

```bash
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
```

2. **Acessar:** http://localhost:5678

3. **Importar o workflow** (`n8n/workflow-scrape-logos.json`)

4. **Ativar e rodar** — sem necessidade de API keys

#### Como Funciona

```
┌──────────────────────┐
│  Lê enderecos.csv    │
│  (posições 16–100)   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Google Search:      │
│  "{nome} pizzaria    │
│   logo"              │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Parse HTML →        │
│  extrai URL da imagem│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Download →          │
│  logos/{posicao}-    │
│  {nome}.jpg          │
└──────────────────────┘
```

1. **Read File** — carrega as pizzarias 16–100 do CSV
2. **HTTP Request** — busca no Google: `"Nome da Pizzaria pizzaria logo"`
3. **Code Node** — extrai URLs de imagens do HTML
4. **HTTP Request** — baixa a imagem
5. **Write Binary File** — salva como `{posicao}-{nome}.jpg`

### Solução 2: Script Python (sem API keys)

```bash
cd scripts
pip install requests beautifulsoup4
python scrape_logos.py --start 16 --end 100
```

O script busca no Google Images e baixa o logo de cada pizzaria automaticamente.

#### Onde são salvos os logos

Pasta `logos/` na raiz do projeto (excluída do git via `.gitignore`).

## Licença

Projeto pessoal — dados coletados de fontes públicas.
