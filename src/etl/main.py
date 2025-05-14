from ext_diario import actualizar_datos_historicos, actualizar_fundamentales
from transform import transformar_empresas, transformar_precios_historicos, transformar_indicadores_fundamentales, calcular_indicadores_tecnicos,calcular_resumen_inversion, calcular_variaciones_precios 
from load import upsert_empresas, upsert_precios_historicos, upsert_fundamentales, upsert_indicadores_tecnicos,upsert_resumen_inversion, upsert_precios_variaciones
from tqdm import tqdm
import os

# Directorios
DIR_RAW = "../../data/raw_data/"
DIR_READY = "../../data/clean_data/"

def main():
    print("🚀 INICIANDO PROCESO COMPLETO DE ACTUALIZACIÓN 🚀")

    # ================
    # EXTRACCIÓN (actualización diaria)
    # ================
    print("\n🔍 Etapa 1: ACTUALIZACIÓN DE DATOS")
    actualizar_datos_historicos(
        historicos_path=DIR_RAW + "nyse_top500_data.csv",
        tickers_path=DIR_RAW + "top_500_marketcap.csv"
    )
    actualizar_fundamentales(
        tickers_path=DIR_RAW + "top_500_marketcap.csv",
        output_file=DIR_RAW + "nyse_top_500_fundamentals_indicators.csv"
    )

    # ================
    # TRANSFORMACIÓN
    # ================
    print("\n🔄 Etapa 2: TRANSFORMACIÓN DE DATOS")
    transformar_empresas(
        input_file=DIR_RAW + "top_500_marketcap.csv",
        output_file=DIR_READY + "empresas_ready.csv"
    )

    transformar_precios_historicos(
        input_file=DIR_RAW + "nyse_top500_data.csv",
        output_file=DIR_READY + "precios_historicos_ready.csv"
    )

    transformar_indicadores_fundamentales(
        input_file=DIR_RAW + "nyse_top_500_fundamentals_indicators.csv",
        output_file=DIR_READY + "indicadores_fundamentales_ready.csv"
    )

    calcular_indicadores_tecnicos(
        input_file=DIR_READY + "precios_historicos_ready.csv",
        output_file=DIR_READY + "indicadores_tecnicos_ready.csv"
    )    
    
    calcular_resumen_inversion(  
        precios_tecnicos_file=DIR_READY + "indicadores_tecnicos_ready.csv",
        fundamentales_file=DIR_READY + "indicadores_fundamentales_ready.csv",
        precios_historicos_file=DIR_READY + "precios_historicos_ready.csv",
        output_file=DIR_READY + "resumen_inversion_ready.csv"
    )
    calcular_variaciones_precios(
        input_file=DIR_READY + "precios_historicos_ready.csv",
        output_file=DIR_READY + "precios_variaciones_ready.csv"
    )

    # ================
    # CARGA
    # ================
    print("\n📥 Etapa 3: CARGA EN BASE DE DATOS")
    upsert_empresas(DIR_READY + "empresas_ready.csv")
    upsert_precios_historicos(DIR_READY + "precios_historicos_ready.csv")
    upsert_fundamentales(DIR_READY + "indicadores_fundamentales_ready.csv")
    upsert_indicadores_tecnicos(DIR_READY + "indicadores_tecnicos_ready.csv")
    upsert_resumen_inversion(DIR_READY + "resumen_inversion_ready.csv")
    upsert_precios_variaciones(DIR_READY + "precios_variaciones_ready.csv")

    print("\n🎯 ¡PROCESO COMPLETO SIN ERRORES! 🎯")

if __name__ == "__main__":
    main()


