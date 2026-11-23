# Dicionário de dados — Trabalho Final ENG037 (2026.2)

Todas as tabelas existem em dois formatos: CSV (UTF-8, separador vírgula, decimal ponto, datas AAAA-MM-DD) na pasta `dados/` e como abas do arquivo `.xlsx` do grupo.
Chaves: `id_atividade`, `id_material`, `id_fornecedor`, `id_equipamento`, `id_zona`, `id_posto`, `codigo_eap`. Dias úteis (du): segunda a sexta, exceto feriados (tabela 11).

## Bloco A. Planejamento

### 01_projeto_parametros — Parâmetros do projeto

Ficha do empreendimento em formato parâmetro–valor: datas, contrato, regras de trabalho e metas da operação.

**Granularidade:** Uma linha por parâmetro (chave: parametro).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `parametro` | texto | — | Nome do parâmetro. | Ver lista de parâmetros no fim deste dicionário. |
| `valor` | texto/número | ver coluna unidade | Valor do parâmetro. | Datas em AAAA-MM-DD; decimais com ponto. |
| `unidade` | texto | — | Unidade de medida do valor. | R$, %, du (dias úteis), h, data, texto etc. |
| `descricao` | texto | — | Explicação do parâmetro. |  |

### 02_eap — Estrutura Analítica do Projeto (EAP)

Hierarquia do escopo: projeto → fases → pacotes de trabalho. O item 1.9 (administração local) é custo indireto, não tem atividade.

**Granularidade:** Uma linha por item da EAP (chave: codigo_eap).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `codigo_eap` | texto | — | Código hierárquico do item. | 1 = projeto; 1.x = fase; 1.x.y = pacote de trabalho. |
| `nivel` | inteiro | — | Nível do item na hierarquia. | 1, 2 ou 3. |
| `codigo_eap_pai` | texto | — | Código do item imediatamente acima. | Vazio no nível 1. |
| `descricao` | texto | — | Nome do item. |  |
| `tipo_item` | texto | — | Natureza do item. | PROJETO, FASE, PACOTE, INDIRETO. |

### 03_atividades — Atividades (pacotes de trabalho)

Cadastro das atividades com quantidade, produtividade orçada e regime de execução. A duração NÃO é informada para atividades por esforço: calcule pela RUP.

**Granularidade:** Uma linha por atividade (chave: id_atividade).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_atividade` | texto | — | Identificador da atividade. | A01, A02, ... |
| `codigo_eap` | texto | — | Pacote de trabalho da EAP ao qual a atividade pertence. | Chave para 02_eap. |
| `nome_atividade` | texto | — | Descrição do serviço. |  |
| `fase` | texto | — | Fase do projeto. | Nome da fase (nível 2 da EAP). |
| `id_zona` | texto | — | Zona física onde o serviço acontece. | Chave para 13_layout_zonas; vazio em atividades sem local físico (projetos, licenças, contratações). |
| `unidade` | texto | — | Unidade de medição do serviço. | m², m³, t, m, un, pontos, pos, mód, % etc. Em atividades de duração fixa a unidade é % (0 a 100). |
| `quantidade_orcada` | número | unidade da atividade | Quantidade total de serviço prevista no orçamento. | 100 quando a unidade é %. |
| `rup_orcada_hh_un` | número | Hh por unidade | Razão Unitária de Produção orçada: homens-hora de toda a equipe direta para produzir uma unidade de serviço. | Vazio em atividades de duração fixa. Menor RUP = maior produtividade. |
| `tipo_duracao` | texto | — | Como a duração é determinada. | ESFORCO: duração = arredondar para cima(quantidade × RUP ÷ (efetivo da equipe × 8 h)). FIXA: usar duracao_fixa_du. |
| `duracao_fixa_du` | inteiro | dias úteis | Duração de atividades que não dependem de esforço (prazos de terceiros, cura, licenças). | Vazio quando tipo_duracao = ESFORCO. |
| `regime_execucao` | texto | — | Quem executa e como é pago. | PROPRIA: equipe CLT, custo = horas × custo/hora. EMPREITADA: preço por unidade medida. CONTRATADA: serviço de terceiros a preço global, medido em %. |
| `preco_unitario_empreitada_rs` | número | R$ por unidade | Preço contratado por unidade de serviço medida. | Preenchido só em regime EMPREITADA. |
| `encarregado` | texto | — | Responsável de campo pela equipe (o 'último planejador'). | Vazio em atividades CONTRATADAS sem equipe no canteiro. |
| `ambiente` | texto | — | Exposição do serviço à chuva. | EXTERNO (sujeito a chuva) ou INTERNO. |
| `numero_lotes_inspecao` | inteiro | lotes | Em quantos lotes o serviço é dividido para inspeção de qualidade (FVS). | 0 quando não há FVS. |

### 04_dependencias — Rede de precedências

Ligações lógicas entre atividades para montar a rede e calcular o caminho crítico.

**Granularidade:** Uma linha por ligação (chave: sucessora + predecessora).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_atividade_sucessora` | texto | — | Atividade que depende da outra. | Chave para 03_atividades. |
| `id_atividade_predecessora` | texto | — | Atividade que condiciona a sucessora. | Chave para 03_atividades. |
| `tipo_dependencia` | texto | — | Tipo de ligação. | TI (término–início): a sucessora começa depois que a predecessora termina. II (início–início): a sucessora começa depois que a predecessora começa. |
| `defasagem_du` | inteiro | dias úteis | Espera mínima adicional da ligação (lag). | TI: início ≥ término da predecessora + defasagem. II: início ≥ início da predecessora + defasagem. |

