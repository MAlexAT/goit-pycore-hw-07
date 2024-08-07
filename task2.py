from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not self._validate_phone(value):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

    @staticmethod
    def _validate_phone(value):
        return value.isdigit() and len(value) == 10

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_to_remove = self.find_phone(phone)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            self.phones.remove(phone_to_edit)
            self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.today()
            next_birthday = self.birthday.value.replace(year=today.year)
            if next_birthday < today:
                next_birthday = self.birthday.value.replace(year=today.year + 1)
            return (next_birthday - today).days
        return None

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days):
        upcoming_birthdays = []
        today = datetime.today()
        end_date = today + timedelta(days=days)
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if today <= next_birthday <= end_date:
                    upcoming_birthdays.append(record)
                elif next_birthday < today:
                    next_birthday = record.birthday.value.replace(year=today.year + 1)
                    if today <= next_birthday <= end_date:
                        upcoming_birthdays.append(record)
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Insufficient arguments provided."
    return inner

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."

@input_error
def show_phone(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return f"Phones for {name}: {', '.join(phone.value for phone in record.phones)}"

@input_error
def show_all_contacts(args, book):
    return '\n'.join(str(record) for record in book.values())

@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if not record.birthday:
        return "No birthday set."
    return f"Birthday for {name}: {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book):
    days = int(args[0])
    upcoming_birthdays = book.get_upcoming_birthdays(days)
    return '\n'.join(
        f"Upcoming birthday: {record.name.value} on {record.birthday.value.strftime('%d.%m.%Y')}"
        for record in upcoming_birthdays
    )

def parse_input(user_input):
    return user_input.strip().split(' ', 1)

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args_str = parse_input(user_input)
        args = args_str.split() if args_str else []

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
import re

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Give me name and phone please."

    return inner

class Bot:
    def __init__(self):
        self.book = AddressBook()

    @input_error
    def add(self, args):
        name, phone = args
        if name in self.book:
            record = self.book.find(name)
            record.add_phone(phone)
        else:
            record = Record(name)
            record.add_phone(phone)
            self.book.add_record(record)
        return "Contact added."

    @input_error
    def add_birthday(self, args):
        name, birthday = args
        record = self.book.find(name)
        if not record:
            return "Contact not found."
        record.add_birthday(birthday)
        return "Birthday added."

    @input_error
    def phone(self, args):
        name = args[0]
        record = self.book.find(name)
        if not record:
            return "Contact not found."
        phones = [phone.value for phone in record.phones]
        return f"Phones for {name}: {', '.join(phones)}"

    @input_error
    def show_all(self, args):
        return '\n'.join(str(record) for record in self.book.values())

    @input_error
    def birthday(self, args):
        name = args[0]
        record = self.book.find(name)
        if not record:
            return "Contact not found."
        if not record.birthday:
            return "No birthday set."
        return f"Birthday for {name}: {record.birthday.value.strftime('%d.%m.%Y')}"

    @input_error
    def upcoming_birthdays(self, args):
        days = int(args[0])
        upcoming_birthdays = self.book.get_upcoming_birthdays(days)
        return '\n'.join(
            f"Upcoming birthday: {record.name.value} on {record.birthday.value.strftime('%d.%m.%Y')}"
            for record in upcoming_birthdays
        )

    def exit(self, args):
        return "Goodbye!"

    def handle_command(self, command_line):
        command_parts = command_line.split()
        command = command_parts[0].lower()
        args = command_parts[1:]

        commands = {
            "add": self.add,
            "birthday": self.add_birthday,
            "phone": self.phone,
            "show": self.show_all,
            "upcoming": self.upcoming_birthdays,
            "exit": self.exit,
            "close": self.exit,
        }

        if command in commands:
            return commands[command](args)
        else:
            return "Unknown command."

def main():
    bot = Bot()
    print("Welcome to your personal assistant bot!")
    while True:
        command_line = input("Enter a command: ")
        result = bot.handle_command(command_line)
        print(result)
        if result == "Goodbye!":
            break

if __name__ == "__main__":
    main()