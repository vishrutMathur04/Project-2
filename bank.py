#!/usr/bin/env python3

import threading
import time
import random
from collections import deque

NUM_TELLERS = 3
NUM_CUSTOMERS = 25

# Concurrency controls
lobby_limit = threading.Semaphore(2)      # at most 2 customers in lobby
vault_access = threading.Semaphore(2)     # at most 2 tellers in safe
manager_access = threading.Semaphore(1)   # one teller with manager at a time

# Synchronization for queueing and starting
arrival_gate = threading.Semaphore(0)     # released once bank opens
queue_ready = threading.Semaphore(0)      # number of customers waiting in line

# Shared collections
customer_line = deque()
assigned_customer = {}
transaction_choice = {}

# Per-customer semaphores (filled in main)
ask_type = {}
recv_type = {}
finish_signal = {}

# Counters / locks
tellers_ready = 0
processed_count = 0
state_lock = threading.Semaphore(1)       # mutex for shared state


# --- helper print functions using exact professor wording ---
def p_teller_ready(tid):
    print(f"Teller {tid} []: ready to serve")
    print(f"Teller {tid} []: waiting for a customer")


def p_customer_want(cid, choice_word):
    # "Customer 0 []: wants to perform a deposit transaction"
    print(f"Customer {cid} []: wants to perform a {choice_word} transaction")


def p_customer_go_to_bank(cid):
    print(f"Customer {cid} []: going to bank.")
    print(f"Customer {cid} []: entering bank.")
    print(f"Customer {cid} []: getting in line.")
    print(f"Customer {cid} []: selecting a teller.")


def p_customer_selects(cid, tid):
    print(f"Customer {cid} [Teller {tid}]: selects teller")
    print(f"Customer {cid} [Teller {tid}] introduces itself")


def p_teller_calling(tid, cid):
    print(f"Teller {tid} [Customer {cid}]: serving a customer")
    print(f"Teller {tid} [Customer {cid}]: asks for transaction")


def p_customer_asks_transaction(cid, tid, kind):
    # "Customer 22 [Teller 1]: asks for withdrawal transaction"
    print(f"Customer {cid} [Teller {tid}]: asks for {kind} transaction")


def p_teller_handling(tid, cid, kind):
    print(f"Teller {tid} [Customer {cid}]: handling {kind} transaction")


def p_teller_manager_start(tid, cid):
    print(f"Teller {tid} [Customer {cid}]: going to the manager")
    print(f"Teller {tid} [Customer {cid}]: getting manager's permission")


def p_teller_manager_granted(tid, cid):
    print(f"Teller {tid} [Customer {cid}]: got manager's permission")


def p_teller_go_safe(tid, cid):
    print(f"Teller {tid} [Customer {cid}]: going to safe")
    print(f"Teller {tid} [Customer {cid}]: enter safe")


def p_teller_leave_safe(tid, cid, kind):
    # "leaving safe" then "finishes deposit/withdrawal transaction."
    print(f"Teller {tid} [Customer {cid}]: leaving safe")
    print(f"Teller {tid} [Customer {cid}]: finishes {kind} transaction.")
    print(f"Teller {tid} [Customer {cid}]: wait for customer to leave.")


def p_customer_leaves(cid):
    print(f"Customer {cid} [Teller {assigned_customer.get(cid,'')}] leaves teller")
    print(f"Customer {cid} []: goes to door")
    print(f"Customer {cid} []: leaves the bank")


def p_teller_done_for_day(tid):
    print(f"Teller {tid} []: leaving for the day")


