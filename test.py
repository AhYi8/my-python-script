from utils.MysqlUtils import MysqlUtils

select_title_content = """
SELECT ID, post_title, post_content
FROM wp_posts
WHERE EXISTS(
    SELECT *
    FROM wp_postmeta
    WHERE post_id = wp_posts.ID AND meta_key = 'description'
)
ORDER BY ID ASC
LIMIT {} OFFSET {};
"""
limit = 500
MysqlUtils.change_database("res_21zys_com")
offset = 0
while True:
    data_list = MysqlUtils.select(select_title_content.format(limit, offset))

    for data in data_list:
        post_id = data



    offset += limit


