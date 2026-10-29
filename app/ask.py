"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    uv run python -m app.ask --interactive  # 会話形式で続けて質問する

ツールは使わない「素の」呼び出し。--interactive では同じチャットを使い続け、
会話履歴を保ったまま追加の質問ができる。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai.chats import Chat
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def create_chat(client: genai.Client) -> Chat:
    return client.chats.create(model=MODEL)


def ask(question: str, chat: Chat | None = None) -> str:
    if chat is None:
        client = genai.Client(api_key=get_api_key())
        chat = create_chat(client)
    response = chat.send_message(question)

    # TODO(第1回 演習): response.usage_metadata から
    #   入力トークン数と出力トークン数を表示してみよう（Copilotに頼んでよい）

    return response.text


def run_interactive(chat: Chat) -> None:
    print("会話を開始します。終了するには exit または Ctrl-D を入力してください。")
    while True:
        try:
            question = input("質問> ")
        except EOFError:
            print()
            return
        if question.strip().lower() in {"exit", "quit"}:
            return
        if not question.strip():
            continue

        print(f"[質問] {question}\n")
        print(ask(question, chat))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?")
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="会話履歴を保ったまま続けて質問する",
    )
    args = parser.parse_args()
    if args.interactive and args.question:
        parser.error("対話モードでは質問を指定しないでください")

    print(f"[model] {MODEL}")
    try:
        if args.interactive:
            client = genai.Client(api_key=get_api_key())
            run_interactive(create_chat(client))
        else:
            question = args.question or DEFAULT_QUESTION
            print(f"[質問] {question}\n")
            print(ask(question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
