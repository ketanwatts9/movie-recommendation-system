"""
tests.py
═════════════════════════════════════════════════
  Unit Tests — Movie Recommendation System
  Uses Python's built-in unittest module.

  Tests cover:
    • Movie class
    • User base class + RegularUser + Admin (inheritance)
    • Jaccard similarity (normal + edge cases)
    • Generator (unseen_movies_gen)
    • DataManager (load/save round-trip)
    • Recommendation logic (with and without genre filter)
═════════════════════════════════════════════════

  To run:   python tests.py
  Or:       python -m unittest tests
═════════════════════════════════════════════════
"""

import unittest
import json
import os
import tempfile

from models       import Movie, User, RegularUser, Admin
from data_manager import DataManager
from recommender  import RecommendationSystem


# ══════════════════════════════════════════════════
#  TEST SUITE 1: Movie class
# ══════════════════════════════════════════════════

class TestMovie(unittest.TestCase):

    def setUp(self):
        """Create a reusable Movie object for each test."""
        self.movie = Movie("movie1", "The Dark Knight", "Action", 2008, 9.0)

    def test_genre_lowercased(self):
        """Genre should always be stored in lowercase."""
        self.assertEqual(self.movie.genre, "action")

    def test_genre_year_tuple(self):
        """genre_year attribute must be a tuple of (genre, year)."""
        self.assertIsInstance(self.movie.genre_year, tuple)
        self.assertEqual(self.movie.genre_year, ("action", 2008))

    def test_to_dict_keys(self):
        """to_dict() must return all required keys."""
        d = self.movie.to_dict()
        for key in ["id", "title", "genre", "year", "rating"]:
            self.assertIn(key, d)

    def test_to_dict_values(self):
        """to_dict() values must match the original data."""
        d = self.movie.to_dict()
        self.assertEqual(d["id"],     "movie1")
        self.assertEqual(d["title"],  "The Dark Knight")
        self.assertEqual(d["genre"],  "action")
        self.assertEqual(d["year"],   2008)
        self.assertEqual(d["rating"], 9.0)

    def test_repr(self):
        """__repr__ must contain the movie id and title."""
        r = repr(self.movie)
        self.assertIn("movie1", r)
        self.assertIn("The Dark Knight", r)


# ══════════════════════════════════════════════════
#  TEST SUITE 2: User, RegularUser, Admin (OOP)
# ══════════════════════════════════════════════════

class TestUserOOP(unittest.TestCase):

    def test_regular_user_role(self):
        """RegularUser must have role == 'regular'."""
        u = RegularUser(1, "Alice")
        self.assertEqual(u.role, "regular")

    def test_admin_role(self):
        """Admin must have role == 'admin'."""
        a = Admin(2, "Bob")
        self.assertEqual(a.role, "admin")

    def test_admin_can_manage(self):
        """Admin.can_manage() must return True."""
        a = Admin(2, "Bob")
        self.assertTrue(a.can_manage())

    def test_role_is_readonly(self):
        """role property must be read-only (encapsulation)."""
        u = RegularUser(1, "Alice")
        with self.assertRaises(AttributeError):
            u.role = "admin"   # should raise — it's a property with no setter

    def test_inheritance_has_seen(self):
        """RegularUser inherits has_seen() from User."""
        u = RegularUser(1, "Alice", liked_items=["movie1"])
        self.assertTrue(u.has_seen("movie1"))
        self.assertFalse(u.has_seen("movie99"))

    def test_inheritance_admin_has_seen(self):
        """Admin also inherits has_seen() from User."""
        a = Admin(2, "Bob", liked_items=["movie3"])
        self.assertTrue(a.has_seen("movie3"))

    def test_add_liked_item_new(self):
        """add_liked_item() returns True when the movie is new."""
        u = RegularUser(1, "Alice")
        result = u.add_liked_item("movie5")
        self.assertTrue(result)
        self.assertIn("movie5", u.liked_items)

    def test_add_liked_item_duplicate(self):
        """add_liked_item() returns False when movie already liked."""
        u = RegularUser(1, "Alice", liked_items=["movie1"])
        result = u.add_liked_item("movie1")
        self.assertFalse(result)
        self.assertEqual(u.liked_items.count("movie1"), 1)   # still only once

    def test_polymorphism_display_type(self):
        """Both RegularUser and Admin must have a display() method (polymorphism)."""
        u = RegularUser(1, "Alice")
        a = Admin(2, "Bob")
        # Both should have the method — polymorphism means same interface
        self.assertTrue(hasattr(u, "display"))
        self.assertTrue(hasattr(a, "display"))
        # They must be different implementations
        self.assertNotEqual(type(u).display, type(a).display)

    def test_regular_user_to_dict(self):
        """RegularUser.to_dict() must include the role field."""
        u = RegularUser(1, "Alice", ["movie1"], ["action"])
        d = u.to_dict()
        self.assertEqual(d["role"], "regular")
        self.assertEqual(d["name"], "Alice")

    def test_admin_to_dict_has_can_manage(self):
        """Admin.to_dict() must include the can_manage field."""
        a = Admin(2, "Bob")
        d = a.to_dict()
        self.assertIn("can_manage", d)
        self.assertTrue(d["can_manage"])


