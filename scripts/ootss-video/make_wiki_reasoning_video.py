"""Compose the WikiTactics SVG replay with the recorded model reasoning."""

import make_reasoning_video as video

video.W = 1500
video.H = 722
video.GAME_W = 991
video.SOURCE_LABEL = 'WikiTactics SVG · 已有轨迹重放'

if __name__ == '__main__':
    video.main()
