


def procedimiento(driver):
    # Entrar al menu
    access_menu = driver.find_element(By.ID, 'menu_img')
    access_menu.click()

    # Ingresa nombre de operacion
    op_prompt = driver.find_element(By.ID, 'buscar_text')
    op_prompt.send_keys('Administrar Personas')

    _elemento = driver.find_element(By.ID, 'elemento_buscar_menu_37000023')
    _elemento.click()
