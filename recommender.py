"""
recommender.py
═════════════════════════════════════════════════
  TEAM MEMBER 3 - Parth — Recommendation Engine + Menu
  Contains: RecommendationSystem class

  Advanced Python features used here:
    • @staticmethod decorator         (3.8)
    • generator  — unseen_movies_gen  (3.8)
    • filter()   — genre filtering    (3.8)
    • map()      — building ID sets   (3.8)
    • lambda     — sort keys          (3.8)
    • tuple      — (score, name) pair (3.3)
═════════════════════════════════════════════════
"""

from data_manager import DataManager
from models import Movie, RegularUser, Admin


# ══════════════════════════════════════════════════
#  CLASS: RecommendationSystem
#  The main engine — runs the menu, handles all
#  features, calculates similarity & recommendations.
# ══════════════════════════════════════════════════

class RecommendationSystem:

    def __init__(self):
        self.db = DataManager()   # composition: uses DataManager to access data

    # ── DECORATOR: @staticmethod ──────────────────
    # Justification: jaccard_similarity does NOT need 'self' —
    # it only works on two User objects passed in. Marking it
    # @staticmethod makes the design intent explicit and lets
    # callers invoke it as RecommendationSystem.jaccard_similarity(a, b).
    @staticmethod
    def jaccard_similarity(user_a, user_b):
        """
        Jaccard Similarity = |A ∩ B| / |A ∪ B|
        Compares two User objects by their liked movie sets.
        Returns a float score: 0.0 (nothing in common) → 1.0 (identical taste)

        Algorithm choice: sets give O(1) membership tests.
        Intersection + union via set operators avoids O(n²) nested loops.
        """
        # map() converts liked_items lists → set of IDs without a manual loop
        set_a = set(map(lambda x: x, user_a.liked_items))
        set_b = set(map(lambda x: x, user_b.liked_items))

        intersection = set_a & set_b   # movies BOTH users liked
        union        = set_a | set_b   # ALL movies between them

        if not union:
            return 0.0
        return round(len(intersection) / len(union), 2)

    # ── GENERATOR: yields unseen movies one at a time ─
    # Justification: a generator is memory-efficient — it does NOT
    # build a full list upfront. For large catalogs this matters.
    @staticmethod
    def unseen_movies_gen(user, all_movies):
        """
        Generator that yields Movie objects the user has NOT seen yet.
        Uses 'yield' so movies are produced one at a time (lazy evaluation),
        saving memory compared to building a full list first.
        """
        seen_set = set(user.liked_items)   # O(1) lookup per check
        for movie in all_movies:
            if movie.id not in seen_set:
                yield movie                # yield instead of return → generator

    # ── Core Recommendation Logic ─────────────────

    def get_recommendations(self, target_user, all_users, all_movies,
                            genre_filter=None, top_n=3):
        """
        Steps:
        1. Compare target user with every other user (Jaccard similarity)
        2. Collect movies similar users liked but target hasn't seen
        3. Apply genre filter using filter() if given
        4. If genre filter gives 0 results → fallback to top-rated in that genre
        5. Return top N results sorted by similarity (lambda sort key)
        """
        # Dict lookup: O(1) per movie fetch — much better than O(n) list scan
        movies_dict     = {m.id: m for m in all_movies}

        # Dict of movie_id → tuple(score, recommended_by_name)
        # Tuple chosen here: score+name are always read together, never mutated
        recommendations = {}

        # Step 1 & 2: Find similar users and collect their unseen movies
        for other_user in all_users:
            if other_user.user_id == target_user.user_id:
                continue   # skip self-comparison

            score = RecommendationSystem.jaccard_similarity(target_user, other_user)
            if score == 0:
                continue   # nothing in common — not useful

            # filter() keeps only IDs the target hasn't seen
            unseen_ids = filter(
                lambda mid: not target_user.has_seen(mid),
                other_user.liked_items
            )

            for movie_id in unseen_ids:
                # Store as tuple(score, name) — immutable pair
                existing = recommendations.get(movie_id)
                if existing is None or score > existing[0]:
                    recommendations[movie_id] = (score, other_user.name)

        # Step 3: Build result list
        results = []
        for movie_id, rec_tuple in recommendations.items():
            score, rec_by = rec_tuple          # unpack the tuple
            movie = movies_dict.get(movie_id)
            if not movie:
                continue

            # filter by genre if requested
            if genre_filter and movie.genre != genre_filter.lower():
                continue

            results.append({
                "movie":          movie,
                "similarity":     score,
                "recommended_by": rec_by,
                "source":         "similarity"
            })

        # lambda as sort key — sort by similarity score descending
        results.sort(key=lambda x: x["similarity"], reverse=True)

        # Step 4: FALLBACK — if genre filter returned nothing, suggest
        # top-rated unseen movies in that genre using the generator
        if genre_filter and len(results) == 0:
            # Use the generator to get unseen movies (lazy, memory-efficient)
            unseen = list(self.unseen_movies_gen(target_user, all_movies))

            # filter() picks only movies in the requested genre
            genre_unseen = list(filter(
                lambda m: m.genre == genre_filter.lower(),
                unseen
            ))

            # lambda sort key: sort by rating descending
            genre_unseen.sort(key=lambda m: m.rating, reverse=True)

            fallback = [
                {
                    "movie":          m,
                    "similarity":     0.0,
                    "recommended_by": "Top-rated pick (no similar user data)",
                    "source":         "fallback"
                }
                for m in genre_unseen[:top_n]
            ]
            return fallback

        return results[:top_n]

    # ── Display Helpers ───────────────────────────

    def print_header(self, text):
        print("\n" + "═" * 52)
        print(f"  {text}")
        print("═" * 52)

    def print_recommendation(self, index, rec):
        movie = rec["movie"]
        print(f"\n  #{index}  {movie.title}  ({movie.year})")
        print(f"       Genre      : {movie.genre}")
        print(f"       IMDb Rating: {movie.rating}")
        if rec["source"] == "fallback":
            print(f"       Why        : 📊 {rec['recommended_by']}")
        else:
            print(f"       Why        : {rec['recommended_by']} liked it  [similarity: {rec['similarity']}]")

    # ── Feature 1: Get Recommendations ───────────

    def feature_get_recommendations(self):
        self.print_header("Get Recommendations")
        users  = self.db.load_users()
        movies = self.db.load_movies()

        user_id_input = input("\n  Enter User ID: ").strip()
        if not user_id_input.isdigit():
            print("  ❌ Invalid ID. Please enter a number.")
            return

        target_user = next((u for u in users if u.user_id == int(user_id_input)), None)
        if not target_user:
            print(f"  ❌ No user found with ID {user_id_input}.")
            return

        all_genres  = sorted(set(m.genre for m in movies))
        print(f"\n  Available genres: {', '.join(all_genres)}")
        genre_input  = input("  Filter by genre? (press Enter to skip): ").strip().lower()
        genre_filter = genre_input if genre_input else None

        top_n_input = input("  How many recommendations? (default 3): ").strip()
        top_n = int(top_n_input) if top_n_input.isdigit() else 3

        self.print_header(f"Recommendations for {target_user.name}")
        liked_titles = [m for m in target_user.liked_items]
        print(f"  Movies already liked: {', '.join(liked_titles)}")
        if genre_filter:
            print(f"  Genre filter applied: {genre_filter}")

        recs = self.get_recommendations(target_user, users, movies, genre_filter, top_n)

        if not recs:
            print("\n  😕 No recommendations found. Add more users or movies!")
        else:
            for i, rec in enumerate(recs, 1):
                self.print_recommendation(i, rec)

    # ── Feature 2: View All Users ─────────────────

    def feature_view_all_users(self):
        self.print_header("All Registered Users")
        users  = self.db.load_users()
        movies = self.db.load_movies()

        if not users:
            print("  No users found.")
            return

        movies_dict = {m.id: m for m in movies}
        for user in users:
            # Polymorphism: display() behaves differently for Admin vs RegularUser
            user.display(movies_dict)

    # ── Feature 3: Add New User ───────────────────

    def feature_add_user(self):
        self.print_header("Add New User")
        users  = self.db.load_users()
        movies = self.db.load_movies()

        new_id = self.db.get_next_user_id(users)
        print(f"  New User ID will be: {new_id}")

        name = input("  Enter name: ").strip()
        if not name:
            print("  ❌ Name cannot be empty.")
            return

        role_input = input("  Role — (1) Regular User  (2) Admin  [default: 1]: ").strip()

        print("\n  Available movies:")
        for movie in movies:
            movie.display()

        liked_input = input("\n  Enter liked movie IDs (comma separated): ").strip()
        liked_ids   = [x.strip() for x in liked_input.split(",") if x.strip()]

        valid_ids   = {m.id for m in movies}
        invalid_ids = [lid for lid in liked_ids if lid not in valid_ids]
        if invalid_ids:
            print(f"  ⚠️  Unknown IDs ignored: {', '.join(invalid_ids)}")
            liked_ids = [lid for lid in liked_ids if lid in valid_ids]

        all_genres       = sorted(set(m.genre for m in movies))
        print(f"\n  Available genres: {', '.join(all_genres)}")
        genres_input     = input("  Enter preferred genres (comma separated): ").strip()
        preferred_genres = [g.strip().lower() for g in genres_input.split(",") if g.strip()]

        # Instantiate the correct subclass based on role choice
        if role_input == "2":
            new_user = Admin(new_id, name, liked_ids, preferred_genres)
        else:
            new_user = RegularUser(new_id, name, liked_ids, preferred_genres)

        users.append(new_user)
        self.db.save_users(users)
        print(f"\n  ✅ {new_user.role.capitalize()} '{name}' added with ID {new_id}!")

    # ── Feature 4: Add Liked Movie to User ────────

    def feature_add_liked_item(self):
        self.print_header("Add Liked Movie to User")
        users  = self.db.load_users()
        movies = self.db.load_movies()

        user_id_input = input("\n  Enter User ID: ").strip()
        if not user_id_input.isdigit():
            print("  ❌ Invalid ID.")
            return

        target_user = next((u for u in users if u.user_id == int(user_id_input)), None)
        if not target_user:
            print(f"  ❌ User ID {user_id_input} not found.")
            return

        print(f"\n  Current likes: {', '.join(target_user.liked_items)}")
        print("\n  Available movies:")
        for movie in movies:
            status = "✅" if target_user.has_seen(movie.id) else "  "
            print(f"    {status} [{movie.id}]  {movie.title}  ({movie.genre})")

        movie_id  = input("\n  Enter movie ID to add: ").strip()
        valid_ids = {m.id for m in movies}

        if movie_id not in valid_ids:
            print("  ❌ Invalid movie ID.")
            return

        added = target_user.add_liked_item(movie_id)
        if added:
            self.db.save_users(users)
            print(f"  ✅ Added '{movie_id}' to {target_user.name}'s liked list!")
        else:
            print("  ⚠️  Already in liked list!")

    # ── Feature 5: Browse by Genre ────────────────

    def feature_browse_by_genre(self):
        self.print_header("Browse Movies by Genre")
        movies = self.db.load_movies()

        all_genres = sorted(set(m.genre for m in movies))
        print(f"\n  Available genres: {', '.join(all_genres)}")
        genre = input("  Enter genre: ").strip().lower()

        # filter() — keeps only movies matching the requested genre
        filtered = list(filter(lambda m: m.genre == genre, movies))

        if not filtered:
            print(f"  ❌ No movies found for genre '{genre}'.")
            return

        print(f"\n  Movies in genre '{genre}':")
        for movie in filtered:
            movie.display()

    # ── Feature 6: Add New Movie ──────────────────

    def feature_add_movie(self):
        self.print_header("Add New Movie")
        movies = self.db.load_movies()
        new_id = self.db.get_next_movie_id(movies)
        print(f"  New Movie ID will be: {new_id}")

        title = input("  Movie title: ").strip()
        if not title:
            print("  ❌ Title cannot be empty.")
            return

        all_genres = ["action", "comedy", "drama", "thriller", "romance", "horror", "sci-fi"]
        print(f"  Genres: {', '.join(all_genres)}")
        genre = input("  Genre: ").strip().lower()

        year_input = input("  Release year: ").strip()
        year       = int(year_input) if year_input.isdigit() else 2024

        rating_input = input("  IMDb rating (e.g. 8.5): ").strip()
        try:
            rating = float(rating_input)
        except ValueError:
            rating = 0.0

        new_movie = Movie(new_id, title, genre, year, rating)
        movies.append(new_movie)
        self.db.save_movies(movies)
        print(f"\n  ✅ Movie '{title}' added with ID {new_id}!")

    # ── Feature 7: Compare Two Users ─────────────

    def feature_compare_users(self):
        self.print_header("Compare Two Users")
        users = self.db.load_users()

        print("\n  Users:")
        for u in users:
            print(f"    [{u.user_id}] {u.name}  ({u.role})")

        id1 = input("\n  Enter first User ID : ").strip()
        id2 = input("  Enter second User ID: ").strip()

        if not id1.isdigit() or not id2.isdigit():
            print("  ❌ Please enter valid numeric IDs.")
            return

        user1 = next((u for u in users if u.user_id == int(id1)), None)
        user2 = next((u for u in users if u.user_id == int(id2)), None)

        if not user1 or not user2:
            print("  ❌ One or both users not found.")
            return

        common = set(user1.liked_items) & set(user2.liked_items)
        score  = RecommendationSystem.jaccard_similarity(user1, user2)

        print(f"\n  {user1.name} likes : {', '.join(user1.liked_items)}")
        print(f"  {user2.name} likes : {', '.join(user2.liked_items)}")
        print(f"\n  Common movies     : {', '.join(common) if common else 'None'}")
        print(f"  Similarity Score  : {score}  ", end="")
        if   score >= 0.5: print("🔥 Very Similar!")
        elif score >  0.0: print("🤝 Some overlap")
        else:              print("😶 Nothing in common")

    # ── Feature 8: List Unseen Movies (uses generator) ──

    def feature_unseen_movies(self):
        self.print_header("Browse Unseen Movies")
        users  = self.db.load_users()
        movies = self.db.load_movies()

        user_id_input = input("\n  Enter User ID: ").strip()
        if not user_id_input.isdigit():
            print("  ❌ Invalid ID.")
            return

        target_user = next((u for u in users if u.user_id == int(user_id_input)), None)
        if not target_user:
            print(f"  ❌ User ID {user_id_input} not found.")
            return

        print(f"\n  Unseen movies for {target_user.name}:")

        # Uses our generator — yields one movie at a time (memory-efficient)
        count = 0
        for movie in self.unseen_movies_gen(target_user, movies):
            movie.display()
            count += 1

        if count == 0:
            print("  🎉 You've seen everything in the catalog!")

    # ── Main Menu Loop ────────────────────────────

    def run(self):
        """Start the app — shows menu in a loop until user exits"""
        while True:
            print("\n")
            print("  ╔══════════════════════════════════════════╗")
            print("  ║     🎬  Movie Recommendation System      ║")
            print("  ╠══════════════════════════════════════════╣")
            print("  ║  1.  Get Recommendations                 ║")
            print("  ║  2.  View All Users                      ║")
            print("  ║  3.  Add New User                        ║")
            print("  ║  4.  Add a Liked Movie to User           ║")
            print("  ║  5.  Browse Movies by Genre              ║")
            print("  ║  6.  Add New Movie to Catalog            ║")
            print("  ║  7.  Compare Two Users (Similarity)      ║")
            print("  ║  8.  Browse Unseen Movies for User       ║")
            print("  ║  0.  Exit                                ║")
            print("  ╚══════════════════════════════════════════╝")

            choice = input("\n  Enter choice: ").strip()

            if   choice == "1": self.feature_get_recommendations()
            elif choice == "2": self.feature_view_all_users()
            elif choice == "3": self.feature_add_user()
            elif choice == "4": self.feature_add_liked_item()
            elif choice == "5": self.feature_browse_by_genre()
            elif choice == "6": self.feature_add_movie()
            elif choice == "7": self.feature_compare_users()
            elif choice == "8": self.feature_unseen_movies()
            elif choice == "0":
                print("\n  👋 Goodbye!\n")
                break
            else:
                print("  ❌ Invalid choice. Please enter 0–8.")
