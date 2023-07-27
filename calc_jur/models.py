from django.db import models


class Salario(models.Model):
    """Model representando um salário mínimo anual"""
    ano = models.CharField(max_length=4)
    valor = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True)

    def __str__(self):
        """String para representar um objeto do Model."""
        return f'{self.ano}  {self.valor}'


class Inpc(models.Model):
    """Model representando um INPC mensal"""
    ano_mes = models.CharField(max_length=6)
    valor = models.DecimalField(max_digits=6, decimal_places=2, default=0, null=True)

    def __str__(self):
        """String para representar um objeto do Model."""
        return f'{self.ano_mes}  {self.valor}'
