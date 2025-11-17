#!/usr/bin/env python3

import threading
import time
import random
from collections import deque

NUM_TELLERS = 3
NUM_CUSTOMERS = 15

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


def out(role, rid, partner_role="", partner_id=None, msg=""):
    """Consistent formatted output for logs."""
    if partner_role:
        print(f"{role} {rid} [{partner_role} {partner_id}]: {msg}")
    else:
        print(f"{role} {rid} []: {msg}")


def teller_thread(tid):
    global tellers_ready, processed_count

    # Teller startup
    out("Teller", tid, msg="ready")
    state_lock.acquire()
    tellers_ready += 1
    is_last = (tellers_ready == NUM_TELLERS)
    state_lock.release()

    # Last teller opens the bank for all customers
    if is_last:
        for _ in range(NUM_CUSTOMERS):
            arrival_gate.release()

    # Main service loop
    while True:
        queue_ready.acquire()   # wait for a customer to be queued or wakeup to exit

        # If everyone processed and no customers queued, exit
        state_lock.acquire()
        if processed_count >= NUM_CUSTOMERS and not customer_line:
            state_lock.release()
            break
        # If no customer now, continue
        if not customer_line:
            state_lock.release()
            continue
        cid = customer_line.popleft()
        assigned_customer[cid] = tid
        state_lock.release()

        out("Teller", tid, "Customer", cid, "calling customer")
        out("Teller", tid, "Customer", cid, "requesting transaction type")

        # Ask for transaction type
        ask_type[cid].release()

        # Wait for customer response
        recv_type[cid].acquire()
        choice = transaction_choice.get(cid, "deposit")
        out("Teller", tid, "Customer", cid, f"received {choice}")

        # If withdraw, talk to manager
        if choice == "withdraw":
            out("Teller", tid, "Manager", 0, "going to manager")
            manager_access.acquire()
            out("Teller", tid, "Manager", 0, "using manager")
            time.sleep(random.randint(5, 30) / 1000.0)
            out("Teller", tid, "Manager", 0, "done with manager")
            manager_access.release()
        else:
            out("Teller", tid, msg="processing deposit")

        # Use safe (vault)
        out("Teller", tid, msg="going to safe")
        vault_access.acquire()
        out("Teller", tid, "Safe", "", "using safe")
        time.sleep(random.randint(10, 50) / 1000.0)
        out("Teller", tid, "Safe", "", "done with safe")
        vault_access.release()

        # Complete transaction, signal customer
        out("Teller", tid, "Customer", cid, "transaction complete")
        finish_signal[cid].release()

        # Wait a tiny bit (simulate finalization) then count
        time.sleep(0)  # yield

        state_lock.acquire()
        processed_count += 1
        state_lock.release()

    out("Teller", tid, msg="no more customers, exiting")


def customer_thread(cid):
    # Start: wait until the bank opens
    out("Customer", cid, msg="waiting for bank to open")
    arrival_gate.acquire()

    # Try to enter the lobby (max 2)
    out("Customer", cid, msg="entering lobby")
    lobby_limit.acquire()

    # Join the queue
    state_lock.acquire()
    customer_line.append(cid)
    out("Customer", cid, msg="queued")
    queue_ready.release()
    state_lock.release()

    # Wait until teller asks for transaction type
    ask_type[cid].acquire()
    out("Customer", cid, msg="choosing transaction")

    # Choose transaction (random)
    choice = random.choice(["deposit", "withdraw"])
    transaction_choice[cid] = choice
    out("Customer", cid, f"Teller", assigned_customer.get(cid, ""), f"tells transaction: {choice}")
    recv_type[cid].release()

    # Wait for teller to finish the transaction
    finish_signal[cid].acquire()
    out("Customer", cid, msg="transaction finished")

    # Leave lobby and free spot
    out("Customer", cid, msg="exiting the bank")
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

    # Start customers
    customers = [threading.Thread(target=customer_thread, args=(c,)) for c in range(NUM_CUSTOMERS)]
    for c in customers:
        c.start()
        time.sleep(0.001)  # small stagger to avoid extreme contention

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
