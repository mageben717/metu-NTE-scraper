import time
from os.path import exists
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import winsound

from webdriver_manager.chrome import ChromeDriverManager

#########################################################
# change myDEPT to your department
# delete departments that you dont want to take courses from the class_codes list
myDEPT='CENG'
class_codes = [ "120", "121", "125", "230", "232", "233", "236", "240", "241", "310", "311", "312", "314", "410", "420", "450", "453","602", "603", "604", "605", "606", "607", "608","610", "611", "612", "639","642", "643", "644", "651", "682", "831", "863"]
#########################################################

start = time.time()

existing_codes=set()
file_existing = None
for encoding in ['utf-8','utf-8-iso','iso-8859-1','cp1252']:
    try:
        file_existing = open("out2.txt", encoding=encoding)
        temp = file_existing.readlines()
        file_existing.close()
        file_existing = open("out2.txt", encoding=encoding)
        break
    except:
        pass
if not file_existing:
    print("out2.txt file encoding error")
    exit()
while True:
    line = file_existing.readline().split()
    if not line:
        break
    if(line[0]=='ALL' or line[0]==myDEPT):
        existing_codes.add(line[1])

def mld_switch(str):
    dict={
        "ARAB": "602",
        "FREN": "603",
        "GERM": "604",
        "JA": "605",
        "ITAL": "606",
        "RUS": "607",
        "SPAN": "608",
        "HEB": "609",
        "GRE": "610",
        "GREEK": "610",
        "CHN": "611",
        "PERS": "612",
        "ENG": "639"
    }
    courseName=""
    for c in str:
        if c==' ' or c.isdigit():
            break
        courseName+=c
    return dict[courseName]

def write_num(str):
    courseCode = ""
    for c in str:
        if c.isdigit():
            courseCode += c
    return courseCode

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
action = ActionChains(driver)





NTE_codes=set()
if exists("./NTE_codes.txt"):
    file = open("NTE_codes.txt", "r")
    for course_code in file.readline().split():
        if course_code not in existing_codes:
            NTE_codes.add(course_code)
else:
    file = open("NTE_codes.txt", "w")
    NTE_URL = "https://muhfd.metu.edu.tr/en/nte-courses"
    driver.get(NTE_URL)
    rows = driver.find_elements(By.XPATH, '//*[@id="content"]/article/div[2]/table/tbody/tr')
    for i in rows:
        cols = i.find_elements(By.TAG_NAME, 'td')
        # getting link and course_code
        class_code = write_num(cols[0].text)
        if (int(class_code) >= 603 and int(class_code) <= 639):
            continue
        i.click()

        if (int(class_code) != 602):
            course_table = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content"]/article/div[2]/table/tbody/tr')))[1:]
            for course in course_table:
                course_code = write_num(course.find_elements(By.TAG_NAME, 'td')[0].text)
                full_code = class_code + ("0" if len(course_code) == 3 else "") + course_code
                if course_code not in existing_codes:
                    NTE_codes.add(full_code)
                file.write(full_code + " ")
        else:  # mld specific case their xpath and table structure are different
            course_table = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content"]/div[2]/table/tbody/tr')))[1:]
            for course in course_table:
                course_name = course.find_elements(By.TAG_NAME, 'td')[0].text
                course_code = write_num(course_name)
                class_code = mld_switch(course_name)
                full_code = class_code + ("0" if len(course_code) == 3 else "") + course_code
                if course_code not in existing_codes:
                    NTE_codes.add(full_code)
                file.write(full_code+" ")
        driver.back()

url = "https://oibs2.metu.edu.tr/View_Program_Course_Details_64/"

#################################
#<option value="572">Aerospace Engineering/Havacılık ve Uzay Mühendisliği </option>
while True:
    driver.get('https://www.google.com')
    driver.get(url)
    for class_code in class_codes:
        el2=driver.find_element(By.CSS_SELECTOR,'option[value="'+class_code+'"]')
        print(el2.text)
        el2.click()
        driver.find_element(By.XPATH,'//*[@id="single_content"]/form/table[3]/tbody/tr/td/input').click()

        # -----------------------fail check---------------
        fm = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#formmessage > font > b")))
        # fm = driver.find_elements(By., "There is no")
        if fm.text == "Information about the department could not be found.":
            continue
        # -----------------------------------------------
        table=WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="single_content"]/form/table[4]/tbody/tr')))[1:]
        for i in range(0,len(table)):
            row=table[i]
            try:
                column=row.find_element(By.XPATH,"./td[2]")
            except:
                table = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@id="single_content"]/form/table[4]/tbody/tr')))[1:]
                row = table[i]
                column = row.find_element(By.XPATH, "./td[2]")
            if column.text in NTE_codes:
                rowTEXT=row.text
                #clicking course
                row.find_element(By.XPATH,"./td[1]/font/input").click()
                driver.find_element(By.XPATH,'//*[@id="single_content"]/form/table[2]/tbody/tr/td[1]/input').click()
                #clicking to sections
                sections=WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'input[name=submit_section]')))
                for j in range(0,len(sections)):
                    section=sections[j]
                    try:
                        section.click()
                    except:
                        sections = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'input[name=submit_section]')))
                        section = sections[j]
                        section.click()
                    fm = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.ID,"formmessage")))
                    #fm = driver.find_elements(By., "There is no")

                    if fm.text=="There is no section criteria to take the selected courses for this section.":
                        print("ALL","\t",rowTEXT,j+1)
                        winsound.Beep(444, 1000)
                        winsound.Beep(333, 1000)
                        winsound.Beep(444, 1000)
                        winsound.Beep(388, 1000)
                        winsound.Beep(444, 1000)

                    table2=driver.find_elements(By.XPATH,'//*[@id="single_content"]/form/table[3]/tbody/tr')[1:]
                    for row2 in table2:
                        dept=row2.find_element(By.XPATH,'./td[1]').text
                        if dept=='ALL' or dept==myDEPT:
                            print(dept,"\t",rowTEXT,j+1)
                            winsound.Beep(444, 1000)
                            winsound.Beep(333, 1000)
                            winsound.Beep(444, 1000)
                            winsound.Beep(388, 1000)
                            winsound.Beep(444, 1000)
                            break
                    driver.back()
                driver.back()
        driver.back()
    time.sleep(60)

end = time.time()
print("done ",end-start," seconds")
