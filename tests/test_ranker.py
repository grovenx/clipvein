from clipvein.models import Post
from clipvein.ranker import rank, score_post


def _post(pid, views, likes=0, reposts=0, video=False):
    return Post(
        id=pid, url=f"u{pid}", author_handle="@x",
        views=views, likes=likes, reposts=reposts, has_video=video,
    )


def test_below_floor_is_dropped():
    p = _post("1", views=1000, likes=500, video=True)
    scored = score_post(p, min_views=50_000)
    assert scored.score == 0.0
    assert "below" in scored.reasons[0]


def test_high_engagement_video_wins():
    weak = _post("weak", views=1_000_000, likes=2_000, video=True)
    strong = _post("strong", views=500_000, likes=40_000, reposts=8_000, video=True)
    cands, top = rank([weak, strong], min_views=50_000, top_n=3)
    assert top[0].post.id == "strong"
    assert all(c.post.id != "belowfloor" for c in cands)


def test_top_n_limit():
    posts = [_post(str(i), views=100_000 + i * 10_000, likes=5_000, video=True) for i in range(10)]
    _cands, top = rank(posts, min_views=50_000, top_n=3)
    assert len(top) == 3
