from typing import Dict, List

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def load_page(url: str) -> webdriver:
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get(url)
    return driver


def find_next_page(driver: webdriver) -> bool:
    pagination = driver.find_element(
        By.XPATH,
        """//*[@id="content"]/div/div[3]/div/div/div/div"""
    )
    current_page = pagination.find_element(By.CLASS_NAME, "current")
    pages = pagination.find_elements(By.TAG_NAME, "span")
    current_page_idx = pages.index(current_page)
    if current_page_idx < len(pages)-1:
        next_page = pages[current_page_idx+1]
        next_page.click()
        return True
    else:
        return False


def get_col_names(driver: webdriver) -> List[str]:
    table_cols = driver.find_elements(
        By.XPATH,
        """//*[@id="content"]/div/div[3]/div/div/div/table/thead/tr/th"""
    )
    col_names = [col.text for col in table_cols]
    return col_names


def get_table_content(driver: webdriver, col_names: List[str]) -> List[Dict[str, str]]:
    content = get_row_info(driver, col_names)
    while find_next_page(driver):
        next_content = get_row_info(driver, col_names)
        content.extend(next_content)
    return content


def get_row_info(driver: webdriver, col_names: List[str]) -> List[Dict[str, str]]:
    info = list()
    row = driver.find_elements(
        By.XPATH,
        """//*[@id="content"]/div/div[3]/div/div/div/table/tbody/tr"""
    )
    for r in row:
        cells = [cell.text for cell in r.find_elements(By.TAG_NAME, "td")]
        info.append(dict(zip(col_names, cells)))
    return info


def select_period(driver, from_year: str, to_year: str) -> None:
    element_from = driver.find_element(
        By.XPATH, """//*[@id="busqueda_historicos_fechaDesde_year"]"""
    )
    select_from = Select(element_from)
    select_from.select_by_value(from_year)
    
    element_to = driver.find_element(
        By.XPATH, """//*[@id="busqueda_historicos_fechaHasta_year"]"""
    )
    select_to = Select(element_to)
    select_to.select_by_value(to_year)

    button = driver.find_element(
        By.XPATH,
        """//*[@id="1"]/form/div[3]/input"""
    )
    button.click()


def download(url: str, output: str) -> str:
    page = load_page(url)
    select_period(page, "2020", "2021")
    columns = get_col_names(page)
    data = get_table_content(page, columns)
    page.close()
    (
        pd.DataFrame(data)
        .applymap(lambda x: x.replace("\n", " "))
        .to_csv(output, index=False)
    )
    return output
