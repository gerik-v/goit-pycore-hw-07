from collections import UserDict
from datetime import datetime, timedelta
from colorama import init, Fore

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
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

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
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now().date()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = self.birthday.value.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones = ', '.join(str(p) for p in self.phones)
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"Contact name: {self.name}, phones: {phones}, birthday: {birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                days_to_birthday = record.days_to_birthday()
                if days_to_birthday is not None and days_to_birthday <= days:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return Fore.RED + "Error: Not enough arguments."
        except ValueError as e:
            return Fore.RED + f"Error: {e}"
        except KeyError:
            return Fore.RED + "Error: Contact not found."
        except Exception as e:
            return Fore.RED + f"Unexpected error: {e}"
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = Fore.GREEN + "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = Fore.GREEN + "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return Fore.GREEN + "Phone number updated."
    return Fore.RED + "Contact not found."

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record:
        return Fore.CYAN + str(record)
    return Fore.RED + "Contact not found."

@input_error
def show_all(args, book: AddressBook):
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return Fore.GREEN + "Birthday added."
    return Fore.RED + "Contact not found."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return Fore.CYAN + f"{record.name}'s birthday is {record.birthday.value.strftime('%d.%m.%Y')}."
    return Fore.RED + "Birthday not found or contact not found."

@input_error
def birthdays(args, book: AddressBook):
    days = int(args[0]) if args else 7
    upcoming_birthdays = book.get_upcoming_birthdays(days)
    if not upcoming_birthdays:
        return Fore.YELLOW + "No upcoming birthdays in the next week."
    return Fore.CYAN + "\n".join(f"{record.name}: {record.birthday.value.strftime('%d.%m.%Y')} in {record.days_to_birthday()} days" for record in upcoming_birthdays)

def parse_input(user_input):
    return user_input.split()

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print(Fore.CYAN + "Good bye!")
            break

        elif command == "hello":
            print(Fore.CYAN + "How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print(Fore.RED + "Invalid command.")

if __name__ == "__main__":
    main()
