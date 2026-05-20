import type { ForumMockData } from '../types/forum'

function minutesAgo(value: number): string {
  return new Date(Date.now() - value * 60 * 1000).toISOString()
}

function hoursAgo(value: number): string {
  return new Date(Date.now() - value * 60 * 60 * 1000).toISOString()
}

function daysAgo(value: number): string {
  return new Date(Date.now() - value * 24 * 60 * 60 * 1000).toISOString()
}

export const forumMockData: ForumMockData = {
  threads: [
    {
      id: 'thread-1',
      user_id: 'user-demo-1',
      author_username: 'EugenTest',
      author_avatar_id: 'avatar-01',
      title: 'Dune: Part Two really earned the hype',
      text: 'Finally watched it and honestly the scale, sound, and tension were insane. Curious whether people think it is stronger than Part One or just louder.',
      category_type: 'movie',
      custom_category: null,
      score: 12,
      replies_count: 3,
      views: 148,
      created_at: hoursAgo(9),
      updated_at: minutesAgo(22),
      last_activity_at: minutesAgo(22),
      edited: false,
      is_trending: true,
    },
    {
      id: 'thread-2',
      user_id: 'user-demo-2',
      author_username: 'BookWorm99',
      author_avatar_id: 'avatar-02',
      title: 'Books with the same lonely sci-fi feeling as Interstellar',
      text: 'Looking for books that hit with that cosmic loneliness + emotional weight combo. Not just hard sci-fi, more about the feeling.',
      category_type: 'book',
      custom_category: null,
      score: 7,
      replies_count: 2,
      views: 63,
      created_at: hoursAgo(14),
      updated_at: hoursAgo(3),
      last_activity_at: hoursAgo(3),
      edited: false,
    },
    {
      id: 'thread-3',
      user_id: 'user-demo-3',
      author_username: 'MediaTester',
      author_avatar_id: 'avatar-03',
      title: 'Forum UX feedback after testing replies and voting',
      text: 'After playing with topic creation, replies, and voting, I think the flow is solid, but topic sorting by score could be clearer and reply nesting should stay one-level only.',
      category_type: 'custom',
      custom_category: 'Feedback',
      score: 5,
      replies_count: 2,
      views: 41,
      created_at: daysAgo(1),
      updated_at: hoursAgo(6),
      last_activity_at: hoursAgo(6),
      edited: true,
    },
  ],

  postsByThread: {
    'thread-1': [
      {
        id: 'post-1',
        thread_id: 'thread-1',
        user_id: 'user-demo-4',
        author_username: 'NoirLover',
        author_avatar_id: 'avatar-04',
        text: 'For me Part Two is way stronger. The political tension and payoff are on another level.',
        score: 4,
        parent_post_id: null,
        created_at: hoursAgo(7),
        updated_at: hoursAgo(7),
        edited: false,
        replies: [
          {
            id: 'reply-1',
            thread_id: 'thread-1',
            user_id: 'user-demo-1',
            author_username: 'EugenTest',
            author_avatar_id: 'avatar-01',
            text: 'Yeah, that is exactly what hit me too. It felt heavier, not just bigger.',
            score: 2,
            parent_post_id: 'post-1',
            created_at: hoursAgo(6),
            updated_at: hoursAgo(6),
            edited: false,
          },
        ],
      },
      {
        id: 'post-2',
        thread_id: 'thread-1',
        user_id: 'user-demo-5',
        author_username: 'CinemaUA',
        author_avatar_id: 'avatar-05',
        text: 'Part One had more mystery. Part Two had more payoff. Depends what you value more.',
        score: 3,
        parent_post_id: null,
        created_at: hoursAgo(4),
        updated_at: hoursAgo(4),
        edited: false,
        replies: [],
      },
    ],

    'thread-2': [
      {
        id: 'post-3',
        thread_id: 'thread-2',
        user_id: 'user-demo-6',
        author_username: 'SciFiShelf',
        author_avatar_id: 'avatar-06',
        text: 'Try The Left Hand of Darkness for atmosphere, and maybe Solaris for that cold emotional distance.',
        score: 5,
        parent_post_id: null,
        created_at: hoursAgo(10),
        updated_at: hoursAgo(10),
        edited: false,
        replies: [
          {
            id: 'reply-2',
            thread_id: 'thread-2',
            user_id: 'user-demo-2',
            author_username: 'BookWorm99',
            author_avatar_id: 'avatar-02',
            text: 'Solaris was already on my radar, good call.',
            score: 1,
            parent_post_id: 'post-3',
            created_at: hoursAgo(9),
            updated_at: hoursAgo(9),
            edited: false,
          },
        ],
      },
    ],

    'thread-3': [
      {
        id: 'post-4',
        thread_id: 'thread-3',
        user_id: 'user-demo-7',
        author_username: 'DevMirror',
        author_avatar_id: 'avatar-07',
        text: 'Agree about one-level replies. Going deeper would make moderation and layout messy fast.',
        score: 2,
        parent_post_id: null,
        created_at: hoursAgo(8),
        updated_at: hoursAgo(8),
        edited: false,
        replies: [],
      },
      {
        id: 'post-5',
        thread_id: 'thread-3',
        user_id: 'user-demo-8',
        author_username: 'PixelNomad',
        author_avatar_id: 'avatar-08',
        text: 'Sorting by latest activity should probably be default. Score sort is useful, but not as the main view.',
        score: 3,
        parent_post_id: null,
        created_at: hoursAgo(7),
        updated_at: hoursAgo(7),
        edited: false,
        replies: [],
      },
    ],
  },
}