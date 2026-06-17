# ADR-004: Cross-Platform Release Strategy

## Status
Proposed

## Date
2026-06-17

## Context
The Catholic Knowledge System must be distributable as standalone binaries across Linux, macOS, and Windows without requiring users to install Python or manage virtual environments. The final validation is that GitHub Actions produces working releases on all three platforms.

## Decision
Use PyInstaller to produce standalone executables, with platform-specific build scripts orchestrated by GitHub Actions. The release workflow triggers on git tags and produces artifacts for all three platforms.

## Rationale
1. **Zero Dependencies**: Users download a single binary, no Python/pip setup required
2. **CI-CD Validation**: GitHub Actions builds confirm cross-platform compatibility
3. **Reproducibility**: Tagged releases produce deterministic binaries
4. **Distribution**: GitHub Releases provides free hosting and download management

## Alternatives Considered
- **cx_Freeze**: Rejected; PyInstaller has better cross-platform support and simpler config
- **Nuitka**: Rejected; compilation time too long for CI
- **Docker**: Rejected; adds runtime dependency, contradicts local-first simplicity
- **Python wheel distribution**: Rejected; requires Python installed on target machine

## Consequences
- Binary size will be ~50-150MB (includes Python runtime + dependencies)
- Ollama must still be installed separately (it's a separate runtime)
- Platform-specific builds required (Linux, macOS universal, Windows)
- PyInstaller config must be maintained in pyproject.toml
