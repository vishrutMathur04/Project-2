# Session 1 — Nov 15, 6:35 PM
Goal: Understand project & create initial structure

I spent this session rereading the PDF carefully. The project is similar to the first one (Driver + Logger + Encryptor), but more complex since it requires multiple independent interactions using only semaphores. I decided to keep the project in one Python file (bank.py) but organize the code differently than before.

Created the GitHub repo, added the Devlog, and made the basic file with constants and imports.

# Session 2 - Nov 15, 6:50 PM
After reviewing the project description again, I now understand how the tellers, customers, and manager need to synchronize using semaphores. The structure is becoming clearer: I need global semaphores for capacity control, shared queues for the line, and per-customer semaphores for handshakes.

Plan for this session:

Define all semaphores required by the project.

Create shared data structures that will hold customer state.

Set up the basic global variables that will be used across threads.

Commit the devlog before coding, then commit the code after finishing.

# Session 3 - Nov 16, 1:30 PM
The overall flow of the program is beginning to make sense: tellers must all report ready before customers begin. Since prints must follow a specific format, adding a helper function now will keep the rest consistent.

Plan for this session:

Add the formatted output function.

Create empty teller and customer thread functions.

Get the structural foundation ready for later functionality.

Commit both devlog and code.

# Session 4 - Nov 16, 1:47 PM



The next requirement is that all tellers must announce readiness before any customer can proceed. This means I need a shared counter protected by a lock and a semaphore to release customers once the bank is open.

Plan for this session:

Implement teller startup announcements.

Update the shared counter safely.

Allow the last teller to release all waiting customers.

Commit devlog and code.

# Session 5 - Nov 16, 3:24 PM

Now that tellers announce readiness and open the bank, the next step is customer arrival. Customers must wait for the bank to open before entering the lobby.

Plan for this session:

Make customers wait on arrival_gate

After release, allow customers to attempt entering the lobby 

# Session 6 - Nov 16, 3:50 PM

Customers need to enter a shared queue so tellers can pull from it later.

Plan for this session:

Implement queue insertion under a protected critical section

Signal tellers via a semaphore that a new customer is ready

Commit appropriately

# Session 7 - Nov 16, 4:45 PM

The teller must block until a customer is ready in the queue.

Plan for this session:

Implement teller waiting on queue_ready

Pull customer ID safely

Commit before/after coding

# Session 8 - Nov 16, 5:00 PM
The teller must ask what transaction the customer wants, and the customer must reply through dedicated semaphores.

Plan for this session:

Add per-customer semaphores for ask/response

Teller triggers ask → customer responds

Commit devlog and code

# Session 9 - Nov 16, 5:11 PM

Withdrawals require manager approval, so both teller and customer behavior must branch depending on the transaction type.

Plan for this session:

Implement conditional branch for withdrawals

Add manager semaphore usage

Add printed messages

Commit code after completion

# Session 10 - Nov 16, 6:00 PM

After completing the transaction, tellers must notify customers that they are finished.

Plan for this session:

Add “finished” signal from teller

Customer waits on finish signal

Commit after coding