### 05_funcoes_mao_de_obra — Funções de mão de obra

Tabela de custo horário por função.

**Granularidade:** Uma linha por função (chave: funcao).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `funcao` | texto | — | Código da função. | SER, PED, CAR, ARM, MON, SOL, ELE, ENC, MEC, TEC, OPE, PIN. |
| `nome_funcao` | texto | — | Nome da função. |  |
| `custo_hora_rs` | número | R$/h | Custo da hora normal com encargos sociais. |  |
| `adicional_hora_extra_pct` | número | % | Acréscimo de custo da hora extra sobre a hora normal (com reflexos). | Custo da HE = custo_hora × (1 + adicional/100). |

### 06_equipamentos — Equipamentos de obra (unidades locadas)

Cadastro de cada unidade de equipamento disponível para a obra, com dados para a decisão locar × comprar.

**Granularidade:** Uma linha por unidade (chave: id_equipamento).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_equipamento` | texto | — | Identificador da unidade. | Tipo + número, ex.: PTA-02. |
| `tipo_equipamento` | texto | — | Código do tipo. | ESC, RET, CAM, ROL, GUI, PTA, MUN, BET, EMP, ALI. |
| `descricao` | texto | — | Descrição do tipo de equipamento. |  |
| `locadora` | texto | — | Empresa locadora. |  |
| `ano_fabricacao` | inteiro | ano | Ano de fabricação da unidade. |  |
| `diaria_orcada_rs` | número | R$/dia | Diária considerada no orçamento. | Cobrada por dia útil em que a unidade está mobilizada. |
| `diaria_contratada_rs` | número | R$/dia | Diária efetivamente contratada com a locadora. |  |
| `valor_compra_novo_rs` | número | R$ | Preço de um equipamento novo equivalente. | Para análise locar × comprar. |
| `custo_manutencao_mensal_proprio_rs` | número | R$/mês | Custo mensal de manutenção se o equipamento fosse próprio. |  |
| `vida_util_anos` | inteiro | anos | Vida útil para depreciação linear. |  |
| `intervalo_preventiva_h` | inteiro | horas de operação | Intervalo recomendado entre manutenções preventivas. |  |

### 07_atividade_recursos — Recursos por atividade

Composição da equipe direta e dos equipamentos de cada atividade (por dia de trabalho).

**Granularidade:** Uma linha por atividade × recurso.

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_atividade` | texto | — | Atividade. | Chave para 03_atividades. |
| `tipo_recurso` | texto | — | Natureza do recurso. | MAO_DE_OBRA ou EQUIPAMENTO. |
| `codigo_recurso` | texto | — | Código da função (05) ou do tipo de equipamento (06). |  |
| `quantidade` | inteiro | pessoas ou unidades | Quantidade do recurso alocada por dia à atividade. | A soma das pessoas é o efetivo da equipe usado no cálculo da duração. |

### 08_materiais — Materiais e equipamentos de processo

Cadastro de insumos, inclusive os equipamentos de processo que serão instalados.

**Granularidade:** Uma linha por material (chave: id_material).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_material` | texto | — | Código do material. |  |
| `descricao` | texto | — | Descrição. |  |
| `unidade` | texto | — | Unidade de compra e de consumo. |  |
| `categoria` | texto | — | Família de suprimento. | CIVIL, ESTRUTURA, ACABAMENTO, ELETRICA, HIDRAULICA, INCENDIO, UTILIDADES, TI, PROCESSO. |
| `preco_orcado_rs` | número | R$ por unidade | Preço unitário do orçamento, posto obra. |  |
| `lead_time_du` | inteiro | dias úteis | Prazo padrão entre o pedido e a entrega. | Data-limite do pedido = data de uso − lead time − margem. |
| `perda_orcada_pct` | número | % | Perda de material considerada no orçamento. | Consumo orçado = quantidade × consumo_por_unidade × (1 + perda/100). |

### 09_atividade_materiais — Consumo de materiais por atividade

Coeficientes de consumo: quanto de cada material é necessário por unidade de serviço.

**Granularidade:** Uma linha por atividade × material.

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_atividade` | texto | — | Atividade consumidora. | Chave para 03_atividades. |
| `id_material` | texto | — | Material consumido. | Chave para 08_materiais. |
| `consumo_por_unidade` | número | un. do material por un. do serviço | Coeficiente teórico de consumo, sem perda. |  |