# ══════════════════════════════════════════════════
#  TEST SUITE 3: Jaccard Similarity
# ══════════════════════════════════════════════════

class TestJaccardSimilarity(unittest.TestCase):

    def test_identical_taste(self):
        """Users with identical liked lists → score of 1.0."""
        a = RegularUser(1, "Alice", ["m1", "m2", "m3"])
        b = RegularUser(2, "Bob",   ["m1", "m2", "m3"])
        self.assertEqual(RecommendationSystem.jaccard_similarity(a, b), 1.0)

    def test_no_overlap(self):
        """Users with no common movies → score of 0.0."""
        a = RegularUser(1, "Alice", ["m1", "m2"])
        b = RegularUser(2, "Bob",   ["m3", "m4"])
        self.assertEqual(RecommendationSystem.jaccard_similarity(a, b), 0.0)

    def test_partial_overlap(self):
        """Alice has m1,m2,m3 — Bob has m2,m3,m4. Intersection=2, Union=4 → 0.5."""
        a = RegularUser(1, "Alice", ["m1", "m2", "m3"])
        b = RegularUser(2, "Bob",   ["m2", "m3", "m4"])
        self.assertEqual(RecommendationSystem.jaccard_similarity(a, b), 0.5)

    def test_empty_both(self):
        """Both users have no liked items → 0.0 (no division by zero)."""
        a = RegularUser(1, "Alice", [])
        b = RegularUser(2, "Bob",   [])
        self.assertEqual(RecommendationSystem.jaccard_similarity(a, b), 0.0)

    def test_empty_one_side(self):
        """One empty, one not → 0.0."""
        a = RegularUser(1, "Alice", [])
        b = RegularUser(2, "Bob",   ["m1", "m2"])
        self.assertEqual(RecommendationSystem.jaccard_similarity(a, b), 0.0)

    def test_score_range(self):
        """Score must always be between 0.0 and 1.0."""
        a = RegularUser(1, "Alice", ["m1", "m2"])
        b = RegularUser(2, "Bob",   ["m2", "m3"])
        score = RecommendationSystem.jaccard_similarity(a, b)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_static_method_callable_without_instance(self):
        """jaccard_similarity must be callable as a static method."""
        a = RegularUser(1, "Alice", ["m1"])
        b = RegularUser(2, "Bob",   ["m1"])
        # Call without creating a RecommendationSystem instance
        score = RecommendationSystem.jaccard_similarity(a, b)
        self.assertEqual(score, 1.0)


# ══════════════════════════════════════════════════
#  TEST SUITE 4: Generator (unseen_movies_gen)
# ══════════════════════════════════════════════════

