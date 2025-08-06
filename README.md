# Shared Files Test

## تحديث هام (2024):

جميع أدوات جلب الإيميلات أو الاجتماعات (retrievers) تم تحسينها لتبحث فقط في أول 100 رسالة أو اجتماع من الخادم (Microsoft Graph API) بدلاً من 2000 أو أكثر.

- هذا يجعل البحث أسرع بكثير ويقلل الضغط على الإنترنت وMicrosoft API.
- تم تقليل الفلترة من جانب العميل قدر الإمكان.
- إذا كنت تحتاج نطاق أوسع، يمكنك تعديل المتغير `max_messages` أو `$top` في الكود، لكن القيمة الافتراضية الآن هي 100.

## الملفات التي تم تحسينها:
- email_date_range_retriever.py
- email_subject_date_range_retriever.py
- email_by_sender_date_retriever.py
- email_by_id_retriever.py
- calendar_subject_date_range_retriever.py
- calendar_date_range_retriever.py
- calendar_by_organizer_date_retriever.py
- calendar_by_date_retriever.py

## نصيحة:
إذا لم تجد كل النتائج التي تريدها، جرب تضييق نطاق البحث بالتاريخ أو المرسل أو الموضوع.

---

# Usage

(شرح الاستخدام كما هو سابقاً) 