### 10_fornecedores — Fornecedores

Cadastro dos fornecedores de materiais e equipamentos de processo.

**Granularidade:** Uma linha por fornecedor (chave: id_fornecedor).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_fornecedor` | texto | — | Código do fornecedor. |  |
| `nome_fornecedor` | texto | — | Razão social (fictícia). |  |
| `cidade` | texto | — | Cidade de origem do fornecimento. |  |
| `distancia_km` | número | km | Distância rodoviária aproximada até a obra de referência. |  |
| `categorias_atendidas` | texto | — | Categorias de material que o fornecedor atende. | Lista separada por ponto e vírgula. |

### 11_calendario — Calendário do projeto

Todos os dias corridos do início do projeto até set/2027, com dias úteis, feriados e chuva observada.

**Granularidade:** Uma linha por dia (chave: data).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `data` | data | AAAA-MM-DD | Dia do calendário. |  |
| `dia_semana` | texto | — | Dia da semana. | seg, ter, qua, qui, sex, sáb, dom. |
| `dia_util` | inteiro | 0/1 | 1 se é dia de trabalho na obra. | Segunda a sexta, exceto feriados. |
| `feriado` | texto | — | Nome do feriado, quando houver. |  |
| `semana` | texto | — | Semana ISO do dia. | Formato AAAA-Snn; mesma chave de 21_plano_semanal. |
| `mes` | texto | AAAA-MM | Mês do dia. |  |
| `dia_util_projeto` | inteiro | du | Número sequencial do dia útil desde o início do projeto (1 = primeiro dia). | Vazio em dias não úteis. Use para converter prazos em du para datas. |
| `chuva_mm` | número | mm/dia | Chuva registrada no pluviômetro do canteiro. | Vazio para datas ainda não observadas. |

### 12_orcamento_linha_de_base — Orçamento da linha de base

Custo direto orçado de cada atividade, aberto por natureza. A soma é o orçamento no término (ONT) de custo direto.

**Granularidade:** Uma linha por atividade (chave: id_atividade).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_atividade` | texto | — | Atividade. | Chave para 03_atividades. |
| `codigo_eap` | texto | — | Pacote de trabalho. |  |
| `custo_mao_de_obra_rs` | número | R$ | Mão de obra própria orçada. | Hh orçadas × custo médio da equipe. |
| `custo_subcontrato_rs` | número | R$ | Empreitada ou serviço contratado orçado. |  |
| `custo_material_rs` | número | R$ | Materiais orçados, com perda. |  |
| `custo_equipamento_rs` | número | R$ | Locação de equipamentos orçada. | Quantidade × diária orçada × duração. |
| `custo_total_rs` | número | R$ | Soma das quatro naturezas. |  |

### 13_layout_zonas — Layout: zonas do empreendimento

Geometria simplificada do terreno, das edificações e das zonas de processo. Base do croqui e do modelo 3D.

**Granularidade:** Uma linha por zona (chave: id_zona).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_zona` | texto | — | Código da zona. |  |
| `nome_zona` | texto | — | Nome da zona. |  |
| `tipo_zona` | texto | — | Natureza da zona. | TERRENO, EDIFICACAO, PROCESSO, PATIO, APOIO, UTILIDADES, CANTEIRO. |
| `id_zona_pai` | texto | — | Zona que contém esta zona. | Zonas de processo ficam dentro da edificação (GALPAO) ou do terreno. |
| `x_m` | número | m | Coordenada X (leste) do canto sudoeste da zona. | Origem no canto sudoeste do terreno. |
| `y_m` | número | m | Coordenada Y (norte) do canto sudoeste da zona. |  |
| `largura_x_m` | número | m | Dimensão da zona no eixo X. |  |
| `comprimento_y_m` | número | m | Dimensão da zona no eixo Y. |  |
| `altura_m` | número | m | Altura para o modelo 3D. | 0 para o terreno. |

### 14_fluxo_zonas — Fluxos entre zonas

Intensidade de movimentação prevista entre zonas na operação da nova unidade. Base da análise de layout (carga × distância).

**Granularidade:** Uma linha por par origem → destino.

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_zona_origem` | texto | — | Zona de onde sai o fluxo. | Chave para 13_layout_zonas. |
| `id_zona_destino` | texto | — | Zona aonde chega o fluxo. |  |
| `viagens_dia` | inteiro | viagens/dia | Número de deslocamentos por dia na operação em regime. |  |
| `meio_transporte` | texto | — | Meio de movimentação. | EMPILHADEIRA, ESTEIRA, PALETEIRA, REBOCADOR, PESSOAS. |
| `carga_media_kg` | inteiro | kg/viagem | Carga média por viagem. |  |