# --- worker threads ---
def teller_thread(tid):
    global tellers_ready, processed_count

    # Teller startup phrasing: ready to serve + waiting for a customer
    state_lock.acquire()
    tellers_ready += 1
    is_last = (tellers_ready == NUM_TELLERS)
    state_lock.release()

    # Print the ready/waiting lines (professor style)
    p_teller_ready(tid)

    # Last teller opens the bank for all customers
    if is_last:
        for _ in range(NUM_CUSTOMERS):
            arrival_gate.release()

    # Main loop: service customers until all processed
    while True:
        queue_ready.acquire()

        # termination check
        state_lock.acquire()
        if processed_count >= NUM_CUSTOMERS and not customer_line:
            state_lock.release()
            break
        if not customer_line:
            state_lock.release()
            continue
        cid = customer_line.popleft()
        assigned_customer[cid] = tid
        state_lock.release()

        # Print selection/intro from customer side (professor sample prints these around selection)
        p_customer_selects(cid, tid)

        # Teller calls and asks for transaction
        p_teller_calling(tid, cid)

        # Ask the customer to state transaction
        ask_type[cid].release()

        # Wait for customer to respond
        recv_type[cid].acquire()
        kind = transaction_choice.get(cid, "deposit")  # 'deposit' or 'withdraw'
        # Teller prints handling
        p_teller_handling(tid, cid, kind)

        # If withdraw -> manager
        if kind == "withdraw":
            p_teller_manager_start(tid, cid)
            manager_access.acquire()
            # granted
            p_teller_manager_granted(tid, cid)
            # small simulated manager time
            time.sleep(random.randint(5, 30) / 1000.0)
            manager_access.release()

        # After manager (if any), go to safe
        p_teller_go_safe(tid, cid)
        vault_access.acquire()
        # simulate using safe
        time.sleep(random.randint(10, 50) / 1000.0)
        vault_access.release()
        # leaving safe and finishing
        p_teller_leave_safe(tid, cid, "withdrawal" if kind == "withdraw" else "deposit")

        # signal customer that transaction finished
        finish_signal[cid].release()

        # let the customer leave and then increment processed_count
        # small yield to allow customer to print leaves
        time.sleep(0)
        state_lock.acquire()
        processed_count += 1
        state_lock.release()

    # Teller leaving for the day
    p_teller_done_for_day(tid)


def customer_thread(cid):
    # Decide upfront what this customer wants (so we can print initial wants block)
    choice = random.choice(["deposit", "withdraw"])
    transaction_choice[cid] = choice
    # initial professor-style desire line
    p_customer_want(cid, "deposit" if choice == "deposit" else "withdrawal")

    # Wait for bank to open
    arrival_gate.acquire()

    # Now perform entering sequence
    p_customer_go_to_bank(cid)

    # Enter lobby (capacity)
    lobby_limit.acquire()

    # Join queue
    state_lock.acquire()
    customer_line.append(cid)
    state_lock.release()

    # signal a teller that someone is waiting
    queue_ready.release()

    # Wait for teller to ask for transaction
    ask_type[cid].acquire()

    # When teller asked, customer prints the "asks for ..." message (professor style)
    # Determine kind word for phrasing
    kind_word = "deposit" if transaction_choice[cid] == "deposit" else "withdrawal"
    # Find assigned teller (may already be set by teller)
    tid = assigned_customer.get(cid, 0)
    p_customer_asks_transaction(cid, tid, kind_word)

    # Respond
    recv_type[cid].release()

    # Wait for teller to complete and signal finish
    finish_signal[cid].acquire()

    # Customer leaves teller and bank (professor style)
    p_customer_leaves(cid)

    # free lobby spot
    lobby_limit.release()


def main():
    random.seed()

    # Create per-customer semaphores
    for cid in range(NUM_CUSTOMERS):
        ask_type[cid] = threading.Semaphore(0)
        recv_type[cid] = threading.Semaphore(0)
        finish_signal[cid] = threading.Semaphore(0)

    # Start tellers first
    tellers = [threading.Thread(target=teller_thread, args=(t,)) for t in range(NUM_TELLERS)]
    for t in tellers:
        t.start()

    # Start customers (correctly, using range and explicit list)
    customers = []
    for cid in range(NUM_CUSTOMERS):
        t = threading.Thread(target=customer_thread, args=(cid,))
        customers.append(t)

    for t in customers:
        t.start()
        # small stagger to avoid extreme contention (keeps output readable)
        time.sleep(0.001)

    # Wait for customers to finish
    for c in customers:
        c.join()

    # All customers done; wake up tellers so they can exit
    for _ in range(NUM_TELLERS):
        queue_ready.release()

    # Wait for tellers to exit
    for t in tellers:
        t.join()

    print("Bank closed for the day.")


if __name__ == "__main__":
    main()
