"""Pytest configuration for image color classifier tests."""
import hypothesis

# Configure hypothesis for property-based testing
hypothesis.settings.register_profile(
    "default",
    max_examples=100,
    deadline=None
)
hypothesis.settings.load_profile("default")