## Bloco B. Execução

### 15_rdo_mao_de_obra — RDO: mão de obra

Efetivo e horas apontados no Relatório Diário de Obra, por atividade e função.

**Granularidade:** Uma linha por dia × atividade × função.

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `data` | data | AAAA-MM-DD | Dia do apontamento. |  |
| `id_atividade` | texto | — | Atividade em que a equipe trabalhou. |  |
| `funcao` | texto | — | Função apontada. | Chave para 05_funcoes_mao_de_obra. |
| `efetivo_previsto` | inteiro | pessoas | Quantas pessoas da função estavam escaladas para a atividade no dia. | Pode superar a equipe orçada quando há reforço. |
| `efetivo_presente` | inteiro | pessoas | Quantas compareceram. | Absenteísmo = 1 − presente ÷ previsto. |
| `horas_normais` | número | Hh | Homens-hora em jornada normal (pessoas × horas). | Jornada de 8 h por dia útil. |
| `horas_extras` | número | Hh | Homens-hora extras. | Custo com adicional da tabela 05. Em EMPREITADA as horas não geram custo de folha. |

### 16_rdo_producao — RDO: produção e ocorrências

Quantidade de serviço executada por dia e principais perdas. Em atividades CONTRATADAS (unidade %), o avanço é informado uma vez por semana.

**Granularidade:** Uma linha por dia × atividade com equipe mobilizada.

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `data` | data | AAAA-MM-DD | Dia do apontamento. |  |
| `id_atividade` | texto | — | Atividade. |  |
| `quantidade_executada` | número | unidade da atividade | Serviço produzido no dia (ou na semana, se unidade = %). | Avanço físico = soma ÷ quantidade_orcada. |
| `ocorrencia` | texto | — | Principal ocorrência do dia, quando relevante. | CHUVA, FALHA_EQUIPAMENTO, FALTA_MATERIAL, RETRABALHO ou vazio. |
| `horas_perdidas_chuva` | número | Hh | Homens-hora improdutivos por chuva. |  |
| `horas_perdidas_equipamento` | número | Hh | Homens-hora improdutivos por equipamento parado. |  |
| `horas_paradas_material` | número | Hh | Homens-hora improdutivos por falta de material. |  |
| `hh_retrabalho` | número | Hh | Homens-hora gastos refazendo serviço reprovado. |  |
| `observacao` | texto | — | Anotação livre do encarregado. |  |

### 17_equipamentos_apontamento — Apontamento diário de equipamentos de obra

Horas de cada equipamento locado em cada dia em que esteve mobilizado (e sendo cobrado).

**Granularidade:** Uma linha por dia × equipamento mobilizado.

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `data` | data | AAAA-MM-DD | Dia. |  |
| `id_equipamento` | texto | — | Unidade. | Chave para 06_equipamentos. |
| `id_atividade` | texto | — | Atividade atendida no dia. | Vazio quando a unidade ficou à disposição sem frente de trabalho. |
| `horas_disponiveis` | número | h | Horas da jornada no dia. | 8 h. |
| `horas_operando` | número | h | Horas efetivamente operando. |  |
| `horas_manutencao_corretiva` | número | h | Horas parado por quebra. |  |
| `horas_manutencao_preventiva` | número | h | Horas parado para manutenção preventiva. |  |
| `horas_ociosas` | número | h | Horas em condições de operar, mas sem uso. | disponíveis − operando − corretiva − preventiva. |
| `numero_falhas` | inteiro | falhas | Quebras iniciadas no dia. | MTBF = horas operando ÷ número de falhas; MTTR = horas de corretiva ÷ número de falhas. |
| `horimetro` | número | h | Leitura acumulada do horímetro ao fim do dia. |  |

### 18_compras_pedidos — Pedidos de compra

Histórico de pedidos de materiais e equipamentos de processo, do pedido à inspeção de recebimento (FVM).

