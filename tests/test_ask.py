from types import SimpleNamespace

from app.ask import ask, run_interactive


class FakeChat:
    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)
        return SimpleNamespace(text=f"回答: {message}")


def test_ask_sends_message_to_existing_chat():
    chat = FakeChat()

    answer = ask("LoRAとは？", chat)

    assert answer == "回答: LoRAとは？"
    assert chat.messages == ["LoRAとは？"]


def test_interactive_mode_keeps_using_same_chat(monkeypatch, capsys):
    chat = FakeChat()
    questions = iter(["LoRAとは？", "さっきの説明を短くして", "exit"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(questions))

    run_interactive(chat)

    assert chat.messages == ["LoRAとは？", "さっきの説明を短くして"]
    assert "回答: さっきの説明を短くして" in capsys.readouterr().out
