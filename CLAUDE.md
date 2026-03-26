# Claude Code Instructions

## Release Process

When releasing to PyPI, always do all three:

1. **Tag the commit**: `git tag v0.X.Y`
2. **Push the tag**: `git push origin --tags`
3. **Create a GitHub release**: `gh release create v0.X.Y --title "v0.X.Y: Short description" --notes "Release notes" --latest`

Don't forget to update `CHANGELOG.md` *before* the release commit.

## Version Bumping

- `pyproject.toml` and `pytheory/__init__.py` must match
- Run `uv lock` after changing the version
- Patch releases (0.X.Y) for bug fixes and small additions
- Minor releases (0.X.0) for new features

## Testing

```
uv run python -m pytest test_pytheory.py -x -q --tb=short -m "not slow"
```

## Publishing

```
uv build && uv publish --token <token> dist/pytheory-0.X.Y*
```

## Music Preferences

- Detune: keep at 8-15, don't go above 25
- Humanize: 0.2 is the sweet spot for melodic parts
- Drum humanize: 0.15 default is good
- No swing unless specifically asked
- Sine and triangle are underrated — use them more
