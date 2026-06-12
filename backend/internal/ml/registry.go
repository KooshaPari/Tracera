package ml

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"time"
)

var (
	safePartPattern = regexp.MustCompile(`^[A-Za-z0-9_.-]+$`)
	semverPattern   = regexp.MustCompile(`^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$`)
)

const indexFile = "registry.json"

type Format string

const (
	FormatSklearn Format = "sklearn"
	FormatPytorch Format = "pytorch"
	FormatONNX    Format = "onnx"
)

type ModelEntry struct {
	Name         string            `json:"name"`
	Version      string            `json:"version"`
	SHA256       string            `json:"sha256"`
	Format       Format            `json:"format"`
	ArtifactPath string            `json:"artifact_path"`
	Metadata     map[string]string `json:"metadata,omitempty"`
	CreatedAt    time.Time         `json:"created_at"`
}

type pinnedVersion struct {
	Version string `json:"version"`
	SHA256  string `json:"sha256"`
}

type registryIndex struct {
	Models map[string]map[string]ModelEntry `json:"models"`
	Pins   map[string]pinnedVersion         `json:"pins"`
}

type ModelRegistry struct {
	root string
}

func NewModelRegistry(root string) (*ModelRegistry, error) {
	if err := os.MkdirAll(filepath.Join(root, "models"), 0o755); err != nil {
		return nil, err
	}
	return &ModelRegistry{root: root}, nil
}

func (r *ModelRegistry) Save(
	name string,
	version string,
	model []byte,
	format Format,
	metadata map[string]string,
) (ModelEntry, error) {
	if err := validateName(name); err != nil {
		return ModelEntry{}, err
	}
	if err := validateVersion(version); err != nil {
		return ModelEntry{}, err
	}
	ext, err := extensionFor(format)
	if err != nil {
		return ModelEntry{}, err
	}

	index, err := r.readIndex()
	if err != nil {
		return ModelEntry{}, err
	}
	if index.Models[name] == nil {
		index.Models[name] = map[string]ModelEntry{}
	}
	if _, exists := index.Models[name][version]; exists {
		return ModelEntry{}, fmt.Errorf("model %q version %q already exists", name, version)
	}

	sum := sha256.Sum256(model)
	digest := hex.EncodeToString(sum[:])
	blobDir := filepath.Join(r.root, "models", name, version, "blobs")
	if err := os.MkdirAll(blobDir, 0o755); err != nil {
		return ModelEntry{}, err
	}
	artifact := filepath.Join(blobDir, digest+ext)
	if err := os.WriteFile(artifact, model, 0o644); err != nil {
		return ModelEntry{}, err
	}
	rel, err := filepath.Rel(r.root, artifact)
	if err != nil {
		return ModelEntry{}, err
	}

	entry := ModelEntry{
		Name:         name,
		Version:      version,
		SHA256:       digest,
		Format:       format,
		ArtifactPath: filepath.ToSlash(rel),
		Metadata:     metadata,
		CreatedAt:    time.Now().UTC(),
	}
	index.Models[name][version] = entry
	index.Pins[name] = pinnedVersion{Version: version, SHA256: digest}
	return entry, r.writeIndex(index)
}

func (r *ModelRegistry) Load(name string, version string) ([]byte, ModelEntry, error) {
	entry, err := r.Get(name, version)
	if err != nil {
		return nil, ModelEntry{}, err
	}
	payload, err := os.ReadFile(filepath.Join(r.root, filepath.FromSlash(entry.ArtifactPath)))
	if err != nil {
		return nil, ModelEntry{}, err
	}
	sum := sha256.Sum256(payload)
	if hex.EncodeToString(sum[:]) != entry.SHA256 {
		return nil, ModelEntry{}, errors.New("model artifact SHA256 mismatch")
	}
	return payload, entry, nil
}

func (r *ModelRegistry) Get(name string, version string) (ModelEntry, error) {
	index, err := r.readIndex()
	if err != nil {
		return ModelEntry{}, err
	}
	versions := index.Models[name]
	if len(versions) == 0 {
		return ModelEntry{}, fmt.Errorf("model %q is not registered", name)
	}
	resolved := version
	if resolved == "" {
		pin, ok := index.Pins[name]
		if !ok {
			return ModelEntry{}, fmt.Errorf("model %q has no pinned version", name)
		}
		resolved = pin.Version
	}
	entry, ok := versions[resolved]
	if !ok {
		return ModelEntry{}, fmt.Errorf("model %q version %q is not registered", name, resolved)
	}
	if version == "" {
		pin := index.Pins[name]
		if entry.SHA256 != pin.SHA256 {
			return ModelEntry{}, errors.New("pinned model SHA256 mismatch")
		}
	}
	return entry, nil
}

func (r *ModelRegistry) List(name string) ([]ModelEntry, error) {
	index, err := r.readIndex()
	if err != nil {
		return nil, err
	}
	var entries []ModelEntry
	for modelName, versions := range index.Models {
		if name != "" && modelName != name {
			continue
		}
		for _, entry := range versions {
			entries = append(entries, entry)
		}
	}
	sort.Slice(entries, func(i, j int) bool {
		return entries[i].CreatedAt.After(entries[j].CreatedAt)
	})
	return entries, nil
}

func (r *ModelRegistry) Pin(name string, version string) (ModelEntry, error) {
	index, err := r.readIndex()
	if err != nil {
		return ModelEntry{}, err
	}
	entry, err := r.Get(name, version)
	if err != nil {
		return ModelEntry{}, err
	}
	index.Pins[name] = pinnedVersion{Version: entry.Version, SHA256: entry.SHA256}
	return entry, r.writeIndex(index)
}

func (r *ModelRegistry) readIndex() (registryIndex, error) {
	index := registryIndex{
		Models: map[string]map[string]ModelEntry{},
		Pins:   map[string]pinnedVersion{},
	}
	payload, err := os.ReadFile(filepath.Join(r.root, indexFile))
	if errors.Is(err, os.ErrNotExist) {
		return index, nil
	}
	if err != nil {
		return index, err
	}
	return index, json.Unmarshal(payload, &index)
}

func (r *ModelRegistry) writeIndex(index registryIndex) error {
	payload, err := json.MarshalIndent(index, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(r.root, indexFile), append(payload, '\n'), 0o644)
}

func extensionFor(format Format) (string, error) {
	switch format {
	case FormatSklearn:
		return ".joblib", nil
	case FormatPytorch:
		return ".pt", nil
	case FormatONNX:
		return ".onnx", nil
	default:
		return "", fmt.Errorf("unsupported model format %q", format)
	}
}

func validateName(value string) error {
	if value == "" || !safePartPattern.MatchString(value) {
		return fmt.Errorf("invalid model name %q", value)
	}
	return nil
}

func validateVersion(value string) error {
	if value == "" || !safePartPattern.MatchString(value) || !semverPattern.MatchString(value) {
		return fmt.Errorf("version must be semver: %q", value)
	}
	return nil
}
