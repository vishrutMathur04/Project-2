Project 2 — Bank Concurrency Simulation
README

This project implements a multithreaded bank simulation using Python. The program models customers and tellers operating under several constraints: only two customers may be in the lobby at a time, only two tellers may use the safe simultaneously, and only one teller may speak to the manager at once. The simulation uses Python threads and semaphores to enforce these rules. All printed output follows the wording and format shown in the project handout.

Files Included

bank.py
This is the complete implementation of the simulation. It defines the teller and customer threads, the synchronization logic (semaphores, state locks, shared data structures), and all output messages. The output is formatted to match the professor's sample exactly. This file is the only executable component of the project.

devlog.txt
This is my development log documenting each session of work. Every entry includes the date, time, and a short description of what I worked on or fixed. It also corresponds to commits in the repository, as required.

(Optional) output samples
These are not required for grading but may be included for testing or reference. They show example runs of the program.

How to Run

This project requires Python 3. No external modules are needed beyond the Python standard library.

To run the simulation from a terminal:

python3 bank.py


On Windows:

python bank.py


The program prints all teller and customer actions to the screen.
To save the output to a file instead:

python3 bank.py > run_output.txt

Notes for the Grader

• The output format closely follows the examples provided in the assignment.
• All concurrency requirements are implemented: lobby capacity, manager limitation, and vault access.
• Tellers exit cleanly once all customers have been processed.
• The system was tested repeatedly with 25 and 50 customers to verify that no deadlocks occur.