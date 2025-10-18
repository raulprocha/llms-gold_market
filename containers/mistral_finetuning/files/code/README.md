# Fine-tuning Mistral 7B com LoRA + QLoRA

## Visão geral
Este repositório contém um pipeline de fine-tuning supervisionado (**SFT**) do modelo [Mistral-7B-Instruct-v0.2](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2), usando:
- **LoRA (Low-Rank Adapters)** para adaptação leve  
- **Quantização 4-bit (NF4)** para reduzir custo de GPU  
- **Máscara de rótulos** para treinar apenas a resposta do assistant  
- **Hugging Face Transformers + PEFT + Datasets**

O objetivo é treinar o modelo para prever, a partir de manchetes financeiras e contexto de mercado, o impacto esperado no par **XAU/USD** em múltiplos horizontes de tempo (6h, 12h, 24h, 48h).

---

## Estrutura do projeto
```
conf/
  config.yaml       # hiperparâmetros e caminhos
src/
  model.py          # carrega modelo + LoRA + quantização
  prompts.py        # constrói prompt e target JSON
  tokenize.py       # aplica chat template e máscara
  data.py           # leitura CSV + split train/val
  train.py          # configuração Trainer
  utils.py          # seeds, checagem env
run.py              # ponto único de entrada
README.md
requirements.txt
```

---

## Como rodar

### 1. Pré-requisitos
- Python 3.10+
- GPU com CUDA (mínimo 24GB recomendado)
- Instalar dependências:
```bash
pip install -r requirements.txt
```

### 2. Configurar token Hugging Face
```bash
export HF_TOKEN="seu_token" 
```

### 3. Preparar dataset
Coloque o CSV em `input/training_database.csv` (ou ajuste em `conf/config.yaml`).  
O dataset precisa ter colunas como:
- `generated_headline`, `label`, `sentiment_strength`, `explanation`  
- `symbol`, `symbol_name`, `correlation_description`  
- Targets: `direction_6h`, `magnitude_6h`, … até `direction_48h`, `magnitude_48h`

### 4. Rodar localmente
```bash
python run.py
```

### 5. Rodar no SageMaker
O script detecta automaticamente o ambiente (`SM_MODEL_DIR`).

---

## Configuração
Todos os hiperparâmetros estão em `conf/config.yaml`.  
Exemplo:

```yaml
train:
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
  learning_rate: 1.5e-4
  num_train_epochs: 3
  lr_scheduler_type: "cosine"
  load_best_model_at_end: true
```

---

## Saídas
- Modelo adaptado salvo em `output/finetuned-mistral`  
- Tokenizer salvo junto  
- Checkpoints por época (limitados a 2 mais recentes)

---

## Referências
- [Hugging Face Transformers Docs](https://huggingface.co/docs/transformers/index)  
- [PEFT: Parameter-Efficient Fine-Tuning](https://huggingface.co/docs/peft/index)  
- [QLoRA Paper](https://arxiv.org/abs/2305.14314)  
- [HF Datasets Docs](https://huggingface.co/docs/datasets/index)  
