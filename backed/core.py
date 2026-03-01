

import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class BaikeRPABot:
    def __init__(self, headless=False, debug=True):
        self.debug = debug
        self.setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 10)
    
    def setup_driver(self, headless):
        options = Options()
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        if headless:
            options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(options=options)
        self.log("浏览器初始化成功")
    
    def log(self, message):
        if self.debug:
            print(f"[RPA] {message}")
    
    def search_single(self, keyword):
        """完整的单次搜索流程"""
        self.log(f"开始处理词条: {keyword}")
        result = {
            'success': False,
            'keyword': keyword,
            'title': '',
            'summary': '',
            'infobox': {},
            'url': ''
        }
        
        try:
            # 1. 打开百度百科
            self.driver.get("https://baike.baidu.com/")
            time.sleep(2)
            
            # 2. 输入关键词
            search_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "query"))
            )
            search_input.clear()
            search_input.send_keys(keyword)
            time.sleep(1)
            
            # 3. 点击搜索按钮
            search_btn = self.driver.find_element(By.CLASS_NAME, "search-btn")
            search_btn.click()
            time.sleep(3)
            
            # 4. 提取标题
            try:
                title_elem = self.driver.find_element(By.CLASS_NAME, "lemmaWgt-lemmaTitle-title")
                result['title'] = title_elem.text
            except:
                result['title'] = self.driver.title.replace('_百度百科', '')
            
            # 5. 提取摘要
            try:
                summary_elem = self.driver.find_element(By.CLASS_NAME, "lemma-summary")
                result['summary'] = summary_elem.text[:200]  # 只取前200字
            except:
                result['summary'] = "未找到摘要"
            
            # 6. 记录URL
            result['url'] = self.driver.current_url
            result['success'] = True
            
            self.log(f"抓取成功: {result['title']}")
            
        except Exception as e:
            self.log(f"抓取失败: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def close(self):
        if self.driver:
            self.driver.quit()
            self.log("浏览器已关闭")