**Granularidade:** Uma linha por pedido (chave: id_pedido).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_pedido` | texto | — | Número do pedido. |  |
| `id_material` | texto | — | Material comprado. | Chave para 08_materiais. |
| `id_atividade` | texto | — | Atividade a que o material se destina. |  |
| `id_fornecedor` | texto | — | Fornecedor. | Chave para 10_fornecedores. |
| `comprador` | texto | — | Comprador responsável pelo pedido. |  |
| `tipo_pedido` | texto | — | Origem do pedido. | PROGRAMADO (plano de compras), EMERGENCIAL (falta em obra), REPOSICAO (substituição de lote rejeitado). |
| `data_requisicao` | data | AAAA-MM-DD | Data em que a obra requisitou o material. |  |
| `data_pedido` | data | AAAA-MM-DD | Data de emissão do pedido ao fornecedor. |  |
| `data_necessidade_obra` | data | AAAA-MM-DD | Data em que o material deveria estar na obra segundo a linha de base. |  |
| `data_prometida` | data | AAAA-MM-DD | Data de entrega prometida pelo fornecedor. |  |
| `data_entrega` | data | AAAA-MM-DD | Data real de entrega. | Vazio para pedidos ainda não entregues. |
| `quantidade_pedida` | número | unidade do material | Quantidade do pedido. |  |
| `preco_unitario_rs` | número | R$ por unidade | Preço unitário pago. | Compare com preco_orcado_rs. |
| `frete_rs` | número | R$ | Frete pago à parte. | Só há frete à parte em entregas expressas; no preço normal o frete está incluso. |
| `frete_expresso` | inteiro | 0/1 | 1 se o pedido exigiu prazo reduzido (compra tardia ou emergência). |  |
| `quantidade_rejeitada_fvm` | número | unidade do material | Quantidade reprovada na inspeção de recebimento (FVM) e devolvida. | Vazio para pedidos ainda não entregues. |

### 19_estoque_movimentos — Movimentos de estoque

Entradas (recebimentos aceitos) e saídas (requisições de material aplicadas nas atividades) do almoxarifado da obra.

**Granularidade:** Uma linha por movimento. Saídas são consolidadas por semana.

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `data` | data | AAAA-MM-DD | Data do movimento. | Saídas: último dia útil da semana. |
| `id_material` | texto | — | Material. |  |
| `tipo_movimento` | texto | — | Sentido. | ENTRADA ou SAIDA. |
| `quantidade` | número | unidade do material | Quantidade movimentada. | Entrada = quantidade pedida − quantidade rejeitada. |
| `id_atividade` | texto | — | Atividade que consumiu o material. | Só em saídas. |
| `id_pedido` | texto | — | Pedido que originou a entrada. | Só em entradas. |
| `documento` | texto | — | Nota fiscal (NF) ou requisição de material (RM). |  |

### 20_custos_apropriados — Custos apropriados

Custo real lançado por item da EAP. Materiais são apropriados quando aplicados (saída do estoque), não quando comprados.

**Granularidade:** Uma linha por lançamento (chave: id_lancamento).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_lancamento` | texto | — | Número do lançamento. |  |
| `data` | data | AAAA-MM-DD | Data de competência (fechamento semanal). |  |
| `codigo_eap` | texto | — | Item da EAP que recebeu o custo. | 1.9 = administração local. DIVERSOS = lançamento sem apropriação correta. |
| `id_atividade` | texto | — | Atividade. | Vazio em custos indiretos e em lançamentos DIVERSOS. |
| `categoria` | texto | — | Natureza do custo. | MAO_DE_OBRA, SUBCONTRATO, MATERIAL, EQUIPAMENTO, INDIRETO. |
| `valor_rs` | número | R$ | Valor lançado. |  |
| `documento` | texto | — | Documento de origem. | FOLHA (folha semanal), MED (medição), RM (requisição de material), LOC (locação), MOB (mobilização), ADM (administração local). |
| `fornecedor` | texto | — | Fornecedor ou locadora, quando aplicável. |  |
| `descricao` | texto | — | Histórico do lançamento. |  |

### 21_plano_semanal — Plano semanal (Last Planner)

Pacotes comprometidos em cada semana e resultado ao fim dela. Base do PPC.

**Granularidade:** Uma linha por semana × pacote (chave: id_pacote).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_pacote` | texto | — | Identificador do pacote semanal. |  |
| `semana` | texto | AAAA-Snn | Semana ISO do compromisso. |  |
| `data_inicio_semana` | data | AAAA-MM-DD | Primeiro dia útil da semana. |  |
| `id_atividade` | texto | — | Atividade do pacote. |  |
| `encarregado` | texto | — | Quem assumiu o compromisso. |  |
| `unidade` | texto | — | Unidade da meta. |  |
| `meta_quantidade` | número | unidade da atividade | Quantidade comprometida para a semana. |  |
| `quantidade_realizada` | número | unidade da atividade | Quantidade realmente executada na semana. |  |
| `concluido` | inteiro | 0/1 | 1 se o pacote foi cumprido (realizado ≥ 97% da meta). | PPC = pacotes concluídos ÷ pacotes planejados. O critério é binário. |
| `causa_nao_cumprimento` | texto | — | Causa principal registrada quando o pacote não foi cumprido. | MATERIAL, CHUVA, MAO_DE_OBRA, EQUIPAMENTO, PROJETO, SERVICO_ANTERIOR, RETRABALHO, PRODUTIVIDADE, LICENCA, TERCEIROS. Campo digitado à mão: há variações de grafia. |

### 22_restricoes — Restrições do lookahead

Lista de restrições identificadas no planejamento de médio prazo e seu tratamento.

**Granularidade:** Uma linha por restrição (chave: id_restricao).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_restricao` | texto | — | Identificador. |  |
| `id_atividade` | texto | — | Atividade restringida. |  |
| `tipo_restricao` | texto | — | Critério da análise de restrições. | PROJETO, MATERIAL, EQUIPE, EQUIPAMENTO, LICENCA. |
| `responsavel` | texto | — | Área responsável por remover a restrição. |  |
| `data_identificacao` | data | AAAA-MM-DD | Quando a restrição entrou na lista. |  |
| `data_necessaria` | data | AAAA-MM-DD | Data-limite para remoção (início da atividade na linha de base). |  |
| `data_remocao` | data | AAAA-MM-DD | Quando foi removida. | Vazio se ainda aberta. |
| `status` | texto | — | Situação na data de extração. | REMOVIDA, EM_ANDAMENTO (aberta, ainda no prazo) ou BLOQUEIA (aberta e vencida). |