class TestUnseenMoviesGenerator(unittest.TestCase):

    def setUp(self):
        self.movies = [
            Movie("m1", "Film A", "action", 2020, 7.0),
            Movie("m2", "Film B", "drama",  2021, 8.0),
            Movie("m3", "Film C", "comedy", 2022, 7.5),
        ]

    def test_generator_returns_unseen(self):
        """Generator must skip movies the user already liked."""
        user = RegularUser(1, "Alice", liked_items=["m1"])
        unseen = list(RecommendationSystem.unseen_movies_gen(user, self.movies))
        ids = [m.id for m in unseen]
        self.assertNotIn("m1", ids)
        self.assertIn("m2", ids)
        self.assertIn("m3", ids)

    def test_generator_all_seen(self):
        """If user has seen everything, generator yields nothing."""
        user = RegularUser(1, "Alice", liked_items=["m1", "m2", "m3"])
        unseen = list(RecommendationSystem.unseen_movies_gen(user, self.movies))
        self.assertEqual(unseen, [])

    def test_generator_none_seen(self):
        """If user has seen nothing, generator yields all movies."""
        user = RegularUser(1, "Alice", liked_items=[])
        unseen = list(RecommendationSystem.unseen_movies_gen(user, self.movies))
        self.assertEqual(len(unseen), 3)

    def test_generator_is_lazy(self):
        """unseen_movies_gen must return a generator object, not a list."""
        import types
        user = RegularUser(1, "Alice", liked_items=[])
        gen = RecommendationSystem.unseen_movies_gen(user, self.movies)
        self.assertIsInstance(gen, types.GeneratorType)


# ══════════════════════════════════════════════════
#  TEST SUITE 5: DataManager (file I/O)
# ══════════════════════════════════════════════════

class TestDataManager(unittest.TestCase):

    def setUp(self):
        """Use temporary files so tests don't touch real data."""
        self.tmp_users = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        self.tmp_items = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )

        # Write minimal valid JSON to both temp files
        json.dump([
            {"user_id": 1, "name": "Alice", "liked_items": ["m1"],
             "preferred_genres": ["action"], "role": "regular"},
            {"user_id": 2, "name": "Bob",   "liked_items": ["m2"],
             "preferred_genres": ["drama"],  "role": "admin"},
        ], self.tmp_users)

        json.dump([
            {"id": "m1", "title": "Film A", "genre": "action", "year": 2020, "rating": 7.0},
            {"id": "m2", "title": "Film B", "genre": "drama",  "year": 2021, "rating": 8.5},
        ], self.tmp_items)

        self.tmp_users.close()
        self.tmp_items.close()

        self.dm = DataManager(
            users_file=self.tmp_users.name,
            items_file=self.tmp_items.name
        )

    def tearDown(self):
        """Delete temp files after each test."""
        os.unlink(self.tmp_users.name)
        os.unlink(self.tmp_items.name)

    def test_load_users_count(self):
        """load_users() must return the correct number of users."""
        users = self.dm.load_users()
        self.assertEqual(len(users), 2)

    def test_load_users_correct_subclass(self):
        """load_users() must create Admin for role='admin', RegularUser otherwise."""
        users = self.dm.load_users()
        roles = {u.name: type(u).__name__ for u in users}
        self.assertEqual(roles["Alice"], "RegularUser")
        self.assertEqual(roles["Bob"],   "Admin")

    def test_load_movies_count(self):
        """load_movies() must return the correct number of movies."""
        movies = self.dm.load_movies()
        self.assertEqual(len(movies), 2)

    def test_save_and_reload_users(self):
        """Users saved then reloaded must preserve name and liked_items."""
        users = self.dm.load_users()
        users[0].add_liked_item("m2")
        self.dm.save_users(users)

        reloaded = self.dm.load_users()
        alice = next(u for u in reloaded if u.name == "Alice")
        self.assertIn("m2", alice.liked_items)

    def test_get_next_user_id(self):
        """get_next_user_id() must return max existing ID + 1."""
        users = self.dm.load_users()
        next_id = self.dm.get_next_user_id(users)
        self.assertEqual(next_id, 3)

    def test_get_next_movie_id(self):
        """get_next_movie_id() must return the next sequential movie ID."""
        movies = [
            Movie("movie1", "A", "drama"),
            Movie("movie2", "B", "action"),
        ]
        next_id = self.dm.get_next_movie_id(movies)
        self.assertEqual(next_id, "movie3")

    def test_get_next_user_id_empty(self):
        """get_next_user_id() on empty list must return 1."""
        self.assertEqual(self.dm.get_next_user_id([]), 1)


