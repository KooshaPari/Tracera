package ml

import (
	"bytes"
	"path/filepath"
	"testing"
)

func TestSaveLoadAndListContentAddressedModel(t *testing.T) {
	registry, err := NewModelRegistry(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}

	first, err := registry.Save("ranker", "1.0.0", []byte("weights-v1"), FormatSklearn, map[string]string{"auc": "0.7"})
	if err != nil {
		t.Fatal(err)
	}
	second, err := registry.Save("ranker", "1.1.0", []byte("weights-v2"), FormatSklearn, map[string]string{"auc": "0.9"})
	if err != nil {
		t.Fatal(err)
	}

	entries, err := registry.List("ranker")
	if err != nil {
		t.Fatal(err)
	}
	if len(entries) != 2 || entries[0].Version != "1.1.0" {
		t.Fatalf("unexpected entries: %#v", entries)
	}
	if first.SHA256 == second.SHA256 {
		t.Fatal("different payloads should produce different SHA256 pins")
	}
	if filepath.ToSlash(second.ArtifactPath)[:len("models/ranker/1.1.0/blobs/")] != "models/ranker/1.1.0/blobs/" {
		t.Fatalf("unexpected artifact path: %s", second.ArtifactPath)
	}
}

func TestPinnedLoadUsesExactVersionAndSHA(t *testing.T) {
	registry, err := NewModelRegistry(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	if _, err := registry.Save("classifier", "1.0.0", []byte("old"), FormatPytorch, nil); err != nil {
		t.Fatal(err)
	}
	if _, err := registry.Save("classifier", "1.1.0", []byte("new"), FormatPytorch, nil); err != nil {
		t.Fatal(err)
	}
	pinned, err := registry.Pin("classifier", "1.0.0")
	if err != nil {
		t.Fatal(err)
	}

	payload, entry, err := registry.Load("classifier", "")
	if err != nil {
		t.Fatal(err)
	}
	if entry.Version != pinned.Version || entry.SHA256 != pinned.SHA256 || !bytes.Equal(payload, []byte("old")) {
		t.Fatalf("unexpected pinned load: %#v %q", entry, payload)
	}
}

func TestONNXAdapterExtension(t *testing.T) {
	registry, err := NewModelRegistry(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}

	entry, err := registry.Save("detector", "2.0.0", []byte("onnx"), FormatONNX, nil)
	if err != nil {
		t.Fatal(err)
	}

	if filepath.Ext(entry.ArtifactPath) != ".onnx" {
		t.Fatalf("expected .onnx artifact, got %s", entry.ArtifactPath)
	}
	payload, _, err := registry.Load("detector", "2.0.0")
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(payload, []byte("onnx")) {
		t.Fatalf("unexpected payload %q", payload)
	}
}

func TestRejectsNonSemverAndDuplicateVersion(t *testing.T) {
	registry, err := NewModelRegistry(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}

	if _, err := registry.Save("embedder", "v1", []byte("bad"), FormatSklearn, nil); err == nil {
		t.Fatal("expected non-semver version to fail")
	}
	if _, err := registry.Save("embedder", "1.0.0", []byte("first"), FormatSklearn, nil); err != nil {
		t.Fatal(err)
	}
	if _, err := registry.Save("embedder", "1.0.0", []byte("second"), FormatSklearn, nil); err == nil {
		t.Fatal("expected duplicate version to fail")
	}
}