### 23_inspecoes_qualidade — Inspeções de serviço (FVS)

Fichas de Verificação de Serviço aplicadas por lote concluído.

**Granularidade:** Uma linha por inspeção (chave: id_inspecao).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_inspecao` | texto | — | Número da ficha. |  |
| `data` | data | AAAA-MM-DD | Data da inspeção. |  |
| `id_atividade` | texto | — | Serviço inspecionado. |  |
| `id_zona` | texto | — | Local. |  |
| `lote` | inteiro | — | Número do lote dentro da atividade. | 1 a numero_lotes_inspecao. |
| `encarregado` | texto | — | Encarregado da equipe executora. |  |
| `itens_verificados` | inteiro | itens | Quantidade de itens da ficha. |  |
| `itens_reprovados` | inteiro | itens | Itens fora da tolerância. |  |
| `resultado` | texto | — | Resultado do lote. | APROVADO ou REPROVADO (gera não conformidade e retrabalho). |
| `hh_retrabalho_estimado` | número | Hh | Homens-hora estimados para corrigir o lote reprovado. | 0 quando aprovado. |

### 24_ocorrencias_seguranca — Ocorrências de segurança

Registro de quase acidentes e acidentes.

**Granularidade:** Uma linha por ocorrência (chave: id_ocorrencia).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_ocorrencia` | texto | — | Identificador. |  |
| `data` | data | AAAA-MM-DD | Data. |  |
| `tipo` | texto | — | Classificação. | QUASE_ACIDENTE, ACIDENTE_SEM_AFASTAMENTO, ACIDENTE_COM_AFASTAMENTO. |
| `id_atividade` | texto | — | Atividade em que ocorreu. |  |
| `funcao_envolvida` | texto | — | Função do trabalhador envolvido. |  |
| `dias_perdidos` | inteiro | dias | Dias de afastamento. | 0 quando não há afastamento. |
| `houve_hora_extra_no_dia` | inteiro | 0/1 | 1 se a equipe fazia hora extra no dia. |  |
| `chuva_no_dia` | inteiro | 0/1 | 1 se choveu 2 mm ou mais no dia. |  |

## Bloco C. Operação

### 25_demanda_historica — Demanda histórica da operação

36 meses de demanda e nível de serviço do site atual da empresa, por família de produto.

**Granularidade:** Uma linha por mês × família.

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `mes` | texto | AAAA-MM | Mês. |  |
| `familia` | texto | — | Família de produto ou serviço. |  |
| `unidade` | texto | — | Unidade de volume. | Igual ao parâmetro unidade_produto. |
| `demanda` | número | unidades/mês | Demanda total do mês (pedidos recebidos). |  |
| `volume_atendido` | número | unidades/mês | Volume efetivamente produzido/expedido no mês. | Menor que a demanda quando o site atual não comporta. |
| `pedidos_no_prazo_pct` | número | % | Percentual de pedidos entregues no prazo e completos (OTIF) no mês. |  |
| `dias_uteis` | inteiro | dias | Dias úteis do mês. |  |

### 26_processo_postos — Postos do processo da nova unidade

Sequência de postos do processo com tempos de ciclo e o número de recursos previsto no projeto. Base de takt, capacidade e gargalo.

