from collections import UserDict
from datetime import datetime, timedelta
import re
from colorama import Fore, Style, init

# Ініціалізація Colorama для використання кольорів у терміналі
init(autoreset=True)

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        self.value = self.validate(value)

    def validate(self, value):
        if not re.match(r"^\d{10}$", value):
            raise ValueError(Fore.RED + "Phone number must be 10 digits.")
        return value

class Birthday(Field):
    def __init__(self, value):
        self.value = self.validate(value)

    def validate(self, value):
        try:
            return datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError(Fore.RED + "Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.today().date()
            next_birthday = self.birthday.value.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            return (next_birthday - today).days
        return None

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"{Fore.CYAN}Name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                days_to_birthday = record.days_to_birthday()
                if days_to_birthday is not None and days_to_birthday <= days:
                    upcoming.append(record)
        return upcoming

class AssistantBot:
    def __init__(self):
        self.book = AddressBook()

    def handle_command(self, command):
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == "add":
            self.add_record(parts[1:])
        elif cmd == "show":
            self.show_all_records()
        elif cmd == "edit":
            self.edit_record(parts[1:])
        elif cmd == "delete":
            self.delete_record(parts[1:])
        elif cmd == "find":
            self.find_record(parts[1:])
        elif cmd == "birthday":
            self.add_birthday(parts[1:])
        elif cmd == "upcoming":
            self.show_upcoming_birthdays()
        elif cmd in ["exit", "close", "bye"]:
            return False
        else:
            print(Fore.RED + "Unknown command.")
        return True

    def add_record(self, args):
        name = args[0]
        phones = args[1:]  # Список телефонів
        record = Record(name)
        for phone in phones:
            try:
                record.add_phone(phone)
            except ValueError as e:
                print(e)
                return
        self.book.add_record(record)
        print(Fore.GREEN + f"Record added: {record}")

    def show_all_records(self):
        if not self.book.data:
            print(Fore.YELLOW + "Address book is empty.")
        else:
            for record in self.book.data.values():
                print(record)

    def edit_record(self, args):
        name = args[0]
        old_phone = args[1]
        new_phone = args[2]
        record = self.book.find(name)
        if record:
            try:
                record.edit_phone(old_phone, new_phone)
                print(Fore.GREEN + f"Phone number updated: {record}")
            except ValueError as e:
                print(e)
        else:
            print(Fore.RED + "Record not found.")

    def delete_record(self, args):
        name = args[0]
        self.book.delete(name)
        print(Fore.GREEN + f"Record deleted: {name}")

    def find_record(self, args):
        name = args[0]
        record = self.book.find(name)
        if record:
            print(record)
        else:
            print(Fore.RED + "Record not found.")

    def add_birthday(self, args):
        name = args[0]
        birthday = args[1]
        record = self.book.find(name)
        if record:
            try:
                record.add_birthday(birthday)
                print(Fore.GREEN + f"Birthday added: {record}")
            except ValueError as e:
                print(e)
        else:
            print(Fore.RED + "Record not found.")

    def show_upcoming_birthdays(self):
        upcoming = self.book.get_upcoming_birthdays()
        if upcoming:
            print(Fore.GREEN + "Upcoming birthdays:")
            for record in upcoming:
                print(f"{record.name.value} on {record.birthday.value.strftime('%d.%m.%Y')}")
        else:
            print(Fore.YELLOW + "No upcoming birthdays.")

def main():
    bot = AssistantBot()
    print(Fore.CYAN + "Welcome to the Assistant Bot! Enter your command:")
    while True:
        command = input(">>> ")
        if not bot.handle_command(command):
            print(Fore.CYAN + "Goodbye!")
            break

if __name__ == "__main__":
    main()
