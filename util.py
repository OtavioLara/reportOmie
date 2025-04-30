import json
import pandas as pd

def pretty_print_dict(dict_json):
    pretty_json = json.dumps(dict_json, indent=2)
    return pretty_json

def generate_report_excel(company_name, competence, report_dict):

    rows = {
    'Sold' : [],
    'RazaoSocialFaturado' : [],
    'CnpjFaturado' : [],
    'CodClienteFaturado' : [],
    'EnderecoClienteFaturado' : [],
    'CepFaturado' : [],
    'CidadeFaturado' : [],
    'UfFaturado' : [],
    'TipoClienteFaturado' : [],
    'RazaoSocialEntrega' : [],
    'CnpjEntrega' : [],
    'CodClienteEntrega' : [],
    'EnderecoClienteEntrega' : [],
    'CepEntrega' : [],
    'CidadeEntrega' : [],
    'UfEntrega' : [],
    'TipoClienteEntrega' : [],
    'TipoDocumento' : [],
    'SegmentoVenda' : [],
    'NotaFiscal' : [],
    'CodigoCupom' : [],
    'DataVenda' : [],
    'CodigoProdutoNestle' : [],
    'NomeProduto' : [],
    'Unidade' : [],
    'UnidadeMedida' : [],
    'Fator' : []
    }

    for cliente in report_dict.values():
        for venda in cliente['vendas']:
            for produto in venda['produtos']:
                rows['Sold'].append(cliente['sold'])
                rows['RazaoSocialFaturado'].append(cliente['razaoSocialFaturado'])
                rows['CnpjFaturado'].append(cliente['cnpjFaturado'])
                rows['CodClienteFaturado'].append(cliente['codCLienteFaturado'])
                rows['EnderecoClienteFaturado'].append(cliente['enderecoClienteFaturado'])
                rows['CepFaturado'].append(cliente['cepFaturado'])
                rows['CidadeFaturado'].append(cliente['cidadeFaturado'])
                rows['UfFaturado'].append(cliente['ufFaturado'])
                rows['TipoClienteFaturado'].append(cliente['tipoClienteFaturado'])
                rows['RazaoSocialEntrega'].append(venda['razaoSocialEntrega'])
                rows['CnpjEntrega'].append(venda['cnpjEntrega'])
                rows['CodClienteEntrega'].append(venda['codClienteEntrega'])
                rows['EnderecoClienteEntrega'].append(venda['enderecoClienteEntrega'])
                rows['CepEntrega'].append(venda['cepEntrega'])
                rows['CidadeEntrega'].append(venda['cidadeEntrega'])
                rows['UfEntrega'].append(venda['ufEntrega'])
                rows['TipoClienteEntrega'].append(venda['tipoClienteEntrega'])
                rows['TipoDocumento'].append(venda['tipoDeDocumento'])
                rows['SegmentoVenda'].append(cliente['segmentoClienteFaturado'])
                rows['NotaFiscal'].append(venda['notaFiscal'])
                rows['CodigoCupom'].append(produto['codCupom'])
                rows['DataVenda'].append(venda['dataVenda'])
                rows['CodigoProdutoNestle'].append(produto['codProdutoNestle_CodEAN'])
                rows['NomeProduto'].append(produto['nomeProduto'])
                rows['Unidade'].append(produto['unidade'])
                rows['UnidadeMedida'].append(produto['unidadeMedida'])
                rows['Fator'].append(produto['fator'])

    df = pd.DataFrame(data=rows)
    df.to_excel(f'reports/report_{company_name}_{competence}.xlsx', index=False)


# { "sold": 0,
#   "secrectKeyDistribuidora": "string",
#   "periodo": "2022-05-02T14:03:47.823Z",
#   "clientes": [ { "cnpjFaturado": "string",
#                   "codCLienteFaturado": "string",
#                   "razaoSocialFaturado": "string",
#                   "enderecoClienteFaturado": "string",
#                   "cepFaturado": "string",
#                   "cidadeFaturado": "string",
#                   "ufFaturado": "string",
#                   "tipoClienteFaturado": "string",
#                   "segmentoClienteFaturado": "string",
#                   "vendas": [ {
#                       "cnpjEntrega": "string",
#                       "codClienteEntrega": "string",
#                       "razaoSocialEntrega": "string",
#                       "enderecoClienteEntrega": "string",
#                       "cepEntrega": "string",
#                       "cidadeEntrega": "string",
#                       "ufEntrega": "string",
#                       "tipoClienteEntrega": "string",
#                       "tipoDeDocumento": "string",
#                       "segmentoClienteEntrega": "string",
#                       "notaFiscal": "string",
#                       "codCupom": "string",
#                       "dataVenda": "string",
#                       "produtos": [ {
#                           "codProdutoNestle_CodEAN": "string",
#                           "nomeProduto": "string",
#                           "unidade": "string",
#                           "unidadeMedida": "string",
#                           "fator": "string" }
#                       ]
#                   } ]
#               } ]
#   }
