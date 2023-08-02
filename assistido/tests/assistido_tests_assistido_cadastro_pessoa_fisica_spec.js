Array.prototype.remove = function() {
    let what, a = arguments, L = a.length, ax;
    while (L && this.length) {
        what = a[--L];
        while ((ax = this.indexOf(what)) !== -1) {
            this.splice(ax, 1);
        }
    }
    return this;
};

describe('Testes Referente a Cadastro de Assistido', () => {
    const DEBUG = true;
    const Leite = require('leite');
    const leite = new Leite();
    const URL_SOLAR = browser.params.url_solar;
    const LOGIN = browser.params.user.login;
    const SENHA = browser.params.user.password;
    const BOTAO_LOGIN = '//*[@id="sign-in"]/div[4]/input';
    const BOTAO_PESSOA_FISICA = '//*[@id="ContentSide"]/div/div[3]/div[1]/div/a[1]';
    const INPUT_CPF = '//*[@id="id_cpf"]';
    const INPUT_NOME = '//*[@id="id_nome"]';
    const INPUT_NOME_APELIDO = '//*[@id="id_apelido"]';
    const INPUT_FILIACAO = '//*[@id="mae0"]';
    const INPUT_DATA_NASCIMENTO = '//*[@id="id_data_nascimento"]';
    const SELECT_ESTADO_CIVIL = '//*[@id="id_estado_civil"]';
    const INPUT_NUMERO_TELEFONE = '/html/body/section/div[1]/div[2]/div/div[2]/div[1]/div/form/div[2]/div/div[1]/div[8]/div/input[1]';
    const INPUT_DESCRICAO_TELEFONE = '/html/body/section/div[1]/div[2]/div/div[2]/div[1]/div/form/div[2]/div/div[1]/div[8]/div/input[2]';
    const INPUT_EMAIL = '//*[@id="id_email"]';
    const INPUT_NOME_SOCIAL = '//*[@id="id_nome_social"]';
    const CHECKBOX_ORIENTACAO_SEXUAL = '//*[@id="id_declara_orientacao_sexual"]';
    const CHECKBOX_DECLARA_IDENTIDADE_GENERO = '//*[@id="id_declara_identidade_genero"]';
    const ABA_DOCUMENTOS_PESSOAIS = '//*[@id="myTab"]/li[8]/a';
    const ABA_MEMBROS = '//*[@id="myTab"]/li[2]/a';
    const BOTAO_SALVAR_CADASTRO_ASSISTIDO = '//*[@id="salvar"]';
    const INPUT_CPF_TELA_BUSCAR = '//*[@id="cpf"]';
    const INPUT_NOME_TELA_BUSCAR = '//*[@id="nome"]';
    const BOTAO_BUSCAR_ASSISTIDO = '//*[@id="ContentSide"]/div/div[2]/div/div/form/div/button';
    const ABA_BOTAO_AVALIACAO = '//*[@id="myTab"]/li[3]/a';
    const BOTAO_FECHAR_MODAL = '//*[@id="modal-avaliacao"]/div[1]/button';
    const INPUT_VALORES_PATRIMONIAIS_MOVEIS = '//*[@id="id_patrimonio-valor_moveis"]';
    const INPUT_VALORES_PATRIMONIAIS_IMOVEIS = '//*[@id="id_patrimonio-valor_imoveis"]';
    const INPUT_VALORES_DE_OUTROS_BENS = '//*[@id="id_patrimonio-valor_outros_bens"]';
    const INPUT_VALORES_DE_INVESTIMENTOS = '//*[@id="id_patrimonio-valor_investimentos"]';
    const INPUT_RENDA_INDIVIDUAL = '//*[@id="id_renda-ganho_mensal"]';
    const INPUT_RENDA_FAMILIAR = '//*[@id="id_renda-ganho_mensal_membros"]';
    const CHECKBOX_SITUACAO_FALECIDO = '//*[@id="situacao_3"]';
    const CHECKBOX_SITUACAO_IDOSO = '//*[@id="situacao_2"]';
    const CHECKBOX_SITUACAO_PNE = '//*[@id="situacao_1"]';
    const CHECKBOX_SITUACAO_PRESO = '//*[@id="situacao_4"]';
    const ABA_ADICIONAL = '//*[@id="myTab"]/li[4]/a';
    const INPUT_NUMERO_RG = '//*[@id="id_rg_numero"]';
    const INPUT_ORGAO_RG = '//*[@id="id_rg_orgao"]';
    const SELECT_COR_RACA = '//*[@id="id_raca"]/option';
    const INPUT_QUANTIDADE_FILHOS = '//*[@id="id_qtd_filhos"]';
    const INPUT_NATURALIDADE = '//*[@id="id_naturalidade"]';
    const INPUT_NATURALIDADE_UF = '//*[@id="id_naturalidade_estado"]';
    const ABA_ENDERECO = '//*[@id="myTab"]/li[5]/a';
    const BOTAO_NOVO_ENDERECO = '//*[@id="endereco"]/div[1]/div[1]/button[1]';
    const SELECT_TIPOS_ENDERECO = '//*[contains(@ng-model, "endereco_selecionado.tipo")]/option';
    const INPUT_CEP = '//*[@id="id_cep"]';
    const SELECT_MUNICIPIOS = '//*[contains(@ng-model, "endereco_selecionado.municipio")]/option';
    const INPUT_BAIRRO = '//*[@id="id_bairro"]';
    const INPUT_LOGRADOURO = '//*[@id="id_logradouro"]';
    const INPUT_NUMERO = '//*[@id="id_numero"]';
    const INPUT_COMPLEMENTO = '//*[@id="id_complemento"]';
    const BUTTON_ADICIONAR_ENDERECO = '//*[@id="endereco"]/div[1]/button[1]';
    const ABA_EMPREGOMORADIA = '//*[@id="myTab"]/li[6]/a';
    const SELECT_ESCOLARIDADE = '//*[contains(@ng-model, "pessoa.escolaridade")]/option';
    const SELECT_TIPOTRABALHO = '//*[contains(@ng-model, "pessoa.tipo_trabalho")]/option';
    const INPUT_PROFISSAO = '//*[contains(@ng-model, "pessoa.profissao")]';
    const INPUT_QUANTIDADE_ANOS_ESTADO = '//*[contains(@ng-model, "pessoa.qtd_estado")]';
    const SELECT_IMOVEL = '//*[contains(@ng-model, "pessoa.moradia.tipo")]/option';
    const INPUT_NUMERO_COMODOS = '//*[contains(@ng-model, "pessoa.moradia.num_comodos")]';
    const CHECKBOX_ESTRUTURA_ESGOTO = '//*[contains(@ng-model, "pessoa.estrutura[1]")]';
    const CHECKBOX_ESTRUTURA_FOSSA = '//*[contains(@ng-model, "pessoa.estrutura[2]")]';
    const CHECKBOX_ESTRUTURA_INSTALACAOSANITARIA = '//*[contains(@ng-model, "pessoa.estrutura[3]")]';
    const CHECKBOX_ESTRUTURA_ENERGIAELETRICA = '//*[contains(@ng-model, "pessoa.estrutura[4]")]';
    const CHECKBOX_ESTRUTURA_AGUAENCANADA = '//*[contains(@ng-model, "pessoa.estrutura[5]")]';
    const CHECKBOX_ESTRUTURA_INTERNET = '//*[contains(@ng-model, "pessoa.estrutura[6]")]';
    const ARRAY_DE_SELECTS_E_OPTIONS_DE_AVALIACAO_CADASTRO = [
            {
                SELECT : '//*[@id="id_patrimonio-tem_moveis"]',
                OPTION : '//*[@id="id_patrimonio-tem_moveis"]/option[1]'
            },
            {
                SELECT: '//*[@id="id_patrimonio-tem_imoveis"]',
                OPTION: '//*[@id="id_patrimonio-tem_imoveis"]/option[1]'
            },
            {
                SELECT: '//*[@id="id_patrimonio-tem_outros_bens"]',
                OPTION: '//*[@id="id_patrimonio-tem_outros_bens"]/option[1]'
            },
            {
                SELECT: '//*[@id="id_patrimonio-tem_investimentos"]',
                OPTION: '//*[@id="id_patrimonio-tem_investimentos"]/option[1]'
            }
    ];
    const abasCadastroPessoaFisica = {
        abaBasico: {
            genero: { 
                possibilidades: ['Masculino', 'Feminino'],
                valorPadrao: 'Masculino',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            },
            estadoCivil: {
                possibilidades: ['Solteiro(a)', 'Casado(a)', 'Viuvo(a)', 'Divorciado(a)', 'União estável', 'Separado judicialmente'],
                valorPadrao: 'Solteiro(a)',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            },
            tipoTelefone: {
                possibilidades: ['Celular', 'Residencial', 'Comercial', 'Recado', 'WhatsApp'],
                valorPadrao: 'Celular',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            },
            orientacaoSexual: {
                possibilidades: ['Bissexual', 'Heterossexual', 'Homossexual'],
                valorPadrao: 'Heterossexual',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            },
            identidadeGenero: {
                possibilidades: ['Homem Transexual', 'Ignorado', 'Mulher Transexual', 'Não se aplica', 'Travesti'],
                valorPadrao: 'Não se aplica',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            }
        },
        abaMembro: {
            membros: {
                possibilidades: ['Pai/Mãe', 'Filho/Filha', 'Irmão/Irmã', 'Tio/Tia', 'Primo/Prima', 'Avô/Avó', 'Outro'],
                valorPadrao: 'Cônjuge/Companheiro(a)',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            },
        },
        abaAvaliacao: { 
            planoSaude: {
                possibilidades: ['Sim', 'Não'],
                valorPadrao: 'Não',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            },
            isentoIR: {
                possibilidades: ['Sim', 'Não'],
                valorPadrao: 'Sim',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            }, 
            previdencia: {
                possibilidades: ['Sim', 'Não'],
                valorPadrao: 'Não',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            }
        },
        abaAdicional: {
            cor: {
                possibilidades: ['Preta', 'Parda', 'Branca', 'Amarela', 'Indígena', 'Não soube responder'],
                valorPadrao: 'Não soube responder',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            },
        },
        abaEndereco: {
            area: {
                possibilidades: ['Urbana', 'Rural'],
                valorPadrao: 'Urbana',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            },
            tipo:{
                possibilidades: ['Residencial', 'Comercial', 'Correspondência', 'Alternativo'],
                valorPadrao: 'Residencial',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            }		
        },
        abaEmpregoMoradia: {
            escolaridade: {
                possibilidades: ['Nenhuma (Analfabeto)', 'Fundamental Incompleto. (1° ao 9° ano)', 'Fundamental Completo. (1° ao 9° ano)', 'Médio Incompleto. (2°grau)', 'Médio Completo. (2° grau)', 'Superior Incompleto', 'Superior Completo', 'Pós-Graduado'],
                valorPadrao: 'Nenhuma (Analfabeto)',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            },
            tipoTrabalho: {
                possibilidades: ['Carteira Assinada', 'Autônomo', 'Servidor Público', 'Aposentado', 'Desempregado'],
                valorPadrao: 'Carteira Assinada',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            },
            imovel: {
                possibilidades: ['Próprio', 'Programa Habitacional (Doação do Gov: Federal, Estadual ou Municipal)', 'Alugado', 'Cedido', 'Financiado'],
                valorPadrao: 'Próprio',
                sortearValoresParaTeste: function() {return sortearValor(this)}
            }
        }
    }

    function sortearValor(contexto){
        let resultadoDoSorteio =(contexto.possibilidades.length > 0) ? contexto.possibilidades[Math.floor(Math.random() * contexto.possibilidades.length)] : contexto.valorPadrao;
        contexto.possibilidades.remove(resultadoDoSorteio);
        return resultadoDoSorteio;
    }

    function selecionarOptionDeUmSelect(select, optionPretendido){
        browser.driver.findElements(by.xpath(select)).then((options) => {
            options.forEach((option => {
                option.getText().then(optionvalue => {
                    if(optionvalue == optionPretendido) option.click();
                });
            }))
        });
    }

    /**
     * Realiza login no solar e acessa pagina de cadastro de assistido pessoa fisica
     */
    beforeAll( () => {
        browser.ignoreSynchronization;
        browser.driver.get(URL_SOLAR)
        .then(() => browser.driver.findElement(by.id("username")).sendKeys(LOGIN))
        .then(() => browser.driver.findElement(by.id("password")).sendKeys(SENHA))
        .then(() => browser.driver.findElement(by.xpath(BOTAO_LOGIN)).click())
        .then(() => {if(DEBUG) console.log(`Foi realizado login no ${URL_SOLAR}`)});
        //browser.driver.manage().window().maximize();
    });
    function test_cadastro_completo(){
        it('cadastro completo', () => {
            let assistido = {
            	cpf : leite.pessoa.cpf({formatado: true}),
                sexo: leite.pessoa.sexo(),
                nomeAssistido: leite.pessoa.nome({ sexo: this.sexo }),
                nomeApelido: leite.pessoa.nome(),
                nomeMaeAssistido: leite.pessoa.nome({ sexo: 'Feminino' }),
                dataNascimento: leite.pessoa.nascimento({ formato: 'DDMMYYYY', string: true }),
                estadoCivil: abasCadastroPessoaFisica.abaBasico.estadoCivil.sortearValoresParaTeste(),
                membro: null,
                email: leite.pessoa.email(),
                orientacaoSexual: abasCadastroPessoaFisica.abaBasico.orientacaoSexual.sortearValoresParaTeste(),
                identidadeGenero: abasCadastroPessoaFisica.abaBasico.identidadeGenero.sortearValoresParaTeste(),
                nomeSocial: leite.pessoa.nome(),
                planoSaude: abasCadastroPessoaFisica.abaAvaliacao.planoSaude.sortearValoresParaTeste(),
                isentoIR: abasCadastroPessoaFisica.abaAvaliacao.isentoIR.sortearValoresParaTeste(),
                previdencia: abasCadastroPessoaFisica.abaAvaliacao.previdencia.sortearValoresParaTeste(),
                cor: abasCadastroPessoaFisica.abaAdicional.cor.sortearValoresParaTeste(),
                area: abasCadastroPessoaFisica.abaEndereco.area.sortearValoresParaTeste(),
                tipoEndereco: abasCadastroPessoaFisica.abaEndereco.tipo.sortearValoresParaTeste(),
                escolaridade: abasCadastroPessoaFisica.abaEmpregoMoradia.escolaridade.sortearValoresParaTeste(),
                tipoTrabalho: abasCadastroPessoaFisica.abaEmpregoMoradia.tipoTrabalho.sortearValoresParaTeste(),
                profissao: 'programador',
                quantidadeAnosEstado: 3,
                imovel: abasCadastroPessoaFisica.abaEmpregoMoradia.imovel.sortearValoresParaTeste(),
                numeroComodos: 5,
                tipoTelefone: abasCadastroPessoaFisica.abaBasico.tipoTelefone.sortearValoresParaTeste(),
                numeroTelefone: '11111111111',
                numeroRG: 5000,
                descricaoTelefone: 'descrição do telefone',
                orgaoExpeditor: 'SSP RO',
                naturalidade: 'Brasileiro',
                naturalidadeUF: 'Rondônia',
                cep: '76890000',
            };
            assistido.membro = (assistido.estadoCivil.toString().trim() != 'Casado(a)') && (assistido.estadoCivil.toString().trim() != 'União estável') ? abasCadastroPessoaFisica.abaMembro.membros.sortearValoresParaTeste(): null;
            if(DEBUG) console.log(JSON.stringify(assistido) + '\n');
            browser.driver.get(`${URL_SOLAR}/assistido/buscar/`)
            .then(() => browser.driver.findElement(by.xpath(BOTAO_PESSOA_FISICA)).click())
            .then(() => browser.driver.findElement(by.xpath(INPUT_CPF)).sendKeys(assistido.cpf))
            .then(() => browser.driver.findElement(by.xpath(INPUT_NOME)).sendKeys(assistido.nomeAssistido))
            .then(() => browser.driver.findElement(by.xpath(INPUT_NOME_APELIDO)).sendKeys(assistido.nomeApelido))
            .then(() => browser.driver.findElement(by.xpath(INPUT_FILIACAO)).sendKeys(assistido.nomeMaeAssistido))
            .then(() => browser.driver.findElement(by.xpath(INPUT_DATA_NASCIMENTO)).click())
            .then(() => browser.driver.findElement(by.xpath(INPUT_DATA_NASCIMENTO)).sendKeys(assistido.dataNascimento))
            .then(() => browser.driver.findElement(by.tagName('body')).click())
            .then(() => browser.driver.findElement(by.xpath(`//label[contains(text(),"${assistido.sexo}")]/input`)).click())
            .then(() => browser.driver.findElement(by.xpath(`//*[@id="id_estado_civil"]/option[text()="${assistido.estadoCivil}"]`)).click())
            .then(() => browser.driver.findElement(by.xpath('/html/body/section/div[1]/div[2]/div/div[2]/div[1]/div/form/div[2]/div/div[1]/div[8]/div/div/button')).click())
            .then(() => browser.driver.findElement(by.xpath(`/html/body/section/div[1]/div[2]/div/div[2]/div[1]/div/form/div[2]/div/div[1]/div[8]/div/div/ul/li/a[contains(text(),"${assistido.tipoTelefone}")]`)).click())
            .then(() => browser.driver.findElement(by.xpath(INPUT_NUMERO_TELEFONE)).sendKeys(assistido.numeroTelefone))
            .then(() => browser.driver.findElement(by.xpath(INPUT_DESCRICAO_TELEFONE)).sendKeys(assistido.descricaoTelefone))
            .then(() => browser.driver.findElement(by.xpath(INPUT_EMAIL)).sendKeys(assistido.email))
            .then(() => {browser.driver.findElement(by.xpath(CHECKBOX_ORIENTACAO_SEXUAL)).click()})
            .then(() => browser.driver.findElement(by.xpath(`//*[@id="id_orientacao_sexual"]/option[text()="${assistido.orientacaoSexual}"]`)).click())
            .then(() => {browser.driver.findElement(by.xpath(CHECKBOX_DECLARA_IDENTIDADE_GENERO)).click()})
            .then(() => browser.driver.findElement(by.xpath(`//*[@id="id_identidade_genero"]/option[text()="${assistido.identidadeGenero}"]`)).click())
            .then(() => {if (assistido.orientacaoSexual != 'Heterossexual') browser.driver.findElement(by.xpath(INPUT_NOME_SOCIAL)).sendKeys(assistido.nomeSocial)})
            .then(() => {if(DEBUG) console.log('Preenchido cadastro básico \n')})
            .then(() => browser.driver.findElement(by.xpath(ABA_DOCUMENTOS_PESSOAIS)).click())
            .then(() => browser.driver.findElement(by.xpath(ABA_MEMBROS)).click())
            .then(() => {
                if((assistido.estadoCivil.toString().trim() != 'Casado(a)') && (assistido.estadoCivil.toString().trim() != 'União estável')){
                    browser.driver.findElement(by.xpath('//*[@id="membros"]/div/div/button')).click();
                    browser.driver.findElement(by.xpath('//html/body/section/div[1]/div[2]/div/div[2]/div[1]/div/form/div[2]/div/div[2]/div[2]/div/div/button')).click();
                    browser.driver.findElement(by.xpath(`//html/body/section/div[1]/div[2]/div/div[2]/div[1]/div/form/div[2]/div/div[2]/div[2]/div/div/ul/li/a[contains(text(),"${assistido.membro}")]`)).click();
                    browser.driver.findElement(by.xpath('//*[@id="membros"]/div[2]/div/input[1]')).sendKeys(leite.pessoa.nome());
                    browser.driver.findElement(by.xpath('/html/body/section/div[1]/div[2]/div/div[2]/div[1]/div/form/div[2]/div/div[2]/div[2]/div/input[2]')).sendKeys("10000");
                }else{
                    browser.driver.findElement(by.xpath('//*[@id="membros"]/div[1]/div/input[1]')).sendKeys(leite.pessoa.nome()); 
                    browser.driver.findElement(by.xpath('/html/body/section/div[1]/div[2]/div/div[2]/div[1]/div/form/div[2]/div/div[2]/div[1]/div/input[2]')).sendKeys("10000");
                }
            })
            .then(() => {if(DEBUG) console.log('Preenchido informações na aba de membros familiares \n')})
            .then(() => browser.driver.findElement(by.xpath(ABA_BOTAO_AVALIACAO)).click())
            .then(() => browser.driver.sleep(1000))
            .then(() => browser.driver.wait(protractor.ExpectedConditions.elementToBeClickable(element(by.xpath(BOTAO_FECHAR_MODAL))), 100000).then(() => {
                browser.driver.findElement(by.xpath(BOTAO_FECHAR_MODAL)).click();
            }))
            .then(() => browser.driver.findElement(by.xpath(INPUT_RENDA_INDIVIDUAL)).sendKeys(1000000))
            .then(() => browser.driver.findElement(by.xpath(INPUT_RENDA_FAMILIAR)).sendKeys(1000000))
            .then(() => browser.driver.findElement(by.xpath(`//*[@id="id_renda-tem_plano_saude"]/option[contains(text(), "${assistido.planoSaude}")]`)).click())
            .then(() => browser.driver.findElement(by.xpath(`//*[@id="id_renda-isento_ir"]/option[contains(text(), "${assistido.isentoIR}")]`)).click())
            .then(() => browser.driver.findElement(by.xpath(`//*[@id="id_renda-previdencia"]/option[contains(text(), "${assistido.previdencia}")]`)).click())
            .then(() => {if(DEBUG) console.log('Preenchido informações na aba de avaliação \n')})
            .then(() => browser.driver.findElement(by.xpath(ABA_ADICIONAL)).click())
            .then(() => browser.driver.findElement(by.xpath(CHECKBOX_SITUACAO_FALECIDO)).click())
            .then(() => browser.driver.findElement(by.xpath(CHECKBOX_SITUACAO_IDOSO)).click())
            .then(() => browser.driver.findElement(by.xpath(CHECKBOX_SITUACAO_PNE)).click())
            .then(() => browser.driver.findElement(by.xpath(CHECKBOX_SITUACAO_PRESO)).click())
            .then(() => browser.driver.findElement(by.xpath(INPUT_NUMERO_RG)).sendKeys(assistido.numeroRG))
            .then(() => browser.driver.findElement(by.xpath(INPUT_ORGAO_RG)).sendKeys(assistido.orgaoExpeditor))
            .then(() => selecionarOptionDeUmSelect(SELECT_COR_RACA, assistido.cor))
            .then(() => browser.driver.findElement(by.xpath(INPUT_QUANTIDADE_FILHOS)).sendKeys(2))
            .then(() => browser.driver.findElement(by.xpath(INPUT_NATURALIDADE)).sendKeys(assistido.naturalidade))
            .then(() => browser.driver.findElement(by.xpath(INPUT_NATURALIDADE_UF)).sendKeys(assistido.naturalidadeUF))
            .then(() => {if(DEBUG) console.log('Preenchido informações na aba adicional \n')})
            .then(() => browser.driver.findElement(by.xpath(ABA_ENDERECO)).click())
            .then(() => browser.driver.sleep(1000))
            .then(() => browser.driver.findElement(by.xpath(BOTAO_NOVO_ENDERECO)).click())
            .then(() => browser.driver.findElement(by.xpath(`//*[contains(text(),"${assistido.area}")]/input`)).click())
            .then(() => selecionarOptionDeUmSelect(SELECT_TIPOS_ENDERECO, assistido.tipoEndereco))
            .then(() => browser.driver.findElement(by.xpath(INPUT_CEP)).sendKeys(assistido.cep))
            .then(() => browser.driver.findElements(by.xpath('//select[contains(@ng-model, "endereco_selecionado.estado")]/option')).then((options) => {
                options[Math.floor(options.length * Math.random())].click();
            }))
            .then(() => browser.driver.sleep(5000))
            .then(() => browser.driver.findElements(by.xpath('//select[contains(@ng-model, "endereco_selecionado.municipio")]/option')).then((options) => {
                options[Math.floor(options.length * Math.random())].click();
            }))
            .then(() => browser.driver.findElement(by.xpath(INPUT_BAIRRO)).sendKeys("Bairro Exemplo"))
            .then(() => browser.driver.findElement(by.xpath(INPUT_LOGRADOURO)).sendKeys("Logradouro Exemplo"))
            .then(() => browser.driver.findElement(by.xpath(INPUT_NUMERO)).sendKeys("11111"))
            .then(() => browser.driver.findElement(by.xpath(INPUT_COMPLEMENTO)).sendKeys("Complemento Exemplo"))
            .then(() => browser.driver.findElement(by.xpath(BUTTON_ADICIONAR_ENDERECO)).click())
            .then(() => {if(DEBUG) console.log('Preenchido informações na aba endereço \n')})
            .then(() => browser.driver.findElement(by.xpath(ABA_EMPREGOMORADIA)).click())
            .then(() => selecionarOptionDeUmSelect(SELECT_ESCOLARIDADE, assistido.escolaridade))
            .then(() => selecionarOptionDeUmSelect(SELECT_TIPOTRABALHO, assistido.tipoTrabalho))
            .then(() => browser.driver.findElement(by.xpath(INPUT_PROFISSAO)).sendKeys(assistido.profissao))
            .then(() => browser.driver.findElement(by.xpath(INPUT_QUANTIDADE_ANOS_ESTADO)).sendKeys(assistido.quantidadeAnosEstado))
            .then(() => selecionarOptionDeUmSelect(SELECT_IMOVEL, assistido.imovel))
            .then(() => browser.driver.findElement(by.xpath(INPUT_NUMERO_COMODOS)).sendKeys(assistido.numeroComodos))
            .then(() => browser.driver.findElement(by.xpath(CHECKBOX_ESTRUTURA_ESGOTO)).click())
            .then(() => browser.driver.findElement(by.xpath(CHECKBOX_ESTRUTURA_FOSSA)).click())
            .then(() => browser.driver.findElement(by.xpath(CHECKBOX_ESTRUTURA_INSTALACAOSANITARIA)).click())
            .then(() => browser.driver.findElement(by.xpath(CHECKBOX_ESTRUTURA_ENERGIAELETRICA)).click())
            .then(() => browser.driver.findElement(by.xpath(CHECKBOX_ESTRUTURA_AGUAENCANADA)).click())
            .then(() => browser.driver.findElement(by.xpath(CHECKBOX_ESTRUTURA_INTERNET)).click())
            .then(() => {if(DEBUG) console.log('Preenchido informações na emprego e moradia \n')})
            .then(() => browser.driver.findElement(by.xpath(ABA_DOCUMENTOS_PESSOAIS)).click())
            .then(() => browser.driver.findElement(by.xpath(BOTAO_SALVAR_CADASTRO_ASSISTIDO)).click())
            .then(() => browser.driver.get(`${URL_SOLAR}/assistido/buscar/`))
            .then(() => browser.driver.findElement(by.xpath(INPUT_NOME_TELA_BUSCAR)).sendKeys(assistido.nomeAssistido))
            .then(() => browser.driver.findElement(by.xpath(BOTAO_BUSCAR_ASSISTIDO)).click())
            .then(() => browser.driver.wait(protractor.ExpectedConditions.visibilityOf(element(by.xpath(`//*[contains(@data-title, "${assistido.nomeAssistido.toUpperCase()}")]`))), 10000)
            .then(() => {
                expect(browser.driver.findElement(by.xpath(`//*[contains(@data-title, "${assistido.nomeAssistido.toUpperCase()}")]`)).getText()).not.toEqual(null); 
            }));
        });
    }
     /**
     * Realiza cadastro completo.
     * Terá sucesso ao buscar assistido os dados estiverem iguais.
     * São 8 testes para fazer todas as possibilidades de inputs.
     **/
    for(let i=0; i<8; i++){
        test_cadastro_completo();
    }
});