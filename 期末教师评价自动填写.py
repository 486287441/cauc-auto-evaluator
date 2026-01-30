import subprocess
import sys
import time
import random

# --- 这一段是新增的，专门为了让你朋友运行更简单 ---
def install_dependencies():
    # 检测是否安装了 selenium 和 webdriver-manager，如果没有则自动安装
    required_packages = ["selenium", "webdriver-manager"]
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            print(f">>> 正在自动安装缺失的库: {package}，请稍候...")
            # 使用国内清华大学镜像源，安装速度极快
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])

# 自动执行安装检查
install_dependencies()

# --- 以下是原有的所有逻辑，未做任何核心修改 ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 仅修改此处的网址和账号 ---
URL = "https://www.cauc.edu.cn/jxpj/wjdc_mobile/login_logout.html"
USERNAME = ""
PASSWORD = "" 

def start_evaluation():
    print(">>> 启动自动化评价脚本...")
    
    mobile_emulation = {"deviceName": "iPhone 12 Pro"}
    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    chrome_options.add_argument('--ignore-certificate-errors')

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        wait = WebDriverWait(driver, 15)

        # 1. 登录
        driver.get(URL)
        print(">>> 正在登录...")
        user_input = wait.until(EC.presence_of_element_located((By.ID, "yhm")))
        user_input.clear()
        user_input.send_keys(USERNAME)
        pass_input = driver.find_element(By.ID, "mm")
        pass_input.clear()
        pass_input.send_keys(PASSWORD)
        driver.find_element(By.ID, "btn_dl").click()
        
        # 2. 菜单跳转
        try:
            eval_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'XSJKPJ')]")))
            eval_menu.click()
        except:
            driver.get("https://www.cauc.edu.cn/jxpj/inspection_mobile/result_endingClassList.html?type=XSJKPJ")

        # 3. 循环评价
        while True:
            time.sleep(3) 
            tasks = driver.find_elements(By.XPATH, "//button[contains(text(), '我要评价')]")
            
            if not tasks:
                # 如果没找到按钮，尝试点一下“未评价”标签刷新
                try:
                    unrated_tab = driver.find_element(By.XPATH, "//a[@status='0']")
                    driver.execute_script("arguments[0].click();", unrated_tab)
                    time.sleep(2)
                    tasks = driver.find_elements(By.XPATH, "//button[contains(text(), '我要评价')]")
                    if not tasks:
                        print(">>> 所有评价任务已完成。")
                        break
                except:
                    break
            
            print(">>> 正在填写问卷...")
            driver.execute_script("arguments[0].click();", tasks[0])

            # 4. 随机选 A-E
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jqradio")))
            all_radios = driver.find_elements(By.CLASS_NAME, "jqradio")
            for i in range(0, len(all_radios), 5):
                try:
                    target = i + random.randint(0, 4)
                    if target < len(all_radios):
                        driver.execute_script("arguments[0].click();", all_radios[target])
                except:
                    continue
            
            # 5. 提交
            print(">>> 提交问卷...")
            try:
                submit_btn = wait.until(EC.presence_of_element_located((By.ID, "but_tj")))
                driver.execute_script("arguments[0].click();", submit_btn)
                time.sleep(2)
                try:
                    wait.until(EC.alert_is_present())
                    driver.switch_to.alert.accept()
                except:
                    confirms = driver.find_elements(By.XPATH, "//*[contains(text(),'确定') or contains(text(),'确认')]")
                    if confirms:
                        driver.execute_script("arguments[0].click();", confirms[0])
            except Exception as e:
                print(f"提交失败: {e}")

            # 6. 【核心修改处】等待4秒并点击“未评价”
            print(">>> 等待4秒后点击‘未评价’并继续下一项...")
            time.sleep(4)
            try:
                # 寻找 status="0" 的未评价按钮并点击
                unrated_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@status='0']")))
                driver.execute_script("arguments[0].click();", unrated_tab)
            except Exception as e:
                # 如果找不到按钮，直接重定向回列表页防止卡死
                driver.get("https://www.cauc.edu.cn/jxpj/inspection_mobile/result_endingClassList.html?type=XSJKPJ")

    except Exception as e:
        print(f"!!! 运行异常: {e}")
    finally:
        print(">>> 脚本已停止。")

if __name__ == "__main__":
    start_evaluation()