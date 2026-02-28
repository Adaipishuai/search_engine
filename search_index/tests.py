import pymysql
from elasticsearch import Elasticsearch, helpers


# # 连接到 Elasticsearch
# es = Elasticsearch(["http://localhost:9200"])
# es.indices.delete(index="bookss", ignore_unavailable=True)
# # 定义索引映射
# mapping = {
#     "mappings": {
#         "properties": {
#             "book_id": {"type": "integer"},
#             "bookName": {"type": "text"},
#             "category": {"type": "text"},
#             "count_char": {"type": "integer"},
#             "cover": {"type": "keyword"},
#             "authors": {"type": "text"},
#             "count_click": {"type": "integer"},
#             "introduction": {"type": "text"},
#             "sourceUrl": {"type": "keyword"},
#             "sourceName": {"type": "keyword"},
#             "status": {"type": "keyword"},
#             "tag": {"type": "keyword"},
#             "score": {"type": "float"}
#         }
#     }
# }
#
# # 创建索引
# response = es.indices.create(index="bookss", body=mapping)
# print(response)



# import pymysql
# from elasticsearch import Elasticsearch, helpers
#
# # 连接到 MySQL 数据库
# mysql_conn = pymysql.connect(
#     host='localhost',
#     user='root',
#     password='root',
#     database='books',
#     charset='utf8mb4'
# )
#
# # 连接到 Elasticsearch
# es = Elasticsearch("http://localhost:9200")
#
# # 从 MySQL 中提取数据
# def fetch_mysql_data():
#     with mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
#         cursor.execute("SELECT * FROM books;")  # 替换为你的表名
#         for row in cursor.fetchall():
#             yield row
#
# # 将数据批量插入到 Elasticsearch 中
# def import_to_elasticsearch():
#     actions = [
#         {
#             "_op_type": "index",  # 默认为索引操作
#             "_index": "bookss",  # 索引名称
#             "_id": row["id"],  # 使用 MySQL 的 id 字段作为文档的 ID
#             "_source": {
#                 "book_id": row["id"],
#                 "bookName": row["bookName"],
#                 "category": row["category"],
#                 "count_char": row["count_char"],
#                 "cover": row["cover"],
#                 "authors": row["authors"],
#                 "count_click": row["count_click"],
#                 "introduction": row["introduction"],
#                 "sourceUrl": row["sourceUrl"],
#                 "sourceName": row["sourceName"],
#                 "status": row["status"],
#                 "tag": row["tag"],
#                 "score": row["score"]
#             }
#         }
#         for row in fetch_mysql_data()
#     ]
#
#     # 批量插入到 Elasticsearch
#     helpers.bulk(es, actions)
#     print("数据已导入 Elasticsearch")
#
# if __name__ == "__main__":
#     import_to_elasticsearch()





# from elasticsearch import Elasticsearch
#
# # 连接到Elasticsearch集群
# es = Elasticsearch(['http://localhost:9200'])
#
# # 定义查询条件，假设范围是 100 到 500 之间
# # query = {
# #     "query": {
# #         "range": {
# #             "count_click": {
# #                 "gte": 1000,
# #                 "lte": 5000
# #             }
# #         }
# #     }
# # }
#
# #简单查询
# query = {
#     "query": {
#         "match": {
#             "bookName": "狂人"
#         }
#     }
# }
# # 执行查询
# response = es.search(index="bookss", body=query)
#
# # 输出查询结果
# print(response)







# from elasticsearch import Elasticsearch
#
# es = Elasticsearch(['http://localhost:9200'])
#
# # 获取索引的映射
# mapping = es.indices.get_mapping(index="bookss")
# print(mapping)
