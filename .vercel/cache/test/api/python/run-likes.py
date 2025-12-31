import json

def handler(request):
    if request.method == "POST":
        data = request.get_json()
        post_url = data.get("post_url")
        
        # رسالة وهمية لغرض التصحيح
        return {"message": f"Process started for {post_url} (Simplified for debugging)."}, 200
    
    return {"error": "Method not allowed"}, 405
