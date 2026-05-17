import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = (
    '"mathchamp AI" adlı bir yapay zeka modelisin. Üniversite akademisyenlerinin öğrencilerine '
    "programlama görevleri atayabildiği ve yapay zeka aracılığıyla ilerlemelerini gerçek zamanlı "
    "olarak takip edebildiği bir platform için tasarlandın. Sana sınıflar ve öğrenciler hakkında "
    "JSON formatında veriler sağlanacaktır; JSON formatı hakkında hiçbir bilgi verme. "
    "JSON verisindeki anahtarlardan hiç bahsetme; her zaman değerlerini kullanarak yanıt ver. "
    "Amacın, eğitim sürecini iyileştirmek için öğretmenlere analizler, öneriler ve öğrenci geri "
    "bildirimleri sunmaktır. Öğretmenler, öğrencileri için kişiselleştirilmiş destek almak amacıyla "
    "sana başvuracaktır. Yanıtların ayrıntılı, açık ve öğretmenlerin özel ihtiyaçlarını karşılayacak "
    "şekilde hazırlanmış olmalıdır. "
    "Tüm yanıtlarını BBCode etiketleri kullanarak biçimlendirmelisin. "
    "Kalın metin için [b]...[/b], italik için [i]...[/i], altı çizili için [u]...[/u], "
    "liste için [list][*]...[/list] etiketlerini kullan, kod için [code]...[/code] etiketlerini kullan."
    "KESİNLİKLE Markdown formatı kullanma: **kalın**, *italik*, # başlık gibi ifadeler YASAKTIR. "
    "Yalnızca ve yalnızca BBCode etiketleri kullan. "
    "Örnek: 'Ders Adı' yerine [b]Ders Adı[/b] şeklinde yaz. "
    "En doğru değerlendirmeyi yapabilmek için derinlemesine bir analize dayandır. "
    "Tüm yanıtların Türkçe olmalıdır."
)

llm = ChatOpenAI(
    base_url = "https://api-i5aa4vm7t.brevlab.com/v1",
    model="qwen3-coder",
    api_key = "aaa",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=1.0,
    max_tokens=8192,
    default_headers={
        "Authorization": f"Bearer {os.getenv('BREVLAB_API_KEY')}"
    }
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

chain = prompt_template | llm


def _to_langchain_messages(history: list) -> list:
    """Convert Gemini-format or OpenAI dict-format history to LangChain message objects."""
    messages = []
    for item in history:
        if not item:
            continue
        role = item.get("role", "user")
        if role == "model":
            role = "assistant"
        if "parts" in item:
            content = item["parts"][0] if item["parts"] else ""
        else:
            content = item.get("content", "")
        content = content or ""
        if role == "assistant":
            messages.append(AIMessage(content=content))
        else:
            messages.append(HumanMessage(content=content))
    return messages


async def send_message(message: str, chat_history: list) -> dict:
    try:
        formatted_history = _to_langchain_messages(chat_history)

        response = await chain.ainvoke({
            "chat_history": formatted_history,
            "input": message,
        })

        ai_text = response.content

        plain_history = []
        for msg in formatted_history:
            if isinstance(msg, HumanMessage):
                plain_history.append({"role": "user", "content": msg.content})
            else:
                plain_history.append({"role": "assistant", "content": msg.content})

        updated_conversation = [
            *plain_history,
            {"role": "user", "content": message},
            {"role": "assistant", "content": ai_text},
        ]

        return {"text": ai_text, "conversation": updated_conversation}
    except Exception as e:
        print(e)
        return {"text": "Bir şeyler yanlış gitti", "conversation": chat_history}