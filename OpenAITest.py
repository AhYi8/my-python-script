from utils.OpenAIUtils import OpenAIUtils, Prompt
article = r"""
一门专为解决家庭问题而设计的实用课程。课程内容涵盖冲突管理、预期管理、建立信任和感情修复等多个方面，帮助学员全面提升婚姻质量。通过学习脑神经科学和亲密关系的知识，学员将学会解决问题、表达情绪和共情他人，改善婚姻中的沟通方式。课程由资深情感导师授课，提供一对一指导和丰富的实战经验分享，确保学员在学习过程中获得全面支持和帮助
"""

openai_utils = OpenAIUtils('mh', prompt=Prompt.ARTICLE_SEO)
response = openai_utils.chat(article)
print(response)