import time
import ctypes
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
from dotenv import load_dotenv
load_dotenv()

class BaikeRPABot:
    def __init__(self, headless=False, debug=True):
        self.debug = debug
        self.setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 10)

    def setup_driver(self, headless):
        self.headless = headless  # 保存供置顶逻辑判断
        options = Options()
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
        if headless:
            options.add_argument('--headless')

        self.driver = webdriver.Chrome(options=options)
        time.sleep(1.5)  # 等待窗口完全初始化再置顶
        self.driver.maximize_window()
        # 强制把新开的Chrome窗口拉到最前面（通过Chrome进程PID找窗口句柄）
        if not self.headless:
            try:
                # Windows 不允许后台进程直接抢前台，用 keybd_event 模拟按键绕过限制
                ctypes.windll.user32.keybd_event(0, 0, 0, 0)
                pid = self.driver.service.process.pid
                EnumWindows        = ctypes.windll.user32.EnumWindows
                EnumWindowsProc    = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
                GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
                IsWindowVisible    = ctypes.windll.user32.IsWindowVisible
                found = []

                def callback(hwnd, lParam):
                    if not IsWindowVisible(hwnd):
                        return True
                    win_pid = ctypes.c_ulong()
                    GetWindowThreadProcessId(hwnd, ctypes.byref(win_pid))
                    if win_pid.value == pid:
                        found.append(hwnd)
                    return True

                EnumWindows(EnumWindowsProc(callback), 0)
                if found:
                    hwnd = found[0]
                    ctypes.windll.user32.ShowWindow(hwnd, 9)       # SW_RESTORE
                    ctypes.windll.user32.BringWindowToTop(hwnd)
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
            except Exception as e:
                self.log(f"置顶窗口失败（不影响使用）: {e}")
        self.log("浏览器初始化成功")

    def log(self, message):
        if self.debug:
            print(f"[RPA] {message}")

    # ── 公开方法 ──────────────────────────────────────────

    def search_single(self, keyword):
        """严格匹配：搜索后提取词条，搜不到则尝试备用站点"""
        self.log(f"开始处理词条: {keyword}")
        self._goto_search(keyword)

        current_url  = self.driver.current_url
        page_source  = self.driver.page_source

        # 多义词选择页（URL 里有 /item/ 但页面提示"本词条是一个多义词"）
        if '/item/' in current_url and '本词条是一个多义词' in page_source:
            self.log("检测到多义词选择页，自动点击第一个义项...")
            first_item = self._find_element_safe(
                #Selenium 的 find_element（单数）的规则就是：在 DOM 
                #里从上到下扫描，遇到第一个匹配的就返回，后面的全忽略。
                By.CSS_SELECTOR, "a[class*='contentItemChild_']"
            )
            if first_item:
                #直接跳转
                href = first_item.get_attribute('href')
                if href:
                    self.driver.get(href)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "[class*='lemmaTitle_']")
                        )
                    )
                    return self._extract_current_page(keyword)

        # 正常词条页
        if '/item/' in current_url and '本词条是一个多义词' not in page_source:
            return self._extract_current_page(keyword)

        # 停在搜索页 / 未找到，依次尝试备用站点
        self.log(f"百度百科未找到词条：{keyword}，尝试备用站点...")
        fallback = self._search_fallback(keyword)
        if fallback:
            return fallback

        # 所有备用站点都没找到
        return {
            'success': False,
            'keyword': keyword,
            'title':   '',
            'summary': '',
            'infobox': {},
            'url':     current_url,
            'error':   f'未检索到词条「{keyword}」，百度百科、墨鱼词典及 AI 均无法解释'
        }

    def search_related(self, keyword):
        """
        相关词条模式：
        - 如果页面有同名词条列表 -> 展开并逐一抓取
        - 如果没有（只有一个词条）-> 直接返回当前页结果
        返回值始终是 list，方便前端统一处理
        """
        self.log(f"[相关模式] 开始处理: {keyword}")
        self._goto_search(keyword)

        current_url = self.driver.current_url
        page_source = self.driver.page_source

        # 情况A：多义词选择页（直接列出义项，无需展开按钮）
        if '/item/' in current_url and '本词条是一个多义词' in page_source:
            self.log("检测到多义词选择页，直接抓取所有义项作为相关词条...")
            links = self._get_related_links(max_count=5)
            if links:
                results = []
                for i, link in enumerate(links):
                    self.log(f"[{i+1}/{len(links)}] 抓取义项: {link['title']}")
                    try:
                        self.driver.get(link['url'])
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "[class*='lemmaTitle_']")
                            )
                        )
                        result = self._extract_current_page(link['title'])
                        result['category'] = link.get('category', '')
                        results.append(result)
                    except Exception as e:
                        self.log(f"抓取失败: {link['title']} - {e}")
                        results.append({
                            'success': False, 'keyword': link['title'],
                            'category': link.get('category', ''),
                            'url': link['url'], 'error': str(e)
                        })
                return results
            # 义项为空则退回抓当前页
            return [self._extract_current_page(keyword)]

        # 情况B：百科搜不到词条（停在搜索页），降级走严格匹配逻辑（含备用站点）
        if '/item/' not in current_url:
            self.log("相关模式：百科未找到词条，降级为严格匹配...")
            result = self._search_fallback(keyword)
            if result:
                return [result]
            return [{
                'success': False, 'keyword': keyword,
                'title': '', 'summary': '', 'infobox': {}, 'url': current_url,
                'error': f'未检索到词条「{keyword}」，百度百科与墨鱼词典均无收录'
            }]

        # 情况C：正常词条页，检查是否存在"展开同名词条"按钮
        toggle_btn = self._find_element_safe(By.CSS_SELECTOR, "[class*='polysemantText_']")
        if not toggle_btn:
            self.log("未发现同名词条入口，直接返回当前词条")
            return [self._extract_current_page(keyword)]

        # 2. 点击展开
        self.log("发现同名词条，正在展开...")
        self.driver.execute_script("arguments[0].click();", toggle_btn)

        # 3. 等待列表出现
        try:
            WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[class*='newPolysemantList_']")
                )
            )
        except Exception:
            self.log("等待列表超时，返回当前词条")
            return [self._extract_current_page(keyword)]

        # 4. 取前5个词条链接
        links = self._get_related_links(max_count=5)
        if not links:
            self.log("列表为空，返回当前词条")
            return [self._extract_current_page(keyword)]

        self.log(f"共找到 {len(links)} 个相关词条（最多取5个）")

        # 5. 逐一进入词条页抓取
        results = []
        for i, link in enumerate(links):
            self.log(f"[{i+1}/{len(links)}] 抓取: {link['title']} -> {link['url']}")
            try:
                self.driver.get(link['url'])
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                )
                result = self._extract_current_page(link['title'])
                result['category'] = link.get('category', '')   # 带上分类（植物/企业/书刊…）
                results.append(result)
            except Exception as e:
                self.log(f"抓取失败: {link['title']} - {e}")
                results.append({
                    'success': False,
                    'keyword': link['title'],
                    'category': link.get('category', ''),
                    'url': link['url'],
                    'error': str(e)
                })

        return results

    # ── 私有方法 ──────────────────────────────────────────

    def _search_fallback(self, keyword):
        """
        百度百科搜不到时，依次尝试：
        1. 墨鱼词典 
        2. DeepSeek AI 解释
        找到后返回结果并注明来源，找不到返回 None
        """
        # 1. 墨鱼词典（专注网络用语）
        result = self._search_moyuoo(keyword)
        if result:
            return result

        # 2. DeepSeek AI 兜底解释
        result = self._search_deepseek(keyword)
        if result:
            return result

        return None

    def _search_moyuoo(self, keyword):
        """在墨鱼词典搜索网络用语，找到返回结果，找不到返回 None"""
        try:
            search_url = f'https://www.moyuoo.com/?s={keyword}'
            self.log(f"尝试墨鱼词典：{search_url}")
            self.driver.get(search_url)

            WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
            )

            # 找搜索结果列表里的第一条文章链接
            # WordPress 标准结构：article h2 a 或 .post-title a
            first_link = None
            for sel in [
                        'li.post-list-item .post-info a',  # 真实结构，最精准
                        'li.post-list-item a.thumb-link',  # 备用
                        'h2 a',                            # 最后兜底
                    ]:
                try:
                    first_link = self.driver.find_element(By.CSS_SELECTOR, sel)
                    if first_link:
                        self.log(f"命中选择器：{sel}")  # 加这一行
                        break
                except Exception:
                    continue

            if not first_link:
                self.log("墨鱼词典未找到相关词条")
                return None

            article_title = first_link.text.strip()
            article_url   = first_link.get_attribute('href')
            self.log(f"墨鱼词典找到：{article_title}，进入词条页...")

            # 进入词条详情页
            self.driver.get(article_url)
            WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
            )

            # 抓正文摘要，WordPress 标准结构通常是 .entry-content
            summary = ''
            try:
                elem = self.driver.find_element(By.CSS_SELECTOR, '.entry-content')
                summary = elem.text[:500].strip()
            except Exception:
                summary = '暂无摘要'

            self.log(f"墨鱼词典抓取成功：{article_title}")
            return {
                'success':       True,
                'keyword':       keyword,
                'title':         article_title,
                'summary':       summary,
                'infobox':       {},
                'url':           self.driver.current_url,
                'source':        '墨鱼词典',
                'from_fallback': True
            }

        except Exception as e:
            self.log(f"墨鱼词典请求失败: {e}")
            return None


            title = ''
            summary = ''
            try:
                title = self.driver.find_element(By.CSS_SELECTOR, 'h1').text.strip()
            except Exception:
                title = self.driver.title.strip()
            try:
                summary = self.driver.find_element(
                    By.CSS_SELECTOR, '[class*="abstract"], .summary, p'
                ).text[:500].strip()
            except Exception:
                summary = '暂无摘要'

            if title and len(title) > 0:
                self.log(f"搜狗百科找到：{title}")
                return {
                    'success': True, 'keyword': keyword,
                    'title': title, 'summary': summary,
                    'infobox': {}, 'url': self.driver.current_url,
                    'source': '搜狗百科', 'from_fallback': True
                }
            return None
        except Exception as e:
            self.log(f"搜狗百科请求失败: {e}")
            return None

    def _search_deepseek(self, keyword):
        """调用 DeepSeek API 对词条进行 AI 解释，作为最终兜底"""
        try:
            self.log(f"尝试 DeepSeek AI 解释：{keyword}")
            resp = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {os.getenv("DEEPSEEK_API_KEY")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'max_tokens': 300,
                    'messages': [
                        {
                            'role': 'system',
                            'content': '你是一个网络用语百科助手。用户会给你一个词条，请简洁地解释它的含义和来源（100字以内）。如果你完全不了解这个词条，直接回复"不了解"三个字。'
                        },
                        {
                            'role': 'user',
                            'content': f'请解释"{keyword}"这个词条'
                        }
                    ]
                },
                timeout=15
            )

            if resp.status_code != 200:
                self.log(f"DeepSeek 请求失败，状态码：{resp.status_code}")
                return None

            answer = resp.json()['choices'][0]['message']['content'].strip()

            if '不了解' in answer or len(answer) < 5:
                self.log("DeepSeek 也不了解该词条")
                return None

            self.log(f"DeepSeek 解释成功：{answer[:30]}...")
            return {
                'success':       True,
                'keyword':       keyword,
                'title':         keyword,
                'summary':       answer,
                'infobox':       {},
                'url':           '',
                'source':        'DeepSeek AI',
                'from_fallback': True
            }

        except Exception as e:
            self.log(f"DeepSeek 请求出错: {e}")
            return None

    def _is_not_found_page(self):
        """判断当前页面是否是未找到/错误页"""
        try:
            body_text = self.driver.find_element(By.TAG_NAME, 'body').text
            not_found_keywords = ['404', '页面不存在', '未找到', 'not found', '没有找到']
            title = self.driver.title.lower()
            return any(kw.lower() in body_text.lower() or kw.lower() in title
                       for kw in not_found_keywords)
        except Exception:
            return False

    def _goto_search(self, keyword):
        """打开百科首页并搜索关键词"""
        self.driver.get("https://baike.baidu.com/")

        search_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input.searchInput"))
        )
        search_input.click()
        search_input.clear()
        search_input.send_keys(keyword)

        search_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "lemmaBtn"))
        )
        search_btn.click()

        # 等待页面跳转（词条页 / 搜索页 / 多义词选择页）
        WebDriverWait(self.driver, 10).until(
            lambda d: '/item/' in d.current_url
                      or 'search' in d.current_url
                      or 'disambig' in d.current_url
                      or '本词条是一个多义词' in d.page_source
        )

    def _extract_current_page(self, keyword):
        """提取当前词条页的标题、摘要、URL"""
        result = {
            'success': False,
            'keyword': keyword,
            'title': '',
            'summary': '',
            'infobox': {},
            'url': self.driver.current_url
        }

        # 标题
        try:
            title_elem = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[class*='lemmaTitle_']")
                )
            )
            result['title'] = title_elem.text.strip()
        except Exception:
            result['title'] = self.driver.title.replace('_百度百科', '').strip()

        # 摘要
        try:
            summary_elem = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[class*='lemmaSummary']")
                )
            )
            result['summary'] = summary_elem.text[:500].strip()
        except Exception:
            result['summary'] = "未找到摘要"

        result['success'] = True
        self.log(f"提取完成: {result['title']}")
        return result

    def _get_related_links(self, max_count=5):
        """
        从展开的同名词条列表里提取所有词条链接。
        用 class*= 模糊匹配，避免哈希后缀变化导致失效。
        返回格式: [{'title': '...', 'url': '...', 'category': '...'}, ...]
        """
        links = []

        try:
            # 所有分类块（植物 / 话题人物 / 企业 …）
            category_blocks = self.driver.find_elements(
                By.CSS_SELECTOR, "[class*='contentItem_']"
            )

            for block in category_blocks:
                # 分类名称
                try:
                    category = block.find_element(
                        By.CSS_SELECTOR, "[class*='contentItemTitle_']"
                    ).text.strip()
                except Exception:
                    category = ''

                # 该分类下的所有词条链接
                anchors = block.find_elements(
                    By.CSS_SELECTOR, "a[href*='/item/']"
                )

                for a in anchors:
                    try:
                        href = a.get_attribute('href')
                        # 词条文字优先取 span，fallback 取 a.text
                        try:
                            title = a.find_element(
                                By.CSS_SELECTOR, "[class*='contentItemChildText_']"
                            ).text.strip()
                        except Exception:
                            title = a.text.strip()

                        if href and title:
                            links.append({
                                'title': title,
                                'url': href,
                                'category': category
                            })
                    except Exception:
                        continue

        except Exception as e:
            self.log(f"提取链接列表失败: {e}")

        return links[:max_count]

    def _find_element_safe(self, by, selector, timeout=5):
        """安全查找元素，找不到返回 None 而不抛异常"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
        except Exception:
            return None

    def close(self):
        if self.driver:
            self.driver.quit()
            self.log("浏览器已关闭")