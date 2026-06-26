import csv,json,os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client=Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL=os.getenv("MODEL","llama-3.3-70b-versatile")
results=[]
with open("reviews.csv",encoding="utf-8") as f:
    for row in csv.DictReader(f):
        prompt=f"""Ты аналитик интернет-магазина.
Верни ТОЛЬКО JSON:
{{"sentiment":"positive|negative|neutral","topic":"..."}}
Отзыв:
{row["review"]}"""
        try:
            r=client.chat.completions.create(
                model=MODEL,
                messages=[{"role":"user","content":prompt}],
                temperature=0
            )
            txt=r.choices[0].message.content.strip()
            txt=txt.replace("```json","").replace("```","").strip()
            obj=json.loads(txt)
            obj["id"]=row["id"]
            obj["review"]=row["review"]
            results.append(obj)
        except Exception as e:
            results.append({"id":row["id"],"review":row["review"],"sentiment":"error","topic":"error","api_error":str(e)})
with open("results.json","w",encoding="utf-8") as f:
    json.dump(results,f,ensure_ascii=False,indent=4)
print("Done")
