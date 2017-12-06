import requests
from scrapy.selector import Selector
import time
from multiprocessing import Pool
import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
s = requests.session()


def get_review(asin, page):
    def get_title(review):
        title = review.xpath('div/div/a[@data-hook="review-title"]/text()').extract_first('')
        return title

    def get_reviewer(review):
        reviewer = review.xpath('div//span[@data-hook="review-author"]/a/text()').extract_first('')
        if len(reviewer) < 2:
            print('reviewer problem')
        return reviewer

    def get_star(review):
        star = review.xpath('div/div/a/i/span/text()').extract_first('')
        star = float(star.replace('5つ星のうち', '').split()[0])
        return star

    def get_verified(review):
        verified = review.xpath('div/div[contains(@class, "review-format-strip")]/span/a/span/text()').extract_first('')
        return verified

    def get_content(review):
        content = review.xpath('div/div[@class="a-row review-data"]/span/text()').extract_first('')
        return content

    def get_helpful(review):
        helpful = review.xpath(
            'div/div[contains(@class, "review-comments")]//span[@data-hook="helpful-vote-statement"]/text()').extract_first(
            '')
        try:
            helpful = int(helpful.strip()[0])
        except Exception as e:
            helpful = 0
        return helpful

    def get_reviewDate(review):

        review_date = review.xpath('div//span[@data-hook="review-date"]/text()').extract_first('')
        review_date = review_date.replace('年', ' ').replace('月', ' ').replace('日', ' ').strip()
        review_date = datetime.datetime.strptime(review_date, "%Y %m %d")
        return review_date

    # 设置参数

    time.sleep(1)
    url = 'https://www.amazon.co.jp/product-reviews/'
    url = url + asin + '/?pageNumber=' + str(page)

    # 读取数据
    r = s.get(url, headers=headers)
    selector = Selector(text=r.text)
    reviews = selector.xpath('//div[@id="cm_cr-review_list"]/div[@data-hook="review"]')
    lst = []
    for review in reviews:
        data = {
            'asin': asin,
            'title': get_title(review),
            'star': get_star(review),
            'verified': get_verified(review),
            'content': get_content(review),
            'helpful': get_helpful(review),
            'review_date': get_reviewDate(review),
            'reviewer': get_reviewer(review),
        }
        lst.append(data)
    return lst


def multi_review(asin, page):
    # 设置参数
    info_lst = []
    for page in range(1, page + 1):
        info = [asin, page]
        info_lst.append(info)

    # 建立进程池
    pool = Pool()
    temp = []
    for info in info_lst:
        temp.append(pool.apply_async(get_review, args=(info[0], info[1])))
    pool.close()
    pool.join()

    # 执行多进程
    lst = []
    for item in temp:
        lst.append(item.get())
    return lst