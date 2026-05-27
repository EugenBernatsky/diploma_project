export const avatarMap: Record<string, string> = {
  avatar_01: '/avatars/avatar_01.jpg',
  avatar_02: '/avatars/avatar_02.jpg',
  avatar_03: '/avatars/avatar_03.jpg',
  avatar_04: '/avatars/avatar_04.jpg',
  avatar_05: '/avatars/avatar_05.jpg',
  avatar_06: '/avatars/avatar_06.jpg',
}

export function getAvatarImageUrl(avatarId?: string | null): string | null {
  if (!avatarId) {
    return null
  }

  return avatarMap[avatarId] ?? null
}