**Granularidade:** Uma linha por posto (chave: id_posto).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_posto` | texto | — | Código do posto. |  |
| `sequencia` | inteiro | — | Ordem do posto no fluxo. |  |
| `nome_posto` | texto | — | Nome do posto. |  |
| `id_zona` | texto | — | Zona onde o posto fica. |  |
| `tempo_ciclo_padrao_s` | número | s por unidade, por recurso | Tempo padrão para um recurso processar uma unidade de produto. | Capacidade teórica de um recurso = tempo disponível ÷ tempo de ciclo. |
| `recursos_site_atual` | inteiro | recursos | Recursos em paralelo no site atual. | 0 se o posto não existe hoje. |
| `recursos_projeto` | inteiro | recursos | Recursos em paralelo previstos no projeto da nova unidade. | O grupo deve verificar se são suficientes. |
| `operadores_por_recurso` | número | pessoas | Operadores necessários por recurso em cada turno. |  |
| `disponibilidade_prevista` | número | fração 0–1 | Disponibilidade esperada (parcela do tempo programado sem parada não planejada). |  |
| `eficiencia_prevista` | número | fração 0–1 | Eficiência (performance) esperada em relação ao ciclo padrão. |  |
| `qualidade_prevista` | número | fração 0–1 | Fração de unidades boas. | OEE previsto = disponibilidade × eficiência × qualidade. |
| `investimento_por_recurso_rs` | número | R$ | Investimento para acrescentar um recurso ao posto. |  |

### 27_producao_apontamento — Apontamento de produção do site atual

Apontamento por turno e por posto do site atual da empresa nas últimas semanas. Base do OEE real.

**Granularidade:** Uma linha por dia × turno × posto.

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `data` | data | AAAA-MM-DD | Dia. |  |
| `turno` | inteiro | — | Turno. | 1 = primeiro turno; o de maior número é o noturno. |
| `id_posto` | texto | — | Posto. | Chave para 26_processo_postos. |
| `recursos_ativos` | inteiro | recursos | Recursos em operação no posto. |  |
| `tempo_programado_min` | número | minutos-recurso | Tempo total programado (minutos do turno × recursos). |  |
| `parada_planejada_min` | número | minutos-recurso | Paradas planejadas (refeição, limpeza, reunião). | Não entra no cálculo da disponibilidade. |
| `parada_nao_planejada_min` | número | minutos-recurso | Paradas não planejadas (quebras, falta de material). |  |
| `setup_min` | número | minutos-recurso | Tempo de preparação e troca. |  |
| `quantidade_produzida` | número | unidade_produto | Unidades processadas no turno (boas + refugo). |  |
| `quantidade_refugada` | número | unidade_produto | Unidades refugadas ou retrabalhadas. |  |
| `operadores_previstos` | inteiro | pessoas | Operadores escalados. |  |
| `operadores_presentes` | inteiro | pessoas | Operadores presentes. |  |

### 28_manutencao_os — Ordens de serviço de manutenção do site atual

Doze meses de ordens de manutenção dos recursos do site atual.

**Granularidade:** Uma linha por ordem de serviço (chave: id_os).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_os` | texto | — | Número da ordem. |  |
| `data_abertura` | data | AAAA-MM-DD | Data de abertura. |  |
| `id_posto` | texto | — | Posto do recurso. |  |
| `recurso` | inteiro | — | Número do recurso dentro do posto. |  |
| `tipo_manutencao` | texto | — | Tipo. | CORRETIVA ou PREVENTIVA. |
| `horas_parada` | número | h | Tempo em que o recurso ficou parado. |  |
| `hh_manutencao` | número | Hh | Homens-hora da equipe de manutenção. |  |
| `custo_pecas_rs` | número | R$ | Custo de peças e materiais. |  |
| `causa` | texto | — | Causa apontada. | MECANICA, ELETRICA, LUBRIFICACAO, DESGASTE, AJUSTE_OPERACAO, INSTRUMENTACAO, PLANO_PREVENTIVO. |
| `turno` | inteiro | — | Turno em que a ordem foi aberta. |  |
| `programada` | inteiro | 0/1 | 1 se a parada estava programada. |  |

### 29_pontos_logisticos — Pontos logísticos e terrenos candidatos

Clientes, fornecedores e terrenos candidatos em coordenadas planas. Base do centro de gravidade.

**Granularidade:** Uma linha por ponto (chave: id_ponto).

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `id_ponto` | texto | — | Código do ponto. | L01... = clientes e fornecedores; TA, TB, TC = terrenos candidatos. |
| `nome_ponto` | texto | — | Nome do ponto. |  |
| `tipo_ponto` | texto | — | Natureza. | CLIENTE, FORNECEDOR, TERRENO_CANDIDATO. |
| `x_km` | número | km | Coordenada X (leste) em relação a Salvador. | Coordenadas aproximadas, em plano. |
| `y_km` | número | km | Coordenada Y (norte) em relação a Salvador. |  |
| `volume_t_mes` | número | t/mês | Volume mensal movimentado entre o ponto e a nova unidade. | Vazio para terrenos. |
| `custo_frete_rs_t_km` | número | R$/(t·km) | Custo unitário de transporte. | Vazio para terrenos. |

### 30_localizacao_fatores — Fatores qualitativos de localização

Pesos e notas dos três terrenos candidatos para o método da pontuação ponderada.

**Granularidade:** Uma linha por fator.

| Campo | Tipo | Unidade | Descrição | Domínio e observações |
|---|---|---|---|---|
| `fator` | texto | — | Fator de localização. |  |
| `peso_pct` | número | % | Peso do fator. | Soma = 100. |
| `nota_terreno_a` | inteiro | 0–10 | Nota do terreno A (o escolhido pela empresa). |  |
| `nota_terreno_b` | inteiro | 0–10 | Nota do terreno B. |  |
| `nota_terreno_c` | inteiro | 0–10 | Nota do terreno C. |  |

