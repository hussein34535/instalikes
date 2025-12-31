import json
import os
# from flask import jsonify # لم نعد نحتاج إلى هذا

# RESULTS_FILE = "results.txt" # لم نعد نستخدم هذا

# Ensure file exists (for local development/initial setup)
# هذا الجزء لم يعد ضروريًا
# if not os.path.exists(RESULTS_FILE):
#     with open(RESULTS_FILE, "w") as f:
#         f.write("")

# Vercel Serverless Function entry point
def handler(request):
    if request.method == "GET":
        # مؤقتًا، أعد رسالة بسيطة
        return {"results": "لا توجد نتائج بعد. (وظيفة النتائج الحقيقية تحتاج إلى تخزين دائم)"}, 200 # استخدام dict بدلاً من jsonify
    return {"error": "Method not allowed"}, 405 # استخدام dict بدلاً من jsonify
