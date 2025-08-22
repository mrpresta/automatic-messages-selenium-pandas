import pandas as pd
import datetime
from urllib.parse import quote
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#CONFIGURA O CHROME
service = Service()
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # abre tela cheia
driver = webdriver.Chrome(service=service, options=options)

#ABRE WHATSAPP WEB
driver.get("https://web.whatsapp.com/")
print("Escaneie o QR Code do WhatsApp...")
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.ID, "pane-side"))  # espera a lista de chats aparecer
)
print("Login realizado com sucesso!")

#LÊ A PLANILHA
df = pd.read_excel("clientes.xlsx", sheet_name="Planilha1")

#DATA DE HOJE
hoje = datetime.datetime.today().date()

#TRANSFORMA EM UM OBJETO DATATIME
df["vencimento"] = pd.to_datetime(df["vencimento"]).dt.date

#FILTRA CLIENTES QUE VENCEM HOJE
df_hoje = df[df["vencimento"] == hoje]

for _, row in df_hoje.iterrows():
    nome = row["Nome"]
    telefone = row["telefone"]
    vencimento = row["vencimento"]
    valor_fatura = row["valor"]


    if isinstance(vencimento, datetime.datetime):
        data_vencimento = vencimento.date()
    elif isinstance(vencimento, datetime.date):
        data_vencimento = vencimento
    else:
        continue
    sleep(5)

    if data_vencimento == hoje:
        #CRIA A MENSAGEM
        mensagem = f"Olá {nome}, o vencimento da sua fatura é hoje {data_vencimento} e ela ficou no valor de R${valor_fatura}"

        try:
            #MONTA A URL
            link = f"https://web.whatsapp.com/send?phone={telefone}&text={quote(mensagem)}"
            driver.get(link)

            #ESPERA O CAMPO DE MENSAGEM APARECER
            campo = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )

            #GARANTE QUE O CAMPO ESTA FOCADO
            campo.click()
            sleep(1)

            # envia a tecla ENTER
            campo.send_keys(Keys.ENTER)

            #RETORNA UM SUCESSO
            print(f"Mensagem enviada para {nome} ({telefone})")

        except Exception as e:
            #RETORNA UM ERRO E IMPLEMENTA O ARQUIVO DE ERROS
            print(f"Erro ao enviar mensagem para {nome}: {e}")
            with open("erros.csv", "a", encoding="utf-8") as arquivo:
                arquivo.write(f"{nome},{telefone}\n")