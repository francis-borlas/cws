import requests

BASE = "http://127.0.0.1:5000"

print("Welcome to CWS!")
start = input("Enter 1 to continue or 2 to exit: ")

while start == "1":
    print("Choose Action")
    input()
    print("1) Create Account")
    print("2) Check Balance")
    print("3) Deposit")
    print("4) Debit")
    print("5) Exit")

    action = input("Type number of selected action: ")

    actionDigit = int(action)

    if isinstance(actionDigit, int) and (actionDigit < 5 and actionDigit > 0):
        if actionDigit == 1:
            email = input("Type your email: ")
            pin = input("Set pin: ")

            response = requests.post(
                BASE + "/users", {"email": email, "pin": pin})
            if response.status_code < 400:
                print("Account creation successful")
            else:
                print(response.json()['message'])
            input()
        if actionDigit == 2:
            email = input("Type your email: ")
            pin = input("Input pin: ")

            response = requests.get(
                BASE + "/users/current-balance", {"email": email, "pin": pin})
            if response.status_code < 400:
                print("Your current balance is " +
                      str(response.json()['current_balance']))
            else:
                print(response.json()['message'])
            input()
        if actionDigit == 3:
            email = input("Type your email: ")
            amount = input("Input amount: ")
            pin = input("Input pin: ")

            response = requests.post(BASE + "/transactions",
                                     {"amount": amount, "tx_type": "Deposit", "email": email, "pin": pin})

            if response.status_code < 400:
                print("Deposit Successful!")
            else:
                print(response.json()['message'])
            input()
        if actionDigit == 4:
            email = input("Type your email: ")
            amount = input("Input amount: ")
            pin = input("Input pin: ")

            response = requests.post(BASE + "/transactions",
                                     {"amount": amount, "tx_type": "Debit", "email": email, "pin": pin})

            if response.status_code < 400:
                print("Debit Successful!")
            else:
                print(response.json()['message'])
            input()
        if actionDigit == 5:
            start = 2
            input()
    else:
        print("Invalid Action")
