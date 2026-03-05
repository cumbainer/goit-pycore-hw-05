from typing import Dict, Callable, List, Tuple

from decorators import input_error
from model.address_book import AddressBook
from model.record import Record


class Bot:
    def __init__(self):
        self._book = AddressBook.load()
        self._commands: Dict[str, Callable[[List[str]], str]] = {
            "add": lambda args: self._add_contact(args),
            "change": lambda args: self._change_phone(args),
            "phone": lambda args: self._show_phones(args),
            "all": lambda args: self._show_all(args),
            "add-birthday": lambda args: self._add_birthday(args),
            "show-birthday": lambda args: self._show_birthday(args),
            "birthdays": lambda args: self._show_birthdays(args),
            "hello": lambda _: "How can I help you?",
        }

    def run(self) -> None:
        print("Welcome to the assistant bot!")
        while True:
            user_input = input("Enter a command: ")
            command, args = self._parse_input(user_input)

            if command in ("close", "exit"):
                self._book.save()
                print("Good bye!")
                break

            handler = self._commands.get(command)
            if handler:
                print(handler(args))
            else:
                print("Invalid command.")

    @input_error
    def _add_contact(self, args: List[str]) -> str:
        name, phone, *_ = args
        record = self._book.find(name)
        message = "Contact updated."
        if record is None:
            record = Record(name)
            self._book.add_record(record)
            message = "Contact added."
        if phone:
            record.add_phone(phone)
        return message

    @input_error
    def _change_phone(self, args: List[str]) -> str:
        name, old_phone, new_phone, *_ = args
        record = self._book.find(name)
        if record is None:
            raise KeyError(name)
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."

    @input_error
    def _show_phones(self, args: List[str]) -> str:
        (name, *_) = args
        record = self._book.find(name)
        if record is None:
            raise KeyError(name)
        return "; ".join(str(p) for p in record.phones)

    @input_error
    def _show_all(self, _args: List[str]) -> str:
        if not self._book.records:
            return "No contacts found."
        return "\n".join(str(r) for r in self._book.records)

    @input_error
    def _add_birthday(self, args: List[str]) -> str:
        name, birthday, *_ = args
        record = self._book.find(name)
        if record is None:
            raise KeyError(name)
        record.add_birthday(birthday)
        return "Birthday added."

    @input_error
    def _show_birthday(self, args: List[str]) -> str:
        (name, *_) = args
        record = self._book.find(name)
        if record is None:
            raise KeyError(name)
        if record.birthday is None:
            return f"No birthday set for {name}."
        return str(record.birthday.value)

    @input_error
    def _show_birthdays(self, _args: List[str]) -> str:
        birthdays = self._book.get_upcoming_birthdays()
        if not birthdays:
            return "No upcoming birthdays."
        return "\n".join(
            f"{b['name']}: {b['congratulation_date']}" for b in birthdays
        )

    @staticmethod
    def _parse_input(user_input: str) -> Tuple[str, List[str]]:
        parts = user_input.strip().split()
        if not parts:
            return "", []
        return parts[0].lower(), parts[1:]
