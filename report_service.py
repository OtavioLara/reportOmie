import requests

import util
from util import *
from functools import lru_cache
from tqdm import trange
from time import sleep
from datetime import datetime

class ReportService:
    requests_number = 0
    
    def __init__(self, company):

        self.company = company
        self.api_path = 'https://app.omie.com.br/api/v1/'
        self.app_keys = {
            'TCM': {
                'app_key': '5053140946854',
                'app_secret': '3f75cfba3b9b101061bf42276cc6be29'
            },
            'NutriArt': {
                'app_key': '5053148613513',
                'app_secret': 'f48820061ff7953aa43e9645eb1f6d39'
            }
        }
        
    def create_request(self, resource, body):
        ReportService.requests_number += 1
        body.update({
            'app_key': self.app_keys[self.company]['app_key'],
            'app_secret': self.app_keys[self.company]['app_secret'],
        })
        r = requests.post(
            url=f'{self.api_path}/{resource}',
            auth=(self.app_keys[self.company]['app_key'], self.app_keys[self.company]['app_secret']),
            headers={'Content-Type': 'application/json'},
            json=body)
    
        return r.json()


    def get_nf_by_page(self, page, page_size):
        resource = 'produtos/nfconsultar/'
        body = {
            'call': 'ListarNF',
            'param': [
                {
                    "pagina": page,
                    "registros_por_pagina": page_size,
                    "apenas_importado_api": "N",
                    "ordenar_por": "CODIGO"
                }
            ]
        }
        return self.create_request(resource, body)

    def get_pedidos(self, page, page_size):
        resource = 'produtos/pedido/'
        body = {
            'call': 'ListarPedidos',
            'param': [
                {
                    "pagina": page,
                    "registros_por_pagina": page_size,
                    "apenas_importado_api": "N"
                }
            ]
        }
        return self.create_request(resource, body)


    @lru_cache(1000)
    def get_client_by_code(self, client_code):
        resource = 'geral/clientes/'
        body = {
            'call': 'ConsultarCliente',
            'param': [
                {
                    "codigo_cliente_omie": client_code,
                }
            ]
        }
        return self.create_request(resource, body)

    @lru_cache(1000)
    def get_caracteristica_client(self, cod_client):
        resource = 'geral/clientescaract/'
        body = {
            'call': 'ConsultarCaractCliente',
            'param': [
                {
                    "codigo_cliente_omie": cod_client,
                    "codigo_cliente_integracao": ""
                }
            ]
        }
        return self.create_request(resource, body)

    @lru_cache(1000)
    def list_caracteristica_produto(self, cod_prod):
        resource = 'geral/prodcaract/'
        body = {
            'call': 'ListarCaractProduto',
            'param': [
                {
                    "nPagina": 1,
                    "nRegPorPagina": 50,
                    "nCodProd": cod_prod
                }
            ]
        }
        return self.create_request(resource, body)

    @lru_cache(1000)
    def get_pedidos_venda_faturada(self):
        resource = 'produtos/pedidovendafat/'
        body = {
            'call': 'ObterPedidosVenda',
            'param': [
                {
                    "cEtapa": "60"
                }
            ]
        }
        return self.create_request(resource, body)

    def load_all_nfes(self, report):
        page_size = 300
        dict_nfes = self.get_nf_by_page(1, page_size)
        total_pages = dict_nfes['total_de_paginas']
        nfe_dict_data = {}
        report.nfe_total = dict_nfes['total_de_registros']
        added_something = True
        for page in range(total_pages,  0, -1):
            if 'nfCadastro' in dict_nfes.keys() and added_something:
                added_something = False
                dict_nfes = self.get_nf_by_page(page, page_size)
                for nfe in dict_nfes['nfCadastro']:
                    report.nfe_count += 1
                    if report.stopped():
                        return
                    if nfe['compl']['nIdPedido'] != 0 and (datetime.strptime(nfe['ide']['dEmi'], '%d/%m/%Y') >= datetime(report.year_competence, month=report.month_competence, day=1)):
                        nfe_dict_data.update({str(nfe['compl']['nIdPedido']): nfe['ide']['nNF']})
                        added_something = True

        with open(f'cache/nfes_{self.company}.json', 'w', encoding='utf8') as f:
            f.write(json.dumps(nfe_dict_data))

# rs = ReportService('NutriArt')
# dict_nfes = rs.get_nf_by_page(20, 1000)
# # print(util.pretty_print_dict(dict_nfes))
# with open(f'cache/teste_{rs.company}.json', 'w', encoding='utf8') as f:
#     f.write(util.pretty_print_dict(dict_nfes))
