# Changelog
Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

Este formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)
e este projeto utiliza para versionamento o padrão `YY.0M.MICRO`, conforme [Calendar Versioning](http://calver.org/).

## [Não Publicado]
## [23.09.2] - 2023-09-15
### Adicionado
- Task para sincronizar usuários a partir do Égide e Athenas (DPE-TO)(!1796)
- Novos tipos Petição Inicial e habeas corpus Nos Tipos de Fases dos Processos (DPE-AC)(!1800)
- Painel Lateral de Avisos Pendentes (DPE-TO)(!1759)

### Corrigido
- Correção verificação se há credencial MNI de cadastro em consulta processo Projudi (DPE-PR)(!1794)
- Correção calculo hipossuficiência na model Renda (DPE-PR)(!1793)

## [23.09.1] - 2023-09-06
### Adicionado
- Adiciona filters assistido_id ao DocumentoViewSet (DPE-PR)(!1773)
- Adiciona novo tipo edital ao módulo de inscrições em plantão com listagem de inscritos (DPE-PR)(!1765)
- Correção cálculo hipossuficiência (DPE-PR)(!1784)
- Correção modal retorno agora (DPE-PR)(!1785)
- Erro ao usar "Atendimento inicial agora" quando não há forma de atendimento por mensagem (DPE-PR)(!1789)
- Mostrar alerta remessa de atendimento somente para defensoria destino (DPE-PR)(!1790)
- Adiciona configuração personalizada para impressão do totem (DPE-ES)(!1775)
- Serializar os demais objetos referentes ao endpoint de prédios (V2) (DPE-PR)(!1631)
- Validade em triagem de assistido (DPE-PR)(!1739)

### Modificado
- Exibir tipo de pedido nas solicitações de diligência (DPE-TO)(!1761)
- Adição de paginação na tela de avisos pendentes (DPE-PA)(!1754)
- Enviar mensagem única para solicitação de documentos em massa para evitar span (DPE-ES)(!1766)
- Adição da redistribuição por defensor na tela de avisos pendentes (DPE-PA)(!1777)
- Adiciona responsividade PC / Tablet aos templates do totem (DPE-ES)(!1778)
- Altera API para serviço assistidos-documentos receba arquivos por URL (DPE-PR)(!1783)
- Permite que supervisionados do defensor também possam atender pelo totem (DPE-ES)(!1788)

### Corrigido
- Erro ao chamar assistido em Recepção e ao exibir Painel de Senhas (DPE-TO)(!1769)
- Erro no carregamento e exibição de informações na Busca de Presos e Prisões (DPE-TO)(!1767)
- Resolve erro na aba documentos local variable 'atendimento_online' referenced before assignment (DPE-ES)(!1774)
- Ajusta filtro de requerentes no painel CRC (DPE-ES)(!1772)
- Falha ao editar usuário (DPE-SE)(!1781)
- Erro ao salvar hora do atendimento (DPE-PR)(!1771)

## [23.08.1] - 2023-08-10
### Adicionado
- Configuração limitar máximo de tentativas de consulta a processo desatualizado (DPE-TO)(!1743)
- Exibir informação que o processo é sigiloso ou bloqueado (DPE-TO)(!1743)
- Configuração para adicionar prefixo de hiperlinks "tel" (DPE-TO)(!1749)
- Configuração de logo da defensoria ao lado esquerdo (na tela de login) (DPE-RR)(!1706)
- Criação de opção rápida para ir ao final do atendimento (DPE-PR)(!1746)
- Permitir baixar todos dos documentos do propac de uma vez (DPE-TO)(!1738)
- Sistema de Totem (DPE-ES)(!1730)
- Possibilita envio de perguntas ao assistido através de notificações Luna (DPE-PR)(!1748)
- Incluir forma atendimento presencial/remoto na busca de atendimentos (DPE-TO)(!1752)
- Configuração para exibição de alertas em atendimentos não encerrados (DPE-AM)(!1760)
- Criar permissão para exclusão/desativação de atendimento realizado (DPE-PR)(!1758)
- Adição do Campo do INFOPEN no módulo do LIVRE (DPE-PA)(!1755)
- Configuração para ativar/desativar persistência do número do agendamento originado do CRC (DPE-ES)(!1764)
- Configuração para bloquear/desbloquear extra-pauta para agendamento via CRC (DPE-ES)(!1764)
- Configuração para salvar atendimento sem finalizar/realizar (DPE-AM)(!1654)
- Configuração para solicitar documento automaticamente (DPE-ES)(!1464)
- Auto-reload que é realizado a cada 3 minutos no Painel CRC (DPE-ES)(!1464)
- Botão de solicitação de documentos (não automático) no Painel CRC (DPE-ES)(!1464)
- Monitorar situação dos documentos (coluna extra para o Painel CRC) (DPE-ES)(!1464)
- Redistribuição em aguardando análise (permissão) no Painel CRC (DPE-ES)(!1464)
- Filtro por nome do requerente no Painel CRC (DPE-ES)(!1464)
- Filtro por status dos documentos no Painel CRC (DPE-ES)(!1464)
- Filtro persistente (se mantem durante a navegação) no Painel CRC (DPE-ES)(!1464)
- Apresentar identificador de Nome Social para o Painel CRC (DPE-ES)(!1464)
- Formatação de texto para o histórico do atendimento para organizar o texto de perguntas e respostas (DPE-ES)(!1464)
- Permissões dedicadas ao CRC para melhor controle e direcionamento de papéis (DPE-ES)(!1464)
- Módulo de envio de perguntas (somente para DPE-ES) (DPE-ES)(!1464)
- Status de "não tem" para os documento da Ficha de Atendimento (DPE-ES)(!1464)

### Modificado
- Incluir detalhes e filtros no endpoint Processos v2 (DPE-TO)(!1726)
- Listar avisos com distribuição por CPF mesmo quando flag de distribuição por defensoria estiver ativa (DPE-PR)(!1751)
- Mantém clique do popover em box pessoas para permitir copiar conteúdo (DPE-ES)(!1753)
- Painel CRC modificado para acompanhar os totais baseados no filtro (DPE-ES)(!1464)
- Admin de Perguntas para o Luna modificado, apresentando qualificações específicas e colunas extras (DPE-ES)(!1464)
- API de recebimento de documentos modificada para aceitar múltiplos documentos (PDF+PDF; PDF+IMAGEM; IMAGEM+IMAGEM) (DPE-ES)(!1464)

### Corrigido
- Erro ao adicionar pessoas em Detalhes do Atendimento (Recepção) (DPE-TO)(!1743)
- Exibição de documentos vinculados da aba EPROC/SEEU/PJE (DPE-PA)(!1744)
- Erro ao excluir atividade extraordinária (DPE-TO)(!1750)
- Correção de permissão ausente no endpoint v1 área (DPE-TO)(!1747)
- Erro ao alterar cadastro do servidor (DPE-TO)(!1757)

## [23.07.1] - 2023-07-21
### Adicionado
- Configuração para exibir nome social no pré-cadastro (129) (DPE-SE)(!1736)
- Fórmula para nome do cônjuge no GED (DPE-SE)(!1737)
- Hiperlink "tel://" nos telefones para acionamento automático do Webex (DPE-TO)(!1704)
- Integração do Solar com o sistema de relatório da DPE-PA (DPE-PA)(!1701)
- Adicionar voz ao painel de senhas (DPE-SE)(!1719)
- Integração de atendimentos com Rocket.Chat (DPE-PR)(!1591)

### Modificado
- Incluido URL do Metabase no endpoint Relatório API v2 (DPE-RO)(!1688)
- Ajustado parâmetros endpoint POST Relatório API v2 (DPE-RO)(!1688)
- Permitir editar o nome de no cadastro de Servidor (DPE-SE)(!1725)
- Permitir incluir documentos em indeferimento mesmo quando está em outro setor (DPE-TO)(!1702)

### Corrigido
- Inversão de defensorias no registro automático das cooperações em remetimentos (DPE-PR)(!1728)
- Valor devido da calculadora de pensão alimentícia (DPE-AM)(!1729)
- Criar grupos de permissão faltantes no comando de geração (DPE-TO)(!1713)

## [23.06.1] - 2023-06-12
### Adicionado
- API Distribuição de Avisos (DPE-RO)(!1698)
- API v2 Painel de Avisos (DPE-RO)(!1715)
- Endpoints para obter defensorias e supervisores do usuário logado (DPE-TO)(!1721)

### Modificado
- Refatoração listagem de documentos (DPE-ES)(!1710)
- Otimizar requisição que traz dados de defensorias (V2) (DPE-PR)(!1707)
- Ajustes API V2 Para Módulo Recepção (DPE-RO)(!1714)

### Corrigido
- Erro ao peticionar (DPE-ES)(!1712)
- Link para exibição de processos na tela de avisos (DPE-ES)(!1711)
- Erro ao salvar Sexo/Gênero do Assistido via API v1 (Luna) (DPE-TO)(!1716)
- Erros ao enviar manifestação para análise (DPE-ES)(!1717)
- Erro ao salvar sistema webservice nas manifestações avulsas (DPE-RO)(!1722)
- Links Fases Processuais Para o Minio Storage (DPE-RO)(!1723)

## [23.05.2] - 2023-05-30
### Adicionado
- Calculadora de Pensão (por data de vencimento e período) (DPE-AM)(!1700)
- Calculadora de Execução Penal (DPE-AM)(!1700)
- Configuração para exibir logo da defensoria ao lado esquerdo (DPE-RR)(!1705)
- Parametrização do campo "Gênero" no cadastro do assistido (DPE-SE)(!1699)

### Modificado
- Buscar GEDs pela defensoria (grupo dono) (DPE-TO)(!1686)
- Busca de Qualificações pela área (DPE-SE)(!1692)
- Exibir pautas no agendamento do atendimento (DPE-SE)(!1694)
- Permitir ao usuário copiar informações do "popover pessoa (DPE-PR)(!1695)
- Retira necessidade de config e redefine o filtro por responsável na tela de peticionamentos (DPE-ES)(!1696)
- Filtro para visualizar atendimentos excluídos em Buscar Atendimentos (DPE-SE)(!1697)

### Corrigido
- Tela de Retorno, voltando a exibir o botao liberar (DPE-PE)(!1691)
- Task de cadastro automático de processos cadastrando atendimentos sem vincular à defensoria (DPE-PA)(!1693)
- Erro de loading para processos originários SEEU (DPE-ES)(!1708)

## [23.05.1] - 2023-05-12
### Adicionado
- Incluir suporte a pre-commit (DPE-TO)(!1678)
- Config para exibir fórmulas ged ao editar modelo (DPE-AM)(!1677)
- Indicadores para Meritocracia (DPE-AM)(!1680)
- Cálculo de hipossuficiência na avaliação do assistido específico para SE (DPE-SE)(!1687)

### Modificado
- Acrescentado dado de superusuario na consulta APIv2 de usuarios (DPE-RO)(!1683)
- Melhorias na exibição do cronômetro (DPE-AM)(!1681)
- Permitir enviar documentos não-GED para oficiais de diligência (DPE-TO)(!1661)

### Corrigido
- Corrige erro 'Settings' object has no attribute 'CHATBOT_LUNA_USERNAME' (DPE-ES)(!1676)
- Erro ao salvar documento do assistido (DPE-AM)(!1679)
- Memory Error na aba documentos do Atendimento (DPE-PA)(!1682)
- Opção "Excluir" não aparece para eventos em edição de indeferimentos (DPE-TO)(!1684)
- Impressão de comprovante de agendamento não funciona na tela de atendimento (DPE-SE)(!1685)

## [23.04.3] - 2023-04-28
### Modificado
- Ajustar a filtragem de servidores (DPE-PR)(!1673)

### Corrigido
- Gerar número de indeferimento ao salvar (DPE-TO)(!1674)
- Permissão para ver menu at. extra (DPE-TO)(!1674)

## [23.04.2] - 2023-04-20
### Adicionado
- Organização de documetnos GED em pastas (DPE-PR)(!1646)
- Nível de sigilo em eventos e/ou documentos de indeferimentos (DPE-PR)(!1612)
- Anexar documentos do atendimento em fases processuais (DPE-RN)(!1653)
- API v2 Associar Eventos a Defensorias (DPE-RO)(!1668)
- API v2 Servidores (DPE-RO)(!1669)
- Peticionamento inicial em processos 2º grau (DPE-ES)(!1665)

### Modificado
- Ocultar botão "Ver intimação" quando documento não está acessível (DPE-PR)(!1671)
- Ajuste em task de distribuir avisos (DPE-ES)(!1665)

### Corrigido
- Botão "retorno agora" que não funciona em alguns casos de remessa de atendimento (DPE-PR)(!1670)
- Corrigir tela atendimento para cadastrados luna (DPE-ES)(!1665)

## [23.04.1] - 2023-04-17
### Adicionado
- Protocolo de petições não-GED em atendimentos de acordo (DPE-TO)(!1633)
- Cadastro de Processos Sigilosos No PROCAPI e Habilitação nos Autos (DPE-RO)(!1624)
- Filtro OR para buscar avisos que vinculados a Defensor ou Defensoria (DPE-PR)(!1664)

### Corrigido
- Ajustes em choices_url dos relatórios para compatibilidade com a API (DPE-AP)(!1645)
- Corrige e Padroniza Filtros Classe/Assunto/Competencia do Procapi_Client (DPE-RO)(!1662)

## [23.03.4] - 2023-03-30
### Corrigido
- Remove normalização ao gravar credencial do sistema de processo eletrônico (DPE-PR)(!1658)
- Erro cadastro de assistido quando não há endereço cadastrado (DPE-PR)(!1657)
- Erro ao salvar Requerido sem Filiação (DPE-TO)(!1659)

## [23.03.3] - 2023-03-24
### Adicionado
- Disponibilizar API v2 na Funcionalidade Servidores (DPE-RO)(!1636)
- Opção "Não realizada/Advogado constituído" nos status das audiências (DPE-RN)(!1644)

### Modificado
- Refatoração do método que salva assistido e correção ao salvar bairro (DPE-TO)(!1639)
- Consultar avisos do defensor sob demanda (DPE-TO)(!1649)
- Habilitar preenchimento do campo "área" no cadastro do Processo (DPE-RN)(!1643)

### Corrigido
- Erro ao buscar geds pelo número + versão (DPE-TO)(!1641)
- Erro ao exibir peticionamentos sem recibo em arquivo (DPE-TO)(!1642)
- Conflitos Serializer ComarcaSerializer e ComarcaComFilhosSerializer (DPE-TO)(!1650)
- Ocultar defensorias inativas ao remeter atendimento (DPE-PR)(!1651)

## [23.03.2] - 2023-03-10
### Adicionado
- Revogar assinatura de documentos GED (DPE-TO)(!1632)
- Filtros na API v2 (Apps Comarca, Contrib, Processo e Relatório) (DPE-TO)(!1600)
- Criar honorários ao distribuir aviso para Central de Honorários (DPE-TO)(!1629)
- Opção de Gênero "Desconhecimento/Não informado" no Cadastro de Assistido (DPE-ES)(!1618)
- Exibir lista de avisos pendentes na aba "PJE/SEEU" (DPDF)(!1620)
- Task para enviar e-mail com avisos distribuídos para defensor (DPE-TO)(!1621)

### Modificado
- Refatoração da view de identificação de processo (DPE-PA)(!1627)

### Corrigido
- Tratamento de exceções específicas da task de enviar manifestação (DPE-PA)(!1605)
- Exibição de Links de Atendimentos do Tipo Acordo Quando Utilizado MinioStorage (DPE-RO)(!1623)
- NoReverseMatch: Reverse for 'processo_visualizar' with keyword arguments (DPE-TO)(!1625)

## [23.03.1] - 2023-03-02
### Adicionado
- Incluir filtro "curadoria" em Buscar Avisos Pendentes (DPDF)(!1606)
- Adicionar campos e filtros em Buscar Avisos (DPE-TO)(!1613)
- Permitir a visualização do teor do processo a partir da tela de distribuição de avisos (DPE-TO)(!1619)

### Corrigido
- Erro ao consultar procapi quando parâmetros vazios são informados (DPDF)(!1611)
- Erro ao readicionar pessoas que foram removidas do atendimento (DPE-TO)(!1614)
- Erro de duplicidade de número ao criar indeferimento (DPE-TO)(!1615)
- Erro ao alterar classe de petição inicial (DPDF)(!1544)
- Sugestão de Defensoria Responsável não aparecendo (DPE-ES)(!1616)
- Corrige exibição constante de alertas de atendimento não encerrado (DPE-TO)(!1617)

## [23.02.2] - 2023-02-24
### Adicionado
- Criar endpoints básicos de todas models na API v2 (DPE-TO)(!1596)
- Configuração para deixar sugestão de defensor e defensoria opcional na distribuição (DPE-PA)(!1601)
- Incluir informações do usuário ao obter JWT Token (DPE-TO)(!1598)

### Modificado
- Refatoração de consultas no banco de dados (DPE-TO)(!1596)
- Criação de índices no banco de dados (DPE-TO)(!1597)
- Habilitar atualização do documento ao visualizar documento do prazo (DPE-PA)(!1594)
- Deixar facultativo a listagem geral de avisos na tela de distirbuição (DPE-PA)(!1599)

### Corrigido
- Erro ao salvar at. extra: data_referencia: informe uma data/hora válida (DPE-TO)(!1603)
- Não carrega lista de defensorias ao cadastrar visita ao preso (DPE-TO)(!1604)
- Corrige exibição constante de alertas de atendimento não encerrado (DPE-PR)(!1602)
- Corrige filtro na inibição de retornos (DPE-RN)(!1607)

## [23.02.1] - 2023-02-10
### Adicionado
- Adiciona flag que indica se pergunta vinculada a qualificação é obrigatória (DPE-PR)(!1576)
- Solicitar confirmação ao sair de um atendimento não encerrado (DPE-PR)(!1582)
- Correção de verificação de credencial MNI (DPE-PR)(!1583)
- Criação do registro de avisos distribuídos (DPE-PA)(!1555)
- Endpoint para criar usuário/servidor via API v1 (DPE-TO)(!1575)
- Versão 2.0 da API Rest (DPE-TO)(!1580, !1584, !1556, !1589, !1587)
- Habilitar autenticação na API v2 por Json Web Token (JWT) (DPE-TO)(!1592)
- Flag que indica se pergunta vinculada a qualificação é obrigatória (DPE-PR)(!1576)
- Solicitar confirmação ao sair de um atendimento não encerrado (DPE-PR)(!1582)
- Campo de observação nas movimentações dos Propac's (DPE-RN)(!1588)
- Campo "área" em eventos e procedimentos (DPE-RN)(!1590)

### Modificado
- Identificar alteração de aviso relacionado ao mesmo prazo (DPE-TO)(!1578)
- Máscara de telefone nas visualizações do sistema (DPE-TO)(!1579)
- Permissões de agendamento para os grupos de defensorias (DPE-AM)(!1572)
- Inibição de retornos duplicados (DPE-RN)(!1581)
- Permitir arquivar / desarquivar atendimento apenas para lotados (DPE-PR)(!1577)

### Corrigido
- Termos autor e réu em Detalhes do Atendimento (DPE-TO)(!1570)
- KeyError: 'tipo_documento' ao agendar atendimento c/ número de processo (DPE-TO)(!1571)
- Listagem de bloqueios de agenda (DPE-AM)(!1573)
- Pastas criadas em um atendimento inicial não aparecem em att. retorno (DPE-PR)(!1574)
- Correção de verificação de credencial MNI (DPE-PR)(!1583)
- Código de comarca sendo ignorado (DPE-ES)(!1585)

## [23.01.2] - 2023-01-20
### Adicionado
- Controle de processos que estão em acompanhamento/finalizados (DPE-AM)(!1557)
- Configuração para usar o gerenciamento de etiquetas simplificado (DPE-PA)(!1568)

### Modificado
- Gravar credencial do Projudi que cadastrou o processo para utilização em outras requisições (DPE-PR)(!1562)

### Corrigido
- Verificação De Desbloqueio de Agenda ao Registrar Fase Processual (DPE-RO)(!1541)
- Documentos Pessoais "Sumindo" Ao Enviar Manifestação Para Análise (DPE-TO)(!1563)
- Acesso indevido a atendimento da parte contrária vinculado ao mesmo processo (DPE-TO)(!1564)
- Flag "pré-cadastro" não está sendo removida de processos cadastrados via honorários (DPE-TO)(!1567)
- Corrige Template de Reset de Senha (DPE-RO/PE)(!1566)
- Correção nos termos autor e réu em Detalhes do Atendimento (DPE-TO)(!1570)

## [23.01.1] - 2023-01-16
### Adicionado
- Incluir novos documentos do peticionamento no final da lista em vez do início (DPE-TO)(!1559)
- Permissão para atender sem a necessidade de liberar atendimento na recepção (DPE-TO)(!1560)
- Suporte ao MINIO (DPE-RO)(!1553)
- Exibir filiação na aba PJE/SEEU (DPDF)(!1554)
- Editar as tarefas (DPDF)(!1554)
- Campo para informar número de processo ao agendar 129/recepção (DPDF)(!1554)
- Regra de distribuição para emenda de iniciais (DPDF)(!1554)

### Modificado
- Ordenar avisos pela data final dos prazos (DPDF)(!1554)
- Vincular Etiquetas por Defensoria/Servidor (DPDF)(!1554)

### Corrigido
- Erro ao carregar admin das tarefas de atendimento (DPE-ES)(!1552)
- Erro ao adicionar novo anexo em peticionamento (DPE-TO)(!1558)

## [22.12.3] - 2022-12-15
### Adicionado
- Campo usuario_requisicao, habilitando consulta processual ao Projudi-PR (DPE-PR)(!1549)
- Busca de honorários marcados como impossibilidade e suspensos (DPE-TO)(!1548)
- Permitir a Restrição de Qualificações por Defensoria (DPE-RO)(!1545)

### Modificado
- Accordion dos documentos do atendimento "sem pasta" vir sempre aberto e no final (DPE-TO)(!1546)

### Corrigido
- Correções e otimizações de desempenho (DPE-TO)(!1547)
- From_email p/ notificações de peticionamento e relatório de plantão (DPE-TO)(!1550)

## [22.12.2] - 2022-12-08
### Adicionado
- Criar pastas para documentos do atendimento (DPE-PR)(!1506)
- Máscara para valor em peticionamento e altera nome de exibição da model Processo (DPE-ES)(!1503)

### Corrigido
- Erro na listagem da defensoria responsável pela cooperação (DPE-AP/TO)(!1542)
- Erro ao exibir data do mês anterior mesmo com DIA_LIMITE_CADASTRO_FASE habilitada (DPE-PE/TO)(!1540)

## [22.12.1] - 2022-12-05
### Adicionado
- Configuração para habilitar/desabilitar inserção de imagens externas no GED (DPE-TO/RO)(!1518)
- Baixar imagens externas do GED ao liberar para assinatura (DPE-TO)(!1518)
- Insere informação da atuação (se existir) na lista de atendimentos (DPE-PR)(!1526)
- Arquivar/Desarquivar atendimento (DPE-PR)(!1411)
- Configuração de Ordenação de Modelo GED por Nomeo (DPE-RO)(!1534)
- Notificação por e-mail ao realizar um agendamento, Retorno, Encaminhamento (DPE-AC)(!1502)
- Salvar/recuperar configurações do Constance em disco (DPE-TO)(!1538)
- Incluir Suporte ao Constance Versão Database (DPE-RO)(!1528)
- Exibir informação da atuação (se existir) na lista de atendimentos (DPE-PR)(!1526)
- Permitir excluir indeferimento e evento de indeferimento (DPE-TO)(!1480)
- Exibir prazo de ciência na busca de avisos pendentes (DPE-TO)(!1527)
- Configuração para habilitar/desabilitar inserção de imagens externas no GED (DPE-TO)(!1518)

### Modificado
- Mostra atendimentos somente de assistidos ativos no painel CRC (DPE-PR)(!1514)
- Melhorias no guichê, adição do tipo sala (DPE-AM)(!1519)
- Habilitar filtro de defensor em avisos mesmo quando distribuição por defensor estiver desabilitada (DPDF/TO)(!1525)
- Incluir em configurações avançadas configs criadas anteriormente (DPE-AM)(!1524)
- Etiquetar avisos distribuídos apenas para defensor (DPE-TO)(!1520)
- Identificar quais prioridades podem ser usadas para peticionamento inicial (DPE-TO)(!1517)

### Corrigido
- Incluir Cadastro de Identidade de Genero (Template DPE-RO)(DPE-RO)(!1535)
- Erro ao criar processos a partir dos avisos (DPE-PA/RO/ES)(!1532, !1536, !1533)
- Erro Na Alteração de Dados Gerais do GED (DPE-RO)(!1530)
- Mostrar atendimento somente de assistidos ativos no painel CRC (DPE-PR)(!1514)
- Busca por prioridades e etiquetas não retorna dados (DPDF/TO)(!1537)
- Grupo de defensorias para agendamento (DPE-AM)(!1523)
- SMTPNotSupportedError /password_reset/ (DPE-SE/TO)(!1522)
- Erro ao salvar histórico de acesso de processo / distribuir processos manualmente (DPE-TO)(!1513)

## [22.11.1] - 2022-11-04
### Adicionado
- Criação simplificada do documento GED para peticionamento (DPE-PA)(!1482)
- Gerenciar Etiquetas das Defensorias (DPDF/DPE-TO)(!1501)
- Inserir Etiquetas nos Avisos (DPDF/DPE-TO)(!1501)
- Filtrar Avisos por Prioridade e Etiqueta (DPDF/DPE-TO)(!1501)
- Exibir Prioridades nos Avisos e Processos (DPDF/DPE-TO)(!1501)
- Botão para redistribuir avisos no Painel de Avisos (DPDF/DPE-TO)(!1501)
- Botão p/ Enviar Mensagem Whatsapp sem a Lista de Documentos (129/recepção) (DPDF/DPE-TO)(!1501)
- Configuração para Remover Nome do Defensor da Mensagem Whatsapp (DPDF/DPE-TO)(!1501)
- Configuração para Definir Tipo de Telefone Padrão no Cadastro do Assistido (DPDF/DPE-TO)(!1501)
- Adicionada Regra para Distribuição por Usuário Webservice (DPDF/DPE-TO)(!1501)

### Modificado
- Altera ícone submenu convênios (DPE-PR)(!1500)
- Inserir link nos atendimentos agendados do CRC que indica quais atendimentos já foram realizados/agendados(DPE-PR)(!1498)
- Inclusão de segundo webservice para consulta de CEP (DPE-ES)(!1507)
- Ordenação das perguntas das qualificações (Luna) (DPE-PR)(!1505)
- Altera ícone submenu convênios (DPE-PR)(!1500)
- Registrar todas consultas de processos e documentos no PROCAPI (DPE-TO)(!1511)
- Exibir ID do Documento em vez do Evento em Processos PJE (DPDF/DPE-TO)(!1501)

### Corrigido
- Erro ao atualizar categoria de agenda no painel CRC (DPE-PR)(!1499)
- Verifica se variável exibir_vulnerabilidade_digital foi definida (DPE-PR)(!1504)
- Template sem validação retornando erro 500 para visualizar petição inicial/intermediaria (DPE-ES)(!1508)
- Correção na Exibição do Número de Telefone ao Salvar Assistido (DPDF/DPE-TO)(!1501)
- Correção da task de cadastro automático de processos a partir dos avisos (DPDF/DPE-TO)(!1501)
- Correção no filtro de avisos por localidade (DPDF/DPE-TO)(!1501)

## [22.10.1] - 2022-10-21
### Adicionado
- Criação de menu Convênios com possibilidade de inclusao de submenus (DPE-PR)(!1490)
- Grupos de defensorias para agendamento (DPE-AM)(!1467)
- Limites na quantidade de acumulações de defensores por defensoria (DPE-PA)(!1441)
- Opções de vulnerabilidade digital nos atendimentos (DPE-AM)(!1466)
- Petição inicial em plantão usando o parâmetro do MNI-PJE (DPE-PA)(!1474)

### Modificado
- Atualizar defensoria responsável pelo processo ao distribuir avisos (DPE-TO)(!1481)
- Destacar demandas do móulo CRC com qualificação especializada (DPE-PR)(!1488)
- Insere filtro que mostra somente atuações que possuam defensorias com categorias na criação de agenda (DPE-PR)(!1493)
- Possibilitar atribuir categoria a pedidos de agendamento do CRC (DPE-PR)(!1489)

### Corrigido
- Comarcas sem varas vinculadas sumiram da lista ajax de comarcas (DPE-TO)(!1478)
- Defensores com atuação futura não aparecem na lista p/ criar agenda (DPE-TO)(!1484)
- Erro ao consultar assistido via API (DPE-PR)(!1494)
- Erro ao marcar retorno em atendimentos que originaram de processos (DPE-TO)(!1483)
- Erro ao reenviar manifestação inicial com apenas um documento ou com documento sem nome (DPE-TO)(!1495)
- Ignorar Documento de Identidade NONE (DPE-TO)(!1491)
- Impedir que manifestação excluída (desativada) seja peticionada (DPE-ES)(!1496)
- Respostas a pedidos de apoio estão com a edição bloqueada (DPE-TO)(!1479)

## [22.09.5] - 2022-09-28
### Adicionado
- Configuração para destravar bloqueio na edição do bairro e logradouro (DPE-TO)(!1476)

### Modificado
- Enviar flag para indicar ao PROCAPI para forçar protocolo de manifestação travada (DPE-TO)(!1472)

### Corrigido
- Correção na sugestão de distribuição de avisos (DPE-ES)(!1471)
- Permitir preencher bairro e logradouro em CEPs gerais (DPE-AP/TO)(!1475)
- Ignorar validação dos CEPs gerais dos municípios (DPE-TO)(!1473)

## [22.09.4] - 2022-09-26
### Adicionado
- Encaminhar atendimento para outra defensoria sem marcar um agendamento (DPE-PR)(!1442)
- Suporte a distribuição de avisos utilizando a defensoria responsável em processos já cadastrados (DPE-RO/ES)(!1456)
- Alteração de dados de contato da defensoria (setor) pelos usuários lotados (DPE-TO)(!1465)

### Modificado
- Validação do CEP no cadastro do assistido (DPE-RO)(!1459)
- Autocomplete na listagem de atuação nos pedidos de cooperações (DPE-PR)(!1461)
- Autocomplete na listagem de tipo de documentos de atendimento (DPE-PR)(!1462)
- Usar procedure de banco para gerar número de atendimento na DPE-AM (DPE-AM)(!1468)
- Salvar atendente do procedimento (DPE-AM)(!1469)

### Corrigido
- Task que cadastra processos a partir dos avisos (DPE-ES)(!1427)
- ParameterError: {'page': 'Unknown parameter.'} (DPE-TO)(!1455)
- Erro ao montar árvore de atendimentos (DPE-TO)(!1457)
- Paginação da Busca de Atendimentos (DPE-TO)(!1458)
- Task que envia e-mails com extrato do plantão (DPE-TO)(!1460)
- Filtrar varas pela comarca e grau ao cadastrar processo (DPE-TO)(!1463)

## [22.09.3] - 2022-09-16
### Adicionado
- Campo para indicar que o papel vai marcar o usuário como defensor (DPE-TO)(!1452)
- Filtros 'comarca' e 'papel' em Buscar Servidores (DPE-TO)(!1452)

### Modificado
- Otimiza Performance dos SQL's da Task que Gera Arvore de Atendimentos (DPE-RO)(!1432)
- Não solicitar senha na criação de usuários quando Égide estiver ativado (DPE-TO)(!1452)
- Transferir pessoas para o atendimento unificado (DPE-TO)(!1451)
- Validação se defensor atuou na defensoria no dia da visita ao preso (DPE-TO)(!1448)

### Corrigido
- Duplicidade em código causando erro na distribuição via regex (DPE-ES)(!1444)
- Comarcas com varas em múltiplos graus não aparecem corretamente no cadastro de processos físicos" (DPE-ES)(!1450)
- Listagem de Defensores Na Modal de "Atendimento Agora" (DPE-RO)(!1449)
- Sigla no cadastro estado e local da prisão está como padrão TO (DPE-TO)(!1447)

### Removido
- Campo 'data de nascimento' do cadastro dos servidores (DPE-TO)(!1452)

## [22.09.2] - 2022-09-13
### Adicionado
- Opção "Selecione..." no campo de responsável na distribuição de atendimentos do CRC (DPE-ES)(!1437)
- Visualização dos eventos do processo (na aba TJ) em timeline (DPE-RN)(!1438)
- Campo prioridade na listagem e no filtro da busca de tarefas (DPE-PR)(!1440)

### Corrigido
- Erro ao carregar lista de audiências (DPE-TO)(!1436)
- Listagem de defensores truncada em Gerenciar Agendas e Eventos (DPE-TO)(!1443)

## [22.09.1] - 2022-09-02
### Adicionado
- Versão da DPE-RO do Cálculo de Hipossuficiência (DPE-RO)(!1430)
- Habilitar preenchimento do campo área no cadastro do processo (DPE-RN)(!1429)
- Permissão para registrar fases processuais de forma retroativa (DPE-RO)(!1393)
- Permitir alterar informações do GED na página de atendimento (DPE-RO)(!1375)
- Configuração de tamanho máximo e extensões de arquivo (DPE-TO)(!1428)

### Modificado
- Impedir subir arquivos grandes ou com extensões inválidas no cadastro do assistido (DPE-TO)(!1428)
- Impedir subir arquivos grandes ou com extensões inválidas no atendimento (DPE-TO)(!1428)
- Impedir subir arquivos grandes ou com extensões inválidas nas tarefas (DPE-TO)(!1428)

### Corrigido
- Corrige bug com solicitações (multidisciplinar) sem data de agendamento (DPE-PR)(!1431)
- Erro na visualização de documentos vinculados do PJE (DPE-PA)(!1433)
- Erro ao peticionar quando existe outra manifestação desativada com status na fila (DPE-TO)(!1434)

## [22.08.4] - 2022-08-24
### Adicionado
- Sempre vincular defensor como quem atendeu em visitas ao preso (DPE-TO)(!1415)
- Flag para incluir anotação no endpoint que lista os atendimentos do assistido (DPE-PR)(!1423)

### Modificado
- Transferir atendimento para defensor que atendeu quando mais de está lotado na mesma defensoria (DPE-TO)(!1418)
- Filtrar comarca/vara de acordo com o grau do processo (DPE-TO)(!1425)
- Inserir todos os campos do Atendimento no detalhamento via API (DPE-PR)(!1420)
- Habilitar a opção de definir o horário na tela de Nova Lotação (DPE-RO)(!1405)
- Remove sugestão de nome do arquivo ao selecionar o tipo do documento a ser enviado (atendimento/assistido) (DPE-PR)(!1414)

### Corrigido
- Correção de bugs capturados pelo Sentry (DPE-TO)(!1413)
- Resposta de pedidos de apoio estão sendo salvas com a data limite como data de resposta (DPE-TO)(!1416)
- Atuações criadas por evento itinerante não estão habilitando a assinatura do GED pelos defensores (DPE-TO)(!1417)
- Parâmetros padrão dos relatórios estão sendo perdidos ao atualizar registro (DPE-TO)(!1419)
- Request duplicado na modal de Apoio Operacional (DPE-TO)(!1421)
- Erro ao carregar cadastro assistido quando comarca não é um município (DPDF)(!1422)
- Corrige e aprimora Task procapi cadastrar processos avisos (DPE-ES)(!1424)

## [22.08.3] - 2022-08-20
### Adicionado
- Upload de múltiplos arquivos (DPE-PR)(!1366)
- Auditoria de Login (DPE-RO)(!1410)

### Modificado
- Permitir alterar requerentes/requeridos após o dia do atendimento em Buscar Atendimento (DPE-TO)(!1403)

### Corrigido
- Listagem de defensorias ao registrar transferência de preso (DPE-TO)(!1401)
- Listagem do campo "defensoria responsável" pelo processo (DPE-TO)(!1402)
- Remoção de bens imóveis (DPE-PR)(!1404)
- Bugs capturados pelo Sentry (DPE-TO)(!1406, !1407)
- Script de importação de tipificações do Livre API (DPE-PA)(!1409)

## [22.08.2] - 2022-08-15
### Adicionado
- Campo para ordenação de qualificações (DPE-PR)(!1387)
- Campo que indica se o imóvel é destinado a residência no cadastro do assistido (DPE-PR)(!1398)
- Comando para importar tipificações do LIVRE/SEEU (DPE-TO)(!1390)
- Configuração exibir nome da defensoria na busca de atendimentos (DPE-AM)(!1380)
- Configuração para enviar token por e-mail para criação de senha de novo usuário (DPE-AM)(!1380)
- Configuração para exibir atuação (matéria do ofício) da defensoria na página Calendário de Agendamento (DPE-AM)(!1380)
- Configuração para exibir atuação (matéria do ofício) da defensoria na página Calendário de Agendamento (DPE-PR)(!1386)
- Configuração para habilitar envio de e-mail do disk 129 (DPE-AM)(!1380)
- Configuração para listar atendimentos da aba histórico em ordem decrescente (mais novos primeiro) (DPE-PR)(!1399)
- Configuração para ocultar período da atuação na página Calendário de Agendamento (DPE-PR)(!1386)
- Configuração permitir filtrar ou não as qualificações pela área da defensoria (DPE-AM)(!1380)
- Configuração permitir vincular processos em agendamento inicial não realizado (DPE-AM)(!1380)
- Incluir filtro "defensoria" em Distribuir Avisos" (DPE-ES)(!1388)
- Scrapy de processos do TJ-AM (DPE-AM)(!1380)

### Modificado
- Endereço da defensoria no e-mail do disk 129 (DPE-AM)(!1380)
- Exibir apenas tarefas de atuações ativas (DPE-AM)(!1380)
- Exibir nome da vara no lugar do código (DPE-ES)(!1350)
- Ordenar GEDS por data de modificação descrescente (DPE-AM)(!1380)
- Permitir cadastrar múltiplas atuações quando defensoria é multirão (DPE-AM)(!1380)
- Pode agendar somente quem faz parte da Defensoria ou do disk 129 (DPE-AM)(!1380)
- Substituir links de redirecionamento do TJ para Consulta Processual do SOLAR (DPE-RO)(!1395)
- Utilização do campo regex de Defensoria/Vara na página Distribuição de Avisos (DPE-ES)(!1389)

### Corrigido
- Campo "Defensoria Responsável" não está filtrando os dados corretamente ao cadastrar processo (DPE-TO)(!1391)
- Correção no Load Balance NGINX (DPE-ES)(!1392)
- Distribuição de avisos por órgão julgador (DPE-ES)(!1388)
- Erro de consumo de memória ao organizar documentos do atendimento por pastas (DPE-RO)(!1379)
- Erro de migrations de relatórios (DPE-AM)(!1380)
- Labels da página de Registrar Recurso de Indeferimento (DPE-AM)(!1380)
- Mensagens de erro para inscrições em plantões (DPE-PR)(!1396)
- Permissão para exibir botão "Informações" no disk 129 (DPE-AM)(!1380)
- Script de instalação (DPDF/TO)(!1397)
- Task de distribuição automática de avisos (DPE-ES)(!1388)
- Validar total de documentos enviados antes de finalizar manifestação (DPE-TO)(!1394)

## [22.08.1] - 2022-08-04
### Adicionado
- Importar sistemas e órgãos julgadores do ProcAPI (DPE-TO)(!1384)

### Modificado
- Permitir aos plantonistas fechar qualquer prazo do processo (DPE-RO)(!1381)

### Corrigido
- Deixar estabelecimento penal opcional ao gerar GED pelos formulários dinâmicos (DPE-ES)(!1372)
- Erro de memória ao obter lista de defensores/defensorias (usar API) (DPE-TO)(!1377)
- Corrige prefixo de versionamento de api sendo exibido no swagger (DPE-PR)(!1382)
- Garantir o envio de todos os documentos da manifestação ao PROCAPI (DPE-PR)(!1383)
- Bug em signal para atualizar situação do honorário através do GED vinculado (DPE-PR)(!1382)

## [22.07.4] - 2022-07-28
### Adicionado
- Integração com Livre API (DPE-TO)(!1373)
- Baixar Relatórios do SEEU (Situação Carcerária, Atestado de Pena, Linha do Tempo) (DPE-TO)(!1373)

### Corrigido
- Correção avaliação renda novo cadastro assistido (DPE-PR)(!1374)

## [22.07.3] - 2022-07-22
### Adicionado
- Endpoint na API para distribuição de avisos pendentes (DPE-RO)(!1335)
- Campo para classificação de renda no cálculo e hipossuficiência (DPE-PR)(!1346)
- Integração dos módulos Honorários e Peticionamento (DPE-TO)(!1367)
- Avaliação hipossuficiência por tipo de renda na tela do atendimento (DPE-PR)(!1368)
- Flag para mostrar situação assistido em apps (DPE-PR)(!1369)

### Modificado
- Utilizar os nomes descritivos dos arquivos ao invés de hashes ao realizar o download (DPE-PR)(!1359)
- Melhorias visuais e configuração p/ vincular titular do setor ao honorário (DPE-TO)(!1370)

### Corrigido
- Prazos marcados pra fechar não são exibidos p/ defensor substituto (DPE-TO)(!1360)
- Correção avaliação hipossuficiência por tipo de renda (DPE-PR)(!1363)

## [22.07.2] - 2022-07-15
### Adicionado
- Módulo para inscrição em plantões e listagem de inscritos (DPE-PR)(!1324)
- Campo para classificação de renda no cálculo de hipossuficiência (DPE-PR)(!1346)
- Alerta ao criar nova manifestação em processo que já possui manifestação aguardando protocolo (DPE-TO)(!1355)
- Múltiplos filtros para listagem de tarefas e ordenação por prazo (DPE-PR)(!1358)

### Modificado
- Organizar documentos do atendimento peticionados em pastas (DPE-TO)(!1356)

### Corrigido
- Erro ao carregar Painel CRC (MemoryError) (DPE-TO)(!1361)

## [22.07.1] - 2022-07-09
### Adicionado
- Docker-compose para utilizar NGINX c/ Load Balance (DPE-ES)(!1080)
- Incluir anotações do agendamento no Painel do Defensor (DPE-SE)(!1320)
- Registro de tarefas em propacs/procedimentos (DPE-PR)(!1344)
- Alerta para núcleo ao preencher formulário em atendimento (DPE-TO)(!1345)

### Modificado
- Adequar alteração de senha EPROC/SEEU ao PROCAPI (DPE-TO)(!1347)
- Forçar pesquisa antes de mostrar botões de cadastro de pessoa em Detalhes do Atendimento (DPE-TO)(!1341)

### Corrigido
- Remover request duplicado na página de Buscar Presos (DPE-TO)(!1295)
- Erro ao gerar GED em formulário de inspeção que contém um presídio inexistente (DPE-TO)(!1351)
- Listar corretamente defensorias p/ notificação de denegação de atendimento (DPE-TO)(!1352)
- Correção de erro de listagem de avisos (DPE-PR)(!1342)

## [22.06.5] - 2022-06-30
### Adicionado
- Paginação na página Distribuir Avisos Pendentes (DPE-TO)(!1338)
- Opção para não pedir senha por 30 dias ao peticionar (DPE-TO)(!1329)
- Atualizar renda do assistido via API (DPE-PR)(!1339)

### Modificado
- Informar o ID do evento itinerante em que servidor já participa ao cadastrar um novo (DPE-RR)(!1331)
- Filtrar avisos por defensores/defensorias disponíveis p/ análise em peticionamento (DPE-TO)(!1332)

### Corrigido
- Exception: O número da certidão civil não é válido para peticionamento! (DPE-TO)(!1334)
- Peticionamento com classe/assunto inválidos (DPE-TO)(!1336)
- Botão "Salvar" de Processo Extrajudicial não fica habilitado na aba "Processos" (DPE-TO)(!1337)

## [22.06.4] - 2022-06-24
### Adicionado
- Definição de formatos suportados para uploads de arquivos (DPE-RO)(!1317)
- Converter vídeos de manifestações SEEU para WEBM (DPE-TO)(!1328)

## [22.06.3] - 2022-06-20
### Adicionado
- Permitir reenviar manifestações travadas na fila em massa (Na Fila/SOLAR) (DPE-TO)(!1308)
- Model dependente no admin e na API (DPE-PR)(!1314)
- Gerar relatórios itinerante em XLSX (Excel) (DPE-TO)(!1319)
- Filtro por nome na consulta via API a situação do assistido (DPE-PR)(!1322)

### Modificado
- Vincular primeiro documento como petição inicial em peticionamento de novo processo (DPE-TO)(!1316)
- Reiniciar workers do serviço uWSGI de forma randômica (DPE-RO)(!1318)
- Permitir escolher em qual sistema peticionar em processos que tramitam simultaneamente em mais de um sistema (DPE-TO)(!1321)

### Corrigido
- Preenchimento do campo "vara" após protocolo das petições iniciais (DPE-TO)(!1315)
- Seleção de defensor em modal de cadastro de processos extrajudiciais (DPE-RO)(!1325)

## [22.06.2] - 2022-06-10
### Adicionado
- Flag na situação de membros da família para inclusão e dedução no cálculo da hipossuficiência (DPE-PR)(!1298)
- Botão para adicionar novo documento (arquivo) em peticionamento (DPE-TO)(!1303)
- Botão para importar mais arquivos do atendimento em peticionamento (DPE-TO)(!1303)
- Vínculo entre qualificações e órgãos de encaminhamento (DPE-PR)(!1304)
- API: Endpoint para perguntas de qualificações e órgãos de encaminhamento (DPE-PR)(!1305)
- Botão para alterar dados (nome/arquivo) de documentos do peticionamento (DPE-TO)(!1306)

### Modificado
- Permitir alterar apenas dados básicos das pessoas na página de peticionamento (DPE-TO)(!1311)

### Corrigido
- Erro ao identificar sentenças de processos eletrônicos (DPE-TO)(!1302)
- Erro ao agendar em dia com horário disponível (DPE-TO)(!1307)
- Erro ao protocolar petição inicial em atendimento para processo (DPE-TO)(!1309)
- Duplicidade de tipos de at. extraordinárias quando usuário possui várias atuações (DPE-TO)(!1310)

## [22.06.1] - 2022-06-03
### Adicionado
- Modal para alterar classe de processo extrajudicial (DPE-PR)(!1294)

### Modificado
- Otimizar importação e associação de tipos de eventos aos tipos de fases processuais (DPE-TO)(!1300)

### Corrigido
- Salvar cadastrado por/modificado por em visitas ao preso (DPE-TO)(!1296)
- Salvar cadastrado por/modificado por em atendimento recepção (DPE-TO)(!1296)
- Salvar cadastrado por em atendimento 129 (DPE-TO)(!1297)
- Erro ao gerar número de processo extrajudicial (DPE-TO)(!1299)

## [22.05.3] - 2022-05-27
### Adicionado
- Incluir Suporte ao Armazenamento pelo Protocolo S3 - Minio (DPE-RO)(!1259)
- Flag para converter primeiro encaminhamento em inicial (multidisciplinar > defensoria) (DPE-PA/TO)(!1290)
- Flag para ativar/desativar agendamento futuro para equipe multidisciplinar (DPE-PA/TO)(!1290)
- Histórico de concessões e revogações de acesso ao atendimento (DPE-TO)(!1292)

### Corrigido
- Cálculo de hipossufiência no cadastro do assistido (DPE-PR)(!1288)
- Considerar despesas dedutíveis no alerta hipossuficiência do atendimento (DPE-PR)(!1289)
- Erro ao criar nova agenda em defensor sem atuação ativa (DPE-TO)(!1291)

## [22.05.2] - 2022-05-18
### Adicionado
- Download de todos documentos do Atendimento/GED/Assistido (DPE-PR)(!1264)
- Botão para imprimir relatório geral do itinerante (DPE-TO)(!1280)
- Incluir dados do evento no relatório do itinerante (DPE-TO)(!1280)
- Converter vídeos para MP4 V2 furante renvio da Manifestação (DPE-RO)(!1282)
- Possibilitar cadastrar processo não localizado como físico (DPE-ES/TO)(!1281)
- Tabela de correspondências de Varas e Órgãos Julgadores (DPE-ES/TO)(!1285)
- Identificar Vara pelo Sistema WebService (DPE-ES/TO)(!1285)

### Modificado
- Identificar Vara do processo pelo Sistema WebService (DPE-ES/TO)(!1285)

### Corrigido
- Preencher campo "Imóvel" com o valor padrão (DPE-TO)(!1283)
- Salvar o tipo e documento do assistido (DPE-TO)(!1286)
- Salvar cadastrado por/modificado por em visitas ao preso (DPE-TO)(!1284)

## [22.05.1] - 2022-05-13
### Adicionado
- Sigilo de dados de endereço e documentos no cadastro do assistido em  conforme a situação da pessoa (DPE-PR)(!1239)
- Suporte à API do Facilita Móvel para envio de SMS (DPE-AC)(!1255)
- Restrição de acesso as abas da ficha de atendimento quando status for privado (DPE-PR)(!1270)
- Permitir marcar quais requerentes/requeridos serão partes no processo inicial (DPE-TO)(!1277)

### Modificado
- Tratamento da notificação de agendamento extra-pauta via SMS (DPE-AC)(!1255)
- Preencher tipo de documento da petição a partir do nome ou tipo do documento original (DPE-TO)(!1275)
- Esconder prazos já fechados para protocolo da lista de seleção (DPE-TO)(!1276)
- Distribuição de avisos utilizando regras específicas (regex) (DPE-PR)(!1273)

### Corrigido
- Erro ao inserir foto do assistido via arquivo (DPE-TO)(!1268)
- Importação das informações da parte (assistido) de processos SEEU (DPE-PR)(!1271)
- Não é registrado o tipo e documento do assistido quando definido (DPE-PR)(!1278)
- Listagem de tarefas quando defensor possui mais de uma atuação ativa na mesma defensoria (DPE-PI)(!1274)
- Erro ao inserir foto do assistido via arquivo (DPE-TO)(!1268)
- Erro ao recuperar senha de usuário (DPE-TO)(!1269)

## [22.04.3] - 2022-04-20
### Adicionado
- Converter formulário inspeção de estabelecimentos penais em GED/PDF (DPE-TO)(!1263)
- Permitir reenviar manifestações com erro em massa (DPE-TO)(!1265)
- Parametrizar lista de tipos de estabelecimentos penais (DPE-TO)(!1266)
- Telefone, e-mail e destinação do estabelecimento penal (DPE-TO)(!1266)
- Diferenciar estabelecimentos penais inspecionados e não inspecionados (DPE-TO)(!1266)

## [22.04.2] - 2022-04-07
### Adicionado
- Pré-cadastro de assistido em Buscar Atendimento (DPE-RN)(!1248)
- Configuração para identificar qual pergunta de formulário contém o nome do estabelecimento penal (DPE-TO)(!1254)
- Coluna com a data da última inspeção na lista de estabelecimentos penais (DPE-TO)(!1254)
- Filtro por tipo de atividade extraordinária e pergunta e resposta de formulário vinculado (DPE-TO)(!1254)
- Filtro atividade extraordinária por ID (DPE-TO)(!1254)

### Corrigido
- Rolagem automática ao clicar no "x" ao remover horário no Cadastro de Agenda (DPE-RR)(!1242)

## [22.04.1] - 2022-04-01
### Adicionado
- Pré-cadastro de pessoa jurídica pelo 129 (DPE-RN)(!1240)
- Botão mensagem whatsapp em agendamentos efetuados na recepção (DPE-TO)(!1246)
- Botão mensagem whatsapp em procedimentos efetuados 129 (DPE-TO)(!1246)
- Botão mensagem whatsapp em manifestações protocoladas (DPE-TO)(!1246)

### Modificado
- Adequações dos campos no Cadastro do Assistido p/ DPE-RN (DPE-RN)(!1225)

### Corrigido
- Não bloquear campo CPF/CNPJ se o número for inválido (DPE-TO)(!1247)
- Ocultar atuações inativas no calendário de agendamento (DPE-PR)(!1249)
- Barra rolagem no modal de requerentes na ficha de atendimento (DPE-TO)(!1250)

## [22.03.4] - 2022-03-24
### Adicionado
- Bloquear alteração de CPF/CNPJ de assistidos cadastrados (DPE-TO)(!1238)
- Alerta ao tentar alterar nome/razão social de um assistido (DPE-TO)(!1238)
- Flag para proteção de alteração de alguns campos do cadastro do assistido (DPE-TO)(!1238)
- Enviar e-mail p/ assistido c/ confirmação de protocolo da petição (DPE-TO)(!1243)

### Modificado
- Permitir peticionar documento anexado como resposta do recurso "Agendar Resposta" (DPE-RO)(!1241)
- Label Botão "Prender" para "Cadastrar Prisão" (DPE-PR)(!1237)

### Corrigido
- Cálculo hipossuficiência da DPE-PR (DPE-PR)(!1233)

## [22.03.3] - 2022-03-11
### Adicionado
- Situação "Cancelada" em Audiências (DPE-AM)(!1234)
- Assinatura do Assistido no GED (DPE-AM)(!1235)

### Corrigido
- Erro ao atender solicitação de apoio quando existe retorno agendado para o mesmo dia (DPE-PI)(!1232)

## [22.03.2] - 2022-03-08
### Adicionado
- Integração com o Metabase (DPE-TO)(!1228)

## [22.03.1] - 2022-03-02
### Adicionado
- API: Endpoint para listar categorias de agenda (DPE-TO)(!1220)
- Configuração para personalizar mensagem de usuário não encontrado no Égide (DPE-TO)(!1221)
- Incluir recurso "Encaminhar Ofício" ao realizar um atendimento (DPE-AM)(!1207)
- Botão no cabeçalho e menu lateral para acesso ao Django Admin (DPE-TO)(!1226)
- Flag "Exibir Em Atendimento" em Qualificações (DPE-RO)(!1219)

### Modificado
- Retornar mensagem de erro em vez de exceção nas tasks de notificação via Luna (DPE-TO)(!1220)

### Corrigido
- Matrícula sendo substituída pelo Papel ao cadastrar servidor (DPE-TO)(!1222)
- Impedir acesso aos menus Buscar e GED quando usuário não tem permissão (DPE-TO)(!1222)
- Previnir envio de GED sem assinatura no peticionamento (DPE-RO)(!1217)
- Exibição de tarefas de cooperação para assessores (DPE-RO)(!1224)
- Impedir duplo clique ao submeter petição para análise e peticionamento (DPE-RO)(!1218)

## [22.02.3] - 2022-02-17
### Adicionado
- API: Notificação de processos criados ou atualizados e manifestações protocoladas (DPE-RO)(!1152)

### Modificado
- API: Encaminhar agendamento p/ defensoria da parte processual ao agendar retorno (DPE-TO)(!1209)
- API: Não exibir pessoas removidas nas partes do atendimento (DPE-TO)(!1209)
- Exibir servidores inativos em Buscar Servidores (DPE-PI)(!1213)
- Apresentação do Nome Social quando for definido identidade de gênero (DPE-PR) (!1215)

### Corrigido
- Nomenclatura de item dos dados iniciais de estrutura de moradia (DPE-PR)(!1211)
- Visitas de atendimentos unificados não aparecem no histórico (DPE-TO)(!1214)

## [22.02.2] - 2022-02-11
### Adicionado
- Botão encerrar atendimento e voltar ao Painel do Defensor (DPE-AM)(!1202, !1203)
- Ponto de corte na consulta de processos desatualizados (DPE-TO)(!1197, !1204)

### Modificado
- Impedir acúmulo de processos em atualização no Celery (DPE-TO)(!1204)
- Permitir preencher classe, comarca e vara de processo eletrônico não encontrado (DPE-TO)(!1212)

### Corrigido
- AttributeError: 'NoneType' object has no attribute 'isnumeric' (DPE-TO)(!1196)
- Permissão para atividades de pedidos de apoios dos núcleos especializados (DPE-TO)(!1198, !1206)
- Acesso à busca pelo calendário de agendamentos não funciona para assessores (DPE-TO)(!1199)
- Data de agendamento de pré-agendamento está sendo preenchida com a data de cadastro (DPE-TO)(!1200)
- Descrição do campo "Anotações do Agendamento" (DPE-TO)(!1205)
- Sincronização de vara judicial por grau do processo judicial (DPE-RO)(!1201)

## [22.02.1] - 2022-02-07
### Adicionado
- Suporte ao Google Analytics 4 (DPE-TO)(!1187)
- Personalizar descrição do campo "Anotações do Defensor" (DPE-PR)(!1190)
- Configuração para limitar as tarefas cumpridas em dias (DPE-AM)(!1191)
- Exclusão de agendamento a partir do Painel do Defensor (DPE-AM)(!1192)

### Modificado
- Permitir alterar tipo e remover qualquer requerente/requerido do atendimento (DPE-TO)(!1189)
- Recuperar nível de sigilo ao sincronizar dados do processo com o PROCAPI (DPE-TO)(!1193)

### Corrigido
- Conflitos aplicando bloqueios por categoria em todas categorias (DPE-TO)(!1188)

## [22.01.2] - 2022-01-28
### Adicionado
- Data de modificação (auditoria) em Processo, Parte e Fase Processual (DPE-TO)(!1179)
- Campo "simultâneos" ao cadastrar / visualizar uma agenda (DPE-TO)(!1184)

### Modificado
- Acionar task para envio imediato da manifestação sem passar pela fila (DPE-TO)(!1185)

### Removido
- Suporte à API da Luna Chatbot (descontinuado) (DPE-TO)(!1181)

### Corrigido
- Manter máscara ao colar nº do processo judicial (DPE-TO)(!1180)
- Listar corretamente defensorias na criação de evento de desbloqueio (DPE-TO)(!1180)
- Impedir preencher certidão de nascimento c/ numeração inválida (DPE-TO)(!1180)
- Verificar se assistido aderiu à Luna antes de tentar enviar notificação (DPE-TO)(!1181)
- Verificação de bloqueios da agenda do defensor no endpoint de horários disponíveis (DPE-TO)(!1183)

## [22.01.1] - 2022-01-22
### Adicionado
- Formulários personalizados (Formulário de Inspeção) em Atividades Extraordinárias (DPE-TO)(!1089)
- Criar cálculo de hipossuficiência conforme deliberação do PR (DPE-PR)(!1160)
- Exibição de Documentos Vinculados na aba "Processo MNI" (DPE-RO)(!1168)

### Modificado
- Vincular plantonista à defensoria com atuação correspondente (DPE-TO)(!1166)
- Remover máscara de CEP ao salvar endereço (DPE-TO)(!1173)
- Ajustes Model Prioridades do Peticionamento (DPE-RO)(!1159)
- Permitir Selecionar Defensoria Itinerante Durante o Cadastro (DPE-RO)(!1165)
- Implementa Atraso de Envio Simultâneo de Manifestações da Mesma Parte (DPE-RO)(!1170)
- Permitir múltipla escolhas, carregamento ajax e texto longo no Formulário de Inspeção (DPE-TO)(!1174)

### Corrigido
- Duplicidade no cadastro de atuações de plantão (DPE-TO)(!1166)
- Filtro "Defensoria" em "Painel da Recepção" (DPE-TO)(!1169)
- Erro ao tentar notificar assistido via Luna (DPE-TO)(!1172)
- Impedir setores que não podem ver Painel do Defensor de serem vinculados às tarefas (DPE-TO)(!1176)
- Mostrar solicitações de pessoas sem endereço principal no Painel de Diligências (DPE-TO)(!1177)
- Validação de Endereço de Múltiplos requerentes/requeridos Na Petição Inicial (DPE-RO)(!1158)

## [21.12.1] - 2021-12-08
### Corrigido
- Preenchimento de input no peticionamento (DPE-TO)(!1162)

## [21.11.2] - 2021-11-19
### Adicionado
- Lista de opções p/ escolha se defensoria pode aceitar agendamentos (DPE-TO)(!1154)
- Filtrar atendimentos por defensoria em Distribuir Atendimentos (DPE-TO)(!1155)
- Filtrar atendimentos por forma de atendimento em Distribuir Atendimentos (DPE-TO)(!1156)
- Pré-selecionar responsável de retornos em Distribuir Atendimentos (DPE-TO)(!1156)
- Aba "Realizados" em Distribuir Atendimentos (DPE-TO)(!1155)

### Modificado
- Definir remoto como forma atendimento padrão se config ativada (DPE-TO)(!1154)
- Melhorias visuais em Distribuir Atendimentos (DPE-TO)(!1155)
- Só exibir defensorias/defensores vinculados ao usuário em Distribuir Atendimentos (DPE-TO)(!1155)

### Corrigido
- Verificar conflitos de horários no endpoint de horários disponíveis para agendamento (DPE-TO)(!1154)

## [21.11.1] - 2021-11-12
### Adicionado
- Novos filtros no Painel GED + Pasta "De hoje" (DPE-AM)(!1113)
- E-mail no cadastro de servidores (DPE-PI)(!1086)
- Permitir incluir foto de assistido via upload (DPE-RR)(!1139)
- Permitir redistribuir pré-agendamento p/ outra comarca (DPE-TO)(!1142)
- Campo "Sigla" nas categorias de agenda (DPE-TO)(!1144)
- Cadastro simplificado de horários por categoria de agenda (DPE-TO)(!1144)
- Campos presencial/remoto no Cadastro de Agendas (DPE-TO)(!1144)
- Campos presencial/remoto no Painel da Recepção e do Defensor (DPE-TO)(!1144)
- Filtro de horários disponíveis por forma de atendimento na API (DPE-TO)(!1144)
- Exibir tamanho dos arquivos do peticionamento (DPE-TO)(!1148)
- Painel de Senhas (Guichê) (DPE-AM)(!1133)
- Habilitar/desabilitar debug com o VSCode (compatibilidade c/ PyCharm) (DPE-PI)(!1145)
- Filtro de defensoria no endpoint de Atendimentos (DPE-AC)(!1141)

### Modificado
- Parametrizar campo usado na exibição dos assuntos em petição inicial (DPE-TO)(!1136)
- Permitir registrar decisão sem a necessidade de encaminhar (DPE-TO)(!1137)
- Ocultar campo "Vara" em petição pendente e atualizar após protocolo (DPE-TO)(!1138)

### Corrigido
- Impede agendar na pauta ou extra-pauta se não tiver permissão (DPE-PI)(!1085)
- Campo "Imóvel" continua inválido mesmo após escolher uma opção válida (DPE-TO)(!1135)
- Atendimentos em atuações de plantão parciais não são liberados para atendimento (DPE-TO)(!1143)
- Marcar retorno na mesma categoria de agenda do último atendimento via API (DPE-TO)(!1144)
- Mostrar nome do defensor da atuação em "Alterar Defensoria?" de Detalhes do Atendimento (DPE-PE)(!1146)
- Erro ao exibir processo de 2° grau quando possui o mesmo numero de 1° grau (DPE-PI)(!1150)

## [21.10.3] - 2021-10-25
### Adicionado
- Botão para copiar número do processo (DPE-RR)(!1125)
- Endpoint p/ criar e alterar bairros (DPE-AC)(!1127)
- Filtros data inicial e data final no endpoint de atendimentos (DPE-AC)(!1127)
- Envio de SMS quando o assessor recusar o atendimento no painel CRC (DPE-AC)(!1127)
- Autenticação na comunicação entre SOLAR e ProcAPI (DPE-TO)(!1128)

### Modificado
-  Deixar telefones, filiacoes, endereço, renda e moradia opcionais ao alterar pessoa via API (DPE-AC)(!1127)

### Corrigido
- Acesso ao Painel da Recepção quando não há atuação vigente para agendamento (DPE-TO)(!1129)
- Task de cadastro automático de processos e assistidos a partir dos de avisos (intimações) (DPE-PR)(!1130)
- Usar campos de auditoria na exclusão de atendimentos (DPE-TO)(!1131)

## [21.10.2] - 2021-10-18
### Adicionado
- Task de cadastro automático de processos e assistidos a partir dos de avisos (intimações) (DPE-PR)(!1092)
- Botão "Atendimento Inicial Agora" no 129 (DPE-RN)(!1118)

### Modificado
- Alterar defensoria pela página Detalhes do Atendimento (DPE-AM)(!1111)
- Excluir agendamento pela página Detalhes do Atendimento (DPE-AM)(!1111)
- Ignorar partes do tipo "Autoridade" no cadastro automático das partes de processo judicial (DPE-RO)(!1124)

### Corrigido
- Script de instalação com banco de dados vazio (DPE-MT)(!1112)
- Critérios de seleção automática de vara ao peticionar (DPE-RO)(!1116)
- Impedir selecionar processos físicos como originários ao peticionar (DPE-RO)(!1116)
- uWSGI Socket Full (DPE-TO)(!1119)
- Fixture para criar cartórios (DPE-TO)(!1120)
- Usuários não lotados estão aparecendo na lista p/ distribuição no Painel CRC (DPE-TO)(!1122)
- Sobreposição de tooltip em processo do atendimento (DPE-RR)(!1123)

## [21.10.1] - 2021-10-13
### Adicionado
- Conversor de número de certidões do formato antigo para o novo (DPE-TO)(!1109)
- Validação do número de certidão no formato novo (DPE-TO)(!1109)
- Endpoint PATH p/ atualizar telefones na API (DPE-RR)(!1106)

### Modificado
- Identificar defensoria a partir da comarca de pré-agendamentos (DPE-TO)(!1108)

### Corrigido
- Carregamento inicial de classes e assuntos no peticionamento inicial (DPE-RO)(!1099)
- Verificação de documento pendente para envio de notificação (DPE-RO)(!1100)
- Salvar endereço de novo assistido via 129 (DPE-TO)(!1102)
- Notificações Signo em Protocolo de Manifestação (DPE-TO)(!1103)
- Notificações Signo em Indeferimento (DPE-TO)(!1104)
- Listagem de classes e assuntos no peticionamento inicial (DPE-TO)(!1107)
- Pré-agendamentos não estão sendo filtrados pelas lotações do usuário (DPE-TO)(!1115)

## [21.09.1] - 2021-09-23
### Adicionado
- Link de acesso ao teor da última decisão de um indeferimento através da aba histórico do atendimento (DPE-PR)(!1067)
- Suporte Jupyter Notebook c/ Docker (DPE-RO)(!1088)
- Permitir cadastrar Processos Judiciais em caso de falha no webservice do TJ (DPE-RO)(!1095)
- Validação de número de Processo Eletrônico no front-end (DPE-RO)(!1095)
- Permitir atribuição dos nomes dos status das tarefas (DPE-PR)(!1096)
- Botão "Encerrar ligação" em Buscar Qualificação via 129 (DPE-AM)(!1074)
- Botão "Encerrar ligação" em Agendar Atendimento via 129 (DPE-AM)(!1074)
- Campos "Necessidade de ofício" e "Detalhes do ofício" ao agendar (DPE-AM)(!1074)
- Enviar e-mail para o assistido com os procedimentos efetuados no 129 (DPE-AM)(!1074)
- Configuração para exigir endereço completo do assistido no 129 (DPE-AM)(!1074)
- Permissão para mostrar/ocultar botão "Encaminhamento" (DPE-AM)(!1074)
- Permissão para mostrar/ocultar botão "Dúvidas" (DPE-AM)(!1074)
- Registro de informações prestadas ao assistido via 129 (DPE-AM)(!1074)
- Registro de reclamações feitas pelo assistido via 129 (DPE-AM)(!1074)
- Painel de Reclamações (DPE-AM)(!1074)
- Informações do último usuário que respondeu uma tarefa em "Buscar Tarefas" (DPE-AM)(!1074)
- Novos filtros de atendimentos em "Painel da Recepção" (DPE-AM)(!1074)

### Modificado
- Cadastro automático de assistido quando possuir filiação no Procapi (DPE-PR)(!1090)
- Permitir acessar conteúdo da janela que acionou ou editou GED a partir da aba documentos de atendimento (DPE-PR)(!1094)
- Obter Competência/Classe/Assuntos filtrados do PROCAPI nas petições iniciais (DPE-RO/TO)(!1054, !1097)
- Só mostrar botão "Cadastrar" depois de fazer uma busca de pessoa no 129 (DPE-AM)(!1074)

### Corrigido
- Integração de notificações no SIGNO (DPE-RO)(!1064)
- Forçar a data_hora ao excluir objetos do Core (DPE-TO)(!1066)
- Script de instalação (DPE-RN)(!1082)
- Leitura de avisos pendentes pelo defensor (DPE-PR)(!1084)
- Exibir corretamente atuações de plantão que iniciaram ao longo do dia (DPE-TO)(!1087)
- Acesso aos Patrimoniais no Django Admin (DPE-RN)(!1091)
- Listagem de atuações quando passado o parâmetro `apenas_defensor` (DPE-RO)(!1093)

## [21.08.2.1] - 2021-08-31
### Modificado
- Adequar templates do GitLab ao novo padrão da DPE-TO (DPE-TO)(!1079)

### Corrigido
- Aumentar limite de caracteres do campo "mensagem" da Manifestação (DPE-TO)(!1069)
- Erro ao abrir Manifestação com algum aviso selecionado (DPE-TO)(!1077)
- Erro de redirecionamento no botão "Agendar" em Atendimento p/ Processo (DPE-TO)(!1081)

## [21.08.2] - 2021-08-26
### Adicionado
- Conversão de áudios ogg e wav em mp3 ao enviar petição para análise (DPE-TO)(!1068)
- Criar um Processo Extrajudicial a necessidade de um atendimento (DPE-RO)(!1053)

### Modificado
- Adequações dos campos no Cadastro do Assistido p/ DPE-TO (DPE-TO)(!1073)

### Corrigido
- Troca o regex SQL para o regex Python (DPE-TO)(!1065)
- Impedir selecionar prazos já fechados no PROCAPI (DPE-TO)(!1070)
- Impedir editar campo histórico em atendimento p/ processo (DPE-TO)(!1071)
- Tratamento na data para evitar a soma de horas do timezone ao cadastrar fase processual (DPE-ES)(!1075)

## [21.08.1] - 2021-08-11
### Adicionado
- Adicionar filtro de defensor em parte no manager de processos (DPE-RR)(!1042)
- Transferir atendimentos para outra atuação (Django Admin) (DPE-TO)(!1045)
- Permitir realizar Atendimentos Iniciais/Retornos sem precisar passar pela Agenda e Recepção (DPE-RO)(!1046)
- Revogar assinatura de documentos GED (Django Admin) (DPE-TO)(!1048)
- Cadastro de mensagem amigável para o peticionamento (DPE-TO)(!1052)
- Cadastro de mensagem de erro para o peticionamento (DPE-TO)(!1052)
- Bloqueio de exclusão de GED com vínculo a peticionamentos (DPE-TO)(!1056)
- Ícones de GED e anexo na lista de documentos do peticionamento (DPE-TO)(!1056)
- Botões de admin na lista de documentos do peticionamento (DPE-TO)(!1056)
- Configuração da duração da sessão do usuário (DPE-ES)(!1057)
- Habilitar critérios padrão de validação de senhas do Django (DPE-ES)(!1059)
- Configuração do tamanho máximo de uploads de imagens no GED (DPE-TO)(!1061)
- Conversão de imagens jfif em pdf ao enviar petição para análise (DPE-TO)(!1062)

### Modificado
- Ação no django-admin para transferir atendimentos e agendamentos para atuação (DPE-TO)(!1045)
- Atualização da configuração do ambiente de desenvolvimento dev-container (DPE-TO)(!1049)
- Páginas de detalhes do peticionamento (DPE-TO)(!1052)
- Desabilitar cache da tabela Defensoria (DPE-ES)(!1055)
- Simplificar o lançamento de fases processuais (DPE-RO)(!1058)

### Corrigido
- Erro ao exibir tipo de documento em Detalhes do Atendimento (Recepção) (DPE-TO)(!1038)
- Erro excluir atividade multidisciplinar (DPE-TO)(!1039)
- Erro ao abrir prazo quando existe avisos com números iguais (DPE-TO)(!1040)
- Corrigir problema de data/hora no botão "Atender Agora" (DPE-RO)(!1044)
- Busca de documentos ativos do peticionamento (DPE-TO)(!1056)
- Erro de encoding ao salvar foto do assistido (DPE-TO)(!1060)

## [21.07.2] - 2021-07-08
### Adicionado
- Parametrização das mensagens enviadas para Luna (DPE-TO)(!1031)
- Enviar notificação exclusão/encaminhamento externo via Luna (Chatbot e Web) (DPE-TO)(!1036)
- Incluir campo "tipo" nas tarefas e cooperações (DPE-PR)(!1033)
- Incluir campo "tipo" em documentos do assistido e do atendimento (DPE-PR)(!1034)

### Corrigido
- Remover do Painel CRC agendamentos remarcados e de retorno (DPE-TO)(!1035)

## [21.07.1] - 2021-07-02
### Adicionado
- Exibir motivos de exclusão ao excluir agendamento pelo Painel da Recepção (DPE-TO)(!1020)
- Campo "Situação" (agendado/realizado) em Buscar Atendimentos (DPE-AM)(!1027)

### Modificado
- Incluir ids do defensor titular e substituto no endpoint de atendimentos da API (DPE-TO)(!1022)
- Impedir o cadastro de assisto sem antes fazer uma busca no Painel 129 (DPE-AM)(!1027)

### Corrigido
- Pacote de erros disparados no Sentry da DPE-TO após Django 3 (DPE-TO)(!1025)
- Erro ao enviar e-mail de restauração de senha (DPE-RO)(!1026)
- Prevenir duplo clique ao salvar fase processual (DPE-RO)(!1028)
- Página de peticionamento fica "piscando" sem parar até travar o navegador (DPE-TO)(!1029)

## [21.06.4] - 2021-06-25
### Adicionado
- Endpoint GET p/ consulta de defensores e respetivas atuações via API (DPE-TO)(!1020)

### Modificado
- Diminuir requests exagerados ao PROCAPI para obter número da versão (DPE-RO)(!1016)
- Melhorias de desempenho na página "Admin > Defensores" (DPE-TO)(!1020)

### Corrigido
- Erro ao buscar documentos e modelos GED (DPE-RN)(!1018)
- Permitir encaminhar atendimento p/ qualquer área se usuário tem permissão (DPE-PI)(!1019)
- Exibir sorteio em indeferimento se setor tem permissão (DPE-PI)(!1019)

## [21.06.3] - 2021-06-19
### Adicionado
- Incluir campo `hipossuficiente` na resposta do endpoint que salva o assistido (DPE-TO)(!1010)
- Campos "observação" e "é uma designação extraordinária?" nas atuações dos defensores (DPE-PR)(!1009)

### Modificado
- Permitir ignorar validação de certificado na comunicação com e-Defensor (DPE-TO)(!1010)
- Usar o `docker-compose.override.yml` para gerenciar alterações locais no docker-compose (DPE-TO)(!1013)
- Permitir informar o número da versão desejada no `update.sh` (DPE-TO)(!1013)

### Corrigido
- Vincular requerentes secundários ao concluir agendamento pelo CRC (DPE-TO)(!1010)
- Vincular processos ao concluir agendamento pelo CRC (DPE-TO)(!1010)
- Formatação da data nas notificações enviadas para Luna (DPE-TO)(!1010)
- Permissão para defensor plantonista assinar ged nas atuações criadas pela task de plantão (DPE-TO)(!1015)
- Erro ao criar tipo de atividade extraordinária (DPE-PR)(!1017)

## [21.06.2] - 2021-06-14
### Adicionado
- Task para envio de e-mail com extrato de processos cadastrados no plantão (DPE-TO)(!999)
- Adicionar campos de patrimônio no cadastro de assistido via API (DPE-TO)(!1002)
- Enviar confirmação de agendamento via Luna (Chatbot e Web) (DPE-TO)(!845)
- Permitir ignorar validação de cerftificado em `CHATBOT_LUNA_VERIFY_CERTFILE` (DPE-TO)(!845)
- Notificação de agendamento inicial e retorno via Luna (Chatbot e Web) (DPE-TO)(!845)
- Tipo de documento "Resolução" ao cadastrar atuação (DPE-PR)(!1001)
- Registro de logs para abertura de prazos (DPE-RO)(!986)
- Parametrização de Configuração do Chat e-Defensor (DPE-PI)(!981)
- Opção "Sorteio" ao agendar atendimento pelo indeferimento (DPE-PI)(!1007)

### Modificado
- Enviar MimeType dos documentos durante peticionamento com certificado digital (DPE-RO)(!988)
- Parametrização dos filtros de busca (defensoria, defensor) de acordo com as FLAGS selecionado no Config (DPE-RO)(!986)
- Transformado em requisição ajax a abertura de prazos dos avisos (DPE-RO)(!986)

### Corrigido
- Erro ao peticionar quando certidão possui mais de 5 zeros (DPE-TO)(!1000)
- Erro ao agendar retorno a partir de atendimento de plantão (DPE-PI)(!991)
- Tratamento de erros de Bad Gateway (502) do PROCAPI (DPE-RO)(!987)
- Distribuição para defensor ou defensoria (antes era obrigatório informar os 2 ao mesmo tempo) (DPE-RO)(!986)
- Erro ao adicionar assinantes no GED (DPE-TO)(!1005)
- Erro ao agendar a partir de processo (DPE-TO)(!1003)
- Erro em aplicar permissões ao alterar papel do servidor (DPE-TO)(!1006)
- Erro ao identificar defensor da atuação para chat do e-Defensor (DPE-PI)(!1007)

### Modificado
- Permitir informar mais de uma URL em `CHATBOT_LUNA_WEBHOOK_URL` (DPE-TO)(!845)

## [21.06.1] - 2021-06-03
### Adicionado
- Todos os campos para cadastro de assistido via API (DPE-TO)(!996)
- Endpoints PUT/PATCH p/ alteração de assistido via API (DPE-TO)(!997)

### Modificado
- Exibir ligações (pré-cadastro) e atendimentos desativados na API (DPE-TO)(!993)

### Corrigido
- Validar existência CPF/CNPJ antes de cadastrar/atualizar assistido via API (DPE-TO)(!997)

## [21.05.2] - 2021-05-26
### Modificado
- Migração Django 3.2 / Python 3.9

## [21.05.1] - 2021-05-13
### Adicionado
- Tratamento de erros na abertura do prazo de avisos ao peticionar (DPE-RO)(!971)
- Assinar documentos GED automaticamente ao peticionar com certificado A1 (DPE-RO)(!972)
- Task para converter processos físicos em eletrônicos via PROCAPI (DPE-RO)(!974)

### Modificado
- Permitir informar número processo no agendamento inicial via API (DPE-TO)(!969)

### Corrigido
- Exibir motivos de exclusão em anotações (DPE-TO)(!967)
- Alterar qualificação do atendimento pela Ficha do Atendimento (DPE-TO)(!968)
- Erro ao agendar retorno via API (DPE-TO)(!976)
- Inconsistência ao identificar o tipo de fase processual (DPE-TO)(!975)

## [21.04.3] - 2021-04-29
### Adicionado
- Criar atendimento de retorno sem a necessidade de fazer um agendamento (DPE-RO)(!945)
- Configurações Dev-Container (para desenvolvimento com VS Code) (DPE-TO)(!948)
- Painel do CRC (para uso com Luna Web) (DPE-TO)(!964)
- Cadastro de Órgãos p/ encaminhamento de atendimento (DPE-TO)(!964)
- Motivos de exclusão de atendimento (DPE-TO)(!964)

### Corrigido
- Limpar excesso de espaços em brancos na busca de assistidos (DPE-ES)(!962)
- Remover papéis inativos no cadastro de servidores (DPE-ES)(!963)
- Erro ao cadastrar endereços quando está duplicado (DPE-TO)(!966)
- Data/hora assinatura do GED (DPE-RO)(!959)

## [21.04.2] - 2021-04-15
### Adicionado
- Campos para personalizar cabeçalho e rodapé de defensorias em modelos públicos do GED (DPE-TO)(!950)

### Modificado
- Melhorias no endpoint para agendamento inicial via API (DPE-TO)(!949)


## [21.04.1] - 2021-04-09
### Adicionado
- Listar qualificações via API (DPE-TO)(!930)
- Listar horários disponíveis para agendamento por defensoria via API (DPE-TO)(!932)
- Cadastrar assistido via API (DPE-TO)(!931)
- Cadastrar agendamento inicial via API (DPE-TO)(!903)
- Filtro nome e estado no endpoint de municípios na API (DPE-TO)(!931)
- Filtro nome e município no endpoint de bairros na API (DPE-TO)(!931)
- Permissão p/ visualizar todas tarefas do gabinete (DPE-RR)(!940)

## [21.03.1] - 2021-03-31
### Adicionado
- Conversão de imagens em pdf ao enviar petição para análise (DPE-TO)(!902)
- Usar modelo padrão para o grupo ao criar documentos e modelos (DPE-TO)(!910)
- Cadastro de outros parâmetros na petição inicial (DPE-RO)(!913)
- Campos de interesse de conciliação e justificativa do não interesse no atendimento (DPE-RN)(!856)
- Suporte à distribuição automática de avisos por Polo e Competência (DPE-RO)(!921)

### Modificado
- Migração para a biblioteca Sentry SDK (DPE-TO)(!914)
- Remover máscara do telefone ao copiar para área de transferência (DPE-TO)(!916)
- Mostrar petições com erro primeiro na Busca de Peticionamentos (DPE-TO)(!992)

### Corrigido
- Obrigatoriedade do campo vara (orgão julgador) (DPE-TO)(!904)
- Só abrir avisos não fechados e sem comunicação (DPE-TO)(!904)
- Esconder defensorias de atuações futuras na página de peticionamento (DPE-TO)(!915)
- Elemento inexistente no chat (DPE-RR)(!908)
- Erro de memória ao requisitar jsreverse (DPE-PR)(!912)
- Impedir marcar avisos fechados ao criar petições (DPE-RO)(!901)
- Impedir enviar manifestações pra fila se falha na assinatura de documentos com token (DPE-TO)(!1368)

## [21.02.2] - 2021-02-25
### Adicionado
- Suporte ao ProcAPI 21.02.3 (baseado no Django 3.1) (DPE-TO)(!897)

### Corrigido
- Correções ortográficas no módulo Honorários (DPE-TO)(!898)
- Correções ortográficas no módulo Indeferimento (DPE-TO)(!898)

### Removido
- Suporte à versões anteriores do ProcAPI (DPE-TO)(!897)

## [21.02.1] - 2021-02-12
### Modificado
- Permitir editar dados e reenviar petição com erro no protocolo (DPE-TO)(!889)
- Permitir remover documento GED do peticionamento quando tiver mais de um (DPE-TO)(!889)
- Exigir informar pelo menos um autor e um réu na petição inicial (DPE-TO)(!889)
- Exigir informar CNPJ de pessoa jurídica em petições iniciais (DPE-TO)(!889)

### Corrigido
- Ignorar pedidos de apoio no calendário de agendamento (DPE-PR)(!883)
- Impedir usuários comuns de ver todos os documentos e modelos do GED (DPE-ES)(!884)
- Unificação de anotações de atendimento e processo (DPE-ES)(!886)
- Validação para finalizar GED ao peticionar (DPE-TO)(!885)
- Erro ao peticionar quando já existem documentos assinados (DPE-TO)(!888)
- Gerando duplicidade de peticionamentos (DPE-TO)(!889)
- Limpar formatação do código do cálculo judicial da petição automaticamente (DPE-TO)(!889)
- Impedir o peticionamento quando pessoa tem certidão sem o tipo informado (DPE-TO)(!889)
- Ordenar as petições aguardando análise por data de registro crescente (DPE-TO)(!889)

## [21.01.2] - 2021-01-22
### Adicionado
- Suporte à distribuição de avisos por defensoria (DPE-RO)(!873)

### Corrigido
- Distribuição de Avisos por Defensoria (DPE-RO)(!876)
- Arquivo Migration Assistido 0039 (DPE-TO)(!877)
- Remover caixa alta e validar formato do e-mail no cadastro do assistido (DPE-TO)(!879)
- Erro ao tentar assinar GED com usuário sem permissão (DPE-TO)(!878)
- Duplicidade de qualificações ao cadastrar processo sem atendimento (DPE-TO)(!702)

## [21.01.1] - 2021-01-14
### Adicionado
- Recurso de tentativas na abertura de prazos dos Avisos (DPE-RO)(!871)

### Corrigido
- Inconsistência ao identificar o tipo de fase processual (DPE-TO)(!869)
- Erro ao agendar no plantão quando atuação foi iniciada após a meia-noite (parcialmente vigente) (DPE-TO)(!867)
- Botão "Abrir indeferimento" some quando nome da defensoria é muito grande (DPE-TO)(!868)

## [20.12.3] - 2020-12-17
### Adicionado
- Campo "Atendimento coletivo" para núcleos (DPE-TO)(!855)
- Vínculo entre Defensoria e Tipos de Atividade Extraordinária (DPE-TO)(!859)
- Tipos de absolvição imprópria (medida de segurança) ao resultado da sentença (DPE-TO)(!861)
- Página de busca de defensorias e associação com at. extraordinárias (DPE-TO)(!862)

### Modificado
- Permitir selecionar responsáveis pela atividade extraordinária (DPE-TO)(!860)
- Filtra o tipo de atividade extraordinária conforme a defensoria (DPE-TO)(!859)

## [20.12.2] - 2020-12-10
### Adicionado
- Abrir prazo ao peticionar em aviso pendente de abertura (DPE-TO)(!854)

### Corrigido
- Erro ao salvar processo vinculado a ação (classe) em área (DPE-TO)(!857)

## [20.12.1] - 2020-12-04
### Adicionado
- Novos filtros "comarca" e "defensor" na página "Distribuir Avisos Pendentes" (DPE-TO)(!852)
- Pré-visualização dos últimos movimentos processuais na página "Distribuir Avisos Pendentes" (DPE-TO)(!852)

### Modificado
- Comando para importar tipos de evento do PROCAPI (DPE-TO)(!851)

## [20.11.4] - 2020-11-26
### Modificado
- Painel de Distribuição Avisos Pendentes (Distribuição Automática) (DPE-TO)(!848)
- Substituir selecionar e avançar por avançar ao escolher processo para peticionamento (DPE-TO)(!849)
- Colocar botões de ação logo após o conteúdo do lado direito em vez de no final da página (DPE-TO)(!849)
- Permitir excluir manifestações com erro de protocolo (DPE-TO)(!849)
- Link direto para petição em andamento ao clicar no botão "Peticionar" na página de Avisos Pendentes (DPE-TO)(!849)

### Corrigido
- Correção no cálculo da numeração de processo extrajudicial + numeração 2021 (DPE-TO)(!847)
- Se usuário logado é um defensor, só mostra o nome dele ao peticionar (DPE-TO)(!849)
- Não somar avisos fechados ou expirados no painel de total de avisos pendentes (DPE-TO)(!849)
- Exibir corretamente datas na seleção de prazos para fechamento (DPE-TO)(!849)

## [20.11.3] - 2020-11-20
### Adicionado
- Criar fase processual ao registrar petições (DPE-TO)(!842)
- Comando para importar tipos de evento do PROCAPI (DPE-TO)(!842)
- Painel de Distribuição Avisos Pendentes (Distribuição Manual) (DPE-TO)(!844)
- Cadastro de Associação de Varas às Defensorias (DPE-TO)(!844)

### Modificado
- Ajuste no código do e-defensor (DPE-RR)(!824)

## [20.11.2] - 2020-11-12
### Adicionado
- Suporte ao Thoth Signer (Assinador Utilizando Certificado A1) (DPE-RO)(!832)
- Recurso para importar varas, classes, assuntos e competências do ProcAPI (DPE-TO)(!837)
- Suporte ao debug de código em container docker com VSCode (DPE-TO)(!838)
- Permissão para alterar agendamentos de qualquer comarca (DPE-TO)(!839)

## [20.11.1] - 2020-11-05
### Modificado
- Atualização Google Analytics (gtag.js) (DPE-TO)(!828)
- Ajustes visuais na página "Buscar Avisos Pendentes" (DPE-TO)(!830)

### Corrigido
- Link para "Ver Intimação" quando aviso não possui evento vinculado (DPE-TO)(!830)

## [20.10.4] - 2020-10-30
### Adicionado
- Grupos de patrimônios e fórmula de cálculo de avaliação da DPE-RN (DPE-TO)(!823)
- Cadastro de Sistema Web Service pelo Django Admin (DPE-TO) (!809)
- Cadastro de Varas da Defensoria pelo Django Admin (DPE-TO) (!809)
- Cadastro de Competência pelo Django Admin (DPE-TO) (!809)
- Cadastro de Assuntos da Qualificação pelo Django Admin (DPE-TO) (!809)
- Preenchimento automático da peticão inicial conforme dados do atendimento (DPE-TO) (!809)

### Corrigido
- Validação para não permitir data final menor que inicial em Buscar Atendimentos, Processos e Tarefas (DPE-ES)(!826)

## [20.10.3] - 2020-10-23
### Adicionado
- Configuração para calcular o número de membros e renda familiar automaticamente (config `CALCULAR_RENDA_FAMILIAR_E_MEMBROS_ASSISTIDO`) (DPE-TO)(!818)
- Tipo de evento no peticionamento (DPE-TO)(!820)

## [20.10.2] - 2020-10-15
### Adicionado
- Incluir certidão de nascimento/casamento no cadastro do assistido (DPE-TO)(!815)

### Modificado
- Permitir definir ordem dos arquivos para peticionamento (DPE-TO)(!813)

### Corrigido
- Exibição da data final na aba "Defensorias" da página "Defensores" (DPE-ES)(!814)

## [20.10.1] - 2020-10-09
### Adicionado
- Adicionar Suporte A Petição Com Assinatura De Documentos Por Certificado Digital A3 Token (DPE-RO)(!795)
- Fila no Celery p/ entrega e atualização de manifestações (DPE-TO)(!808)

### Modificado
- Liberar GED para assinatura automaticamente ao enviar para análise (DPE-TO)(!811)
- Assinar documentos GED automaticamente ao peticionar com as credenciais válidas (DPE-TO)(!811)

### Corrigido
- Impedir agendar no mesmo dia/horário (DPE-TO)(!807)

## [20.09.7] - 2020-09-28
### Adicionado
- Painel de Avisos Pendentes (Intimações) (DPE-TO)(!803)

### Modificado
- Layout da página Buscar Avisos Pendentes (Intimações) (DPE-TO)(!803)
- Incluir filtros: defensor, tipo e situação na página Buscar Avisos Pendentes (Intimações) (DPE-TO)(!803)
- Validar usuário/senha do consultante antes de colocar petição na fila para protocolo (DPE-TO)(!804)

## [20.09.6] - 2020-09-28
### Adicionado
- Permitir ativar/desativar busca automática de processos no ProcAPI em Buscar Processos (DPE-RO)(!799)

## [20.09.5] - 2020-09-18
### Adicionado
- Página Buscar Avisos Pendentes (Intimações) (DPE-TO)(!796)
- Permitir fechar prazos de avisos (intimações) ao peticionar (DPE-TO)(!796)

## [20.09.4] - 2020-09-15
### Modificado
- Recuperar credenciais e definir usuário logado como manifestante do peticionamento (DPE-TO)(!791)

## [20.09.3] - 2020-09-10
### Adicionado
- Incluir dados de auditoria da consulta aos processos (DPE-PR)(!775)
- Incluir IP do cliente na consulta aos documentos dos processos (DPE-PR)(!775)
- Opção "Encaminhar" ao remarcar agendamento pelo 129 (DPE-TO)(!789)

## [20.09.2] - 2020-09-08
### Adicionado
- Configurações `PROCESSO_CALCULADORA_CALCULO_URL` e `PROCESSO_CALCULADORA_CONSULTA_URL` (DPE-TO)(!784)
- Campo "Código do Cálculo Judicial" no peticionamento inicial (DPE-TO)(!784)

## [20.09.1] - 2020-09-04
### Adicionado
- Campo "Competência Judicial" no peticionamento inicial (DPE-TO)(!782)

### Corrigido
- Excluir modelo e documento GED (DPE-TO)(!780)

## [20.08.2] - 2020-08-21
### Adicionado
- Peticionamento em processo novo (inicial) (DPE-TO)(!764)
- Peticionamento em processo existente (interlocutória) (DPE-TO)(!753)
- Página de busca/acompanhamento de petições (DPE-TO)(!757)
- Criar pacote de arquivos para peticionamento (DPE-TO)(!754)
- Task para monitorar protocolo das petições (DPE-TO)(!759)
- Task para enviar documentos das petições (DPE-TO)(!760)
- Chat e-Defensor (DPE-RR)(!763)
- Painel administrativo para TI (DPE-TO)(!769)

## [20.08.1] - 2020-08-06
### Adicionado
- Personalização da Forma de Atendimento padrão (DPE-TO)(!758)
- Forma de Atendimento ao cadastrar visita ao preso (DPE-TO)(!758)
- Forma de Atendimento ao alterar visita ao preso (DPE-TO)(!758)
- Situação do Indeferimento com a ação tomada (DPE-TO)(!765)

### Modificado
- Obrigatoriedade de o defensor selecionar uma Forma de Atendimento (DPE-TO)(!758)

### Corrigido
- Visualização dos Indeferimentos baixados no histórico (DPE-TO)(!765)

## [20.07.2] - 2020-07-14
### Adicionado
- Vínculo automático de pessoa jurídica ao cadastrar novo processo eletrônico (DPE-RO)(!752)
- Permissão para acesso ao filtro "Servidor" nos relatórios (DPE-TO)(!755)

### Corrigido
- Diferenciar retornos das solicitações de apoio (DPE-TO)(!756)

## [20.07.1] - 2020-07-03
### Adicionado
- Página de Busca de Tarefas (DPE-TO)(!748)
- Configuração para alterar o nome do módulo Atendimento (config `NOME_MODULO_ATENDIMENTO`) (DPE-SC)(!747)
- Configuração exibir/ocultar campo "Data/Hora Término" de Audiência (config `EXIBIR_DATA_HORA_TERMINO_CADASTRO_AUDIENCIA`) (DPE-TO)(!747)
- Coluna "Responsável" em Buscar Atendimento (config `BUSCAR_ATENDIMENTO_EXIBIR_COL_RESPONSAVEL`) (DPE-SC)(!747)
- Colunas "Vara" e "Tipo" em Buscar Audiência (DPE-SC)(!747)

### Modificado
- Permitir cadastrar o mesmo número de processo em graus diferentes (DPE-TO)(!743)
- Usar nome do documento em vez da uuid ao baixar arquivo (DPE-SC)(!747)
- Preencher horário de término da audiência automaticamente (DPE-SC)(!747)
- Preencher defensor responsável pela audiência automaticamente (DPE-SC)(!747)

## [20.05.4] - 2020-05-28
### Adicionado
- Config para permitir recebimento de negativa antes do registro do recurso de indeferimento (DPE-TO)(!533)

### Corrigido
- Permitir usuário acessar indeferimentos de defensorias das suas outras lotações (DPE-RO)(!736)

## [20.05.3] - 2020-05-22
### Adicionado
- Permitir alterar documento da atuação do defensor (DPE-TO)(!727)
- Envio de SMS com [Movile](https://api-messaging.movile.com/v1/send-sms) (DPE-RR)(!708)
- Usando NGINX na imagem Docker para ganho de performace (DPE-RO)(!728)
- Minificação/Compressão inicial de CSS, JS e HTML (DPE-RO)(!730)

## [20.05.2] - 2020-05-14
### Adicionado
- Mostrar setor solicitado em pedido de apoio no histórico do defensor (DPE-TO)(!722)
- Botões "Primeira Página" e "Última Página" na navegação do Painel GED (DPE-TO)(!723)
- Configuração para permitir criar anotação em agendamento (DPE-TO)(!725)

### Corrigido
- Inconsistências ao criar agendas quando defensorias são desmarcadas (DPE-TO)(!721)

## [20.05.1] - 2020-05-07
### Adicionado
- Anotações do agendamento e recepção de agendamentos remarcados ou excluídos (DPE-TO)(!716)
- Funções SQL para o relatório de Quantitativo de Agendamentos e Atendimentos Agrupado (DPE-TO)(!710)
- Funções SQL para o relatório de Quantitativo de Atividades Agrupado (DPE-TO)(!710)

### Corrigido
- Contagem de dias na mini-ficha do LIVRE (DPE-TO)(!712)
- Acesso ao Django > Processo > Parte (DPE-TO)(!713)
- Cadastrar novo Encaminhamento 129 pelo Django Admin (DPE-TO)(!714)
- Critérios para permissão de cadastro/alteração/exclusão de fases processuais (DPE-TO)(!717)

## [20.04.4] - 2020-04-30
### Adicionado
- Envio de documentos do assistido via ajax (DPE-TO)(!700)
- Reabrir atendimento de diligência finalizado (DPE-TO)(!705)

### Modificado
- Permitir cadastrar substituição em titularidade de vigência futura (DPE-TO)(!707)
- Só fazer distribuição de agendamento com intervenção do usuário (DPE-PI) (!640)

### Corrigido
- Impedir registrar audiência realizada com data futura (DPE-TO)(!698)
- Mostrar botões de ações após incluir requerente em atendimento para processo (DPE-TO)(!701)
- Impedir cadastro duplicado de evento de indeferimento (DPE-TO)(!703)
- Impedir cadastro de evento/agenda com data final menor que inicial (DPE-TO)(!704)

## [20.04.3] - 2020-04-16
### Adicionado
- Campo "Data expedição RG" no cadastro de assistido (DPE-TO)(!695)
- Recurso de atividades extraordinárias no Painel do Defensor (DPE-TO)(!696)

## [20.04.2] - 2020-04-06
### Adicionado
- Campo "multiplicador" no registro de atividades de atendimentos (DPE-TO)(!690)

## [20.04.1] - 2020-04-02
### Adicionado
- Exibir data e usuário que respondeu documento agendado (DPE-TO)(!684)
- Listar documentos do atendimento na API (DPE-TO)(!685)
- Receber documentos pendentes na API (DPE-TO)(!686)
- Análise de Documentos Pendentes enviados via API (DPE-TO)(!687)
- Consultar Defensorias via API (DPE-TO)(!688)

## [20.03.2] - 2020-03-21
### Adicionado
- Campo "Forma de Atendimento" para o atendimento (DPE-TO)(!680)

## [20.03.1] - 2020-03-04
### Adicionado
- Campo "Defensoria" às fases processuais (DPE-TO)(!677)

## [20.02.2] - 2020-02-20
### Adicionado
- Configuração para habilitar registro de atividades em pedidos de apoio dos núcleos especializados (DPE-TO)(!670)
- Download de documentos judiciais via ProcAPI (DPE-TO)(!672)
- Acesso aos processos judiciais relacionados via ProcAPI (DPE-TO)(!672)
- Incluir informações detalhadas dos patrimônios do assistido (DPE-RO)(!671)

## [20.02.1] - 2020-02-11
### Adicionado
- Configuração para gerar relatórios no formato XLSX sem paginação (DPE-TO)(!667)
- Select2 aos filtros da página 'Relatórios' (DPE-TO)(!667)

## [20.01.1] - 2020-01-31
### Adicionado
- Central de Relatórios (DPE-TO)(!553, !658)

## [19.12.3] - 2019-12-27
### Adicionado
- Migração interna de servidores (DPE-TO)(!656)

## [19.12.2] - 2019-12-19
### Adicionado
- Permissão para realizar atendimentos retroativos (sem necessidade de criar evento) (DPE-CE)(!648)

## [19.12.1] - 2019-12-11
### Adicionado
- Permitir remarcar encaminando para outra defensoria (DPE-TO)(!646)

## [19.11.5] - 2019-11-29
### Adicionado
- Configuração para remover cooperações cumpridas do painel do setor solicitado (DPE-TO)(!639)

## [19.11.4] - 2019-11-22
### Adicionado
- Permissão para encaminhar atendimento p/ defensoria de área diferente (DPE-TO)(!635)

## [19.11.3] - 2019-11-20
### Modificado
- Esconder campos de Atividades Extraordinárias quando só há uma opção disponível para escolha (DPE-TO)(!632)

## [19.11.2] - 2019-11-13
### Adicionado
- Scripts para instalação e atualização via Docker (DPE-TO)(!622)

## [19.11.1] - 2019-11-12
### Adicionado
- Recurso de atividades extraordinárias no Painel da Equipe Multidisciplinar (DPE-TO)(!614)
- Incluir campo "Nº Presentes" nas Atividades Extraordinárias (DPE-TO)(!606)
- Registrar atendimentos a crianças na brinquedoteca (DPE-TO)(!615)
- Permissão para acesso ao filtro "Defensor" nos relatórios (DPE-TO)(!619)

## [19.10.4] - 2019-10-25
### Adicionado
- Parametrização do campo "Situação" do Assistido (DPE-CE)(!601)
- Campo data/hora de término de audiência (DPE-CE)(!588)

### Corrigido
- Obrigando preencher CPF, mesmo quando a opção "não possui" está marcada (DPE-RO)(!602)

## [19.10.3] - 2019-10-22
### Modificado
- Permitir escolher o defensor ao agendar no itinerante (DPE-TO) (!604)
- Mostrar agendas comum por padrão ao encaminhar atendimento do itinerante (DPE-TO) (!604)
- Remover restrição de evento itinerante na mesma regional (DPE-TO) (!604)
- Restringir adicionar servidores em eventos que acontecem simultaneamente (DPE-TO) (!604)
- Possibilitar a recuperação do histórico não salvo (DPE-TO) (!604)

## [19.10.2] - 2019-10-17
### Modificado
- Aumento do tamanho do campo de descrição na solicitação de apoio operacional (DPE-CE)(!590)
- Relatório "Atividades Anual - Recursal", adicionado sub-relatório "GEDs Assinados" (DPE-TO)(!559)
- Configuração para mostrar pergunta de acesso público/privado em todos os atendimentos (DPE-TO)(!597)

### Corrigido
- Validação do CPF na página Cadastro do Assistido (DPE-RO)(!595)
- Habilitar preenchimento de valores monetários no cadastro de assistido na aba avaliação apenas quando valor setado como sim (DPE-RO)(!598)

## [19.10.1] - 2019-10-10
### Adicionado
- Funcionalidade de Atividades Extraordinárias (DPE-CE/DPE-TO)(!554, !586)
- Parametrização do campo "Orientação Sexual" (DPE-CE)(!576)
- Parametrização do campo "Identidade de Gênero" (DPE-CE)(!582)
- Relatório de "PERFIL DE ASSISTIDOS ATENDIDOS E ATENDIMENTOS" (DPE-TO)(!583)

### Corrigido
- Relatório "ATIVIDADES DA EQUIPE MULTIDISCIPLINAR" (DPE-TO)(!593)

## [19.09.1] - 2019-09-26
### Adicionado
- Permitir importar documentos dos atendimentos vinculados ao PROPAC (DPE-CE)(!570)
- Configurado no Admin Django a personalização de quais informações serão exibidas em cada atendimento da Lista de Atendimentos do Assistido (DPE-RO)(!568)
- Parametrização de menus adicionais (extras) (ajuda, manuais, vídeos, sistema antigo) (DPE-TO)(!565)

### Modificado
- Inserção da Anotação do Defensor/Atendente na Lista de Atendimentos do Assistido (DPE-RO)(!568)
- Aplicar cor e logo personalizáveis na página de login (DPE-RR)(!551)
- Configuração para mostrar anotação do defensor dentro ou fora dos detalhes no histórico de atendimentos (DPE-RO)(!574)

### Corrigido
- Exibição do botão "Editar qualificação" mediante permissão correspondente (DPE-TO)(!563)
- Verifica se o CPF está vazio antes de aplicar máscara (DPE-RR)(!569)
- Mostrar atividades multidisciplinar de outras atuações vigentes na mesma comarca (DPE-CE)(!566)

## [19.08.5] - 2019-08-22
### Adicionado
- Novos filtros "resultado" e "tipo de baixa" em Buscar Indeferimentos (DPE-TO)(!550)
- Usar Docker para deploy em ambiente de homologação (DPE-TO)(!495)
- Atalhos para marcar retorno/encaminhamento no Painel da Recepção (DPE-TO)(!555)

### Corrigido
- Exibição de indeferimentos recebidos (removidas prateleiras deferidos e indeferidos) (DPE-CE)(!560)
- Copiar atividades e participantes de atendimento multidisciplinar para novo agendamento (!557)
- Impedir a exclusão de agendamento que contenha atividades vinculadas (!557)

### Adicionado
- Funções de banco de dados para buscar relatórios GED assinados (DPE-TO)
- Relatório de GEDs Assinados para a turma recursal (DPE-TO)

## [19.08.4] - 2019-08-06
### Corrigido
- Data de nascimento no popover descontando um dia (DPE-CE)(!540)

## [19.08.3] - 2019-08-07
### Modificado
- Liberar cadastro de múltiplos indeferimentos no mesmo atendimento se não for no mesmo dia (DPE-TO)(!552)

## [19.08.2] - 2019-08-02
### Adicionado
- Relatório de "ATENDIMENTOS - QUANTITATIVO DE AGENDAMENTOS AGRUPADO" (DPE-TO)(!550)

### Modificado
- Adicionado o filtro por Diretoria no Relatório "ATENDIMENTOS - AGENDAMENTOS POR PERÍODO" (DPE-TO)(!550)

## [19.08.1] - 2019-08-01
### Corrigido
- Erro ao abrir diligência com documentos pendentes (DPE-TO)(!549)

## [19.07.6] - 2019-07-24
### Modificado
- Identificar defensor com diferentes usuários em webservices MNI (DPE-TO)(!547)

## [19.07.5] - 2019-07-22
### Adicionado
- Bloqueio de agendas por categoria (DPE-TO)(!545)

### Corrigido
- Ordem dos arquivos de migração de banco de dados (DPE-TO)(!546)

## [19.07.4] - 2019-07-19
### Corrigido
- Ordenar eventos da aba "Processos Judiciais" do Atendimento pela data de protocolo (DPE-TO)(!543)
- Redirecionamento link documento do painel do defensor para documento do atendimento (DPE-TO)(!543)
- Atualização dependência psycopg2 (2.8.3) (DPE-TO)(!543)

## [19.07.3] - 2019-07-17
### Adicionado
- Enviar mensagem ao assistido via chatbot (DPE-TO)(!327)

### Corrigido
- Atendimento sendo liberado antes do dia do agendamento (DPE-TO)(!542)

## [19.07.2] - 2019-07-15
### Corrigido
- Declaração de Mudança de Endereço - mostrar endereço principal ativo (DPE-TO)(!541)
- Erro ao alterar visita (DPE-TO)(!536)

## [19.07.1] - 2019-07-04
### Modificado
- Padronização de ícones para a biblioteca Font Awesome 5.0 (DPE-TO)(!507)

## [19.06.7] - 2019-06-27
### Modificado
- Marcar modelos de documentos eletrônicos (GED) como públicos (DPE-TO)(!482)
- Agrupar processos de indeferimentos por classe (DPE-TO)(!535)

### Corrigido
- Erro ao usar templatetags com caracteres especiais nos modelos de documentos eletrônicos (GED) (DPE-CE)(!534)

## [19.06.6] - 2019-06-17
### Modificado
- Permitir que setor solicitante finalize alertas (DPE-TO)(!532)

### Corrigido
- Erro ao criar alertas (DPE-TO)(!532)
- Erro ao vincular documento a um atendimento válido (DPE-TO)(!532)

## [19.06.5] - 2019-06-11
### Modificado
- Relatório de Atividades Anuais - Recursal, filtro por comarca (DPE-TO)(!531)

## [19.06.4] - 2019-06-07
### Adicionado
- Finalizar tarefas/cooperações/alertas em massa (DPE-TO)(!529)

### Corrigido
- Erro ao gerar XLSX do relatório "ATENDIMENTOS - TEMPO DE ESPERA (DPE-TO)(!528)

## [19.06.3] - 2019-06-05
### Corrigido
- Relatório "ATENDIMENTOS - TEMPO DE ESPERA": coluna "Atendido por" não corresponde ao registrado (DPE-TO)(!524)
- Inconsistência ao avaliar renda do assistido na página "Atender" (DPE-TO)(!525)
- Diligências pendentes sendo listadas como finalizadas (DPE-TO)(!526)

## [19.06.2] - 2019-06-04
### Adicionado
- Opção "Reavaliar Decisão" em processo de indeferimento (DPE-TO)(!520)
- Opção "Anotações" em processo de indeferimento (DPE-TO)(!523)

## [19.06.1] - 2019-06-03
### Modificado
- Permitir registrar baixa de indeferimento sem decisão (DPE-TO)(!522)

### Corrigido
- Parte sem endereço não aparece no Painel de Diligências (DPE-TO)(!519)
- Erro ao baixar documentos do atendimento (DPE-TO)(!521)

## [19.05.10] - 2019-05-31
### Corrigido
- Erro ao excluir visita dentro do prazo (DPE-TO)(!516)
- Erro ao gerar relatório de Atividades da Multidisciplinar (DPE-TO)(!517)
- Regras para finalizar tarefas (DPE-TO)(!518)

## [19.05.9] - 2019-05-30
### Adicionado
- Inclusão da nova configuração para ativação do eSAJ (DPE-CE)(!467)
- Campo "modificado por" em atendimentos (DPE-TO)(!514)

### Modificado
- Cadastro Nova Fase Processual - Trazer alguns campos preenchidos automaticamente (DPE-CE)(!467)
- Tornar o campo Defensoria Responsável não obrigatorio caso modo eSAJ ativo (DPE-CE)(!467)
- Remover bloqueio de cadastro de processo por número inválido caso modo eSAJ ativo (DPE-CE)(!467)
- Novas regras para geração de nome de usuário quando nomes são similares (DPE-CE)(!477)
- Nacionalidade e País de origem de novo assistido vir por padrão Brasil (DPE-TO)(!505)

### Corrigido
- Erro ao gerar declaração de hipossuficiência no cadastro de nova pessoa (DPE-CE)(!508)
- Salvando novo município/uf do assistido pelo 129 (DPE-CE)(!511)
- Ignorar retornos na listagem de atendimentos do Painel Simplificado (DPE-CE)(!512)

## [19.05.8] - 2019-05-29
### Adicionado
- Configuração de "Pode Assinar GED" ao criar lotação de servidores (DPE-TO)(!492)
- Botão de adicionar nova lotação ao cadastrar novo usuário (DPE-TO)(!492)
- Dados de login na busca de usuários (DPE-TO)(!492)

### Modificado
- Botão de Carta Convite via assistido modificado para modal dentro da aba Documentos (DPE-TO)(!492)
- Detalhes do atendimento, aba documentos: botão Novo Anexo padronizado com botão da Ficha de Atendimento (DPE-TO)(!492)
- Detalhes do atendimento, aba documentos: botão Novo GED padronizado com botão da Ficha de Atendimento (DPE-TO)(!492)
- Botões de ver/editar modificados com ícone e retirada de texto (DPE-TO)(!492)

### Corrigido
- Cadastro de usuários: erro na importação de script angularJS (DPE-TO)(!492)

## [19.05.7] - 2019-05-27
### Modificado
-  Acesso a múltiplos setores no Painel de Indeferimentos (DPE-TO)(!509)

## [19.05.6] - 2019-05-24
### Modificado
- Bloquear cadastro de evento itinerante pra mesma defensoria e período (DPE-TO)(!501)

### Corrigido
- Salvar anotação quando há mais de um defensor na mesma defensoria (DPE-TO)(!506)

## [19.05.5] - 2019-05-24
### Modificado
- Cadastro Nova Fase Processual - Trazer alguns campos preenchidos automaticamente (DPE-CE)(!467)

### Corrigido
- Limitar caracteres da caixa de texto do motivo de exclusão (DPE-TO)(!500)
- Criado um novo filter para formatação de CEP (DPE-CE)(!474)
- Permissão para usuário comum acessar API (DPE-TO)(!499)
- Redirecionamento inválido ao rodar sob HTTPS (DPE-TO)(!499)
- Filtragem dos atendimentos no Painel Simplificado (DPE-TO)(!503)

## [19.05.4] - 2019-05-17
### Adicionado
- Botão "Transferir" parte processual dentro da aba de Processos (DPE-TO)(!488)
- Tarefa entre setores (cooperação) (DPE-TO)(!487)
- Prateleiras de alertas e cooperações por defensoria no Painel do Defensor (DPE-TO)(!487)
- Devolver tarefa/cooperação para solicitante (DPE-TO)(!487)

### Modificado
- Melhorias na visualização das respostas das tarefas (em linha de tempo) (DPE-TO)(!487)
- Permitir escolher múltiplos setores para notificação de denegação de procedimento (DPE-TO)(!493)

### Corrigido
- Cadastro de qualificações em duplicidade (DPE-TO)(!491)
- Ignorar verificação de processo de indeferimento ao reabrir atendimento multidisciplinar (DPE-CE)(!497)

## [19.05.3] - 2019-05-08
### Corrigido
- "Aba "Liberados" no Painel do Defensor mostrando atendimentos realizados" (DPE-TO)(!490)

## [19.05.2] - 2019-05-06
### Corrigido
- Erro ao salvar membros da família (DPE-TO)(!486)
- Erro ao salvar cadastro do assistido via 129 (DPE-TO)(!486)
- Erro ao enviar documentos de novo assistido (DPE-TO)(!486)

## [19.05.1] - 2019-05-06
### Adicionado
- Relatório de Quantitativo de Atividades Indenizatórias (DPE-TO)(!484)

## [19.04.9] - 2019-04-29
### Modificado
- Adicionado nova aba "Liberados" no Painel do Defensor (DPE-CE)(!485)

## [19.04.8] - 2019-04-29
### Corrigido
- Erro ao editar indeferimento de atendimento (DPE-TO)(!483)

## [19.04.7] - 2019-04-26
### Corrigido
- Erro ao salvar assistido pelo 129 (DPE-CE)(!481)

## [19.04.6] - 2019-04-25
### Adicionado
- Cadastro de múltiplos endereços do assistido (DPE-TO) (!458)
- Histórico de endereços do assistido (DPE-TO) (!458)
- Auditoria do cadastro de endereços (DPE-TO) (!458)
- Botão para ver/editar o cadastro do assistido na diligência (DPE-TO)(!458)
- Visualização de todos os endereços no página de diligência (DPE-TO)(!458)
- Tipos de endereço (DPE-TO)(!458)
- Bloqueio de exlcusão de dados com regras "on_delete" (DPE-TO)(!458)
- Definição de campos do cadastro de assistido com "auto_complete off" (DPE-TO)(!458)
- Cadastro de membros da família do assistido (dependentes) (DPE-PI)(!447)
- Incluir "Separado judicialmente" no estado civil (DPE-CE)(!461)
- Config. 'Aceita agendamento na pauta?' por defensoria (129/recepção sempre tem acesso à pauta) (DPE-CE)(!457)
- Criar alerta/tarefa para defensor de origem em decisão de recurso da Classe Especial (DPE-TO)(!462)
- Config. 'CONTABILIZAR_ACORDO_TIPO_AMBOS' para realizar ou não acordo em que ambas as partes não comparecerem (DPE-TO)(!478)
- Config. 'Tipo do Painel de Acompanhamento' por defensoria para visualização de Painel de Acompanhamento Completo/Simplificado (DPE-CE)(!459)

### Modificado
- Aumenta campo de e-mail do assistido (DPE-TO)(!458)
- Otimização: não recarregar a página ao salvar assistido (DPE-TO)(!458)
- Painel de Diligências com apenas o endereço principal (DPE-TO)(!458)
- Inclusão de select2 nos selects de "Agendar Atendimento" (DPE-CE)(!454)

### Corrigido
- Formato de data em Atendimento Atender (DPE-TO)(!458)
- Perda de dados do cadastro de assistido (DPE-TO)(!458)
- Controle de transação no cadastro do assistido (DPE-TO)(!458)

## [19.04.5] - 2019-04-10
### Modificado
- Permitir corrigir conflitos automaticamente c/ categoria de agendas (DPE-TO)(!473)

### Corrigido
- Pedidos de apoio que não geram tarefa para acompanhamento (DPE-TO)(!472)
- Impedir criar tarefa sem setor responsável (DPE-TO)(!472)
- Limpar cache da listagem de agendas do defensor ao excluir agenda (DPE-TO)(!473)
- Remover agendamentos extra-pauta nos conflitos de agendamento (DPE-TO)(!473)

## [19.04.4] - 2019-04-08
### Corrigido
- Validação de renda do assistido na página "Atender" (DPE-TO)(!470)
- Visualizar e baixar documentos dos PROPACs (de redes externas) (DPE-TO)(!471)

## [19.04.3] - 2019-04-05
### Corrigido
- Erro ao salvar informação "parte" do processo" (DPE-TO)(!469)

## [19.04.2] - 2019-04-03
### Adicionado
- Dados do órgão de atuação (`defensoria`) no rodapé do GED (DPE-TO)(!466)
- Apoio Operacional para Atendimento ao Processo (DPE-TO)(!412)
- Flag `pode_vincular_processo_judicial` na defensoria (DPE-TO)(!425)
- Coluna "Documentos" na aba "Processos" (DPE-TO)(!468)

### Modificado
- Mostrar apenas defensorias do usuário ao cadastrar processo (DPE-TO)(!425)
- Identificar área a partir da classe processual (DPE-TO)(!425)
- Permitir alterar tipo parte e defensoria responsável do processo a qualquer momento (DPE-TO)(!468)

### Removido
- Campo "Defensor Responsável" do processo (DPE-TO)(!425)

## [19.04.1] - 2019-04-02
### Corrigido
- Permitir registrar anotação em atendimentos públicos (DPE-TO)(!463)
- Inconsistência nos dados de auditória do cadastro do assistido (DPE-TO)(!464)
- Excluir processos em peticionamento dos totalizadores do painel de indeferimento (DPE-TO)(!465)

## [19.03.6] - 2019-03-13
### Adicionado
- Nova forma de apresentação de "defensor/defensoria" na página de agendamento (DPE-TO)(!456)

### Modificado
- Relatório "ATIVIDADES ANUAL - RECURSAL" (DPE-TO)(!456)

### Corrigido
- Relatório "ATENDIMENTOS - DENEGAÇÕES" (DPE-TO)(!456)

## [19.03.5] - 2019-03-11
### Modificado
- Deixar nome de exibição da atuação no agendamento configurável (DPE-CE)(!453)
- Possibilitar a utilização do livre com núcleos (DPE-CE)(!451)

### Corrigido
- Exibir processos judiciais vinculados ao atendimento na aba E-PROC (DPE-TO)(!452)

## [19.03.4] - 2019-03-11
### Corrigido
- Busca de atendimentos no Painel do Defensor (DPE-TO)(!452)

## [19.03.3] - 2019-03-07
### Corrigido
- Não mostrar progressões de presos em regime aberto (DPE-TO)(!450)
- Impedir liberar atendimento antes da data agendada (via backend) (DPE-TO)(!450)

## [19.03.2] - 2019-03-01
### Corrigido
- Informações da mini-ficha do livre na página de Atendimento (DPE-TO)(!449)
- Não mostrar progressões de prisões baixadas (DPE-TO)(!449)

## [19.03.1] - 2019-03-01
### Adicionado
- Incluir na API filtro do tipo da parte do atendimento (DPE-TO)(!448)

## [19.02.15] - 2019-02-28
### Adicionado
- Distribuição Automática de Agendamentos (DPE-PI)(!330)

## [19.02.14] - 2019-02-28
### Adicionado
- Permissão para gerenciar agenda por núcleo (DPE-CE)(!443)

### Modificado
- Permitir registrar despacho de indeferimento sem incluir documentos (DPE-TO)(!446)

### Corrigido
- Consulta RawSQL foi redefinida utilizando um model para a View SQL (DPE-TO)(!424)
- Exibir botões de "ações" de Histórico da Ficha de Atendimento  após Salvar (DPE-TO)(!444)
- Impedir gerar resposta do tempo em duplicidade (DPE-CE)(!441)

## [19.02.13] - 2019-02-26
### Modificado
- Permitir registrar despacho de indeferimento a qualquer momento (DPE-TO)(!445)
- Conteúdo HTML no termo de aceite (DPE-TO)(!445)

## [19.02.12] - 2019-02-22
### Corrigido
- Busca de atendimentos e processos (DPE-TO)(!440)
- Conteúdo HTML no termo de aceite (DPE-TO)(!440)

## [19.02.11] - 2019-02-22
### Adicionado
- Relatório de "Atendimentos - Denegações" (DPE-TO)(!434)

### Corrigido
- Bug conflito de propriedades de auditoria em assistido (DPE-TO) (!435)
- Bug ao gerar Árvore de Atendimento com Termo de Acordo (DPE-TO)(!437)
- Ocultar  atendimento carregado na árvore (DPE-TO)(!439)

## [19.02.10] - 2019-02-19
### Adicionado
- Busca de processos por defensoria (DPE-TO) (!423)
- Busca de processos por data de movimentação processual (DPE-TO) (!423)

### Modificado
- Atendimento com tipo de prioridade absoluta (DPE-TO)(!422)
- Ao buscar por defensor, mostrar apenas processos das defensorias que o defensor está lotado (DPE-TO) (!423)
- Menu "Busca Rápida" permitir buscar pelo número do atendimento ou do processo (DPE-TO) (!423)

### Corrigido
- Carregamento com ng-cloak no Painel do Defensor (DPE-TO)(!422)

## [19.02.9] - 2019-02-18
### Adicionado
- Termo de Aceite (DPE-CE) (!427)

### Modificado
- Redirecionar para novo número de atendimento quando tentar acessar remarcado (DPE-TO) (!431)

### Corrigido
- Erro ao abrir painel do defensor sem atuação (DPE-TO) (!431)
- Assumir hoje ao realizar atendimento agendado para o futuro (DPE-TO) (!431)

## [19.02.8] - 2019-02-15
### Corrigido
- Busca de Arquivo de Acordo ao gerar a Árvore de Atendimento (DPE-TO) (!428)

## [19.02.7] - 2019-02-14
### Corrigido
- Busca de Substituto ao gerar a Árvore de Atendimento (DPE-TO)(!426)

## [19.02.6] - 2019-02-08
### Modificado
- Criação da árvore de atendimento (DPE-TO)(!411)
- Organização da estrutura de arquivos da Ficha de Atendimento (DPE-TO)(!411)

### Corrigido
- Visualização dos horários de atendimento Extra-Pauta na árvore de atendimento (DPE-TO)(!411)
- Visualização da árvore de atendimento sem o atendimento do dia (DPE-TO)(!411)

### Removido
- Carregamento de Assuntos do Atendimento na página da Ficha de Atendimento (DPE-TO)(!411)
- Recarregamento da página da Ficha de Atendimento ao Salvar o Atendimento (DPE-TO)(!411)

## [19.02.5] - 2019-02-08
### Adicionado
- Criar alerta/tarefa para defensor de origem no ato da justificativa (DPE-TO) (!415)

## [19.02.4] - 2019-02-08
### Adicionado
- Permissão para ver todas comarcas ao cadastrar nova atuação (DPE-TO) (!421)

## [19.02.3] - 2019-02-07
### Adicionado
- Novo tipo de decisão de indeferimento "Recebimento" (DPE-TO) (!417)

### Modificado
- Altera o nome do botão CONDEGE para Pet. Integrado (DPE-TO)(!416)
- Esconder ícones de notificação quando SIGNO estiver desabilitado (DPE-CE) (!419)
- Melhorias de desempenho Paniel Multidisciplinar (DPE-TO) (!420)

### Corrigido
- Permitir redistribuir qualquer solicitação em andamento (DPE-TO) (!420)

## [19.02.2] - 2019-02-05
### Corrigido
- Abrir modal pedido de apoio (DPE-TO)(!413)
- Relatório "Visitas por Defensor" (DPE-TO) (!414)

## [19.02.1] - 2019-02-01
### Adicionado
- Link configurável para site de peticionamento integrado do CONDEGE (DPE-TO) (!410)
- Incluir documentos na solicitação ou no recurso de indeferimento (DPE-TO) (!409)

## [19.01.11] - 2019-01-29
### Corrigido
- Task de atualizar processo entre o Solar e ProcAPI (DPE-TO)(!408)
- Visualização de nome social na busca de processos (DPE-TO)(!408)
- Upload de documentos da fase processual (DPE-TO)(!408)

## [19.01.10] - 2019-01-28
### Modificado
- Permitir unificar atendimentos do tipo visita (DPE-TO) (!407)

### Corrigido
- Impedir cadastrar visita sem vínculo a um atendimento/processo (DPE-TO) (!407)
- Transferir para a visita todos os dados do atendimento p/ processo (DPE-TO) (!407)

## [19.01.9] - 2019-01-25
### Adicionado
- Painel de Diligências: busca de solicitação por CPF e CNPJ (DPE-TO) (!405)

### Modificado
- Permitir editar documento GED ao registrar novo indeferimento (DPE-TO) (!406)
- Painel de Diligências: busca sem limite de data (DPE-TO) (!405)

## [19.01.8] - 2019-01-24
### Adicionado
- Atributo conta_estatistica em Qualificação e DocumentoTipo (DPE-TO) (!404)

## [19.01.7] - 2019-01-23
### Adicionado
- Cadastro de Indeferimentos por Denegação de Procedimento da Classe Especial (DPE-TO) (!403)
- Cadastro da Subdefensoria Pública Geral para responder aos Indeferimentos da Classe Especial (DPE-TO) (!403)
- Registra o Indeferimento conforme a atuação do usuário logado (DPE-TO) (!403)

### Corrigido
- Cadastro de Indeferimento do atendimento do dia quando há Defensor Substituto (DPE-TO) (!403)

## [19.01.6] - 2019-01-22
### Adicionado
- Novos tipos de partes (polos) processuais (DPE-TO) (!402)

### Modificado
- Adicionados campos defensor/defensoria na anotação (DPE-TO) (!402)
- Ajustes no layout da Busca de Processos (novos tipos de parte) (DPE-TO) (!402)

## [19.01.5] - 2019-01-22
### Corrigido
- Emissão do relatório de Comparecimento na página da Recepção (DPE-TO) (!400)
- Forçar obrigatoriedade dos campos do Cadastro de Visita ao Preso (DPE-TO) (!401)

## [19.01.4] - 2019-01-21
### Corrigido
- Cadastro de Indeferimentos (DPE-TO) (!398)
- Finalizar atividades multidisciplinar/diligência (DPE-TO) (!399)

## [19.01.3] - 2019-01-15
### Corrigido
- Relatório de Atividades (DPE-TO) (!397)
- Relatório de Atendimentos - Quantitativo Agrupado (DPE-TO) (!397)

## [19.01.2] - 2019-01-09
### Corrigido
- Relatório de Atividades da Equipe Multidisciplinar (DPE-TO) (!395)

## [19.01.1] - 2019-01-08
### Corrigido
- Função SQL do relatório de Atendimentos - Quantitativo Agrupado (DPE-TO) (!394)

## [18.12.12] - 2018-12-18
### Modificado
- Permitir concluir cadastro de indeferimentos não concluídos (DPE-TO) (!392)

### Corrigido
- Ignorar arquivos pendentes na visualização de Indeferimento (DPE-TO) (!392)

## [18.12.11] - 2018-12-14
### Modificado
- Não listar agendamentos remarcados no endpoint de atendimentos de pessoasassistidas na API REST (DPE-TO) (!389)
- Listar processos vinculados a um determinado atendimento na API REST (DPE-TO) (!391)

## [18.12.10] - 2018-12-12
### Adicionado
- Criado comprovante de agendamento (DPE-CE) (!386, #884)

### Modificado
- Inclusão do salário base para hipossuficiência no cadastro de Pessoa (DPE-CE) (!376, #881)

### Corrigido
- Registrar decisão ao clicar nos botões "Deferir/Indeferir" em Indeferimento (DPE-TO) (!388)

## [18.12.9] - 2018-12-12
### Corrigido
- Identificar o nome do documento processual pelo tipo (DPE-TO) (!387)

## [18.12.8] - 2018-12-11
### Modificado
- Qualificar anotação (DPE-TO) (!385)

## [18.12.7] - 2018-12-10
### Modificado
- Inclusão de filtro por servidor no relatório de agendamentos por período (DPE-TO) (!384)

## [18.12.6] - 2018-12-07
### Adicionado
- Auditoria de cadastro de pessoa (DPE-TO) (!382)

## [18.12.5] - 2018-12-07
### Modificado
- Permitir editar cabeçalho de evento em edição (DPE-TO) (!380)

### Corrigido
- Listar setores em "Enviar para diligiência" do Painel do Defensor (DPE-TO)

## [18.12.4] - 2018-12-07
### Corrigido
- URLs com erro de chamada ajax (DPE-TO)

## [18.12.3] - 2018-12-06
### Modificado
- A página de liberar atendimento pela Recepção foi remodelada para utilização de ajax (DPE-TO) (!377)

## [18.12.2] - 2018-12-05
### Adicionado
- Cancelar pedido de apoio não respondido (DPE-TO) (!374, #837)

### Modificado
- Aumentar campo de texto das anotações do histórico (DPE-TO) (!374, #839)
- Ajustes na visualização de detalhes em "Buscar Atendimentos" (DPE-TO) (!374)

## [18.12.1] - 2018-12-04
### Adicionado
- Permissão para requalificar atendimentos de meses passados (DPE-TO) (!374)
- Mostrar setor que solicitou diligência no Painel de Diligências (DPE-TO) (!374)
- Filtrar solicitações de diligência pelo setor que solicitou (DPE-TO) (!374)

### Modificado
- Configuração para registrar ou não a visualização de atendimento se superusuário (DPE-TO) (!374)
- Configuração para registrar ou não a visualização de tarefa se superusuário (DPE-TO) (!374)
- Ignorar extra-pauta nos horários disponíveis para agendamento na API (DPE-TO) (!375)

### Corrigido
- Vínculo da tarefa à defensoria de origem quando for solicitado pedido de apoio (DPE-TO) (!374)
- Exibir apenas atendimentos onde o vínculo da pessoa está ativo na API (DPE-TO) (!374)

## [18.11.12] - 2018-11-30
### Corrigido
- Correção no carregamento da agenda Itinerante (DPE-TO) (!372)

## [18.11.11] - 2018-11-28
### Corrigido
- Correção de Filiações no cadastro de pessoa jurídica (DPE-TO) (!371)

### Modificado
- Campo "nome fantasia" alterado para 256 caracteres (DPE-TO) (!371)

## [18.11.10] - 2018-11-26
### Corrigido
- Cadastro de CPF de assistido (DPE-TO) (!369)
- IntegrityError: honorarios.views.possibilidade_honorarios (DPE-TO) (!370)
- W605 invalid escape sequence (DPE-TO) (!370)

## [18.11.9] - 2018-11-26
### Modificado
- Substituir função por related_name em `PessoaAssistida.filiacoes` (DPE-TO) (!368)

## [18.11.8] - 2018-11-23
### Adicionado
- Permissão para excluir anotação (DPE-RO) (!366)

### Modificado
- Só permitir anotações depois de realizar atendimento do dia (DPE-RO) (!366)

## [18.11.7] - 2018-11-22
### Adicionado
- Autorização evento de desbloqueio retroativo (DPE-TO) (!363)

### Corrigido
- Mostra mês do agendamento por padrão apenas se for mês vigente ou posterior (DPE-TO) (!363)

## [18.11.6] - 2018-11-21
### Adicionado
- Configuração para não exibir alerta de Hipossuficiência (DPE-CE) (!364)

## [18.11.5] - 2018-11-19
### Adicionado
- Relatório de Agendamentos por Período (DPE-TO) (!362)
- Permitir registrar atendimento retroativo (desbloqueio) (DPE-TO) (!361)

### Corrigido
- Visualização do quantitativo de Visitas ao Preso no relatório de Atividades Mensal por Comarca/Defensor (DPE-TO) (!360)

## [18.11.4] - 2018-11-09
### Modificado
- Forçar importação de sentença do ProcAPI mesmo se tipo correspondente estiver desativado (DPE-TO) (!358)

### Corrigido
- Mostrar "Atualmente preso em" em Atendimento para Processo de Presos (DPE-TO) (!357, #870)
- Não retornar todos atendimentos se nome do assistido buscado não existir (!359)

## [18.11.3] - 2018-11-08
### Adicionado
- Buscar Processos de Indeferimento (DPE-TO) (!355, #869)
- Registro de acesso à página "Atendimento do Defensor" (DPE-TO) (!354, #868)

### Corrigido
- Vincular atendimento como "Em atendimento" só para quem tem permissão de editar o atendimento (DPE-TO) (!353, #867)

## [18.11.2] - 2018-11-05
### Modificado
- Relatório de Atividades Mensal por Comarca/Defensor com cabeçalho de data inicial e final (DPE-TO) (!350, #862)
- Relatório de Atividades Mensal por Atuação dos Defensores com filtros de data inicial e final (DPE-TO) (!349, #861)

### Corrigido
- Redirecionamento de página ao marcar retorno (DPE-TO) (!351)

## [18.11.1] - 2018-11-01
### Adicionado
- Recurso para unificar fichas de atendimento duplicadas (DPE-TO) (!347)

## [18.10.9] - 2018-10-30
### Adicionado
- Máscara de CPF/CNPJ na lista de assistidos da página de Busca de Assistido

### Modificado
- Relatório de Atividades Mensal por Comarca/Área com filtros de data inicial e final (DPE-TO) (!345, #858)
- Relatório de Atividades Mensal por Comarca/Defensor com filtros de data inicial e final (DPE-TO) (!344, #857)
- Relatório de Atividades Mensal por Defensoria com filtros de data inicial e final (DPE-TO) (!343, #855)

### Corrigido
- Label dos botões 'Cadastar Nova Pessoa Jurídica e Física' na página de busca de assistido

## [18.10.8] - 2018-10-29
### Adicionado
- Botão visualizar atendimento (DPE-RO) (!333)
- Destaque do dia atual na página de Agendamento (DPE-RO) (!333)

### Modificado
- Relatório de Atividades Mensal por Comarca com filtros de data inicial e final (DPE-TO) (#854)

## [18.10.7] - 2018-10-26
### Adicionado
- Relatório "Termo de Declaração" em "Atendimento do Defensor" (DPE-GO) (!332)

### Modificado
- Redimensionar tamanho da foto do usuário ao salvar (proporção 480x480) (!243)
- Esconder modelos globais da pasta de modelos do Painel GED (!324)

### Corrigido
- Cadastro de requerente/requerido perdendo marcação de "Não possui" (!331)
- Erro ao recuperar perfil de campos obrigatórios na página 129 (!331)

## [18.10.6] - 2018-10-22
### Modificado
- Obrigar informar o tipo de pessoa em Pessoa e PerfilCamposObrigatorios
- Remover obrigatoriedade da data de nascimento do assistido
- Redireciona para 129 se ligação em andamento
- Ao encerrar ligação, redirecionar para página anterior
- Esconder botão "Unificar" cadastros de assistidos se não tiver permissão

### Corrigido
- Erro ao buscar pelo CPF no 129
- Erro ao excluir atendimento na busca de atendimentos
- Erro ao buscar pessoa c/ dt nascimento < 1900
- Erro ao buscar atendimento pelo número
- Erro de integridade ao unificar cadastros de assistidos

## [18.10.5] - 2018-10-19
### Adicionado
- Recurso para unificar cadastro de assistido duplicado

## [18.10.4] - 2018-10-19
### Corrigido
- Mover relacionamentos dependentes quando agendamento for remarcado

## [18.10.3] - 2018-10-19
### Adicionado
- Cadastro de Pessoa Jurídica
- Cadastro de Salário para pessoa jurídica
- Cadastro de Campo Obrigatório para pessoa jurídica
- Visualização do Nome Social para pessoa física
- Visualização do Nome Fantasia pra pessoa jurídica
- Buscas por nome Social e Nome Fantasia
- Máscara de número de atendimento, CPF e CNPJ em labels do angularJS
- Visualização com popover aplicada em diversas telas onde há Pessoa

### Modificado
- Visualizção de atendimentos da Recepção
- Visualização do popover

### Corrigido
- Autocomplete de endereço no cadastro de Assistido

## [18.10.2] - 2018-10-17
### Adicionado
- Inclusão de layout configurável (cores e logo) (DPE-CE)

## [18.10.1] - 2018-10-16
### Adicionado
- Configuração "GED_PODE_BAIXAR_DOCUMENTO_NAO_ASSINADO" (DPE-CE)

## [18.09.9] - 2018-09-24
### Corrigido
- Registrar justificativa em atendimento com impedimento
- Habilitar botão para excluir documento anexo (upload) no atendimento
- Solicitação de apoio operacional sem data agendamento informada

## [18.09.8] - 2018-09-21
### Adicionado
- Campos de auditoria de Bairro

### Modificado
- Normalização do nome de Biarro

### Corrigido
- `MultipleObjectsReturned` ao tentar salvar Bairro no cadastro de assistido

## [18.09.7] - 2018-09-20
### Modificado
- Ajustes ao identificar comarca do processo via ProcAPI v18.09.1

## [18.09.6] - 2018-09-14
### Corrigido
- `MultipleObjectsReturned` ao tentar marcar retorno em atendimento com múltiplos cronômetros registrados

## [18.09.5] - 2018-09-12
### Corrigido
- API REST: `defensor` no serviço `pessoasassistidas/{}/atendimentos/`

## [18.09.4] - 2018-09-11
### Adicionado
- Campo setor responsável (defensoria) nas tarefas (#602)

### Modificado
- Quem cadastrou deve acompanhar a tarefa (#628)

## [18.09.3] - 2018-09-11
### Modificado
- API REST: incluídos campos `area` e `qualificacao` do atendimento
- API REST: em `defensor` mostrar nome do substituto em vez do titular do atendimento

## [18.09.2] - 2018-09-05
### Adicionado
- Configuração de application_id para ser exibida junto ao número da versão
- Campo "tentado/consumado" na prisão

### Modificado
- Permitir salvar detração sem informar a data final

### Corrigido
- Link do botão Agendar Encaminhamento em Atendimento do Defensor
- Não mostrar ou contabilizar prisões baixadas
- Filtro de comarca a partir da defensoria em vez do processo
- Remover campo "município" no cadastro da detração

## [18.09.1] - 2018-09-03
### Adicionado
- Botão Negação p/ Atendimento Realizado ou Atendimento p/ Processo (#679)

## [18.08.19] - 2018-08-31
### Adicionado
- Criada API REST (em `api/v1/`)para viabilização de integração com Luna Chatbot(Chatboot do DPE-TO para facebook) (!308)
   - Adicionado novo campo `uso_interno` em contrib.Servidor para explicitar usuário do sistema
   - Implementado Autenticação na API via [método TOKEN](http://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication).
   - Implementado documentação Swagger da API (somente pode ser visualizada/utilizada se `user.is_staff=True` ou `servidor.uso_interno=True`
   - Implementado task celery em `luna_chatbot_client.tasks.chatbot_notificar_requerente_remarcacao_atendimento` para notificar Luna Chatbot ao remarcar atendimento.
   - Implementado em `atendimento/agendamento/utils` função `proximos_horarios_disponiveis` para obter em Python o próximo horário disponível para agendamento, dado um numero de atendimento.
   - Implementado endpoint na API para marcar retorno de atendimento.
   - Implementado endpoint na API para obter horário disponível para agendamento para um determinado atendimento.
   - Implementado endpoint na API consultar informações de atendimentos, bairros, comarcas, endereços, municipios, partes de um atendimento, pessoas assistidas.
   - Implementado endpoint na API para obter lista de processos pendentes de atualização no celery (complementação ao !288)
   - Implementado criação de usuário do chatbot via migration, que embora seja criado automaticamente, é criado desativado por padrão. Você deve ativa-lo manualmente caso queria utiliza-lo

### Modificado
- Atualizado Django 1.8.17 para 1.8.19

## [18.08.18] - 2018-08-24
### Corrigido
- Salvar anotações ao registrar recurso de indeferimento (#825)

## [18.08.17] - 2018-08-23
### Adicionado
- Exclusão de GED não Finalizado

## [18.08.16] - 2018-08-23
### Adicionado
- Criar grupos de permissão e papéis padrão (#823)

## [18.08.15] - 2018-08-22
### Corrigido
- Link para download dos arquivos em "Detalhes do Atendimento" (#822)

## [18.08.14] - 2018-08-22
### Corrigido
- Prazo de resposta de documento de atendimento não deve ser copiado para Pedido de Apoio (#821)

## [18.08.13] - 2018-08-17
### Modificado
- Desativa a lotação ao desativar o servidor (#813)
- Define controle de transação para a edição de servidor

## [18.08.12] - 2018-08-16
### Corrigido
- Corrigir upload de arquivos em pedido de apoio pela Página "Detalhes do Atendimento" (!296)

## [18.08.11] - 2018-08-16
### Corrigido
- Bugfix: Conversão de Inquérito Policial em Ação Penal (!295)

## [18.08.10] - 2018-08-15
### Modificado
- Ajustes Admin: Core e Itinerante (!294)

## [18.08.9] - 2018-08-10
### Corrigido
- Migrations for 'processo': Create proxy model ProcessoDashboard

## [18.08.8] - 2018-08-09
### Corrigido
- Lista de documentos no painel do defensor vinculados aos atendimentos de retorno

## [18.08.7] - 2018-08-09
### Adicionado
- Incluido configuração para exibir/ocultar "Não possui" nos campos opcionais do cadastro do assistido (!291)

## [18.08.6] - 2018-08-09
### Modificado
- Registrar em cadastrou a lotação do servidor (!290)
- Link para o Admin do Django (!290)

## [18.08.5] - 2018-08-08
### Modificado
- Importar `VersionAdmin` de `reversion.admin` em vez de `reversion` em todos os arquivos `admin.py` para faciliar migração de versão do [django-reversion](https://django-reversion.readthedocs.io) (!264)
- Removido utilizações de `RequestContext` pois foi removida em versão posterior do django (!264)
- Substituido função `render_to_response` por `render` para padronizar e facilitar migração de versão do django (!264)

## [18.08.4] - 2018-08-07
### Modificado
- Otimização tab "Atividades" da página "Atendimento do Defensor" (!289)

## [18.08.3] - 2018-08-07
### Modificado
- Melhorias consulta processo celery e dashboard inicial de processo no admin (!288)

## [18.08.2] - 2018-08-07
### Modificado
- Arquivos javscript com otimizações e correções para futura minificação com django-compression

## [18.08.1] - 2018-08-02
### Corrigido
- Botão de excluir prisão !50

## [18.07.7] - 2018-07-26
### Adicionado
- Configurar mínimo de caracteres para busca de atendimentos pelo nome da pessoa (#798)
- Configurar máximo de pessoas para busca de atendimentos pelo nome da pessoa (#798)

## [18.07.6] - 2018-07-24
### Adicionado
- Filtros nos Admin de Core
- Links de Admin na página de visualização do Indeferimento

### Corrigido
- Bug ao solicitar diligência a partir do Indeferimento
- Bug ao retornar mensagem na tentativa de registro de suspeição

### Modificado
- Mostrar medida pretendida apenas em denegação com recurso

## [18.07.5] - 2018-07-24
### Corrigido
- Erro ao executar strptime devido a bug na implementacao do interpretador python da serie 2.7.x ( #792 !280 )

### Modificado
- Configuracao de acesso ao REDIS e MEMCACHED via novas variaveis de ambiente "REDIS_DATABASE_URL" e "MEMCACHED_DATABASE_URL" ( #795 !280 )

## [18.07.4] - 2018-07-24
### Adicionado
- Configuração para acesso de múltimos banco de dados "DATABASE_URL" e "DATABASE_REPLICACAO_URL" (#796)

## [18.07.3] - 2018-07-12
### Adicionado
- Obrigatoriedade de histórico no despacho de indeferimento (#791)
- Mostrar justificativa e medida pretendia no histórico do indeferimento

### Corrigido
- Salvar justificativa e medida pretendida ao registrar suspeição
- Mostrar Indeferimentos de todos os atendimentos do histórico

## [18.07.2] - 2018-07-05
### Removido
- Tooltip com detalhes sobre tipo de telefone nas páginas de cadastro do assistido

## [18.07.1] - 2018-07-03
### Adicionado
- Configuração de application_name e max_age para conexão com banco de dados

## [18.06.21] - 2018-06-29
### Corrigido
- Erro ao registrar atuação/lotação (#784)
- Erro ao registrar impossibilidade de honorários (#785)
- Erro de integridade ao atualizar cabecalho do processo (#786)
- Erro ao distribuir atendimentos (#787)
- Erro ao realizar atendimento (#788)
- Erro de precedência dos migrations (#789)

## [18.06.20] - 2018-06-27
### Adicionado
- Remover comarca ou defensoria de evento sem excluir todos eventos (#783)

## [18.06.19] - 2018-06-27
### Modificado
- Ordem de atendimentos na página da recepção

## [18.06.18] - 2018-06-26
### Adicionado
- Cadastrar classe, assunto, vara e comarca automaticamente via ProcAPI (#717)

## [18.06.17] - 2018-06-25
### Corrigido
- Desativar registro de defensor apenas se servidor não possuir atuações vigentes (#749)
- Mostrar principais atividades realizadas no Painel de Diligências (#782)

## [18.06.16] - 2018-06-22
### Adicionado
- Legenda nos campos para cadastro de telefone do assistido
- Balão com informações básicas do assistido na página Atendimento do Defensor
- Balão com informações básicas do assistido na página Atendimento da Recepção
- Balão com informações básicas do assistido na página Atendimento de Diligência
- Link p/ Admin na página de Atendimento

### Modificado
- Adicionar nome do contato ao cadastrar telefone via 129

### Corrigido
- URL para acesso ao GED pela página Perfil do Defensor

## [18.06.15] - 2018-06-20
### Adicionado
- Adicionar nome de contato para telefones do assistido (#781)

## [18.06.14] - 2018-06-20
### Modificado
- Otimização da view de banco de dados utilizada na página da recepção

### Corrigido
- Ignorar solicitações de apoio no relatório de Primeiro Atendimento do Dia

### Removido
- Índices do banco de dados subutilizados

## [18.06.13] - 2018-06-20
### Adicionado
- Registrar data/hora do início e término da consulta de novos processos no ProcAPI

## [18.06.12] - 2018-06-19
### Modificado
- Guarda data do último processo atualizado em vez da data final da consulta (#780)

## [18.06.11] - 2018-06-19
### Modificado
- Ignora url do captcha do GED ao forçar autenticação com Égide

## [18.06.10] - 2018-06-18
### Modificado
- Página de atendimentos da recepção otimizada com requisições sob demanda ajax

## [18.06.9] - 2018-06-18
### Corrigido
- Erro ao salvar novo assistido via 129 "numero_membros: Certifique-se que este valor seja maior ou igual a 1 (#779)

## [18.06.8] - 2018-06-14
### Corrigido
- Mostrar apenas tarefas de atendimentos itinerantes realizados pelo defensor (#778)

## [18.06.7] - 2018-06-14
### Adicionado
- Informar novo defensor e defensoria responsáveis ao registrar tranferência de preso (#776)
- Registrar baixa de prisões (#377)
- Opção para converter Inquerito Policial em Ação Penal (#419)

### Corrigido
- Filtrar presos a partir da lotação de servidores (#774)

## [18.06.6] - 2018-06-12
### Adicionado
- Mensagem fixa ao clicar em Renda Individual e Renda Familiar no cadastro do assistido (#775)

## [18.06.5] - 2018-06-11
### Adicionado
- Tabela de Cargos
- Vínculo de Atuação com Cargo
- Define o cargo no vínculo de participante do atendimento
- Opção de reabrir atividade
- Histórico das atividades visível para o defensor
- Cadastro de cargos conforme as profissões
- Cadastro de cargo para oficial de diligência

### Corrigido
- Distribuição de atendimentos da diligência conforme nova estrutura de cargos
- Distribuição de atividades da multidisciplinar conforme nova estrutura de cargos

### Modificado
- Relatório buscando dados conforme a atuação do servidor e seu cargo
- Exibição de username no painel da multidisciplinar

### Removido
- Profissão de Servidor

## [18.06.4] - 2018-06-06
### Modificado
- Mostrar como "Solto" quando regime do preso for aberto

### Corrigido
- Não mostrar processos em que já foi registrada soltura do preso

## [18.06.3] - 2018-06-06
### Corrigido
- Identificar diretoria e não comarca como setor p/ encaminhamento indeferimento

## [18.06.2] - 2018-06-05
### Corrigido
- Validação da renda do assistido (#768)

## [18.06.1] - 2018-06-04
### Corrigido
- Correção nos nomes dos métodos para avaliação de renda

## [18.05.17] - 2018-05-30
### Modificado
- Atualizado djdocuments para 0.0.52 para ordenar painel ged Documentos Finalizados por data de finalização.
- painel "Documentos Finalizados" agora mostra o username de quem finalizou o documento e no balão quem criou e quem finalizou documento.

## [18.05.16] - 2018-05-30
### Adicionado
- Campos: membros economicamente ativos e possui outros bens no Cadastro de Assistido (#766)
- Índices para cálculo de renda (#766)
- Renda per capita  (#766)

## [18.05.15] - 2018-05-30
### Adicionado
- Zap Defensoria no cadastro do assistido (#767)
- Informar adesão ao Zap Defensoria na página de Atendimento (#767)
- Zap Defensoria personalizável no Admin (#767)

## [18.05.14] - 2018-05-28
### Adicionado
- Acesso restrito para a defensoria (!28)
- Permissão para criar Propac/PA apenas de sua lotação (!28)

### Modificado
- Propac disponível para todas as defensorias (!28)
- Somente a defensoria responsável pode editar o Propac/PA (!28)
- Layout da página de edição/movimentação

## [18.05.13] - 2018-05-25
### Adicionado
- Notificações via SIGNO
- Notificação ao modificar cadastro assistido
- Notificação ao liberar atendimento na recepção
- Notificação ao marcar documento como pronto para assinatura (#584)
- Notificação ao adicionar novos assinates
- Notificação ao finalizar documento (#585)

## [18.05.12] - 2018-05-24
### Adicionado
- Criar core genérico para gerenciamento de processos
- Movimentação de indeferimento entre setores
- Envio de diligência pelo módulo indeferimento
### Modificado
- Unificar módulos DPG, CG e Diretorias no módulo Indeferimento

## [18.05.11] - 2018-05-22
### Modificado
- Liberar inclusão de arquivos em atendimento p/ processo c/ apoio

## [18.05.10] - 2018-05-21
### Modificado
- Remover cacheops de Defensor

## [18.05.9] - 2018-05-17
### Adicionado
- criar lotação para assessores no Itinerante
- criar lotação para novos participantes em Itinerante já autorizado
### Modificado
- Mostrar tarefa para defensor que já atuou no itinerante

## [18.05.8] - 2018-05-15
### Modificado
- atualizado djdocuments para 0.0.48 (removido botao de assinar da pagina de edição) para corrigir (#759)

## [18.05.7] - 2018-05-15
### Corrigido
- Pode agendar na pauta se não for encaminhamento (#757)

## [18.05.6] - 2018-05-14
### Adicionado
- Adicionada biblioteca Cacheops

### Modificado
- Otimizações de querys na view de horarios

## [18.05.5] - 2018-05-11
### Corrigido
- Tratamento para agendamento na pauta e na extra-pauta quando não tem atuação (#757)

## [18.05.4] - 2018-05-10
### Corrigido
- Migrate faltando: app defensor

## [18.05.3] - 2018-05-09
### Adicionado
- Configuração encaminhamento pauta/extra-pauta por defensoria (#756)

## [18.05.2] - 2018-05-04
### Corrigido
- Listar municípios da UF do usuário ao cadastrar itinerante (#750)

## [18.05.1] - 2018-05-02
### Modificado
- Correção da função int_or_not necessária para processamento da variavel EMAIL_TIMEOUT (!230)

## [18.04.23] - 2018-04-27
### Modificado
- Ordem de exibição nos modelos de documentos (#748)

## [18.04.22] - 2018-04-26
### Adicionado
- Configurações opcionais de e-mail no .env (!227)
- Botão "Baixar" Documento GED em atendimento

### Corrigido
- Upload anexo em atendimento
- Recuperar lista de atuação de defensores

## [18.04.21] - 2018-04-25
### Adicionado
- Pré-visualização de documentos do Atendimento (#723)
- Aba Documentos do Atendimento (#723)
- Aba de Tarefas do Atendimento (#723)
- Documentos GED em edição e liberados para assinatura (#723)
- Melhorias visuais na janela de visualização do GED (#723)
- Página para criação de GED no atendimento (#723)

### Modificado
- Painel GED: com pré-visualização do documento (#723)
- Painel GED: com separação por pastas (#723)
- Painel GED: vínculo de documento com Atendimento
- Envio de anexo sem pessoa vinculada (#723)

## [18.04.20] - 2018-04-24
### Corrigido
- Excepts de qualidade da ferramenta Tox (#736)

## [18.04.19] - 2018-04-24
### Modificado
- Campos ajax definidos com autocomplete off no cadastro de assistido (#741)

### Corrigido
- Campo valores móveis no cadastro de assistido (#740)
- Excepts de qualidade da ferramenta Tox (#736)

## [18.04.18] - 2018-04-23
### Adicionado
- Menu de ajuda para vídeos (#739)

## [18.04.17] - 2018-04-23
### Modificado
- Permitir gerar impedimento e suspeição em agendamento (#738)

## [18.04.16] - 2018-04-20
### Modificado
- Filtro de Tarefas no painel do defensor para mostrar solicitações de apoio (#737)

## [18.04.15] - 2018-04-19
### Adicionado
- Busca de solicitações no painel de diligência (#680)

## [18.04.14] - 2018-04-18
### Modificado
- Exibir processos pendentes de todos supervisores do assessor (#735)

## [18.04.13] - 2018-04-18
### Adicionado
- Painel da Corregedoria (#699)

## [18.04.12] - 2018-04-17
### Corrigido
- Finalizar atendimento inicial multidisciplinar sem tentar criar tarefa (#733)
- Filtro de agendamentos por categoria no painel do defensor (#704)

## [18.04.11] - 2018-04-17
### Corrigido
- Filtro de comarca e profissionais da página de relatórios (#732)

## [18.04.10] - 2018-04-16
### Modificado
- Define o defensor de diligência conforme quem finalizou a atividade (#645)

### Corrigido
- Correção do tamanho do menu lateral (#726)

## [18.04.9] - 2018-04-13
### Modificado
- Desagrupar diligências da mesma pessoa (#727)
- Otimizar página de confirmação de solicitação de diligência

## [18.04.8] - 2018-04-11
### Corrigido
- Vincular documento ou tarefa ao último atendimento válido (#726)

## [18.04.7] - 2018-04-09
### Adicionado
- Enviar anexo na diligência (#635)

## [18.04.6] - 2018-04-05
### Modificado
- Melhorias no admin de Defensor e Atuação

## [18.04.5] - 2018-04-05
### Corrigido
- Duplicidade de documento ao enviar para diligência (#635)

## [18.04.3] - 2018-04-04
### Corrigido
- Vincular pedido ao apoio de núcleo especializado (#722)

## [18.04.2] - 2018-04-04
### Corrigido
- Marcar retorno p/ última defensoria válida (ignorar pedidos de apoio) (#724)
- Permitir agendar mesmo com pedidos de apoio não respondidos (#725)

## [18.04.1] - 2018-04-03
### Adicionado
- Relatório de declaração de mudança de endereço do assistido (#721)

## [18.03.10] - 2018-03-27
### Adicionado
- Validação da "data_agendamento" antes de salvar pedido de apoio (#715)

## [18.03.9] - 2018-03-22
### Adicionado
- Adicionado o botão de imprimir declaração de hipossuficiência no campo do requerido (#668)

### Corrigido
- Validação de área no cadastro de endereço do assistido (#698)
- Ativar/Desativar automaticamente registro de defensor.(#615)

## [18.03.8] - 2018-03-21
### Modificado
- Removido caches de página (#714)

## [18.03.7] - 2018-03-16
### Corrigido
- Redirecionamento de página ao adicionar interessado em atendimento ao preso (#667)
- Erro ao fazer upload do Termo de Conciliação em Atendimento de Acordo (#710)

## [18.03.6] - 2018-03-14
### Adicionado
- Incluido configuração para colocar URL acesso ao para o sistema anterior ao SOLAR (#706)

### Modificado
- Movido URL_API_PLANTAO para o .env (#707)
- Definir por padrão como desativada (False) configurações opcionais feitas via constance (#708)
- Movido configurações de email da aplicação para arquivo .env, para que possa ser customizável (#706)
- Modificado configurações do raven para que ele seja opcional o envio de relatórios erros para o servidor do Sentry (#709)

## [18.03.5] - 2018-03-09
### Adicionado
- Filtro de busca pelo Id do GED no admin de AtendimentoDocumento (#700)
- Número do GED na listagem do admin de AtendimentoDocumento (#700)
- Adicionado assinatura de GED com verificação via EGIDE. Faz parte do (#683)

### Corrigido
- Remover opção "não possui" do estado e município no cadastro de pessoas (#697)

### Modificado
- Atualizado versão do djdocuments para 0.0.44. Essa versão introduz
dois novos campos no model Documento do djdocuments, que tem o objetivo
de persistir o html gerado do código QD + url de validação e assinaturas.
É necessário intervenção manual, consulte a issue #701 para saber como aplicar
as correções nos registros do banco.

## [18.03.4] - 2018-03-06
### Adicionado
- Campo "telefone" no cadastro de prédios (#693)
### Corrigido
- Remover zeros à esquerda do código de tipo de fase processual ao salvar e ao recuperar da API (#695)
- Salvar evento no LIVRE apenas de atendimento ao interessado realizado (#696)
- Alterar conteúdo do cabecalho e rodapé do documento GED

## [18.03.3] - 2018-03-05
### Adicionado
- Gerenciar cadastro de prédios, andares e endereços (#694)

### Modificado
- Alteração links domínio "gov.br" para "def.br"
- Redirecionar automaticamente p/ recepção se comarca tem apenas um prédio

### Corrigido
- Remover referências ao TO (estado 17) !176

## [18.03.2] - 2018-03-02
### Adicionado
- Link de Admin para Processo e suas Fases (#690)

### Corrigido
- Login sem autenticação pelo Egide (#691)
- Reativação de Processo e suas Fases ativas (#690)

## [18.03.1] - 2018-03-01
### Modificado
- Pesquisar Servidor por username na autenticação via EGIDE !166
- Melhoria na criação de logs de erros para autenticação via EGIDE !166
- Adicionado urls publicas do GED para não validar autenticação com EGIDE !168

## [18.02.10] - 2018-02-28
### Adicionado
- Autenticação via EGIDE (#683) !161
- Backport do Django 1.11 das implementações das views de autenticação e gerenciamento de senhas (#686) !161

### Modificado
- Atualizado djdocuments para 0.0.46

## [18.02.9] - 2018-02-28
### Adicionado
- Personalizar nome e URL de acesso consulta processual (#678)

### Corrigido
- Cadastro de processo que estava inativo (#687)

## [18.02.8] - 2018-02-26
### Adicionado
- Link de Admin para os Documentos do Atendimento (#684)

### Modificado
- "tipo_nacional" como tipo padrão de movimento processual (#675)
- Ajustes na verificação de usuário da movimentação processual (#677)

### Corrigido
- Permissão para qualificar atendimento
- Trazer movimentações processuais de todas páginas da API
- Desempenho da página Admin de Atendimento Documento com documento_resposta somente leitura (#685)

## [18.02.7] - 2018-02-22
### Corrigido
- Filtro de listagem de documentos ativos do atendimento (#682)

## [18.02.6] - 2018-02-20
### Corrigido
- Mostrar nome do defensor que cadastrou o impedimento (#676)

### Adicionado
- Mostrar campo "Recorrido" na página de detalhes do impedimento para o DPG (#676)

## [18.02.5] - 2018-02-16
### Adicionado
- Exibir número da versão do sistema (#672)

### Modificado
- Mostrar apenas impedimentos com recurso registrado no painel DPG (#671)
- Incluir razão e medida no documento modelo de suspeição (#673)

### Corrigido
- Erro de integridade ao recuperar processos da api (#642)
- Erro ao carregar conteúdo do atendimento via ajax (#670)

## [18.02.4] - 2018-02-15
### Adicionado
- Painel do DPG
- Painel do Diretor Regional (!146)
- Registrar indeferimento de atendimento por não caracterização de hipossuficiência (!146)
- Registrar indeferimento de atendimento por outros motivos (!146)
- Registrar impedimento de atendimento (!146)
- Registrar arguição de suspeição (!146)
- Registrar recurso para indeferimento de atendimento (!146)

### Modificado
- Mostrar de qual diligência é a certidão ao finalizar (#666)

## [18.02.3] - 2018-02-08
### Modificado
- Mostrar nome do documento no painel de diligências (#658)

### Corrigido
- Erro ao exibir diligências (não mostrando todas/não mostrando atividades) (#662)
- Só excluir atendimento para processo ao excluir o último processo vinculado (#643)
- Define grau do processo ao criar novo via procapi (#656)
- Mostrar apenas documentos finalizados em diligências (#663)

## [18.02.2] - 2018-02-07
### Modificado
- Relatório de processos pendentes com filtro de defensor (#657)

### Corrigido
- Erro ao finalizar diligência (duplicando documentos) (#660)

## [18.02.1] - 2018-02-06
### Adicionado
- Cores para os ícones de enviar diligência (#646)

### Modificado
- Ícones de diligência (#646)
- Ícone de Núcleo/Distribuir (#646)

### Corrigido
- Erro ao distribuir atendimendo de diligência (#655)

## [18.01.8] - 2018-01-26
### Adicionado
- Botão do Atendimento para o diligente (#630)
- Registrar suspensão de Honorário (#637)
- Recarregar página de Atender Diligência após assinar/finalizar GED (#587)
- Preenchimento automático da finalização da diligência com última atividade (#589)
- Painel de Acompanhamento de Petição (#663)
- Adicionado possibilidade de deixar modelo indisponivel para utilização (#624)
- Página "Selecionar Perfil" como padrão para defensores, assessores e estagiários (#647)

### Corrigido
- Link de GED na página de Atender Diligência (#644)

### Modificado
- Ícones e tooltip da página de Atender Diligência (#644)

### Corrigido
- Link do botão para excluir Honorário (#634)
- Impedir registro duplicado de número de processo (#641)

## [18.01.7] - 2018-01-23
### Adicionado
- Mostra responsável pela diligência (#591)
- Tooltip de ícones da diligência (#591)
- Campo "observações" e "resposta" visível para o diligente (#636)
- Deixar anotações da diligência opcionais (#588)

## [18.01.6] - 2018-01-22
### Adicionado
- Link que vai da Diligência para o Atendimento (#630)

### Corrigido
- Filtro de busca de Solicitações ativas (#590)

## [18.01.5] - 2018-01-19
### Adicionado
- Links para acessar o Admin de atendimento de diligência (#620)
- Botão Imprimir Hipossuficiência no cadastro do assistido (#623)

### Modificado
- Autopreencher "não possui" durante o dia da última modificação do cadastro do assistido (#621)
- Autopreencher "não possui" apenas se tipo de cadastro de assistido completo (#621)

### Corrigido
- Trocar nome de grupo pelo nome da permissão (#616)
- Remover id de núcleo por tipo acordo (#622)
- Preservar parâmetro de pesquisa ao recarregar página "Buscar Assistido" (#575)
- Botão Imprimir Hipossuficiência no cadastro do assistido (#623)
- Utilização de variável do constance na view de Agenda (#618)

## [18.01.4] - 2018-01-18
### Adicionado
- Campo de Hora Inicial padrão da agenda no Constance (#618)

## [18.01.3] - 2018-01-18
### Modificado
- Preservar parâmetros de busca ao recarregar página "Buscar Atendimento" (#617)
- Adicionar parâmetros de busca com GET e preservar ao recarregar página "Buscar Assistido" (#575)

## [18.01.2] - 2018-01-16
### Corrigido
- Erro ao capturar dados do cronômetro no painel da recepção (#613)
- Alterando qualificação de outro atendimento pela sessão (#612)
- Liberar acesso ao atendimento a partir da defensoria do processo (#607)
- Vincular atendimento de plantão ao defensor em vez do servidor (#606)
- Mostrar apenas defensores no relatório 'Plantões por período e defensor' (#608)
- Ajustes na validação de campos obrigatórios (#605)
- Redirecionamento da página de cadastro de assistido
- Desbloqueio dos campos para upload de arquivos do cadastro de assistido

## [18.01.1] - 2018-01-10
### Corrigido
- Marcar processos criados automaticamente como pre-cadastro (#604)

## [17.12.6] - 2017-12-21
### Corrigido
- Agendamento de atendimento em plantão (#603)

## [17.12.5] - 2017-12-15
### Corrigido
- Validação de campos obrigatórios ao salvar (#598)

## [17.12.4] - 2017-12-11
### Corrigido
- Cadastro de atividades de diligência (#596)
- Visualização de data do prazo da diligência (#596)

## [17.12.3] - 2017-12-06
### Adicionado
- Personalizar campos obrigatórios no Cadastro de Pessoas (#388, #571)
- Descrição ao "parar mouse" em cima do botão de "Enviar para Diligência" (#580)
- Nome do campo de observações na tela de Enviar Diligência (#580)
- Registrar data da última alteração do cadastro do assistido (#576)

## [17.12.2] - 2017-12-04
### Corrigido
- Diferença do total de presos do Painel do Livre e Busca de Presos (#574)

## [17.12.1] - 2017-12-01
### Corrigido
- Atualizado djdocuments para 0.0.41 para corrigir a issue #572
- Atualizado fork do django-simple-history para corrigir a issue #572
- Corrigir filtro angular "track by $index" em app processo para corrigir a issue #573

## [17.11.8] - 2017-11-30
### Adicionado
- Criado fixtures para polular dados iniciais dos models `Bem`, `Profissao`, `EstruturaMoradia` e `Deficiencia`, `Documento`, `Pais`, `Estado`, `Municipio` das apps `assistido` e `contrib` respectivamente

## [17.11.7] - 2017-11-29
### Adicionado
- Criado comando `createsolarsuperuser`

### Modificado
- Marcar processos antes de atualizar via ProcAPI (#568)
- Atualização SQLs com dados básicos do sistema (#570)

### Corrigido
- Formato numeração e-proc "NNNNNNN-DD.AAAA.J.TR.OOOO" (#569)

## [17.11.6] - 2017-11-27
### Adicionado
- Filtro para defensorias/núcleos que aceitam encaminhamento (#564)

## [17.11.5] - 2017-11-24
### Corrigido
- Filtro de eventos de bloqueios no agendamento de atendimento #562

## [17.11.4] - 2017-11-20
### Corrigido
- Atualizado djdocuments para 0.0.40 para corrigir a issue #552

### Modificado
- Otimizado a inicialização de alguns js no template default ( 814e1b0305d5940635bb212b44fa92b31fdf227e )

## [17.11.3] - 2017-11-10
### Corrigido
- Permitir alterar qualificação de agendamento (#537)

## [17.11.2] - 2017-11-09
### Adicionado
- Mostrar quem cadastrou a fase processual (#533)
- Mostrar nome do assistido e ícones em fases processuais (#529)

### Modificado
- Ordena tarefas por data inicial no painel do defensor (#532)
- Atualizado djdocuments para 0.0.39 para corrigir a issue #534

### Corrigido
- Permitir excluir fase processual cadastrada no mês vigente (#535)

## [17.11.1] - 2017-11-06
### Modificado
- Atendimento com prazo deve vir na ordem normal de exibição (#530)

### Corrigido
- Busca de presos no Livre (#531)

## [17.10.11] - 2017-10-30
### Adicionado
- Personalização da imagem utilizada para documentos assinados no GED (#525)

### Modificado
- Djdocuments para 0.0.38 (#525)

## [17.10.10] - 2017-10-27
### Adicionado
- Personalização de GOOGLE_ANALYTICS_ID (#524)

### Corrigido
- Função de conversão de model CEP para JsonResponse (#522) (!73)
- Ao cadastrar endereço de assistido, pré-selecionar estado do usuário logado (#523) (!73)

## [17.10.9] - 2017-10-26
### Adicionado
- Personalizar Time Zone (#521)

### Modificado
- Vincular novo documento ao atendimento aberto em vez do inicial (#513)

### Corrigido
- Incremento 3 horas ao realizar audiências (erro conversão hora timezone > utc) (#520)

## [17.10.8] - 2017-10-20
### Adicionado
- Editar anotação do agendamento no dia do cadastro (#517)

### Modificado
- Acesso Público por padrão para Agendamento Inicial e Atendimento para Processo (#504)

### Corrigido
- Busca de atuação para Multidisciplinar (#518)
- Botão "Carregar mais" não ir ao topo da página (#485)
- Campo de data no cadastro de atuação (#469)
- Filtro de Tarefas (painel de defensor) para trazer apenas Ativas e com qualquer data inicial (#489)
- Redirecionamento de URL ao clicar no botão "Voltar" da página "Detalhes do Atendimento" (#496)
- Exibição de mensagem de erro no Cadastro de Movimentação PAD, campo Data de Protocolo (#483)

## [17.10.7] - 2017-10-18
### Adicionado
- Cria função (e migrate) buscar_assistido_filiacao (0da62e0a8cb03f6f79cce3181859c7f07c6bb34f)

### Modificado
- Relatório de hipossuficiência (#516)
- Exibir anotações agendamento/recepção ao agendar novo atendimento (#511)

## [17.10.6] - 2017-10-17
### Adicionado
- Permissão para agendar em dias com bloqueio na agenda (#463)

### Modificado
- Remarcar atendimento inicial para qualquer defensor da área (#503)
- Permitir agendar encaminhamento de atendimento na pauta (#499)

### Corrigido
- Limpar caches ao modificar defensoria (#502)
- Mostrar comarca da lotação do servidor como padrão no painel multidisciplinar (#515)
- Erro ao cadastrar prisão quando algumas datas não são informadas (038f8cb8a4b9a1dc7cbcfecddc07b31671c9e759)

## [17.10.5] - 2017-10-16
### Adicionado
- Criado migrate com as funcões que foram criadas manualmente (#451)
- Exibir status "Em atendimento" para recepção e defensor (#492)

## [17.10.4] - 2017-10-11
### Adicionado
- Permitir escolher dias extra-pauta ao cadastrar agenda (#466)
- Permitir informar grau ao cadastrar processo físico (c3dddcd13d3e0ff3d133cfd66462d420ac45cf1b)

### Modificado
- Permitir escolher sábado e domingo ao cadastrar agenda (#488)
- Ignorar bloqueios (feriados) na agenda itinerante (#512)

### Corrigido
- Manter campos habilitados na página 'Cadastro de Agenda' (#468)
- Problema ao salvar agenda com mais de 2 atuações (#498)

## [17.10.3] - 2017-10-04
### Corrigido
- Impedir cadastro duplicado de assistido ao tentar salvar sem a filiação ( #429 )

## [17.10.2] - 2017-10-03
### Corrigido
- Impedir cadastro de prisão com datas futuras ( !52 )

## [17.10.1] - 2017-10-02
### Adicionado
- Excluir prisão ( !50 )
- Personalizar URL do Chronus no `.env` ( b9c4d70e73f79cb0babd633466fa739185a70c27 )
- Ativa/Desativa cadastro de múltiplas atuações simultâneas na mesma defensoria ( d30fa7d784bc1c448542b54af8f5908497c646bd )
- Ativa/Desativa consulta no PROCAPI ao cadastrar novo processo ( 3b62f15d963d25624d703a13cbb6d1c644618a75 )

### Modificado
- Consultar CEP diretamente no webservice dos Correios ( efb6d06db6a265995301a770ea726d83c8b1ced5 )

### Corrigido
- Permitir excluir telefone enquanto cadastra novo assistido ( f590b92df6054aa6dff5a78550ebe99400892b20 )
- Criar apenas um evento para bloqueio geral ( 347e0d4232a38cb4672b5a30f757a8f44c80af37 )
- Validar se CPF existe apenas em assistidos ativos ( 5d57dd04d01fbe8df66d9e765f47cb7b062140af )
- Filtrar varas a partir da comarca selecionada no cadastro de processo ( 8918226270eb726c7877f67b069ba5158c603a62 )
- Parâmetro de data para relatórios ( a105815df2656e877e731b1039d99c2025bfb1dc )
- Remover max-height das modais ( 2d8dd367d6d99c9314edbfb7e82e3eca7eb7abe0 )

## [17.09.3] - 2017-09-13
### Adicionado
- Prazo de resposta para documentos (ofícios) (!46)

## [17.09.2] - 2017-09-13
### Adicionado
- Módulo dos Oficiais de Diligências (!45)

## [17.09.1] - 2017-09-06
### Adicionado
- Formulário 'consumidor.gov.br' (!44)

## [16.12.1] - 2016-12-08
### Adicionado
- Módulo da Equipe Multidisciplinar

## [16.03.1] - 2016-03-29
### Adicionado
- Módulo Itinerante
