import requests
import re
import time
import os
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

def get_image_urls_from_html(keyword, page=0):
    """
    通过百度图片搜索的HTML页面获取图片URL
    :param keyword: 搜索关键词
    :param page: 页码 (0为第一页)
    :return: 图片URL列表
    """
    # 构造搜索URL
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word={encoded_keyword}&pn={page * 20}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://image.baidu.com/"
    }
    
    try:
        print(f"正在请求搜索页: {url}")
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        html_content = resp.text
        
        # 使用正则表达式匹配图片URL
        # 百度图片页中的图片链接通常以 "https://img" 或 "http://img" 开头，并包含 "src" 属性
        # 这个正则表达式匹配常见的图片格式
        pattern = r'"objURL":"(https?://[^"]+?\.(?:jpg|jpeg|png|gif|bmp|webp))"'
        img_urls = re.findall(pattern, html_content, re.IGNORECASE)
        
        print(f"[DEBUG] 从HTML中提取到 {len(img_urls)} 个原始图片链接")
        
        # 清理和去重
        cleaned_urls = []
        seen = set()
        for url in img_urls:
            # URL解码
            decoded_url = urllib.parse.unquote(url)
            if decoded_url not in seen:
                seen.add(decoded_url)
                cleaned_urls.append(decoded_url)
        
        print(f"[DEBUG] 清理去重后剩余 {len(cleaned_urls)} 个有效链接")
        return cleaned_urls[:10]  # 返回前10个
        
    except Exception as e:
        print(f"获取图片URL时发生错误: {e}")
        return []

def download_image(url, index, folder="images"):
    """
    下载单张图片
    :param url: 图片URL
    :param index: 图片序号
    :param folder: 保存文件夹
    :return: 下载是否成功
    """
    if not url:
        return False
    try:
        os.makedirs(folder, exist_ok=True)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://image.baidu.com/"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            # 尝试从URL中获取扩展名
            ext = url.split('.')[-1].split('?')[0].split('&')[0].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                ext = 'jpg'
            import time
            import random  # 导入 random 模块

            timestamp = time.strftime("%Y%m%d%H%M%S")
            unique_suffix = f"{timestamp}{random.randint(100, 999)}"
            filename = f"{folder}/img_{index}_{unique_suffix}.{ext}"
            with open(filename, "wb") as f:
                f.write(resp.content)
            print(f"✅ 成功下载: {filename}")
            return True
        else:
            print(f"❌ 下载失败 (状态码 {resp.status_code}): {url}")
    except Exception as e:
        print(f"❌ 下载时发生异常: {e}")
    return False

def main():
    keyword = input("输入关键词: ").strip()
    if not keyword:
        print("关键词不能为空")
        return
    
    start = time.time()
    print(f"正在搜索关键词: '{keyword}' ...")
    img_urls = get_image_urls_from_html(keyword, page=0)
    print(f"成功提取到 {len(img_urls)} 个图片URL")

    if not img_urls:
        print("\n⚠️  仍然未找到图片。")
        print("可能原因：")
        print("1. 关键词过于冷门或敏感")
        print("2. 网络问题或百度暂时屏蔽")
        print("3. 请尝试更换关键词或稍后再试")
        return

    success = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download_image, url, i) for i, url in enumerate(img_urls)]
        for f in futures:
            if f.result():
                success += 1

    end = time.time()
    print(f"\n✅ 下载报告：成功 {success}/{len(img_urls)}，耗时 {end - start:.2f}秒")

if __name__ == "__main__":
    main()