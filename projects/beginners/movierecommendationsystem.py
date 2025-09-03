# Movie Recommendation System (Basic)

import json
import os
import math
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

class Movie:
    def __init__(self, movie_id: int, title: str, genres: List[str], year: int = None):
        self.id = movie_id
        self.title = title
        self.genres = genres
        self.year = year
        self.ratings = []
        self.average_rating = 0.0
        self.rating_count = 0
    
    def add_rating(self, rating: float):
        """Add a rating to the movie"""
        if 1.0 <= rating <= 5.0:
            self.ratings.append(rating)
            self.rating_count = len(self.ratings)
            self.average_rating = sum(self.ratings) / self.rating_count
    
    def to_dict(self) -> Dict:
        """Convert movie to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'genres': self.genres,
            'year': self.year,
            'ratings': self.ratings,
            'average_rating': self.average_rating,
            'rating_count': self.rating_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Movie':
        """Create movie from dictionary"""
        movie = cls(data['id'], data['title'], data['genres'], data.get('year'))
        movie.ratings = data.get('ratings', [])
        movie.average_rating = data.get('average_rating', 0.0)
        movie.rating_count = data.get('rating_count', 0)
        return movie
    
    def __str__(self):
        year_str = f" ({self.year})" if self.year else ""
        rating_str = f" - Rating: {self.average_rating:.1f}/5.0 ({self.rating_count} ratings)" if self.rating_count > 0 else ""
        return f"{self.title}{year_str} [{', '.join(self.genres)}]{rating_str}"

class User:
    def __init__(self, user_id: int, name: str):
        self.id = user_id
        self.name = name
        self.ratings = {}  # movie_id -> rating
        self.favorite_genres = []
    
    def rate_movie(self, movie_id: int, rating: float):
        """Rate a movie"""
        if 1.0 <= rating <= 5.0:
            self.ratings[movie_id] = rating
    
    def get_rating(self, movie_id: int) -> Optional[float]:
        """Get user's rating for a movie"""
        return self.ratings.get(movie_id)
    
    def update_favorite_genres(self, movies: Dict[int, Movie]):
        """Update favorite genres based on highly rated movies"""
        genre_scores = defaultdict(list)
        
        for movie_id, rating in self.ratings.items():
            if movie_id in movies and rating >= 4.0:
                movie = movies[movie_id]
                for genre in movie.genres:
                    genre_scores[genre].append(rating)
        
        # Calculate average rating per genre
        genre_averages = {}
        for genre, ratings in genre_scores.items():
            if len(ratings) >= 2:  # At least 2 highly rated movies
                genre_averages[genre] = sum(ratings) / len(ratings)
        
        # Sort genres by average rating
        self.favorite_genres = sorted(genre_averages.keys(), 
                                    key=lambda g: genre_averages[g], 
                                    reverse=True)[:5]
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'ratings': self.ratings,
            'favorite_genres': self.favorite_genres
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user from dictionary"""
        user = cls(data['id'], data['name'])
        user.ratings = data.get('ratings', {})
        # Convert string keys back to int
        user.ratings = {int(k): v for k, v in user.ratings.items()}
        user.favorite_genres = data.get('favorite_genres', [])
        return user

class MovieRecommendationSystem:
    def __init__(self, data_file: str = "movie_data.json"):
        self.data_file = data_file
        self.movies = {}  # movie_id -> Movie
        self.users = {}   # user_id -> User
        self.load_data()
        
        # Sample data if no data exists
        if not self.movies:
            self._create_sample_data()
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Load movies
                for movie_data in data.get('movies', []):
                    movie = Movie.from_dict(movie_data)
                    self.movies[movie.id] = movie
                
                # Load users
                for user_data in data.get('users', []):
                    user = User.from_dict(user_data)
                    self.users[user.id] = user
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading data: {e}")
                self.movies = {}
                self.users = {}
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            data = {
                'movies': [movie.to_dict() for movie in self.movies.values()],
                'users': [user.to_dict() for user in self.users.values()]
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def _create_sample_data(self):
        """Create sample movies for demonstration"""
        sample_movies = [
            (1, "The Shawshank Redemption", ["Drama", "Crime"], 1994),
            (2, "The Godfather", ["Drama", "Crime"], 1972),
            (3, "The Dark Knight", ["Action", "Crime", "Drama"], 2008),
            (4, "Pulp Fiction", ["Crime", "Drama"], 1994),
            (5, "Forrest Gump", ["Drama", "Romance"], 1994),
            (6, "Inception", ["Action", "Sci-Fi", "Thriller"], 2010),
            (7, "The Matrix", ["Action", "Sci-Fi"], 1999),
            (8, "Goodfellas", ["Biography", "Crime", "Drama"], 1990),
            (9, "The Lord of the Rings: The Return of the King", ["Adventure", "Drama", "Fantasy"], 2003),
            (10, "Fight Club", ["Drama"], 1999),
            (11, "Star Wars: Episode IV - A New Hope", ["Adventure", "Fantasy", "Sci-Fi"], 1977),
            (12, "The Lord of the Rings: The Fellowship of the Ring", ["Adventure", "Drama", "Fantasy"], 2001),
            (13, "One Flew Over the Cuckoo's Nest", ["Drama"], 1975),
            (14, "Interstellar", ["Adventure", "Drama", "Sci-Fi"], 2014),
            (15, "Casablanca", ["Drama", "Romance", "War"], 1942),
            (16, "Titanic", ["Drama", "Romance"], 1997),
            (17, "The Avengers", ["Action", "Adventure", "Sci-Fi"], 2012),
            (18, "Jurassic Park", ["Adventure", "Sci-Fi", "Thriller"], 1993),
            (19, "The Lion King", ["Animation", "Adventure", "Drama"], 1994),
            (20, "Toy Story", ["Animation", "Adventure", "Comedy"], 1995)
        ]
        
        for movie_id, title, genres, year in sample_movies:
            movie = Movie(movie_id, title, genres, year)
            # Add some sample ratings
            import random
            for _ in range(random.randint(10, 50)):
                rating = random.uniform(3.0, 5.0) if random.random() > 0.3 else random.uniform(1.0, 5.0)
                movie.add_rating(rating)
            
            self.movies[movie_id] = movie
        
        self.save_data()
    
    def add_movie(self, title: str, genres: List[str], year: int = None) -> Movie:
        """Add a new movie"""
        movie_id = max(self.movies.keys()) + 1 if self.movies else 1
        movie = Movie(movie_id, title, genres, year)
        self.movies[movie_id] = movie
        self.save_data()
        return movie
    
    def add_user(self, name: str) -> User:
        """Add a new user"""
        user_id = max(self.users.keys()) + 1 if self.users else 1
        user = User(user_id, name)
        self.users[user_id] = user
        self.save_data()
        return user
    
    def rate_movie(self, user_id: int, movie_id: int, rating: float):
        """User rates a movie"""
        if user_id not in self.users or movie_id not in self.movies:
            return False
        
        user = self.users[user_id]
        movie = self.movies[movie_id]
        
        # Remove old rating if exists
        old_rating = user.get_rating(movie_id)
        if old_rating is not None:
            movie.ratings.remove(old_rating)
        
        # Add new rating
        user.rate_movie(movie_id, rating)
        movie.add_rating(rating)
        
        # Update user's favorite genres
        user.update_favorite_genres(self.movies)
        
        self.save_data()
        return True
    
    def get_movies_by_genre(self, genre: str) -> List[Movie]:
        """Get all movies in a specific genre"""
        return [movie for movie in self.movies.values() 
                if genre.lower() in [g.lower() for g in movie.genres]]
    
    def search_movies(self, query: str) -> List[Movie]:
        """Search movies by title"""
        query = query.lower()
        return [movie for movie in self.movies.values() 
                if query in movie.title.lower()]
    
    def get_top_rated_movies(self, limit: int = 10, min_ratings: int = 5) -> List[Movie]:
        """Get top rated movies"""
        eligible_movies = [movie for movie in self.movies.values() 
                          if movie.rating_count >= min_ratings]
        return sorted(eligible_movies, key=lambda m: m.average_rating, reverse=True)[:limit]
    
    def calculate_user_similarity(self, user1_id: int, user2_id: int) -> float:
        """Calculate similarity between two users based on their ratings"""
        if user1_id not in self.users or user2_id not in self.users:
            return 0.0
        
        user1 = self.users[user1_id]
        user2 = self.users[user2_id]
        
        # Find common movies
        common_movies = set(user1.ratings.keys()) & set(user2.ratings.keys())
        
        if len(common_movies) < 2:
            return 0.0
        
        # Calculate Pearson correlation coefficient
        sum1 = sum(user1.ratings[movie] for movie in common_movies)
        sum2 = sum(user2.ratings[movie] for movie in common_movies)
        
        sum1_sq = sum(user1.ratings[movie] ** 2 for movie in common_movies)
        sum2_sq = sum(user2.ratings[movie] ** 2 for movie in common_movies)
        
        sum_products = sum(user1.ratings[movie] * user2.ratings[movie] for movie in common_movies)
        
        n = len(common_movies)
        
        # Calculate Pearson correlation
        numerator = sum_products - (sum1 * sum2 / n)
        denominator = math.sqrt((sum1_sq - sum1**2/n) * (sum2_sq - sum2**2/n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def get_user_based_recommendations(self, user_id: int, limit: int = 10) -> List[Tuple[Movie, float]]:
        """Get recommendations based on similar users (collaborative filtering)"""
        if user_id not in self.users:
            return []
        
        target_user = self.users[user_id]
        
        # Find similar users
        similarities = []
        for other_user_id, other_user in self.users.items():
            if other_user_id != user_id:
                similarity = self.calculate_user_similarity(user_id, other_user_id)
                if similarity > 0:
                    similarities.append((other_user_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get recommendations from similar users
        recommendations = defaultdict(list)
        
        for similar_user_id, similarity in similarities[:10]:  # Top 10 similar users
            similar_user = self.users[similar_user_id]
            
            for movie_id, rating in similar_user.ratings.items():
                # Only recommend movies the target user hasn't rated
                if movie_id not in target_user.ratings and rating >= 4.0:
                    recommendations[movie_id].append(rating * similarity)
        
        # Calculate weighted average scores
        movie_scores = []
        for movie_id, scores in recommendations.items():
            if movie_id in self.movies:
                avg_score = sum(scores) / len(scores)
                movie_scores.append((self.movies[movie_id], avg_score))
        
        # Sort by score and return top recommendations
        movie_scores.sort(key=lambda x: x[1], reverse=True)
        return movie_scores[:limit]
    
    def get_content_based_recommendations(self, user_id: int, limit: int = 10) -> List[Movie]:
        """Get recommendations based on user's favorite genres and ratings"""
        if user_id not in self.users:
            return []
        
        user = self.users[user_id]
        
        # Get unrated movies
        unrated_movies = [movie for movie in self.movies.values() 
                         if movie.id not in user.ratings]
        
        # Score movies based on genre preferences
        movie_scores = []
        
        for movie in unrated_movies:
            score = 0.0
            
            # Genre-based scoring
            for i, genre in enumerate(user.favorite_genres):
                if genre in movie.genres:
                    score += (len(user.favorite_genres) - i) * 2  # Higher weight for more preferred genres
            
            # Add movie's average rating as a factor
            if movie.rating_count > 0:
                score += movie.average_rating
            
            movie_scores.append((movie, score))
        
        # Sort by score and return top recommendations
        movie_scores.sort(key=lambda x: x[1], reverse=True)
        return [movie for movie, score in movie_scores[:limit]]
    
    def get_hybrid_recommendations(self, user_id: int, limit: int = 10) -> List[Movie]:
        """Get hybrid recommendations combining collaborative and content-based filtering"""
        if user_id not in self.users:
            return []
        
        # Get both types of recommendations
        user_based = self.get_user_based_recommendations(user_id, limit * 2)
        content_based = self.get_content_based_recommendations(user_id, limit * 2)
        
        # Combine recommendations
        all_recommendations = {}
        
        # Add user-based recommendations with weight
        for movie, score in user_based:
            all_recommendations[movie.id] = all_recommendations.get(movie.id, 0) + score * 0.7
        
        # Add content-based recommendations with weight
        for movie in content_based:
            all_recommendations[movie.id] = all_recommendations.get(movie.id, 0) + movie.average_rating * 0.3
        
        # Sort and return top recommendations
        sorted_recommendations = sorted(all_recommendations.items(), 
                                      key=lambda x: x[1], reverse=True)
        
        return [self.movies[movie_id] for movie_id, score in sorted_recommendations[:limit]]
    
    def get_movie_statistics(self) -> Dict:
        """Get movie database statistics"""
        if not self.movies:
            return {}
        
        total_movies = len(self.movies)
        total_ratings = sum(movie.rating_count for movie in self.movies.values())
        
        # Genre distribution
        genre_count = defaultdict(int)
        for movie in self.movies.values():
            for genre in movie.genres:
                genre_count[genre] += 1
        
        # Year distribution
        year_count = defaultdict(int)
        for movie in self.movies.values():
            if movie.year:
                decade = (movie.year // 10) * 10
                year_count[f"{decade}s"] += 1
        
        return {
            'total_movies': total_movies,
            'total_users': len(self.users),
            'total_ratings': total_ratings,
            'average_ratings_per_movie': total_ratings / total_movies if total_movies > 0 else 0,
            'most_common_genres': sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:10],
            'movies_by_decade': dict(year_count)
        }

