.PHONY: docs test sync-skill

docs:
	uv run --group docs sphinx-build -b html docs docs/_build/html

test:
	uv run pytest test_pytheory.py -v

# ── Claude Code plugin ──────────────────────────────────────────────
# The skill source of truth lives in plugin/. `sync-skill` mirrors it into the
# standalone marketplace repo (default: ~/repos/pytheory-skill), stamps the
# PyTheory version onto the marketplace manifest as an informational marker, and
# copies the LICENSE. The standalone repo is what gets pushed to GitHub and
# submitted to the plugin marketplace.
#
# The plugin itself has NO version in plugin.json on purpose: actively-developed
# plugins are versioned by git commit SHA, so every pushed commit is a new
# version that installed users pick up — the skill can evolve independently of
# PyTheory releases.
SKILL_REPO ?= $(HOME)/repos/pytheory-skill
VERSION := $(shell python3 -c "import re; print(re.search(r'__version__ = \"([^\"]+)\"', open('pytheory/__init__.py').read()).group(1))")

sync-skill:
	@mkdir -p "$(SKILL_REPO)"
	rsync -a --delete --exclude '.git/' --exclude '.git' plugin/ "$(SKILL_REPO)/"
	cp LICENSE "$(SKILL_REPO)/LICENSE"
	@perl -pi -e 's/"version": "[^"]*"/"version": "$(VERSION)"/' \
		"$(SKILL_REPO)/.claude-plugin/marketplace.json"
	@echo "Synced skill (PyTheory v$(VERSION)) -> $(SKILL_REPO)"
	@echo "Next: cd $(SKILL_REPO) && claude plugin validate . && git add -A && git commit && git push"
