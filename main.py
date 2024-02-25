# main.py

import chainlit as cl
from openai import OpenAI
from sinch import Client

client = OpenAI(
    api_key="<api-key>",
    base_url="https://api-alpha.julep.ai/v1"
)

# Configure SinchSMS
sinch_client = Client(
    key_id="",
    key_secret="",
    project_id=""
)

class SpaceExplorerChat:
    def __init__(self, model, settings):
        self.prompt_template = """
        situation
        you are a sustainability expert, answer the questions as an sustainability enthusiast
        """
        self.model = model
        self.settings = settings
        self.history = []

    def respond(self, message: str):
        print("responding to message")
        full_prompt = self._build_full_prompt(message)

        completion = client.completions.create(
            model=self.model, prompt=full_prompt, **self.settings
        )

        response_text = completion.choices[0].text.strip()
        print("response is", response_text)
        last_full_stop_index = response_text.rfind('.')
        if last_full_stop_index != -1:
            response_text = response_text[:last_full_stop_index + 1]
        self._update_history(message, response_text)


        return response_text

    def _build_full_prompt(self, message: str):
        history_str = "\n".join(self.history)
        full_prompt = f"""{self.prompt_template}{history_str}
        user (Explorer)
        {message} 
        assistant (sustainability expert)
        """
        return full_prompt

    def _update_history(self, message: str, response_text: str):
        self.history.append(f"""
                            user (Explorer)
                            {message} 
                            assistant (sustainability expert)
                            {response_text} """)

def get_generic_list():

        return ["Program1: Ocean Cleanup", "Program2: Online Environment Portection Course ", "Program3: School Visit on Env Education"]


def send_sms(user_number, message):
    # Send SMS using SinchSMS
    if "Program1" in message:
        message="At juhu beach, 7 a.m please bring a hat with you. see you there"
    elif "Program2" in message:
        message="At Zoom, 7 a.m the link will be shared an hour before the session. see you there"
    else:
        message="At KV school, 7 a.. see you there"

    send_batch_response = sinch_client.sms.batches.send(
    body=message,
    to=[user_number],
    from_="+447520651104",
    delivery_report="none"
)

model_name = "julep-ai/samantha-1-turbo"
settings = {
    "temperature": 0.4,
    "max_tokens": 120,
    "frequency_penalty": 0.75,
    "best_of": 2,
    "stop": ["<", "<|"]
}

space_explorer_chat = SpaceExplorerChat(model_name, settings)
@cl.on_chat_start
async def start():
    image = cl.Image(path="aa.gif", name="image1", display="inline",size="large")
    # Attach the image to the message
    await cl.Message(content="HELLO SUSTAINABILITY SEEKER, I AM HERE TO HELP YOU!",elements=[image],author="ECO FRIEND").send()
    await cl.Avatar(name="SEEKER",url="https://avatars.githubusercontent.com/u/128686189?s=400&u=a1d1553023f8ea0921fba0debbe92a8c5f840dd9&v=4",).send()
     # Sending an action button within a chatbot message
@cl.on_message
async def main(message: cl.Message):
    # Check for generic list query
    if "sustainability programs" in message.content.lower():
        # Extract the query field (e.g., sustainability, events, etc.)
    #    ?
        # Fetch generic list (e.g., sustainability programs, events) from the placeholder function
        generic_list = get_generic_list()
        print("generic list is",generic_list)
        response = f"Available programs: {', '.join(generic_list)}"
    elif "register me into" in message.content.lower():
        await cl.Message(content="Please enter your phone number.").send()

        phone_number_response = await cl.AskUserMessage(content="What is your name?", timeout=10).send()
        # Extract the phone number from the user's response
        if phone_number_response["output"]:
            print("yieuripoerop",phone_number_response)
            user_number = phone_number_response["output"].strip()

        # Extract the program from the user's request
            program = message.content.split("register me into")[1].strip()
            # Add user registration logic here
            # Send registration SMS
            send_sms(user_number, f"Registered you into {program} program. Confirmation details will be sent to your email!")
            response = f"Registered you into {program} program. Confirmation details sent to your phone: {user_number}"
    else:
        # Respond as per the SpaceExplorerChat logic
        response = space_explorer_chat.respond(message.content)

    await cl.Message(content=response).send()
