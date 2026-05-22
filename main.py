"""
main.py
═════════════════════════════════════════════════
  ENTRY POINT — Run this file to start the app.
  Just imports the system and starts it.

  To run:  python main.py
═════════════════════════════════════════════════
"""

from data_manager import DataManager
from recommender import RecommendationSystem


if __name__ == "__main__":

    # Check minimum requirement: at least 2 users must exist
    db    = DataManager()
    users = db.load_users()

    if len(users) < 2:
        print("❌ Need at least 2 users in users.json to run!")
    else:
        app = RecommendationSystem()
        app.run()
