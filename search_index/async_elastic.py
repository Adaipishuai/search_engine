from elasticsearch import Elasticsearch
import logging,random,requests
from custom_users.models import  *
import jieba
from collections import Counter

class ElasticsearchHelper:
    DEFAULT_THRESHOLD = 0.7
    DEFAULT_SIZE = 10

    def __init__(self, hosts=None, index=None):
        self.hosts = hosts or "http://localhost:9200"
        self.index = index or "bookss"
        self.es = Elasticsearch(self.hosts)
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    def check_index_exists(self):
        """检查索引是否存在"""
        return self.es.indices.exists(index=self.index)

    def simple_search(self, query, threshold=None, size=None, page=1, sort_field=None, sort_order="desc"):
        """
        搜索文本相似度，返回排序后的结果，低于阈值的结果不返回
        :param query: 搜索的关键词
        :param threshold: 相似度阈值，低于此值的结果不返回
        :param size: 每页返回的结果数量
        :param page: 当前页码
        :param sort_field: 排序字段，默认按相关性排序
        :param sort_order: 排序顺序，"asc" 或 "desc"，默认降序
        :return: 搜索结果
        """
        threshold = threshold or self.DEFAULT_THRESHOLD
        size = size or self.DEFAULT_SIZE
        from_ = (page - 1) * size

        if not self.check_index_exists():
            logging.error(f"索引 {self.index} 不存在")
            return {"total": 0, "results": [], "page": page, "size": size}

        body = {
            "query": {
                "query_string": {
                    "query": query,
                    "fields": ["*"],
                    "analyze_wildcard": True,
                    "default_operator": "AND"
                }
            },
            "min_score": threshold,
            "from": from_,
            "size": size
        }

        if sort_field:
            body["sort"] = [{sort_field: {"order": sort_order}}]

        # 高亮支持
        body["highlight"] = {
            "fields": {"*": {}},
            "pre_tags": ["<strong>"],
            "post_tags": ["</strong>"]
        }

        try:
            response = self.es.search(index=self.index, body=body)
            results = []
            for hit in response['hits']['hits']:
                source = hit["_source"]
                if "highlight" in hit:
                    source["highlight"] = hit["highlight"]
                results.append(source)
            return {
                "total": response['hits']['total']['value'],
                "results": results,
                "page": page,
                "size": size
            }
        except Exception as e:
            logging.error(f"Elasticsearch 搜索错误: {e}")
            return {"total": 0, "results": [], "page": page, "size": size, "error": str(e)}

    # def advanced_search(self, query=None, authors=None, tags=None,
    #                     click_range=None, char_range=None,
    #                     page=1, size=10):
    #     """
    #     高级搜索功能，支持全文匹配、高亮和范围检索。
    #     :param query: 搜索关键词
    #     :param authors: 作者名称（精确匹配）
    #     :param tags: 标签（精确匹配）
    #     :param click_range: 点击量范围 (min, max)
    #     :param char_range: 字数范围 (min, max)
    #     :param page: 当前页码
    #     :param size: 每页结果数
    #     :return: 搜索结果
    #     """
    #     from_ = (page - 1) * size
    #     must_clauses = []
    #
    #     # 按书名或简介全文搜索
    #     if query:
    #         must_clauses.append({
    #             "multi_match": {
    #                 "query": query,
    #                 "fields": ["bookName^2", "introduction"],  # 权重提升书名字段
    #                 "operator": "or"
    #             }
    #         })
    #
    #     # 作者精确匹配
    #     if authors:
    #         must_clauses.append({"term": {"authors.keyword": authors}})
    #
    #     # 标签精确匹配
    #     if tags:
    #         must_clauses.append({"term": {"tag.keyword": tags}})
    #
    #     # 点击量范围
    #     if click_range:
    #         must_clauses.append({
    #             "range": {"count_click": {"gte": click_range[0], "lte": click_range[1]}}
    #         })
    #
    #     # 字数范围
    #     if char_range:
    #         must_clauses.append({
    #             "range": {"count_char": {"gte": char_range[0], "lte": char_range[1]}}
    #         })
    #
    #     # 构造查询
    #     body = {"query": {
    #         "bool": {
    #             "must": must_clauses
    #         }
    #     },
    #         "from": from_,
    #         "size": size,
    #         "highlight": {
    #         "fields": {"*": {}},
    #         "pre_tags": ["<strong>"],
    #         "post_tags": ["</strong>"]
    #     }}
    #     try:
    #         response = self.es.search(index=self.index, body=body)
    #         return {
    #             "total": response['hits']['total']['value'],
    #             "results": [
    #                 {
    #                     "source": hit["_source"],
    #                     "highlight": hit.get("highlight", {})
    #                 } for hit in response['hits']['hits']
    #             ],
    #             "page": page,
    #             "size": size
    #         }
    #     except Exception as e:
    #         print(f"Elasticsearch 搜索错误: {e}")
    #         return {
    #             "total": 0,
    #             "results": [],
    #             "page": page,
    #             "size": size
    #         }

    def advanced_search(self, query=None, authors=None, tags=None,
                        click_range=None, char_range=None,
                        page=1, size=10):
        """
        高级搜索功能，支持全文匹配、高亮和范围检索。
        :param query: 搜索关键词
        :param authors: 作者名称（精确或模糊匹配）
        :param tags: 标签（精确或模糊匹配）
        :param click_range: 点击量范围 (min, max)
        :param char_range: 字数范围 (min, max)
        :param page: 当前页码
        :param size: 每页结果数
        :return: 搜索结果
        """
        from_ = (page - 1) * size
        must_clauses = []

        # 1. 按书名或简介全文搜索（包含权重和模糊查询）
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": ["bookName^2", "introduction"],  # 提升书名字段的权重
                    "operator": "or",  # 使用 'or'，允许部分匹配
                    "type": "best_fields",  # 使用 best_fields，允许字段之间的匹配
                    "fuzziness": "AUTO"  # 允许模糊匹配
                }
            })

        # 2. 作者精确或模糊匹配
        if authors:
            must_clauses.append({
                "match": {
                    "authors": {
                        "query": authors,
                        "operator": "or",  # 允许部分匹配
                        "fuzziness": "AUTO"  # 允许拼写错误匹配
                    }
                }
            })

        # 3. 标签精确或模糊匹配
        if tags:
            must_clauses.append({
                "match": {
                    "tag": {
                        "query": tags,
                        "operator": "or",  # 允许部分匹配
                        "fuzziness": "AUTO"  # 允许拼写错误匹配
                    }
                }
            })

        # 4. 点击量范围查询（支持最小和最大值指定）
        if click_range:
            must_clauses.append({
                "range": {
                    "count_click": {
                        "gte": click_range[0],  # 最小点击量
                        "lte": click_range[1]  # 最大点击量
                    }
                }
            })

        # 5. 字数范围查询（支持最小和最大值指定）
        if char_range:
            must_clauses.append({
                "range": {
                    "count_char": {
                        "gte": char_range[0],  # 最小字数
                        "lte": char_range[1]  # 最大字数
                    }
                }
            })

        # 构造查询体
        body = {
            "query": {
                "bool": {
                    "should": must_clauses  # 允许多个条件之间的宽松匹配
                }
            },
            "from": from_,
            "size": size,
            "highlight": {  # 高亮支持
                "fields": {"*": {}},
                "pre_tags": ["<strong>"],
                "post_tags": ["</strong>"]
            }
        }

        try:
            # 执行搜索
            response = self.es.search(index=self.index, body=body)
            return {
                "total": response['hits']['total']['value'],  # 总匹配数
                "results": [
                    {
                        "source": hit["_source"],
                        "highlight": hit.get("highlight", {})  # 高亮内容
                    } for hit in response['hits']['hits']
                ],
                "page": page,
                "size": size
            }
        except Exception as e:
            logging.error(f"Elasticsearch 搜索错误: {e}")
            return {
                "total": 0,
                "results": [],
                "page": page,
                "size": size
            }



