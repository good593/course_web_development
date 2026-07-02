import enum 

class CHATBOT_ROLE(enum.Enum):
    user = (enum.auto, "사용자")
    assistant = (enum.auto, "LLM 모델")

# message
class CHATBOT_MESSAGE(enum.Enum):
    role = (enum.auto, "작성자")
    content = (enum.auto, "메세지")