# ══════════════════════════════════════════════════
#  TEST SUITE 6: Recommendation Logic
# ══════════════════════════════════════════════════

class TestRecommendations(unittest.TestCase):

    def setUp(self):
        self.engine = RecommendationSystem()

        self.movies = [
            Movie("m1", "Dark Knight",   "action",  2008, 9.0),
            Movie("m2", "Superbad",      "comedy",  2007, 7.6),
            Movie("m3", "The Godfather", "drama",   1972, 9.2),
            Movie("m4", "Avengers",      "action",  2012, 8.0),
            Movie("m5", "Inception",     "thriller",2010, 8.8),
        ]

        self.alice = RegularUser(1, "Alice", ["m1", "m2"])
        self.bob   = RegularUser(2, "Bob",   ["m2", "m3", "m4"])
        self.carol = RegularUser(3, "Carol", ["m1", "m5"])
        self.users = [self.alice, self.bob, self.carol]

    def test_basic_recommendations(self):
        """Alice should get recommendations from similar users."""
        recs = self.engine.get_recommendations(self.alice, self.users, self.movies)
        self.assertGreater(len(recs), 0)

    def test_no_self_recommendations(self):
        """Recommended movies must not include ones Alice already liked."""
        recs = self.engine.get_recommendations(self.alice, self.users, self.movies)
        rec_ids = [r["movie"].id for r in recs]
        for rid in rec_ids:
            self.assertNotIn(rid, self.alice.liked_items)

    def test_genre_filter_applied(self):
        """All results must match the requested genre when filter is set."""
        recs = self.engine.get_recommendations(
            self.alice, self.users, self.movies, genre_filter="drama"
        )
        for rec in recs:
            self.assertEqual(rec["movie"].genre, "drama")

    def test_top_n_respected(self):
        """Result count must not exceed top_n."""
        recs = self.engine.get_recommendations(
            self.alice, self.users, self.movies, top_n=1
        )
        self.assertLessEqual(len(recs), 1)

    def test_fallback_fires_when_no_similar_user_for_genre(self):
        """Fallback must activate when genre filter finds nothing via similarity."""
        # Alice only shares movies with Bob/Carol in action/comedy.
        # Ask for 'thriller' — no similar user has thriller → fallback.
        loner = RegularUser(1, "Loner", ["m1"])
        others = [RegularUser(2, "X", ["m2"]), RegularUser(3, "Y", ["m3"])]
        recs = self.engine.get_recommendations(
            loner, [loner] + others, self.movies, genre_filter="thriller"
        )
        # Should still get results from fallback (top-rated thriller = m5 Inception)
        self.assertGreater(len(recs), 0)
        for rec in recs:
            self.assertEqual(rec["source"], "fallback")

    def test_no_recommendations_for_isolated_user(self):
        """User with no overlap with anyone should get 0 similarity results (before fallback)."""
        island = RegularUser(99, "Island", ["m5"])
        others = [RegularUser(1, "A", ["m1"]), RegularUser(2, "B", ["m2"])]
        recs = self.engine.get_recommendations(island, [island] + others, self.movies)
        # Either 0 results or fallback — none should be from similarity
        similarity_recs = [r for r in recs if r["source"] == "similarity"]
        self.assertEqual(len(similarity_recs), 0)


# ══════════════════════════════════════════════════
#  Run all tests
# ══════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)
