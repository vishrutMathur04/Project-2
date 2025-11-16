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

    