def get_user_search_history(user):
    search_history = SearchHistory.objects.filter(user=user).values_list('query', flat=True)
    return list(search_history)

def analyze_search_history(search_history):
    # 使用jieba进行分词
    words = []
    for query in search_history:
        words.extend(jieba.cut(query))  # 分词并将词汇添加到列表
    word_count = Counter(words)  # 统计词频
    return word_count
def load_stopwords(file_path):
    # 读取停用词文件并返回一个停用词集合
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords = set(line.strip() for line in file.readlines())
    return stopwords
def recommend_search_term(user):
    # 提取搜索历史
    search_history = get_user_search_history(user)

    if not search_history:
        return "没有搜索历史，无法推荐"

    # 分词并统计词频
    word_count = analyze_search_history(search_history)

    # 过滤掉一些无意义的词，比如空格，常见的停用词等
    stopwords = load_stopwords('search_index/stopwords.txt')
    filtered_word_count = {word: count for word, count in word_count.items() if word not in stopwords}

    if not filtered_word_count:
        return "没有足够的搜索词可供推荐"

    # 根据频率选择一个词
    recommended_word = random.choices(list(filtered_word_count.keys()), weights=filtered_word_count.values(), k=1)[0]

    return recommended_word


def recommend_book(recommended_word):
    es = Elasticsearch(["http://localhost:9200"])

    # 执行查询
    response = es.search(
        index="bookss",
        body={
            "query": {
                "bool": {
                    "should": [
                        {"match": {"category": f"{recommended_word}"}},
                        {"match": {"tag": f"{recommended_word}"}}
                    ],
                    "minimum_should_match": 1
                }
            }
        }
    )

    # 获取查询结果
    hits = response['hits']['hits']

    # 检查查询结果是否为空
    if not hits:
        raise ValueError(f"No books found for the word '{recommended_word}'")

    # 随机选择一个结果
    random_hit = hits[random.randint(0, len(hits) - 1)]
    book_id = random_hit['_id']

    return book_id


def img():

    try:
        a = requests.get('https://free.wqwlkj.cn/wqwlapi/daily.php?type=json')
        img_url = a.json()['\u56fe\u7247']
    except:
        img_url = 'https://api.suyanw.cn/api/bing.php'
    return img_url