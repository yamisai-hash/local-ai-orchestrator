# run_scheduler_once.py -- evaluate lanes once and print which would run.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from scheduler import Scheduler

def main():
    sched = Scheduler.from_config(os.path.join(os.path.dirname(__file__), "..", "configs", "lanes.example.yaml"))
    for decision in sched.evaluate_once():
        print(f"{decision['lane']:>14}: {'RUN' if decision['eligible'] else 'skip':>4}  ({decision['reason']})")

if __name__ == "__main__":
    main()
