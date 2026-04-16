# Sanalika AI Auto Reply

أداة بسيطة لقراءة الرسائل الواردة والرد عليها تلقائياً باستخدام الذكاء الاصطناعي.

## الفكرة
- الأداة تراقب ملف `chat_in.txt` (كل سطر = رسالة جديدة).
- تولّد رد عبر OpenAI API.
- تكتب الردود في `chat_out.txt`.

> يمكنك ربط `chat_in.txt` و `chat_out.txt` بأي ماكرو/تكامل خارجي لقراءة وكتابة الدردشة داخل اللعبة.

## التشغيل

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="YOUR_KEY"
python sanalika_auto_reply.py
```

## الخيارات

```bash
python sanalika_auto_reply.py \
  --input-file chat_in.txt \
  --output-file chat_out.txt \
  --poll-interval 1.0 \
  --model gpt-4o-mini
```

## ملاحظات مهمة
- التزم بشروط استخدام اللعبة.
- لا تستخدم الأداة للإزعاج أو السبام.
- من الأفضل مراجعة الردود قبل الإرسال التلقائي الكامل.


---

## أداة ترجمة فورية (English -> Arabic) داخل مربع متحرك
تم إضافة ملف جديد: `ai_translate_box.py`.

### المميزات
- مربع (نافذة) مستقل تقدر تحركه بحرية من شريط العنوان.
- تقدر تتحكم في حجمه (تكبير/تصغير) بشكل مباشر.
- أي كلام إنجليزي يتكتب في المربع الأول بيتترجم تلقائيًا في المربع الثاني (Live Caption).
- يوجد زر **ترجمة الآن** للتحديث الفوري، مع استمرار الترجمة التلقائية أثناء الكتابة.
- الاختصار **Ctrl+Enter** للترجمة اليدوية السريعة وقت الحاجة.

### التشغيل
```bash
export OPENAI_API_KEY="YOUR_KEY"
python ai_translate_box.py
```

> الموديل الافتراضي: `gpt-4o-mini` (وتقدر تغيّره من خانة Model داخل النافذة).
