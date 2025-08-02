import pandas as pd
import numpy as np
from datetime import datetime
import re

def processar_liquidacoes_pagas(caminho_arquivo, silencioso=False):
    try:
        df = pd.read_csv(caminho_arquivo, sep=';', skiprows=3, encoding='latin-1')
        
        if not silencioso:
            print("🔍 Colunas encontradas no arquivo:")
            print(df.columns.tolist())
        
        df = df.dropna(subset=['Fornecedor', 'Valor'])
        
        colunas_desejadas = []
        mapeamento_colunas = {}
        
        for col in df.columns:
            if 'Data' in col and 'Liquid' in col:  # Busca por "Liquid" em vez de "Liquidação"
                colunas_desejadas.append(col)
                mapeamento_colunas[col] = 'data'
            elif 'Fornecedor' in col:
                colunas_desejadas.append(col)
                mapeamento_colunas[col] = 'fornecedor'
            elif 'Valor' in col:
                colunas_desejadas.append(col)
                mapeamento_colunas[col] = 'valor'
            elif 'Tipo' in col and 'Licit' in col:  # Busca por "Licit" em vez de "Licitação"
                colunas_desejadas.append(col)
                mapeamento_colunas[col] = 'tipo_licitacao'
            elif 'Empenho' in col:
                colunas_desejadas.append(col)
                mapeamento_colunas[col] = 'empenho'
        
        df_limpo = df[colunas_desejadas].copy()
        df_limpo = df_limpo.rename(columns=mapeamento_colunas)
        
        df_limpo['data'] = pd.to_datetime(df_limpo['data'], format='%d/%m/%Y', errors='coerce')
        
        df_limpo['fornecedor_limpo'] = df_limpo['fornecedor'].apply(limpar_nome_fornecedor)
        
        df_limpo['valor'] = df_limpo['valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        
        df_limpo = df_limpo.sort_values('data', ascending=False)
        
        total_gasto = df_limpo['valor'].sum()
        total_registros = len(df_limpo)
        
        if not silencioso:
            print(f"✅ Arquivo processado com sucesso!")
            print(f"📊 Total de registros: {total_registros}")
            print(f"💰 Total gasto: R$ {total_gasto:,.2f}")
            print(f"📅 Período: {df_limpo['data'].min().strftime('%d/%m/%Y')} a {df_limpo['data'].max().strftime('%d/%m/%Y')}")
        
        return df_limpo
        
    except Exception as e:
        if not silencioso:
            print(f"❌ Erro ao processar arquivo: {e}")
        return None

def limpar_nome_fornecedor(fornecedor):
    if pd.isna(fornecedor):
        return "N/A"
    
    fornecedor_limpo = re.sub(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', '', fornecedor)
    fornecedor_limpo = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '', fornecedor_limpo)
    fornecedor_limpo = re.sub(r'\*\*\*\*\d+\*\*\*\*', '', fornecedor_limpo)  # Remove CPF mascarado
    
    fornecedor_limpo = fornecedor_limpo.replace(' - ', '').strip()
    
    return fornecedor_limpo if fornecedor_limpo else "N/A"

def gerar_relatorio_resumo(df):
    if df is None or df.empty:
        print("❌ Nenhum dado para gerar relatório")
        return
    
    print("\n" + "="*50)
    print("📋 RELATÓRIO RESUMO - LIQUIDAÇÕES PAGAS")
    print("="*50)
    
    print("\n🏆 TOP 10 FORNECEDORES POR VALOR:")
    top_fornecedores = df.groupby('fornecedor_limpo')['valor'].sum().sort_values(ascending=False).head(10)
    for i, (fornecedor, valor) in enumerate(top_fornecedores.items(), 1):
        print(f"{i:2d}. {fornecedor[:40]:<40} R$ {valor:>12,.2f}")
    
    print("\n📊 GASTOS POR TIPO DE LICITAÇÃO:")
    gastos_tipo = df.groupby('tipo_licitacao')['valor'].sum().sort_values(ascending=False)
    for tipo, valor in gastos_tipo.items():
        print(f"   {tipo:<30} R$ {valor:>12,.2f}")
    
    print("\n📅 GASTOS POR MÊS:")
    df['mes_ano'] = df['data'].dt.to_period('M')
    gastos_mes = df.groupby('mes_ano')['valor'].sum().sort_values(ascending=False)
    for mes, valor in gastos_mes.head(6).items():
        print(f"   {str(mes):<15} R$ {valor:>12,.2f}")

def main():
    caminho_arquivo = r"c:\Users\joaop\Downloads\Liquidações pagas (1).csv"
    
    print("🔄 Processando arquivo de liquidações pagas...")
    df = processar_liquidacoes_pagas(caminho_arquivo)
    
    if df is not None:
        print("\n📋 PRIMEIRAS 5 LIQUIDAÇÕES:")
        print(df[['data', 'fornecedor_limpo', 'valor', 'tipo_licitacao']].head().to_string(index=False))
        
        gerar_relatorio_resumo(df)
        
        print("\n📋 TODOS OS DADOS PROCESSADOS:")
        print("=" * 100)
        print(df[['data', 'fornecedor_limpo', 'valor', 'tipo_licitacao', 'empenho']].to_string(index=False))
        
        print(f"\n📊 ESTATÍSTICAS FINAIS:")
        print(f"   Total de registros: {len(df)}")
        print(f"   Valor total: R$ {df['valor'].sum():,.2f}")
        print(f"   Valor médio: R$ {df['valor'].mean():,.2f}")
        print(f"   Maior valor: R$ {df['valor'].max():,.2f}")
        print(f"   Menor valor: R$ {df['valor'].min():,.2f}")
        
        return df
    else:
        print("❌ Falha no processamento dos dados")
        return None

if __name__ == "__main__":
    main()

