import os
import zipfile
import urllib.request
import pandas as pd

def baixar_e_gerar_tabela_cidades():
    print("⏳ 1/4 - Baixando bases de dados geográficas mundiais...")
    
    # URL da base oficial do GeoNames (cidades com mais de 15.000 habitantes)
    # Nota: Para incluir cidades ainda menores (>500 hab), troque para 'cities500.zip'
    url_cities = "http://download.geonames.org/export/dump/cities15000.zip"
    url_countries = "http://download.geonames.org/export/dump/countryInfo.txt"

    # Download dos arquivos
    urllib.request.urlretrieve(url_cities, "cities15000.zip")
    urllib.request.urlretrieve(url_countries, "countryInfo.txt")

    # Descompacta o arquivo de cidades
    with zipfile.ZipFile("cities15000.zip", "r") as zip_ref:
        zip_ref.extractall(".")

    print("⚙️ 2/4 - Processando países e continentes...")
    
    # Mapeamento de continentes
    continentes_map = {
        'AF': 'Africa', 'AN': 'Antarctica', 'AS': 'Asia',
        'EU': 'Europe', 'NA': 'North America', 'OC': 'Oceania', 'SA': 'South America'
    }

    # Carrega informações de Países e Continentes
    paises_df = pd.read_csv(
        "countryInfo.txt", 
        sep="\t", 
        comment="#", 
        header=None,
        usecols=[0, 4, 8], 
        names=["ISO", "Country", "ContinentCode"]
    )
    paises_df["Continent"] = paises_df["ContinentCode"].map(continentes_map)

    print("⚙️ 3/4 - Formatando cidades no padrão solicitado...")
    
    # Carrega as Cidades (Coluna 1 = Nome em Inglês/ASCII, Coluna 8 = Código ISO do País, Coluna 10 = Código do Estado/Região)
    cidades_df = pd.read_csv(
        "cities15000.txt", 
        sep="\t", 
        header=None, 
        low_memory=False,
        usecols=[1, 8, 10], 
        names=["City", "ISO", "State_Code"]
    )

    # Cruza os dados das cidades com os dados dos países
    tabela_final = pd.merge(cidades_df, paises_df, on="ISO", how="left")

    # Criando a coluna no formato solicitado: "New York, United States"
    tabela_final["Cidade_Pais"] = tabela_final["City"] + ", " + tabela_final["Country"]

    # Reordenando as colunas (incluindo Estado e Continente como complementares)
    tabela_final = tabela_final[["Cidade_Pais", "City", "Country", "State_Code", "Continent"]].dropna(subset=["Country"])

    print("💾 4/4 - Salvando arquivo de saída...")
    
    arquivo_saida = "tabela_cidades_mundo.csv"
    tabela_final.to_csv(arquivo_saida, index=False, encoding="utf-8")
    
    # Limpeza de arquivos temporários baixados
    for temp_file in ["cities15000.zip", "cities15000.txt", "countryInfo.txt"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    print(f"\n✅ Concluído com sucesso! {len(tabela_final):,} cidades geradas no arquivo '{arquivo_saida}'.")

if __name__ == "__main__":
    baixar_e_gerar_tabela_cidades()