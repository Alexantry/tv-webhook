from flask import Flask, request, jsonify, abort
import os, datetime, logging

# 创建 Flask 应用
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 共享密钥（稍后我们会在 Render 里设置）
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# 健康检查接口（Render 用来判断服务是否在线）
@app.route("/", methods=["GET"])
def health():
    return "OK", 200

# Webhook 接口 — TradingView 会 POST 到这里
@app.route("/webhook", methods=["POST"])
def webhook():
    # 检查密钥
    token = request.headers.get("X-Auth-Token", "")
    if WEBHOOK_SECRET and token != WEBHOOK_SECRET:
        app.logger.warning("❌ 未授权的请求")
        abort(401, description="Unauthorized")

    # 确保接收到 JSON
    if not request.is_json:
        abort(400, description="Expect JSON body")

    # 获取 JSON 数据
    data = request.get_json(silent=True) or {}
    app.logger.info("🔔 收到 TradingView 警报：%s @ %s", data, datetime.datetime.utcnow())

    # 这里可以添加你的自动下单逻辑，比如 place_order(...)
    return jsonify({"status": "ok", "received": data}), 200

# 程序入口（在本地运行时使用）
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
