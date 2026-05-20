export type MockReview = {
  id: number
  author: string
  rating: number
  text: string
  timeAgo: string
  helpful: number
}

export const mockReviews: MockReview[] = [
  {
    id: 1,
    author: 'Sarah Jenkins',
    rating: 4.8,
    text: 'A visual masterpiece with a strong emotional core. The scale is huge, but the human story still lands hard.',
    timeAgo: '2 days ago',
    helpful: 124,
  },
  {
    id: 2,
    author: 'Michael Chen',
    rating: 4.4,
    text: 'Ambitious, intelligent, and surprisingly emotional. A few pacing issues, but still a seriously strong watch.',
    timeAgo: '1 week ago',
    helpful: 89,
  },
  {
    id: 3,
    author: 'Elena Rodriguez',
    rating: 4.9,
    text: 'This is exactly the kind of big science-fiction storytelling I come back for. Great tension, great atmosphere.',
    timeAgo: '2 weeks ago',
    helpful: 215,
  },
]