import re
import csv
import time
from tabulate import tabulate
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

fieldnames = ['busqueda']

headerColumns = ["BUSQUEDA",
  "TITULO 1", "SKU 1", "PRECIO 1.1", "VENDEDOR 1", "PRECIO 1.2",
  "TITULO 2", "SKU 2", "PRECIO 2.1", "VENDEDOR 2", "PRECIO 2.2",
  "TITULO 3", "SKU 3", "PRECIO 3.1", "VENDEDOR 3", "PRECIO 3.2",
  "TITULO 4", "SKU 4", "PRECIO 4.1", "VENDEDOR 4", "PRECIO 4.2",
]

printColumns = ["Titulo", "SKU", "Precio", "Vendedor", "Subprecio"]

def writeOutputFile(cells):
  global outputFile
  for i in range(len(cells)):
    outputFile.write("" if cells[i] == None else cells[i] )
    outputFile.write('\n' if i==len(cells)-1 else ';')

def checkSKU(link):
  textArray = link.split("-")
  for text in textArray:
    if (len(text) == 9 and text.isnumeric()):
        return(text)

def getNumber(text):
  return re.sub('\D', '', text)

def scrapSearch(search, driver):
  page = "https://www.exito.com/s?q=%s&sort=price_asc&page=0" % (search)

  
  driver.get(page)

  WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CSS_SELECTOR, '[class^="productCard_productCard__"]'))

  articles = driver.find_elements(By.CSS_SELECTOR, '[class^="productCard_productCard__"]')

  acc = 0
  outputArray = [search]
  printArray = []
  for article in articles:
    # Title 
    title = article.find_element(By.CSS_SELECTOR, '[class^="styles_name__"]').text

    # Price 
    price = article.find_element(By.CSS_SELECTOR, '[class^="ProductPrice_container__price__"]').text

    # Subprice
    try:
      article.find_element(By.CLASS_NAME, "exito-product-summary-3-x-priceMKP")
      subprice = article.find_element(By.CLASS_NAME, "exito-product-summary-3-x-priceMKP").get_attribute("innerText")
    except NoSuchElementException:
      subprice = ''

    # Seller
    seller = article.find_element(By.CSS_SELECTOR, 'div[data-fs-product-name-container="true"]').get_attribute("innerText").replace("Vendido por: ", "")

    # SKU 
    articleLink = article.find_element(By.CSS_SELECTOR, '[class^="productCard_productLinkInfo__"]').get_attribute("href")
    sku = checkSKU(articleLink)

    data = [title, sku, getNumber(price), seller, getNumber(subprice)]
    printArray.append(data)

  sortedPrintArray = sorted(printArray, key=lambda x: int(x[2]))
  
  resultPrintArray = sortedPrintArray[:4]

  for item in resultPrintArray:
    for value in item:
      outputArray.append(value)

  print("\n\n \t\t\t ##### {} ##### \n\n".format(search))
  print(tabulate(resultPrintArray, headers=printColumns, tablefmt="github"))
  writeOutputFile(outputArray)

def init():
  global outputFile
  outputFile=open('resultadosExito.csv','w') # open outputfile
  writeOutputFile(headerColumns)
  
if __name__ == '__main__':
  start_time = time.time() # Record start time
  init()

  options = webdriver.ChromeOptions()
  options.add_experimental_option("excludeSwitches", ['enable-logging'])
  options.add_argument('log-level=3')
  options.add_argument("--headless")
  options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
  chrome_prefs = {"profile.managed_default_content_settings.images": 2}
  options.add_experimental_option("prefs", chrome_prefs)

  driver = webdriver.Chrome(options=options)

  with open("busquedasExito.csv") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';', fieldnames=fieldnames) 
    for row in reader: # cada linea en el archivo
      # Si hay columnas vacias se eliminan
      if row.get(None): row.pop(None)
      else:
        for attempt in range(3): 
          try: 
            # Scrap Lines
            scrapSearch(row['busqueda'], driver)
          except KeyboardInterrupt:
            print("\n\n\nProceso Interrumpido por el usuario.")
            exit()
          except: 
            print("\nHubo un error en el {} intento de busqueda de: {}".format(attempt+1, row['busqueda']))
            continue
          else: 
            break
        else:
          writeOutputFile(["Error en la busqueda de {}".format(row['busqueda'])])
  
  driver.quit()
  end_time = time.time() # Record end time
  print("Total time taken: {:.2f} seconds".format(end_time - start_time)) # Calculate and print total time taken