def display_movie_list(movies: List[Movie], title: str = "Movies"):
    """Display a list of movies"""
    print(f"\n=== {title} ===")
    if not movies:
        print("No movies found.")
        return
    
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie}")

def display_recommendations(recommendations: List[Tuple[Movie, float]], title: str = "Recommendations"):
    """Display recommendations with scores"""
    print(f"\n=== {title} ===")
    if not recommendations:
        print("No recommendations available.")
        return
    
    for i, (movie, score) in enumerate(recommendations, 1):
        print(f"{i}. {movie} (Score: {score:.2f})")

def main():
    """Main function to run the movie recommendation system"""
    system = MovieRecommendationSystem()
    current_user_id = None
    
    while True:
        print("\n=== Movie Recommendation System ===")
        print("1. Register/Login User")
        print("2. Browse Movies")
        print("3. Search Movies")
        print("4. Rate Movie")
        print("5. Get Recommendations")
        print("6. View Top Rated Movies")
        print("7. Add New Movie")
        print("8. View Statistics")
        print("9. User Profile")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                print("\n1. Register new user")
                print("2. Login existing user")
                user_choice = input("Enter choice: ").strip()
                
                if user_choice == '1':
                    name = input("Enter your name: ").strip()
                    if name:
                        user = system.add_user(name)
                        current_user_id = user.id
                        print(f"User registered! Your ID is: {user.id}")
                elif user_choice == '2':
                    try:
                        user_id = int(input("Enter your user ID: ").strip())
                        if user_id in system.users:
                            current_user_id = user_id
                            print(f"Logged in as: {system.users[user_id].name}")
                        else:
                            print("User not found!")
                    except ValueError:
                        print("Invalid user ID!")
            
            elif choice == '2':
                print("\n1. All movies")
                print("2. Movies by genre")
                browse_choice = input("Enter choice: ").strip()
                
                if browse_choice == '1':
                    movies = list(system.movies.values())
                    display_movie_list(movies, "All Movies")
                elif browse_choice == '2':
                    genre = input("Enter genre: ").strip()
                    movies = system.get_movies_by_genre(genre)
                    display_movie_list(movies, f"Movies in {genre}")
            
            elif choice == '3':
                query = input("Enter movie title to search: ").strip()
                if query:
                    movies = system.search_movies(query)
                    display_movie_list(movies, f"Search Results for '{query}'")
            
            elif choice == '4':
                if current_user_id is None:
                    print("Please login first!")
                    continue
                
                try:
                    movie_id = int(input("Enter movie ID to rate: ").strip())
                    if movie_id not in system.movies:
                        print("Movie not found!")
                        continue
                    
                    rating = float(input("Enter rating (1.0-5.0): ").strip())
                    if system.rate_movie(current_user_id, movie_id, rating):
                        print("Rating added successfully!")
                    else:
                        print("Error adding rating!")
                        
                except ValueError:
                    print("Invalid input!")
            
            elif choice == '5':
                if current_user_id is None:
                    print("Please login first!")
                    continue
                
                print("\n1. User-based recommendations")
                print("2. Content-based recommendations")
                print("3. Hybrid recommendations")
                rec_choice = input("Enter choice: ").strip()
                
                if rec_choice == '1':
                    recommendations = system.get_user_based_recommendations(current_user_id)
                    display_recommendations(recommendations, "User-based Recommendations")
                elif rec_choice == '2':
                    recommendations = system.get_content_based_recommendations(current_user_id)
                    display_movie_list(recommendations, "Content-based Recommendations")
                elif rec_choice == '3':
                    recommendations = system.get_hybrid_recommendations(current_user_id)
                    display_movie_list(recommendations, "Hybrid Recommendations")
            
            elif choice == '6':
                try:
                    limit = int(input("Enter number of movies to show (default 10): ").strip() or "10")
                    top_movies = system.get_top_rated_movies(limit)
                    display_movie_list(top_movies, f"Top {limit} Rated Movies")
                except ValueError:
                    print("Invalid number!")
            
            elif choice == '7':
                title = input("Enter movie title: ").strip()
                if not title:
                    print("Title cannot be empty!")
                    continue
                
                genres_input = input("Enter genres (comma-separated): ").strip()
                genres = [g.strip() for g in genres_input.split(',') if g.strip()]
                
                year_input = input("Enter year (optional): ").strip()
                year = int(year_input) if year_input else None
                
                movie = system.add_movie(title, genres, year)
                print(f"Movie added with ID: {movie.id}")
            
            elif choice == '8':
                stats = system.get_movie_statistics()
                print("\n=== Movie Database Statistics ===")
                print(f"Total movies: {stats['total_movies']}")
                print(f"Total users: {stats['total_users']}")
                print(f"Total ratings: {stats['total_ratings']}")
                print(f"Average ratings per movie: {stats['average_ratings_per_movie']:.1f}")
                
                if stats['most_common_genres']:
                    print("\nMost common genres:")
                    for genre, count in stats['most_common_genres'][:5]:
                        print(f"  {genre}: {count}")
                
                if stats['movies_by_decade']:
                    print("\nMovies by decade:")
                    for decade, count in sorted(stats['movies_by_decade'].items()):
                        print(f"  {decade}: {count}")
            
            elif choice == '9':
                if current_user_id is None:
                    print("Please login first!")
                    continue
                
                user = system.users[current_user_id]
                print(f"\n=== Profile: {user.name} ===")
                print(f"User ID: {user.id}")
                print(f"Total ratings: {len(user.ratings)}")
                
                if user.favorite_genres:
                    print(f"Favorite genres: {', '.join(user.favorite_genres)}")
                
                if user.ratings:
                    print("\nRecent ratings:")
                    recent_ratings = list(user.ratings.items())[-5:]
                    for movie_id, rating in recent_ratings:
                        if movie_id in system.movies:
                            movie = system.movies[movie_id]
                            print(f"  {movie.title}: {rating}/5.0")
            
            elif choice == '0':
                print("Thank you for using the Movie Recommendation System!")
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
