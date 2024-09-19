import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException

headerColumns = ['Pais', 'Entidad estatal', 'Referencia', 'Descripción', 'Fase actual', 'Fecha de publicación',	'Fecha de presentación de ofertas',	'Cuantía Estado', 'Detalle']

def writeOutputFile(cells):
  global outputFile
  for i in range(len(cells)):
    outputFile.write("" if cells[i] == None else cells[i] )
    outputFile.write('\n' if i==len(cells)-1 else ';')

def click_pagination_button():
    try:
        # Espera hasta que el botón de paginación esté presente y clickeable
        next_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'tblMainTable_trRowMiddle_tdCell1_tblForm_trGridRow_tdCell1_grdResultList_Paginator_goToPage_MoreItems'))  # Cambia el ID o XPATH
        )
        next_button.click()
        return True
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
        print("No se puede hacer clic en el botón de paginación o no existe")
        return False
    except StaleElementReferenceException:
        return click_pagination_button() 

def scrap(driver):
  page = 'https://community.secop.gov.co/Public/Tendering/ContractNoticeManagement/Index?currentLanguage=es-CO&Page=login&Country=CO&SkinName=CCE'
  
  driver.get(page)

  button_found = False

  while not button_found:
    try:
        # Intenta encontrar el botón una vez que el CAPTCHA esté resuelto
        button = driver.find_element(By.ID, 'btnSearchButton')  # Cambia el ID o XPATH del botón
        button_found = True
        print("El botón ha sido clickeado.")
    except (NoSuchElementException, ElementNotInteractableException):
        # Si no se encuentra el botón o aún no está interactivo, espera un momento antes de volver a intentar
        print("Esperando a que el botón esté disponible...")
        time.sleep(5)

  # Inyecta un script que detecte cuando el botón es clickeado
  driver.execute_script("""
      var button = arguments[0];
      button.addEventListener('click', function() {
          window.buttonClicked = true;
      });
  """, button)

  # Espera hasta que el botón sea clickeado por el usuario
  button_clicked = False
  while not button_clicked:
      # Verifica si el botón ha sido clickeado
      button_clicked = driver.execute_script("return window.buttonClicked === true;")
      if not button_clicked:
          print("Esperando a que el usuario haga clic en el botón...")
          time.sleep(5)

  print("El usuario hizo clic en el botón, continuando con el programa...")

  page_number = 1

  while True:
    if not click_pagination_button():
        break  # Si el botón no existe o no se puede hacer clic, salimos del bucle
    # Aquí puedes agregar código para procesar el contenido de la página actual antes de pasar a la siguiente página
    print(f"Procesando contenido de la página {page_number}...\n")
    page_number += 1
    time.sleep(2)  # Pausa para cargar la nueva página después de cada clic

  # Se obtienen y guardan los datos de la página
  print("Obteniendo y guardando los datos de la página")
  results = driver.find_elements(By.CSS_SELECTOR, '[id^="tblMainTable_trRowMiddle_tdCell1_tblForm_trGridRow_tdCell1_grdResultList_tr"]') 

  for result in results:
    data = []
    columns = result.find_elements(By.TAG_NAME, 'td')

    for idx, column in enumerate(columns):
      if idx == 0:
        country = column.find_element(By.TAG_NAME, 'span').get_attribute('title')
        data.append(country)
      else:
        data.append(column.text)

    writeOutputFile(data)

def init():
  global outputFile
  outputFile = open('resultados-secop.csv','w', encoding="utf-8")
  writeOutputFile(headerColumns)

if __name__ == '__main__':
  init()

  options = webdriver.ChromeOptions()

  options.add_experimental_option("excludeSwitches", ['enable-logging'])
  options.add_argument('log-level=3')
  # options.add_argument("--headless")
  options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
  # chromePrefs = {"profile.managed_default_content_settings.images": 2}
  # options.add_experimental_option("prefs", chromePrefs)

  driver = webdriver.Chrome(options=options)

  scrap(driver)

  driver.quit()
