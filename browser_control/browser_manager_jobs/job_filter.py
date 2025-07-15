import re


class JobFilter:
    def __init__(self, filters_config):
        """Initialize job filter with configuration."""
        self.title_filter_words = [
            w.lower() for w in filters_config.get("titleFilterWords", [])
        ]
        self.title_skip_words = [
            w.lower() for w in filters_config.get("titleSkipWords", [])
        ]
        self.bad_words = [w.lower() for w in filters_config.get("badWords", [])]

    def should_skip_by_title(self, job_title):
        """Check if a job should be skipped based on title filters."""
        job_title_lower = job_title.lower()

        # Check title filter words (must match at least one if specified)
        if self.title_filter_words:
            matched = any(
                filter_word in job_title_lower
                for filter_word in self.title_filter_words
            )
            if not matched:
                return True, "Title doesn't match filter words"

        # Check title skip words (skip if any match)
        if self.title_skip_words:
            matched_words = [
                word for word in self.title_skip_words if word in job_title_lower
            ]
            if matched_words:
                return True, f"Title contains skip words {matched_words}"

        return False, "Title passed all filters"

    def should_skip_by_description(self, job_description):
        """Check if a job should be skipped based on description content."""
        if not self.bad_words:
            return False, "No bad words filter"

        job_description_lower = job_description.lower()

        # Check for bad words using word boundaries
        for bad_word in self.bad_words:
            if re.search(r"\b" + re.escape(bad_word) + r"\b", job_description_lower):
                return True, f"Job description contains bad word: {bad_word}"

        return False, "Job description doesn't contain bad words"

    def get_filter_summary(self):
        """Get a summary of current filter settings for logging."""
        return {
            "titleFilterWords": self.title_filter_words[:5]
            + (["..."] if len(self.title_filter_words) > 5 else []),
            "titleSkipWords": self.title_skip_words[:5]
            + (["..."] if len(self.title_skip_words) > 5 else []),
            "badWords": self.bad_words[:5]
            + (["..."] if len(self.bad_words) > 5 else []),
        }
