# Generated by Django 3.2 on 2023-02-14 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0057_distribuicao_redistribuicao'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='documentofase',
            index=models.Index(fields=['fase', 'eproc'], name='processo_doc_fase_idx_001'),
        ),
        migrations.AddIndex(
            model_name='documentofase',
            index=models.Index(fields=['fase', 'nome'], name='processo_doc_fase_idx_002'),
        ),
        migrations.AddIndex(
            model_name='fase',
            index=models.Index(fields=['processo', 'ativo'], name='processo_fase_idx_001'),
        ),
        migrations.AddIndex(
            model_name='fase',
            index=models.Index(fields=['processo', 'tipo', 'data_protocolo'], name='processo_fase_idx_002'),
        ),
        migrations.AddIndex(
            model_name='manifestacao',
            index=models.Index(condition=models.Q(desativado_em=None), fields=['cadastrado_por'], name='processo_manifestacao_idx_001'),
        ),
        migrations.AddIndex(
            model_name='manifestacao',
            index=models.Index(condition=models.Q(desativado_em=None), fields=['parte', 'defensoria', 'situacao'], name='processo_manifestacao_idx_002'),
        ),
        migrations.AddIndex(
            model_name='manifestacaodocumento',
            index=models.Index(fields=['manifestacao', 'origem'], name='processo_manifest_doc_idx_001'),
        ),
        migrations.AddIndex(
            model_name='manifestacaodocumento',
            index=models.Index(condition=models.Q(desativado_em=None), fields=['manifestacao'], name='processo_manifest_doc_idx_002'),
        ),
        migrations.AddIndex(
            model_name='parte',
            index=models.Index(fields=['processo', 'defensoria'], name='processo_parte_idx_001'),
        ),
        migrations.AddIndex(
            model_name='parte',
            index=models.Index(fields=['processo', 'ativo'], name='processo_parte_idx_002'),
        ),
    ]
