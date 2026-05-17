import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = (
    "Öğretmenlerin öğrencilerine programlama görevleri atayabildiği ve ilerlemelerini takip edebildiği "
    "bir platformda kod analizi yapan bir yapay zeka modelisin. "
    "Öğrenci tarafından sağlanan kodun tamamlanma yüzdesini hesaplayacaksın. "
    "En doğru değerlendirmeyi yapabilmek için kodun derinlemesine analizini esas alacaksın. "
    "Vereceğin açıklama, öğretmeni öğrencinin ilerleme durumu hakkında bilgilendirmelidir. "
    "Tüm yanıtlarını BBCode etiketleri kullanarak biçimlendirmelisin. "
    "Kalın metin için [b]...[/b], italik için [i]...[/i], altı çizili için [u]...[/u], "
    "liste için [list][*]...[/list] etiketlerini kullan, kod için [code]...[/code] etiketlerini kullan."
    "KESİNLİKLE Markdown formatı kullanma: **kalın**, *italik*, # başlık gibi ifadeler YASAKTIR. "
    "Yalnızca ve yalnızca BBCode etiketleri kullan. "
    "Örnek: 'Tamamlanma Oranı' yerine [b]Tamamlanma Oranı[/b] şeklinde yaz. "
    "Tüm yanıtların Türkçe olmalıdır. "
    "YALNIZCA tam olarak iki anahtar içeren geçerli bir JSON nesnesiyle yanıt vermelisin: "
    '\"summary\" (string, BBCode formatında) ve \"percentage\" (0 ile 100 arasında bir sayı). '
    "JSON nesnesi dışında herhangi bir metin ekleme."
)

llm = ChatOpenAI(
    base_url = "https://api-i5aa4vm7t.brevlab.com/v1",
    model="qwen3-coder",
    api_key = "aaa",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=1.0,
    max_tokens=8192,
    model_kwargs={"response_format": {"type": "json_object"}},
    default_headers={
        "Authorization": "Bearer senin-key-in"
    }
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
])

chain = prompt_template | llm | JsonOutputParser()


async def analyze_code(task: str, language: str, code: str) -> dict:
    user_prompt = (
        f"Task: '{task}' kodunu {language} dilinde yaz.\n\n"
        f"Öğrencinin kodu:\n```{language}\n{code}\n```"
    )

    return await chain.ainvoke({"input": user_prompt})