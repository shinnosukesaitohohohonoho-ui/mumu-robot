from pathlib import Path
import json
import subprocess
import urllib.request

folder = Path(__file__).resolve().parent

actions = {
    "forward": "move_forward.sh",
    "left": "turn_left.sh",
    "right": "turn_right.sh",
}

labels = {
    "forward": "前進",
    "left": "左",
    "right": "右",
    "none": "動かない",
}

system_prompt = """
あなたは車輪付きロボットへの日本語指示を分類します。
動作は forward（前進）、left（左旋回）、
right（右旋回）、none（動かない）の4つです。
停止、否定、曖昧な指示、質問、雑談、
複数の動作を含む指示、対応できない動作はnoneにしてください。
分類例：
「前に進んで」→ forward
「左を向いて」→ left
「右を向いて」→ right
「左には回らないで」→ none
「前に進まないで」→ none
「右を向かないで」→ none
「止まって」→ none
「こんにちは」→ none
返答は指定されたJSON形式だけにしてください。
"""


def choose_action(text):
    body = {
        "model": "qwen3:4b",
        "stream": False,
        "think": False,
        "keep_alive": "5m",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        "format": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["forward", "left", "right", "none"],
                }
            },
            "required": ["action"],
            "additionalProperties": False,
        },
        "options": {"temperature": 0},
    }

    request = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.load(response)

    answer = json.loads(result["message"]["content"])
    action = answer["action"]

    if action not in labels:
        raise ValueError("対応していない動作です")

    return action


while True:
    command = input("ムム君へのお願い（終了で終わる）: ").strip()

    if command == "終了":
        print("またね！")
        break

    if not command:
        continue

    negative_words = (
        "ない", "なく", "ません", "ぬ",
        "禁止", "やめ", "止ま", "停止", "ストップ", "待って",
    )

    if any(word in command for word in negative_words):
        print("否定・停止の表現があるため、動作を見送ります。")
        continue

    try:
        action = choose_action(command)
    except Exception as error:
        print(f"AIの応答を確認できませんでした: {error}")
        continue

    print(f"AIの判断: {labels[action]}")

    if action == "none":
        print("今回は動きません。")
        continue

    confirm = input("この動作を実行しますか？（yで実行）: ").strip()

    if confirm.lower() != "y":
        print("実行を取りやめました。")
        continue

    script = folder / actions[action]

    try:
        subprocess.run(["bash", str(script)], check=True)
    except subprocess.CalledProcessError:
        print("動作の実行中にエラーが出ました。")
