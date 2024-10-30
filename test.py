
def test_g4f_create():
    from g4f.client import Client


    prompt = r"""
    #01 You are a professional article SEO optimization master. 
    #02 Your task is to extract a description of about 150 words and 5-7 keywords from the article I provide. 
    #03 Follow the user’s requirements carefully & to the letter.
    #04 You must respond to my request in the following format, structured as follows: description: #{1}#{2}keyword: #{3}.Among them, #{1} is filled with a description, #{2} is filled with two line breaks, and #{3} is filled with a keyword.
    #05 Ensure that the description and keywords are primarily in Chinese.
    #06 Your description and keywords for the summary must be completely dependent on the article provided by the user.
    #07 If the article provided by the user has too few words, the #02 may not be followed.
    #08 Your responses should be informative and logical.
    #09 You can only give one reply for each conversation turn.
    """
    article = r"""
    一门专为解决家庭问题而设计的实用课程。课程内容涵盖冲突管理、预期管理、建立信任和感情修复等多个方面，帮助学员全面提升婚姻质量。通过学习脑神经科学和亲密关系的知识，学员将学会解决问题、表达情绪和共情他人，改善婚姻中的沟通方式。课程由资深情感导师授课，提供一对一指导和丰富的实战经验分享，确保学员在学习过程中获得全面支持和帮助
    """

    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": article},
        ],
    )
    print(response.choices[0].message.content)

def test_g4f_generate():
    from g4f.client import Client

    client = Client()
    response = client.images.generate(
        model="dall-e-3",
        prompt="a white siamese cat",
        # Add any other necessary parameters
    )

    image_url = response.data[0].url
    print(f"Generated image URL: {image_url}")


test_g4f_create()