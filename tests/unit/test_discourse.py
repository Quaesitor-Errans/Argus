from argus.analysis.discourse_analyzer import (
    DiscourseAnalyzer,
)


def test_basic_metrics():
    analyzer = DiscourseAnalyzer()

    text = (
        "We must protect our country. "
        "They threaten us. "
        "Together we will prevail!"
    )

    metrics = analyzer.analyze(text)

    assert metrics.word_count > 0
    assert metrics.sentence_count == 3
    assert metrics.question_count == 0
    assert metrics.exclamation_count == 1