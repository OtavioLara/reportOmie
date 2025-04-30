from datetime import datetime
from report_service import ReportService
import json
from threading import Thread, Event
from util import generate_report_excel
from ReportExceptions import *
import logging
logger = logging.getLogger(__name__)


class ReportGenerator(Thread):

    def __init__(self, company, sold_code, month_competence, year_competence, fill_empty_segmento_venda):
        super().__init__()
        self.nfe_total = 0
        self.nfe_count = 0
        self.registers_total = 0
        self.registers_cur = 0
        self.company = company
        self.report_service = ReportService(self.company)
        self.missing_nestle_code_products = {}
        self.sold_code = sold_code
        self.month_competence = month_competence
        self.year_competence = year_competence
        self.fill_empty_segmento_venda = fill_empty_segmento_venda
        self._stop_event = Event()

        self.exception = None

    def create_products(self, pedido):
        products_list = [det['produto'] for det in pedido['det']]
        products_data = []
        for product in products_list:
            product_characteristics = self.report_service.list_caracteristica_produto(product['codigo_produto'])
            cod_produto_nestle = ''
            if 'listaCaracteristicas' not in product_characteristics.keys():
                continue
            for characteristic in product_characteristics['listaCaracteristicas']:
                if characteristic['cNomeCaract'] == 'CODIGO NESTLE':
                    cod_produto_nestle = characteristic['cConteudo']
            if cod_produto_nestle == '':
                self.missing_nestle_code_products.update({product['codigo_produto'] :
                                                         {'Codigo': product['codigo_produto'],
                                                          'Descrição': product['descricao']}
                                                     })
            product_data = {
                'codCupom': product['codigo'],
                "codProdutoNestle_CodEAN": cod_produto_nestle,
                "nomeProduto": product['descricao'],
                "unidade": product['quantidade'],
                "unidadeMedida": "UNI",
                "fator": "1"
            }
            products_data.append(product_data)

        return products_data


    def create_venda(self, client, codigo_client_caracteristica, segmento_venda, pedido, data_venda, nfes):
        if len(client['enderecoEntrega']) > 0:
            endereco_entrega = client['enderecoEntrega']
            endereco_entrega_str = (f"{endereco_entrega['entEndereco']}, "
                                f"{endereco_entrega['entNumero']}, "
                                f"{endereco_entrega['entBairro']}")
            cep_entrega = endereco_entrega['entCEP']
            cidade_entrega = endereco_entrega['entCidade']
            uf_entrega = endereco_entrega['entEstado']
            cnpj_entrega = endereco_entrega['entCnpjCpf'] if 'entCnpjCpf' in endereco_entrega.keys() else client['cnpj_cpf']
            razao_social_entrega = endereco_entrega['entRazaoSocial'] if 'entRazaoSocial' in endereco_entrega.keys() else client['razao_social']
        else:
            endereco_entrega_str = client['endereco']
            cep_entrega = client['cep']
            cidade_entrega = client['cidade']
            uf_entrega = client['estado']
            cnpj_entrega = client['cnpj_cpf']
            razao_social_entrega = client['razao_social']

        products_data = self.create_products(pedido)
        cod_pedido = str(pedido['cabecalho']['codigo_pedido'])
        if cod_pedido not in nfes.keys():
            raise NotaFiscalNotFoundException(str(pedido['cabecalho']['codigo_pedido']))
        else:
            num_nfe = nfes[str(pedido['cabecalho']['codigo_pedido'])]

        return {
            'razaoSocialEntrega': razao_social_entrega,
            'cnpjEntrega': cnpj_entrega,
            'codClienteEntrega': codigo_client_caracteristica,
            'enderecoClienteEntrega': endereco_entrega_str,
            'cepEntrega': cep_entrega,
            'cidadeEntrega': cidade_entrega,
            'ufEntrega': uf_entrega,
            'tipoClienteEntrega': client['tipo_cliente'],
            'tipoDeDocumento': 'V',
            'segmentoClienteEntrega': segmento_venda,
            'notaFiscal': num_nfe,
            'dataVenda': data_venda,
            'produtos': products_data,
        }

    def create_report_from_omie(self):
        page = 1
        page_size = 500
        pedidos_json = self.report_service.get_pedidos(page, page_size)
        data_list = {}
        self.report_service.load_all_nfes(self)

        with open(f'cache/nfes_{self.company}.json', 'r') as f:
            nfes = json.loads(f.read())

        self.registers_total = self.report_service.get_pedidos(1, 2)['total_de_registros']
        while pedidos_json.get('pagina') is not None:
            for pedido in pedidos_json['pedido_venda_produto']:
                self.registers_cur += 1
                if 'dFat' not in pedido['infoCadastro'].keys():
                    continue
                data_pedido = datetime.strptime(pedido['infoCadastro']['dFat'], "%d/%m/%Y")
                data_venda = data_pedido.strftime("%Y-%m-%d")
                start_competence = datetime(self.year_competence, self.month_competence, 1)
                end_competence = datetime(self.year_competence, self.month_competence+1, 1)
                etapa = pedido['cabecalho']['etapa']
                if (etapa != '70' and etapa != '60') or (data_pedido < start_competence or data_pedido >= end_competence):
                    continue

                client = self.report_service.get_client_by_code(pedido['cabecalho']['codigo_cliente'])
                if 'pessoa_fisica' in client.keys():
                    client['tipo_cliente'] = 'PF' if client['pessoa_fisica'] == 'S' else 'PJ'
                else:
                    client['tipo_cliente'] = 'PF'
                client_caracteristica = self.report_service.get_caracteristica_client(pedido['cabecalho']['codigo_cliente'])
                segmento_venda, codigo_client_caracteristica = None, None
                if 'caracteristicas' in client_caracteristica.keys():
                    for caracteristica in client_caracteristica['caracteristicas']:
                        if caracteristica['campo'] == 'SEGMENTO DA VENDA':
                            segmento_venda = caracteristica['conteudo']
                        elif caracteristica['campo'] == 'CODIGO DO CLIENTE':
                            codigo_client_caracteristica = caracteristica['conteudo']
                if segmento_venda is None and self.fill_empty_segmento_venda:
                    if client['tipo_cliente'] == 'PF':
                        segmento_venda = 'Venda Balcão'
                    else:
                        segmento_venda = ''
                elif segmento_venda is None and not self.fill_empty_segmento_venda:
                    segmento_venda = ''
                if codigo_client_caracteristica is None:
                    codigo_client_caracteristica = ''

                venda = self.create_venda(client, codigo_client_caracteristica, segmento_venda, pedido, data_venda, nfes)

                if data_list.get(client['cnpj_cpf']):
                    data = data_list.get(client['cnpj_cpf'])
                    data['vendas'].append(venda)
                else:
                    data = {
                        'sold': self.sold_code,
                        'razaoSocialFaturado': client['razao_social'],
                        'cnpjFaturado': client['cnpj_cpf'],
                        'codCLienteFaturado': codigo_client_caracteristica,
                        'enderecoClienteFaturado': client['endereco'],
                        'cepFaturado': client['cep'],
                        'cidadeFaturado': client['cidade'],
                        'ufFaturado': client['estado'],
                        'tipoClienteFaturado': client['tipo_cliente'],
                        'segmentoClienteFaturado': segmento_venda,
                        'vendas': [venda]
                    }

                data_list.update({data['cnpjFaturado']: data})
            page += 1
            pedidos_json = self.report_service.get_pedidos(page, page_size)
        return data_list

    def run(self):
        try:
            start_time = datetime.now()
            report = self.create_report_from_omie()
            generate_report_excel(self.company, f'{self.month_competence:02d}{self.year_competence}', report)
            total_time = datetime.now() - start_time
            print(str(self.report_service.requests_number / (total_time.seconds / 60)) + 'Rq/Minute')
        except Exception as e:
            self.exception = e


    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
# rg = ReportGenerator('TCM', 1234, 3, 2025, True)
# print(rg.report_service.get_nf_by_page(1, 2))