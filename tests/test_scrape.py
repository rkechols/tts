import pytest

from tts.scrape.main import chapter_name_from_url, slug_to_title, slugify


@pytest.mark.parametrize(
    "url_and_slug",
    [
        ("https://crosswiredgeeks.com/biologicalchronicle-book9chapter1/", "chapter-1"),
        ("https://crosswiredgeeks.com/biologicalchronicle-book9interlude/", "interlude"),
        ("https://crosswiredgeeks.com/biologicalchronicle-book9chapter2/", "chapter-2"),
        ("https://crosswiredgeeks.com/biologicalchronicle-book9chapter12/", "chapter-12"),
        ("https://crosswiredgeeks.com/biologicalchronicle-book10editorsnote/", "editorsnote"),
        ("https://crosswiredgeeks.com/biologicalchronicle-book10chapter3/", "chapter-3"),
        ("https://crosswiredgeeks.com/biologicalchronicle-book10chapter10/", "chapter-10"),
    ],
)
def test_chapter_name_from_url(url_and_slug: tuple[str, str]):
    url, slug = url_and_slug
    assert chapter_name_from_url(url) == slug


@pytest.mark.parametrize(
    "slug_and_title",
    [
        ("chapter-2", "Chapter 2"),
        ("chapter-10", "Chapter 10"),
        ("editorsnote", "Editorsnote"),
        ("extra-content", "Extra Content"),
    ],
)
def test_slug_to_title(slug_and_title: tuple[str, str]):
    slug, title = slug_and_title
    assert slug_to_title(slug) == title


@pytest.mark.parametrize(
    "s_and_slug",
    [
        ("Sea of Darkness", "sea-of-darkness"),
        ("Journey’s End", "journeys-end"),  # noqa: RUF001
        ("Journey's End", "journeys-end"),
    ],
)
def test_slugify(s_and_slug: tuple[str, str]):
    s, slug = s_and_slug
    assert slugify(s) == slug
