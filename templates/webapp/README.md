# template-domain-webapp

Domain template layer for web applications. Composes shared commons and language layers.

## Layer Contract

- layer_type: domain
- layer_name: template-domain-webapp
- versioning: semver

## Composition

- base: template-commons
- language layers:
  - template-lang-typescript (primary)
  - template-lang-python (secondary, optional)