## Parâmetros da tabela 01_projeto_parametros

| Parâmetro | Unidade | Descrição |
|---|---|---|
| `empresa` | texto | Nome fictício da empresa do estudo de caso. |
| `empreendimento` | texto | Nome do empreendimento. |
| `cidade` | texto | Município da nova unidade. |
| `data_inicio_projeto` | data | Primeiro dia útil do projeto (dia útil 1). |
| `data_corte_historico` | data | Último dia coberto pelos arquivos CSV. |
| `data_status` | data | Data de status do trabalho: fim da semana de campo, que o grupo lança no sistema. |
| `data_contratual_entrega` | data | Data de conclusão prevista em contrato com o cliente interno/investidor. |
| `orcamento_custo_direto_rs` | R$ | Soma do orçamento da linha de base (tabela 12). |
| `administracao_local_orcada_mes_rs` | R$/mês | Custo indireto mensal orçado (equipe de gestão, canteiro, consumos). |
| `bdi_pct` | % | Benefícios e Despesas Indiretas aplicados sobre o custo para formar o preço de venda. |
| `preco_venda_contrato_rs` | R$ | Preço de venda do contrato de implantação. |
| `multa_atraso_dia_rs` | R$/dia útil | Multa contratual por dia útil de atraso em relação à data contratual. |
| `ganho_operacional_dia_rs` | R$/dia útil | Margem de contribuição que a nova unidade gera por dia útil em operação. |
| `jornada_h_dia` | h | Jornada normal por dia útil. |
| `limite_hora_extra_dia_h` | h | Máximo de horas extras por pessoa por dia. |
| `adicional_hora_extra_pct` | % | Acréscimo de custo da hora extra com reflexos. |
| `efetivo_maximo_canteiro` | pessoas | Máximo de trabalhadores simultâneos que as áreas de vivência do canteiro comportam (NR-18). |
| `meta_ppc_pct` | % | Meta de PPC da empresa. |
| `sistema_operacional` | texto | Sistema de gestão que será implantado na nova unidade. |
| `unidade_produto` | texto | Unidade de volume da operação. |
| `demanda_alvo_dia` | unidade_produto/dia | Demanda de projeto que a nova unidade deve atender no pico. |
| `turnos_nova_unidade` | turnos/dia | Número de turnos previsto. |
| `horas_por_turno` | h | Duração de cada turno. |
| `paradas_planejadas_pct` | % | Parcela do turno reservada a paradas planejadas; desconte do tempo disponível ao calcular o takt. |
| `capacidade_site_atual_mes` | unidade_produto/mês | Capacidade nominal mensal do site atual da empresa. |

## Convenções oficiais de cálculo

1. **Duração (atividades ESFORCO):** arredondar para cima (quantidade_orcada × rup_orcada_hh_un ÷ (efetivo da equipe × 8 h)). Efetivo = soma das pessoas em 07_atividade_recursos.
2. **Rede:** TI → início ≥ término da predecessora + defasagem; II → início ≥ início da predecessora + defasagem. Tudo em dias úteis; o dia útil 1 é `data_inicio_projeto`.
3. **Linha de base:** todas as atividades nas datas mais cedo. **Valor planejado (VP):** custo orçado da atividade distribuído linearmente pelos dias úteis da sua duração na linha de base.
4. **Avanço físico da atividade:** soma de `quantidade_executada` ÷ `quantidade_orcada` (limitado a 100%). **Valor agregado (VA):** avanço × custo orçado total da atividade.
5. **Custo real (CR):** soma de `valor_rs` das categorias diretas (tudo menos INDIRETO) até a data. IDC = VA ÷ CR; IDP = VA ÷ VP; EnT = ONT ÷ IDC.
6. **PPC:** pacotes com `concluido` = 1 ÷ pacotes planejados na semana. **RUP real:** Hh apontadas (normais + extras) ÷ quantidade executada.
7. **Disponibilidade de equipamento:** 1 − (corretiva + preventiva) ÷ horas disponíveis. MTBF = horas operando ÷ falhas. MTTR = horas de corretiva ÷ falhas.
8. **Tempo disponível por dia na operação:** turnos × horas por turno × 3.600 s × (1 − paradas planejadas). Takt = tempo disponível ÷ demanda-alvo do dia.
9. **Capacidade do posto:** recursos × tempo disponível ÷ tempo de ciclo × OEE previsto. OEE = disponibilidade × eficiência × qualidade.
10. **OEE real (tabela 27):** disponibilidade = tempo operando ÷ (programado − parada planejada), com tempo operando = programado − planejada − não planejada − setup; eficiência = (quantidade × ciclo padrão) ÷ tempo operando; qualidade = (produzida − refugada) ÷ produzida.
