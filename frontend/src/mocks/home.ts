import type { HomePageData } from '../types/home'

export const homePageData: HomePageData = {
  hero: {
    badge: '#1 TRENDING IN SCI-FI',
    title: 'MediaCompass',
    accentTitle: 'Navigate the Stories.',
    description:
      'Dive into a personalized ocean of cinematic masterpieces and literary wonders. Discover your next obsession with our advanced AI recommendation engine.',
    backgroundImage:
      'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1600&q=80',
    actions: [
      {
        label: 'Explore Recommendations',
        to: '/recommendations',
        variant: 'primary',
      },
      {
        label: 'Learn More',
        to: '/catalog',
        variant: 'secondary',
      },
    ],
  },

  recentlyAdded: [
    {
      id: 1,
      title: 'The Last Horizon',
      category: 'MOVIE',
      rating: 8.9,
      image:
        'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=900&q=80',
    },
    {
      id: 2,
      title: 'Digital Silence',
      category: 'BOOK',
      rating: 4.5,
      image:
        'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=900&q=80',
    },
    {
      id: 3,
      title: 'Neon Echoes',
      category: 'TV SERIES',
      rating: 9.2,
      image:
        'https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=900&q=80',
    },
    {
      id: 4,
      title: 'Shadow Protocol',
      category: 'MOVIE',
      rating: 7.8,
      image:
        'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=900&q=80',
    },
    {
      id: 5,
      title: 'Beyond the Void',
      category: 'BOOK',
      rating: 8.4,
      image:
        'https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=900&q=80',
    },
  ],

  popularFilms: [
    {
      id: 101,
      title: 'Interstellar Echo',
      year: 2024,
      rating: 8.8,
      genres: ['Sci-Fi', 'Drama'],
      image:
        'https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 102,
      title: 'Shadow District',
      year: 2023,
      rating: 8.3,
      genres: ['Thriller', 'Crime'],
      image:
        'https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 103,
      title: 'Solar Drift',
      year: 2025,
      rating: 9.1,
      genres: ['Sci-Fi', 'Adventure'],
      image:
        'https://images.unsplash.com/photo-1440404653325-ab127d49abc1?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 104,
      title: 'Blue Hour Case',
      year: 2022,
      rating: 7.9,
      genres: ['Mystery', 'Drama'],
      image:
        'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=600&q=80',
    },
  ],

  hotTopics: [
    {
      id: 1,
      title: "Is 'The Last Horizon' the best sci-fi of 2026?",
      replies: 42,
      views: 842,
      timeAgo: '2h ago',
      author: 'SpaceFan99',
    },
    {
      id: 2,
      title: "Books similar to 'Digital Silence' but with more grit?",
      replies: 24,
      views: 128,
      timeAgo: '5h ago',
      author: 'BookWorm',
    },
    {
      id: 3,
      title: 'Plot hole discussion: Neon Echoes Episode 4',
      replies: 17,
      views: 2100,
      timeAgo: '10m ago',
      author: 'CyberNix',
    },
    {
      id: 4,
      title: 'Weekly Reading Club: Nebula Award nominees',
      replies: 56,
      views: 442,
      timeAgo: '1d ago',
      author: 'Admin',
    },
  ],

  promoTiles: [
    {
      id: 1,
      alt: 'Reading device',
      image:
        'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 2,
      alt: 'Abstract media art',
      image:
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 3,
      alt: 'Cinema setup',
      image:
        'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 4,
      alt: 'Bookshelf',
      image:
        'https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 5,
      alt: 'Laptop and media',
      image:
        'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 6,
      alt: 'Creative workspace',
      image:
        'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 7,
      alt: 'Book cover layout',
      image:
        'https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 8,
      alt: 'Notebook and ideas',
      image:
        'https://images.unsplash.com/photo-1515378791036-0648a814c963?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 9,
      alt: 'Soft abstract illustration',
      image:
        'https://images.unsplash.com/photo-1516321497487-e288fb19713f?auto=format&fit=crop&w=600&q=80',
    },
  ],
}