import logging
logger = logging.getLogger(__name__)
class ReportException(Exception):
    """Exceção pai que será lançada para cada erro do relatório gerado"""
    def __init__(self, company, competence, child_message):
        self.company = company
        self.competence = competence
        message = f"Erro para a emperesa {company} na competência {competence}: \n\t{child_message}"
        logger.error(message)
        super().__init__(message)

class NotaFiscalNotFoundException(ReportException):
    """Exceção lançada quando o não é encontrada uma Nota Fiscal baseada no número do pedido"""
    def __init__(self, company, competence, num_pedido):
        self.num_pedido = num_pedido
        message = f"Não foi encontrada a NFe baseada no número de pedido: {self.num_pedido}"
        super().__init__(company, competence, message)