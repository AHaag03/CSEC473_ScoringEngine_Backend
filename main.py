import time
from scoring_engine import ScoringEngine

def main():
    engine = ScoringEngine()
    while True:
        engine.run_once()
        print("Current scores:", engine.get_scores())
        time.sleep(engine.poll_interval)

if __name__ == "__main__":
    main()
