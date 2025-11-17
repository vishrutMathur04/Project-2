#!/usr/bin/env python3

import threading
import time
import random
from collections import deque

NUM_TELLERS = 3
NUM_CUSTOMERS = 50


# Concurrency controls
lobby_limit = threading.Semaphore(2)
vault_access = threading.Semaphore(2)
manager_access = threading.Semaphore(1)

# Synchronization for queueing and starting
arrival_gate = threading.Semaphore(0)
entry_lock = threading.Semaphore(1)

# Shared collections
customer_line = deque()
assigned_customer = {}
transaction_choice = {}

# Per-customer semaphores
ask_type = {}
recv_type = {}
finish_signal = {}
exit_signal = {}

# Counters
tellers_ready = 0
customers_done = 0

# Lock for modifying shared state
state_lock = threading.Semaphore(1)

def out(role, rid, partner_role="", partner_id=None, msg=""):
    if partner_role:
        print(f"{role} {rid} [{partner_role} {partner_id}]: {msg}")
    else:
        print(f"{role} {rid} []: {msg}")


def teller_thread(tid):
    out("Teller", tid, msg="initialized")
    # Detailed operations added later


def customer_thread(cid):
    out("Customer", cid, msg="started")
    # Detailed operations added later

def teller_thread(tid):
    global tellers_ready

    out("Teller", tid, msg="ready")

    state_lock.acquire()
    tellers_ready += 1
    last_one = (tellers_ready == NUM_TELLERS)
    state_lock.release()

    if last_one:
        for _ in range(NUM_CUSTOMERS):
            arrival_gate.release()

def customer_thread(cid):
    out("Customer", cid, msg="waiting for bank to open")

    arrival_gate.acquire()   # wait for tellers to finish startup

    out("Customer", cid, msg="entering lobby")
    lobby_limit.acquire()    # capacity limit

def customer_thread(cid):
    arrival_gate.acquire()
    lobby_limit.acquire()

    state_lock.acquire()
    customer_line.append(cid)
    out("Customer", cid, msg="queued")
    queue_ready.release()
    state_lock.release()

def teller_thread(tid):

    # existing startup code...

    while True:
        queue_ready.acquire()

        state_lock.acquire()
        if not customer_line:
            state_lock.release()
            continue
        cid = customer_line.popleft()
        state_lock.release()

        out("Teller", tid, "Customer", cid, "calling customer")
        assigned_customer[cid] = tid

        # next: handshake asking for transaction type

def teller_thread(tid):

    # after retrieving cid...

    out("Teller", tid, "Customer", cid, "requesting transaction type")
    ask_type[cid].release()     # ask customer

    recv_type[cid].acquire()    # wait for response
    choice = transaction_choice[cid]
    out("Teller", tid, "Customer", cid, f"received {choice}")


def customer_thread(cid):
    ask_type[cid].acquire()
    out("Customer", cid, msg="choosing transaction")

    # default choice for now (“deposit”)
    transaction_choice[cid] = "deposit"
    recv_type[cid].release()

def teller_thread(tid):
    # after receiving choice...
    if choice == "withdraw":
        manager_access.acquire()
        out("Teller", tid, "Manager", 0, "processing withdrawal")
        manager_access.release()
    else:
        out("Teller", tid, msg="processing deposit")

def teller_thread(tid):
    # after processing...
    finish_signal[cid].release()
    out("Teller", tid, "Customer", cid, "transaction complete")

def customer_thread(cid):
    finish_signal[cid].acquire()
    out("Customer", cid, msg="transaction finished")

def customer_thread(cid):
    # ... previous code ...

    finish_signal[cid].acquire()  
    out("Customer", cid, msg="exiting the bank")

    lobby_limit.release()    # free lobby space

def teller_thread(tid):
    global processed_count

    while True:
        queue_ready.acquire()

        state_lock.acquire()
        if processed_count == NUM_CUSTOMERS:
            state_lock.release()
            break
        if not customer_line:
            state_lock.release()
            continue

        cid = customer_line.popleft()
        state_lock.release()

        # ... service logic ...

        state_lock.acquire()
        processed_count += 1
        state_lock.release()

def main():
    for cid in range(NUM_CUSTOMERS):
        ask_type[cid] = threading.Semaphore(0)
        recv_type[cid] = threading.Semaphore(0)
        finish_signal[cid] = threading.Semaphore(0)

    tellers = [threading.Thread(target=teller_thread, args=(t,)) 
               for t in range(NUM_TELLERS)]
    customers = [threading.Thread(target=customer_thread, args=(c,))
                 for c in range(NUM_CUSTOMERS)]

    for t in tellers: t.start()
    for c in customers: c.start()

    for c in customers: c.join()
    for t in tellers: t.join()

    print("Bank closed for the day.")




    


