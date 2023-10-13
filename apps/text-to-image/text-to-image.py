# Import dependencies
import os
import evadb
import sys
import pandas as pd
# import requests
# import subprocess

# from PIL import Image
# from io import BytesIO

# Connect to EvaDB
cursor = evadb.connect().cursor()

# to collect all user prompts
def get_user_input():
    print('Welcome to EvaDB!')
    print('Enter your image prompts one by one; type \'exit\' to stop entering prompts.')
    print('========================================')
    prompts = []
    prompt=None

    # receive all prompts from user
    while True:
        prompt = input(
            'Enter prompt: '
        ).strip()
        if prompt in ['Exit', 'exit', 'EXIT']:
            print("========================================\nAll prompts are entered!")
            break
        prompts.append(prompt)
        print(prompt)

    return prompts


# to set the replicate API token environment variable
def set_replicate_token() -> None:
    # key = input('Enter your Replicate API Token: ').strip()
    key = 'r8_4vh07os7RJTeSrcuQT7tCFtcJDDOqJE4LbaZp'

    try:
        os.environ['REPLICATE_API_TOKEN'] = key
        print('Environment variable for Replicate set successfully.')
    except Exception as e:
        print("! Session ended with an error.")
        print(e)
        print("===========================================")

# to set the OpenAI API token environment variable
def set_openai_token() -> None:
    # key = input('Enter your OpenAI API Token: ').strip()
    key = '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'

    try:
        os.environ['OPENAI_KEY'] = key
        print('Environment variable for OpenAI set successfully.')
    except Exception as e:
        print("! Session ended with an error.")
        print(e)
        print("===========================================")

if __name__ == "__main__":
    model = input('Select the diffusion model you want. r for Replicate, d for DALL-E, b for both: ').strip()
    if model != 'r' and model != 'd' and model != 'b':
        print("No support for this model, please run again and select a supported model.")
        sys.exit(0)

    # getting user input
    prompts = get_user_input()

    # delete the table if it already exists
    cursor.query("""DROP TABLE IF EXISTS ImageGen
                """).execute()

    # create the table specifying the type of the prompt column
    cursor.query("""CREATE TABLE IF NOT EXISTS ImageGen (
                prompt TEXT(100))
                    """).execute()

    # insert the prompts into the table
    for prompt in prompts:
        cursor.query(f"""INSERT INTO ImageGen (prompt) VALUES ('{prompt}')""").execute()
    
    # get the image url from the two models respectively
    if model == 'r' or model == 'b':
        # setting api token as env variable
        set_replicate_token()

        # set up the stable diffusion UDF available at functions/stable_diffusion.py
        stable_diffusion_query = f"""CREATE FUNCTION IF NOT EXISTS StableDiffusion
                                IMPL  'functions/stable_diffusion.py';
                                """
        cursor.query(stable_diffusion_query).execute()

        # run Stable Diffusion on the Prompts
        table = cursor.table("ImageGen").select("StableDiffusion(prompt)").df()

        # list of generated images
        image_url = list(table[table.columns[0]])

        # print the url
        print("Images generated by Replicate:")
        for i in range(len(image_url)):
            print(prompts[i] + ": " + image_url[i])

    if model =='d' or model == 'b':
        # setting api token as env variable
        set_openai_token()

        # set up the stable diffusion UDF available at functions/dalle.py
        dalle_query = f"""CREATE FUNCTION IF NOT EXISTS DallE
                                IMPL  'functions/dalle.py';
                                """
        cursor.query(dalle_query).execute()

        # run Stable Diffusion on the Prompts
        table = cursor.table("ImageGen").select("DallE(prompt)").df()

        # list of generated images
        image_url = list(table[table.columns[0]])

        # print the url
        print("Images generated by DALL-E:")
        for i in range(len(image_url)):
            print(prompts[i] + ": " + image_url[i])

    # # Send a GET request to the image URL
    # response = requests.get(image_url[0])

    # # Check if the request was successful
    # if response.status_code == 200:
    #     # Open the image from the response content
    #     img = Image.open(BytesIO(response.content))

    #     # Save the image to a temporary file
    #     temp_image_path = "temp_image.jpg"
    #     img.save(temp_image_path)

    #     # Open the image with the default image viewer
    #     # subprocess.Popen(["xdg-open", temp_image_path])  # On Linux
    #     # subprocess.Popen(["open", temp_image_path])      # On macOS
    #     subprocess.Popen(["start", temp_image_path], shell=True)  # On Windows
    # else:
    #     print("Failed to download the image. Status code:", response.status_code)

